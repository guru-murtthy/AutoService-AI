from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Header, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.all_models import Business, Customer, Conversation, Message, Lead, Quotation
from app.schemas.all_schemas import EnquiryRequest, EnquiryResponse
from app.services.enquiry_service import process_customer_enquiry
from app.core.idempotency import check_and_store_idempotency_key

router = APIRouter(prefix="/public/chat", tags=["public_chat"])

class PublicChatMessageRequest(BaseModel):
    customer_name: str
    phone: str
    message: str
    email: Optional[str] = None

@router.post("/{business_id}/message", response_model=EnquiryResponse)
async def post_public_customer_message(
    business_id: str,
    payload: PublicChatMessageRequest,
    x_idempotency_key: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    """
    Public Customer Web Chat intake endpoint: /api/v1/public/chat/{business_id}/message
    Processes natural language enquiry, extracts structured requirements, checks missing info,
    and returns AI response & quote state.
    Includes Idempotency protection.
    """
    biz = db.query(Business).filter(Business.id == business_id).first()
    if not biz:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Business not found")

    if x_idempotency_key:
        is_unique = check_and_store_idempotency_key(x_idempotency_key, "PUBLIC_CHAT_MESSAGE", db)
        if not is_unique:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Duplicate message event ignored by idempotency filter")

    enquiry_req = EnquiryRequest(
        business_id=business_id,
        customer_name=payload.customer_name,
        phone=payload.phone,
        email=payload.email,
        message=payload.message
    )

    res = await process_customer_enquiry(enquiry_req, db)
    return res

@router.get("/{business_id}/history")
def get_public_customer_chat_history(
    business_id: str,
    phone: str,
    db: Session = Depends(get_db)
):
    cust = db.query(Customer).filter(Customer.business_id == business_id, Customer.phone == phone).first()
    if not cust:
        return {"messages": [], "lead": None, "quotation": None}

    conv = db.query(Conversation).filter(Conversation.business_id == business_id, Conversation.customer_id == cust.id).first()
    if not conv:
        return {"messages": [], "lead": None, "quotation": None}

    messages = db.query(Message).filter(Message.conversation_id == conv.id).order_by(Message.created_at.asc()).all()
    lead = db.query(Lead).filter(Lead.business_id == business_id, Lead.customer_id == cust.id).first()
    
    quotation = None
    if lead:
        q = db.query(Quotation).filter(Quotation.lead_id == lead.id).order_by(Quotation.created_at.desc()).first()
        if q:
            quotation = {
                "quotation_number": q.quotation_number,
                "total": q.total,
                "status": q.status,
                "pdf_url": f"/api/v1/quotations/{q.id}/pdf"
            }

    return {
        "messages": [{"id": m.id, "sender": m.sender_type, "message": m.message, "created_at": m.created_at.isoformat()} for m in messages],
        "lead": {
            "status": lead.status,
            "destination": lead.destination,
            "vehicle_type": lead.vehicle_type,
            "travel_date": lead.travel_date
        } if lead else None,
        "quotation": quotation
    }
