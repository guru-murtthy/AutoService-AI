from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.all_models import Business, AuditLog

router = APIRouter(prefix="/settings", tags=["settings"])

class BusinessProfileSchema(BaseModel):
    name: str
    business_type: Optional[str] = "travel_and_tour"
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    location: Optional[str] = None
    gst_number: Optional[str] = None
    logo_url: Optional[str] = None
    contact_person: Optional[str] = None
    currency: str = "INR"
    timezone: str = "Asia/Kolkata"

@router.get("/business/{business_id}")
def get_business_profile(business_id: str, db: Session = Depends(get_db)):
    biz = db.query(Business).filter(Business.id == business_id).first()
    if not biz:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Business not found")
    return {
        "id": biz.id,
        "name": biz.name,
        "business_type": biz.business_type,
        "phone": biz.phone,
        "email": biz.email,
        "address": biz.address,
        "location": biz.location,
        "gst_number": biz.gst_number,
        "logo_url": biz.logo_url,
        "contact_person": biz.contact_person,
        "currency": biz.currency,
        "timezone": biz.timezone,
        "pilot_business": biz.pilot_business,
        "pilot_status": biz.pilot_status
    }

@router.post("/business/{business_id}")
def update_business_profile(business_id: str, payload: BusinessProfileSchema, db: Session = Depends(get_db)):
    biz = db.query(Business).filter(Business.id == business_id).first()
    if not biz:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Business not found")

    biz.name = payload.name
    biz.business_type = payload.business_type or "travel_and_tour"
    biz.phone = payload.phone
    biz.email = payload.email
    biz.address = payload.address
    biz.location = payload.location
    biz.gst_number = payload.gst_number
    biz.logo_url = payload.logo_url
    biz.contact_person = payload.contact_person
    biz.currency = payload.currency
    biz.timezone = payload.timezone

    db.commit()
    db.refresh(biz)

    audit = AuditLog(
        actor_type="user",
        business_id=business_id,
        action="BUSINESS_PROFILE_UPDATED",
        resource_type="business",
        resource_id=business_id
    )
    db.add(audit)
    db.commit()

    return {"status": "updated", "business_id": biz.id, "name": biz.name}
