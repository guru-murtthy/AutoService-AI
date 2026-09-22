import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.database import Base
from app.models.all_models import Business, Customer, Lead, FollowUp
from app.schemas.all_schemas import EnquiryRequest
from app.services.enquiry_service import process_customer_enquiry
from app.services.followup_service import check_customer_opt_out, handle_customer_opt_out, schedule_default_followups, process_due_followups

@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()

def test_opt_out_keyword_detection():
    assert check_customer_opt_out("Please STOP sending me messages") == True
    assert check_customer_opt_out("UNSUBSCRIBE") == True
    assert check_customer_opt_out("do not contact me again") == True
    assert check_customer_opt_out("I need a car to Coorg") == False

@pytest.mark.asyncio
async def test_opt_out_cancellation_flow(db_session):
    b = Business(id="biz_opt", name="Opt Test Agency", owner_id="o1")
    db_session.add(b)
    db_session.commit()

    # Initial enquiry
    req1 = EnquiryRequest(business_id="biz_opt", customer_name="Opt Customer", phone="+919111122222", message="Need a car to Ooty for 2 days")
    res1 = await process_customer_enquiry(req1, db_session)

    # Schedule followups
    schedule_default_followups(res1.lead_id, db_session)
    active_f = db_session.query(FollowUp).filter(FollowUp.lead_id == res1.lead_id, FollowUp.status == "SCHEDULED").all()
    assert len(active_f) == 3

    # Customer sends opt out message
    req2 = EnquiryRequest(business_id="biz_opt", customer_name="Opt Customer", phone="+919111122222", message="Please STOP contacting me")
    res2 = await process_customer_enquiry(req2, db_session)

    assert "unsubscribed" in res2.reply_message.lower()

    # Lead status should be OPTED_OUT
    lead = db_session.query(Lead).filter(Lead.id == res1.lead_id).first()
    assert lead.status == "OPTED_OUT"

    # All followups should be OPTED_OUT
    opted_f = db_session.query(FollowUp).filter(FollowUp.lead_id == res1.lead_id, FollowUp.status == "OPTED_OUT").all()
    assert len(opted_f) == 3
