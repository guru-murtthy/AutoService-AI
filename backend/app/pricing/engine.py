from typing import Dict, Any, List
from sqlalchemy.orm import Session
from app.models.all_models import PricingConfig
from app.schemas.all_schemas import QuoteCalculationRequest, QuoteCalculationResponse, QuoteItemSchema

# Standard Default Indian Tour & Rental Vehicle Rates
DEFAULT_RATES = {
    "5-seater": {"base_per_day": 1999.0, "rate_per_km": 14.0, "driver_allowance_per_day": 400.0},
    "7-seater": {"base_per_day": 2599.0, "rate_per_km": 18.0, "driver_allowance_per_day": 500.0},
    "tempo-traveller": {"base_per_day": 4500.0, "rate_per_km": 24.0, "driver_allowance_per_day": 600.0}
}

def calculate_deterministic_quote(
    req: QuoteCalculationRequest,
    db: Session
) -> QuoteCalculationResponse:
    """
    CRITICAL RULE: Deterministic Calculation Engine.
    LLM is never permitted to set prices. All pricing rules are derived from
    database PricingConfig or strict default rate tables.
    """
    v_type = req.vehicle_type.lower()
    days = max(1, req.duration_days)

    # Fetch custom pricing config from database if present
    cfg = db.query(PricingConfig).filter(
        PricingConfig.business_id == req.business_id,
        PricingConfig.vehicle_type == v_type
    ).first()

    if cfg:
        base_rate = cfg.base_price_per_day
        rate_per_km = cfg.rate_per_km
        driver_allowance_rate = cfg.driver_allowance_per_day
        tax_pct = cfg.tax_percentage
    else:
        # Fallback to default rate lookup
        defaults = DEFAULT_RATES.get(v_type, DEFAULT_RATES["7-seater"])
        base_rate = defaults["base_per_day"]
        rate_per_km = defaults["rate_per_km"]
        driver_allowance_rate = defaults["driver_allowance_per_day"]
        tax_pct = 5.0  # 5% GST for passenger transport

    items: List[QuoteItemSchema] = []

    # 1. Base Vehicle Daily Rental Charge
    vehicle_total = base_rate * days
    items.append(QuoteItemSchema(
        description=f"Vehicle Rental ({req.vehicle_type.title()}) for {days} Day(s)",
        quantity=float(days),
        unit_price=base_rate,
        total=vehicle_total
    ))

    # 2. Additional Kilometres (if specified beyond standard daily allowance of 250 km/day)
    km_total = 0.0
    if req.estimated_km and req.estimated_km > (250 * days):
        extra_km = req.estimated_km - (250 * days)
        km_total = extra_km * rate_per_km
        items.append(QuoteItemSchema(
            description=f"Extra Kilometres ({extra_km:.0f} km @ ₹{rate_per_km}/km)",
            quantity=extra_km,
            unit_price=rate_per_km,
            total=km_total
        ))

    # 3. Driver Allowance
    driver_total = 0.0
    if req.include_driver_allowance:
        driver_total = driver_allowance_rate * days
        items.append(QuoteItemSchema(
            description=f"Driver Allowance ({days} Day(s) @ ₹{driver_allowance_rate:,.0f}/day)",
            quantity=float(days),
            unit_price=driver_allowance_rate,
            total=driver_total
        ))

    subtotal = vehicle_total + km_total + driver_total
    discount = max(0.0, req.discount_amount)
    discounted_subtotal = max(0.0, subtotal - discount)
    
    tax = (discounted_subtotal * tax_pct) / 100.0
    total = discounted_subtotal + tax

    return QuoteCalculationResponse(
        subtotal=round(subtotal, 2),
        tax=round(tax, 2),
        discount=round(discount, 2),
        total=round(total, 2),
        currency="INR",
        items=items
    )
