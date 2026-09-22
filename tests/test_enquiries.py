import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.database import Base
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
async def test_enquiry_extraction_and_missing_fields(db_session):
    req = EnquiryRequest(
        business_id="test_b",
        customer_name="Rahul Sharma",
        phone="+919876543210",
        message="I need a 7 seater from Bangalore to Coorg for 3 days starting Oct 10th for 6 people"
    )

    res = await process_customer_enquiry(req, db_session)

    assert res.extracted.origin == "Bangalore"
    assert res.extracted.destination == "Coorg"
    assert res.extracted.vehicle_type == "7-seater"
    assert res.extracted.duration_days == 3
    assert res.extracted.passenger_count == 6
    assert res.missing_fields == []
    assert res.lead_score >= 80
