from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.all_models import PricingConfig, Business

router = APIRouter(prefix="/pricing", tags=["pricing"])

class PricingConfigSchema(BaseModel):
    vehicle_type: str
    base_price_per_day: float
    included_km_per_day: float = 250.0
    rate_per_km: float = 14.0
    driver_allowance_per_day: float = 400.0
    tax_percentage: float = 5.0
    cancellation_policy: Optional[str] = "Full refund 48h prior to departure."
    validity_days: int = 7
    terms_and_conditions: Optional[str] = "1. Tolls at actuals. 2. Driver allowance per day."

@router.get("/{business_id}")
def get_pricing_configs(business_id: str, db: Session = Depends(get_db)):
    configs = db.query(PricingConfig).filter(PricingConfig.business_id == business_id).all()
    if not configs:
        # Generate default pricing profile for business
        default_configs = [
            PricingConfig(business_id=business_id, vehicle_type="5-seater", base_price_per_day=1999.0, rate_per_km=14.0, driver_allowance_per_day=400.0),
            PricingConfig(business_id=business_id, vehicle_type="7-seater", base_price_per_day=2599.0, rate_per_km=18.0, driver_allowance_per_day=500.0),
            PricingConfig(business_id=business_id, vehicle_type="tempo-traveller", base_price_per_day=4500.0, rate_per_km=24.0, driver_allowance_per_day=600.0)
        ]
        db.add_all(default_configs)
        db.commit()
        configs = default_configs

    return [{
        "id": c.id,
        "vehicle_type": c.vehicle_type,
        "base_price_per_day": c.base_price_per_day,
        "included_km_per_day": c.included_km_per_day,
        "rate_per_km": c.rate_per_km,
        "driver_allowance_per_day": c.driver_allowance_per_day,
        "tax_percentage": c.tax_percentage,
        "cancellation_policy": c.cancellation_policy,
        "validity_days": c.validity_days,
        "terms_and_conditions": c.terms_and_conditions
    } for c in configs]

@router.post("/{business_id}")
def update_pricing_config(business_id: str, payload: PricingConfigSchema, db: Session = Depends(get_db)):
    cfg = db.query(PricingConfig).filter(
        PricingConfig.business_id == business_id,
        PricingConfig.vehicle_type == payload.vehicle_type
    ).first()

    if not cfg:
        cfg = PricingConfig(business_id=business_id, vehicle_type=payload.vehicle_type, base_price_per_day=payload.base_price_per_day)
        db.add(cfg)

    cfg.base_price_per_day = payload.base_price_per_day
    cfg.included_km_per_day = payload.included_km_per_day
    cfg.rate_per_km = payload.rate_per_km
    cfg.driver_allowance_per_day = payload.driver_allowance_per_day
    cfg.tax_percentage = payload.tax_percentage
    if payload.cancellation_policy: cfg.cancellation_policy = payload.cancellation_policy
    cfg.validity_days = payload.validity_days
    if payload.terms_and_conditions: cfg.terms_and_conditions = payload.terms_and_conditions

    db.commit()
    db.refresh(cfg)
    return {"status": "updated", "vehicle_type": cfg.vehicle_type, "base_price": cfg.base_price_per_day}
