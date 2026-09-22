from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.all_schemas import EnquiryRequest, EnquiryResponse
from app.services.enquiry_service import process_customer_enquiry

router = APIRouter(prefix="/enquiries", tags=["enquiries"])

@router.post("", response_model=EnquiryResponse)
async def handle_enquiry(req: EnquiryRequest, db: Session = Depends(get_db)):
    """
    POST /api/v1/enquiries
    Intake customer enquiry message, extract structured fields using AI,
    detect missing information, update conversation context, and update lead CRM status.
    """
    try:
        res = await process_customer_enquiry(req, db)
        return res
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing customer enquiry: {str(e)}"
        )
