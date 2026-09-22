import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.database import Base
from app.models.all_models import Business, Customer, Lead
from app.schemas.all_schemas import EnquiryRequest
from app.services.enquiry_service import process_customer_enquiry

@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()

@pytest.mark.asyncio
async def test_public_chat_flow_complete(db_session):
    b = Business(id="biz_chat", name="Coorg Travels", owner_id="owner_1")
    db_session.add(b)
    db_session.commit()

    req = EnquiryRequest(
        business_id="biz_chat",
        customer_name="Amit Verma",
        phone="+919888877777",
        message="Need a 5 seater from Bangalore to Mysore for 2 days starting Oct 15 for 4 passengers"
    )

    res = await process_customer_enquiry(req, db_session)

    assert res.extracted.origin == "Bangalore"
    assert res.extracted.destination == "Mysore"
    assert res.extracted.vehicle_type == "5-seater"
    assert res.extracted.duration_days == 2
    assert res.extracted.passenger_count == 4
    assert res.missing_fields == []
    assert "Mysore" in res.reply_message

    # Verify persistent records
    cust = db_session.query(Customer).filter(Customer.phone == "+919888877777").first()
    assert cust is not None
    assert cust.name == "Amit Verma"

    lead = db_session.query(Lead).filter(Lead.customer_id == cust.id).first()
    assert lead is not None
    assert lead.destination == "Mysore"

@pytest.mark.asyncio
async def test_public_chat_flow_missing_info(db_session):
    req = EnquiryRequest(
        business_id="biz_chat",
        customer_name="Neha Gupta",
        phone="+919777766666",
        message="I need a car to Coorg"
    )

    res = await process_customer_enquiry(req, db_session)

    assert res.extracted.destination == "Coorg"
    assert "duration_days" in res.missing_fields
    assert "travel_date" in res.missing_fields
    assert "passenger_count" in res.missing_fields
    assert "number of days" in res.reply_message
