import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.database import Base
from app.schemas.all_schemas import QuoteCalculationRequest
from app.pricing.engine import calculate_deterministic_quote

@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()

def test_deterministic_pricing_7seater(db_session):
    req = QuoteCalculationRequest(
        business_id="test_b",
        vehicle_type="7-seater",
        duration_days=3,
        estimated_km=850.0,  # 3 days * 250 = 750 km included, 100 extra km @ ₹18/km
        include_driver_allowance=True,
        discount_amount=0.0
    )

    res = calculate_deterministic_quote(req, db_session)

    # Base rental: 2599 * 3 = 7797
    # Extra km: 100 * 18 = 1800
    # Driver allowance: 500 * 3 = 1500
    # Subtotal: 7797 + 1800 + 1500 = 11097
    # GST (5%): 554.85
    # Total: 11651.85
    assert res.subtotal == 11097.0
    assert res.tax == 554.85
    assert res.total == 11651.85
    assert res.currency == "INR"
    assert len(res.items) == 3
