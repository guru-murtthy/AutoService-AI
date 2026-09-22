from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.core.database import get_db
from app.models.all_models import Lead, Quotation, Booking, Customer, FollowUp, AgentTask
from app.services.revenue_service import calculate_revenue_metrics
from app.services.emergency_stop import is_emergency_stop_active

router = APIRouter(prefix="/dashboard", tags=["dashboard"])

@router.get("/summary")
def get_dashboard_summary(business_id: str, db: Session = Depends(get_db)):
    total_leads = db.query(Lead).filter(Lead.business_id == business_id).count()
    new_leads = db.query(Lead).filter(Lead.business_id == business_id, Lead.status == "NEW").count()
    qualified_leads = db.query(Lead).filter(Lead.business_id == business_id, Lead.status == "QUALIFIED").count()
    quoted_leads = db.query(Lead).filter(Lead.business_id == business_id, Lead.status == "QUOTED").count()
    booked_leads = db.query(Lead).filter(Lead.business_id == business_id, Lead.status == "BOOKED").count()

    total_quotes = db.query(Quotation).join(Lead).filter(Lead.business_id == business_id).count()
    pending_quotes = db.query(Quotation).join(Lead).filter(Lead.business_id == business_id, Quotation.status == "PENDING_APPROVAL").count()
    approved_quotes = db.query(Quotation).join(Lead).filter(Lead.business_id == business_id, Quotation.status == "APPROVED").count()

    pending_followups = db.query(FollowUp).join(Lead).filter(Lead.business_id == business_id, FollowUp.status == "SCHEDULED").count()
    failed_tasks = db.query(AgentTask).filter(AgentTask.status == "FAILED").count()

    revenue_metrics = calculate_revenue_metrics(business_id, db)
    emergency_active = is_emergency_stop_active(db)

    conversion_rate = round((booked_leads / total_leads * 100.0), 1) if total_leads > 0 else 0.0

    return {
        "metrics": {
            "total_leads": total_leads,
            "new_leads": new_leads,
            "qualified_leads": qualified_leads,
            "quoted_leads": quoted_leads,
            "booked_leads": booked_leads,
            "total_quotes": total_quotes,
            "pending_quotes": pending_quotes,
            "approved_quotes": approved_quotes,
            "pending_followups": pending_followups,
            "failed_tasks": failed_tasks,
            "conversion_rate_pct": conversion_rate,
            "emergency_stop_active": emergency_active
        },
        "revenue": revenue_metrics
    }
