import uuid
from datetime import datetime, timedelta
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.all_models import Quotation, QuotationItem, Lead, Business, Customer, AuditLog
from app.schemas.all_schemas import QuoteCalculationRequest, QuoteCalculationResponse, QuotationCreateRequest, QuotationResponse
from app.pricing.engine import calculate_deterministic_quote
from app.quotations.pdf_generator import generate_quotation_pdf

router = APIRouter(prefix="/quotations", tags=["quotations"])

@router.post("/calculate", response_model=QuoteCalculationResponse)
def calculate_quote(req: QuoteCalculationRequest, db: Session = Depends(get_db)):
    """
    POST /api/v1/quotations/calculate
    Pure deterministic price breakdown endpoint.
    """
    return calculate_deterministic_quote(req, db)

@router.post("", response_model=QuotationResponse)
def create_quotation(req: QuotationCreateRequest, db: Session = Depends(get_db)):
    """
    POST /api/v1/quotations
    Create a new Quotation record in PENDING_APPROVAL status.
    """
    lead = db.query(Lead).filter(Lead.id == req.lead_id).first()
    if not lead:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lead not found")

    q_number = f"QT-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:4].upper()}"
    valid_until = datetime.utcnow() + timedelta(days=req.valid_days)

    quotation = Quotation(
        lead_id=lead.id,
        quotation_number=q_number,
        subtotal=req.calculation.subtotal,
        tax=req.calculation.tax,
        discount=req.calculation.discount,
        total=req.calculation.total,
        currency="INR",
        status="PENDING_APPROVAL",  # Approval workflow requirement
        valid_until=valid_until
    )
    db.add(quotation)
    db.commit()
    db.refresh(quotation)

    for item in req.calculation.items:
        q_item = QuotationItem(
            quotation_id=quotation.id,
            description=item.description,
            quantity=item.quantity,
            unit_price=item.unit_price,
            total=item.total
        )
        db.add(q_item)
    
    lead.status = "QUOTED"
    db.commit()

    # Record Audit Log
    audit = AuditLog(
        actor_type="system",
        action="QUOTATION_CREATED",
        resource_type="quotation",
        resource_id=quotation.id,
        metadata_json={"quotation_number": q_number, "total": req.calculation.total}
    )
    db.add(audit)
    db.commit()

    return QuotationResponse.model_validate(quotation)

@router.get("/{quote_id}/pdf")
def download_quotation_pdf(quote_id: str, db: Session = Depends(get_db)):
    quotation = db.query(Quotation).filter(Quotation.id == quote_id).first()
    if not quotation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Quotation not found")

    lead = db.query(Lead).filter(Lead.id == quotation.lead_id).first()
    customer = db.query(Customer).filter(Customer.id == lead.customer_id).first() if lead else None
    business = db.query(Business).filter(Business.id == lead.business_id).first() if lead else None

    items = db.query(QuotationItem).filter(QuotationItem.quotation_id == quotation.id).all()
    calc_dict = {
        "subtotal": quotation.subtotal,
        "tax": quotation.tax,
        "discount": quotation.discount,
        "total": quotation.total,
        "items": [{"description": i.description, "quantity": i.quantity, "unit_price": i.unit_price, "total": i.total} for i in items]
    }

    pdf_bytes = generate_quotation_pdf(
        quotation_number=quotation.quotation_number,
        business_name=business.name if business else "AutoService Travel",
        customer_name=customer.name if customer else "Valued Customer",
        customer_phone=customer.phone if customer else "N/A",
        travel_details={
            "origin": lead.origin if lead else "Bangalore",
            "destination": lead.destination if lead else "Outstation",
            "vehicle_type": lead.vehicle_type if lead else "7-seater"
        },
        calculation=calc_dict,
        valid_until=quotation.valid_until.strftime("%d %b %Y") if quotation.valid_until else "7 Days"
    )

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"inline; filename={quotation.quotation_number}.pdf"}
    )

@router.post("/{quote_id}/approve", response_model=QuotationResponse)
def approve_quotation(quote_id: str, db: Session = Depends(get_db)):
    """
    Human Owner Approval Action.
    Moves status from PENDING_APPROVAL -> APPROVED.
    """
    quotation = db.query(Quotation).filter(Quotation.id == quote_id).first()
    if not quotation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Quotation not found")

    quotation.status = "APPROVED"
    quotation.approved_by = "business_owner"
    db.commit()
    db.refresh(quotation)

    audit = AuditLog(
        actor_type="user",
        action="QUOTATION_APPROVED",
        resource_type="quotation",
        resource_id=quotation.id
    )
    db.add(audit)
    db.commit()

    return QuotationResponse.model_validate(quotation)
