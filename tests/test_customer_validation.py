import pytest
from pydantic import ValidationError
from app.schemas.all_schemas import EnquiryRequest, QuoteCalculationRequest, ExtractedRequirement

def test_enquiry_phone_validation():
    # Valid phone
    req = EnquiryRequest(business_id="b1", customer_name="Rahul", phone="+91 98765 43210", message="Hi")
    assert req.phone == "+91 98765 43210"

    # Invalid short phone should raise ValidationError
    with pytest.raises(ValidationError):
        EnquiryRequest(business_id="b1", customer_name="Rahul", phone="123", message="Hi")

def test_enquiry_name_validation():
    # Empty name should raise ValidationError
    with pytest.raises(ValidationError):
        EnquiryRequest(business_id="b1", customer_name="   ", phone="+919876543210", message="Hi")

def test_quote_calculation_validation():
    # Zero or negative duration should raise ValidationError
    with pytest.raises(ValidationError):
        QuoteCalculationRequest(business_id="b1", vehicle_type="7-seater", duration_days=0)

    with pytest.raises(ValidationError):
        QuoteCalculationRequest(business_id="b1", vehicle_type="7-seater", duration_days=-3)
