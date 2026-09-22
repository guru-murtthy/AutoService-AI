import pytest
from datetime import date
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.database import Base
from app.models.all_models import Business, Customer, Lead, Quotation, Booking, Payment
from app.schemas.all_schemas import EnquiryRequest, QuoteCalculationRequest, QuotationCreateRequest
from app.services.enquiry_service import process_customer_enquiry
from app.pricing.engine import calculate_deterministic_quote
from app.quotations.pdf_generator import generate_quotation_pdf
from app.services.followup_service import schedule_default_followups, process_due_followups
from app.services.analytics_service import generate_daily_report

@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()

@pytest.mark.asyncio
async def test_full_business_lifecycle_e2e(db_session):
    # 1. Setup Business
    b = Business(id="b_e2e", name="Coorg Tour Operators", owner_id="owner_1", subscription_plan="STARTER")
    db_session.add(b)
    db_session.commit()

    # 2. Customer Enquiry Intake & Requirement Extraction
    req = EnquiryRequest(
        business_id="b_e2e",
        customer_name="Priya Patel",
        phone="+919988776655",
        message="I need a 7 seater from Bangalore to Coorg for 3 days starting Oct 10th for 5 people"
    )
    enquiry_res = await process_customer_enquiry(req, db_session)
    assert enquiry_res.lead_id is not None
    assert enquiry_res.missing_fields == []

    # 3. Calculate Deterministic Quotation
    calc_req = QuoteCalculationRequest(
        business_id="b_e2e",
        vehicle_type=enquiry_res.extracted.vehicle_type,
        duration_days=enquiry_res.extracted.duration_days,
        estimated_km=800.0
    )
    calc_res = calculate_deterministic_quote(calc_req, db_session)
    assert calc_res.total > 0

    # 4. Generate PDF Quotation
    pdf_bytes = generate_quotation_pdf(
        quotation_number="QT-E2E-001",
        business_name="Coorg Tour Operators",
        customer_name="Priya Patel",
        customer_phone="+919988776655",
        travel_details={"origin": "Bangalore", "destination": "Coorg", "vehicle_type": "7-seater"},
        calculation=calc_res.model_dump(),
        valid_until="7 Days"
    )
    assert len(pdf_bytes) > 1000

    # 5. Schedule & Process Follow-ups
    followups = schedule_default_followups(enquiry_res.lead_id, db_session)
    assert len(followups) == 3

    # 6. Confirm Booking & Payment
    lead = db_session.query(Lead).filter(Lead.id == enquiry_res.lead_id).first()
    quote = Quotation(lead_id=lead.id, quotation_number="QT-E2E-001", subtotal=calc_res.subtotal, tax=calc_res.tax, total=calc_res.total, status="ACCEPTED")
    db_session.add(quote)
    db_session.commit()

    booking = Booking(lead_id=lead.id, quotation_id=quote.id, status="CONFIRMED", booking_amount=calc_res.total)
    db_session.add(booking)
    db_session.commit()

    payment = Payment(booking_id=booking.id, amount=calc_res.total, status="SUCCESS", provider="mock")
    db_session.add(payment)
    lead.status = "BOOKED"
    db_session.commit()

    # 7. Generate Daily Report
    report = generate_daily_report("b_e2e", date.today(), db_session)
    assert report.enquiries_count == 1
    assert report.bookings_count == 1
    assert report.revenue_amount == calc_res.total
    assert report.net_contribution > 0
