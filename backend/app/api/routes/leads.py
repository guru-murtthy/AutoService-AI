from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import verify_business_access
from app.models.all_models import Lead, Customer
from app.schemas.all_schemas import LeadResponse, LeadStatusUpdate

router = APIRouter(prefix="/leads", tags=["leads"])

@router.get("", response_model=List[LeadResponse])
def list_leads(business_id: str, verified: bool = Depends(verify_business_access), db: Session = Depends(get_db)):
    leads = db.query(Lead).filter(Lead.business_id == business_id).order_by(Lead.updated_at.desc()).all()
    results = []
    for l in leads:
        customer = db.query(Customer).filter(Customer.id == l.customer_id).first()
        res = LeadResponse(
            id=l.id,
            business_id=l.business_id,
            customer_id=l.customer_id,
            customer_name=customer.name if customer else "Unknown",
            customer_phone=customer.phone if customer else None,
            destination=l.destination,
            origin=l.origin,
            duration_days=l.duration_days,
            travel_date=l.travel_date,
            passenger_count=l.passenger_count,
            vehicle_type=l.vehicle_type,
            budget=l.budget,
            status=l.status,
            lead_score=l.lead_score,
            created_at=l.created_at
        )
        results.append(res)
    return results

@router.patch("/{lead_id}/status", response_model=LeadResponse)
def update_lead_status(lead_id: str, payload: LeadStatusUpdate, db: Session = Depends(get_db)):
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lead not found")
    
    lead.status = payload.status
    db.commit()
    db.refresh(lead)

    customer = db.query(Customer).filter(Customer.id == lead.customer_id).first()
    return LeadResponse(
        id=lead.id,
        business_id=lead.business_id,
        customer_id=lead.customer_id,
        customer_name=customer.name if customer else "Unknown",
        customer_phone=customer.phone if customer else None,
        destination=lead.destination,
        origin=lead.origin,
        duration_days=lead.duration_days,
        travel_date=lead.travel_date,
        passenger_count=lead.passenger_count,
        vehicle_type=lead.vehicle_type,
        budget=lead.budget,
        status=lead.status,
        lead_score=lead.lead_score,
        created_at=lead.created_at
    )
