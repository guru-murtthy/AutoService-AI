from datetime import datetime, date, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.all_models import Lead, Quotation, Booking, Payment, Expense, FollowUp, AgentTask, Conversation
from app.schemas.all_schemas import DailyReportResponse

def generate_daily_report(business_id: str, target_date: date, db: Session) -> DailyReportResponse:
    start_dt = datetime.combine(target_date, datetime.min.time())
    end_dt = datetime.combine(target_date, datetime.max.time())

    # 1. Enquiries & Qualified Leads
    enquiries_count = db.query(Lead).filter(
        Lead.business_id == business_id,
        Lead.created_at >= start_dt,
        Lead.created_at <= end_dt
    ).count()

    qualified_leads = db.query(Lead).filter(
        Lead.business_id == business_id,
        Lead.created_at >= start_dt,
        Lead.created_at <= end_dt,
        Lead.status != "NEW"
    ).count()

    # 2. Quotations
    quotes_query = db.query(Quotation).join(Lead).filter(
        Lead.business_id == business_id,
        Quotation.created_at >= start_dt,
        Quotation.created_at <= end_dt
    )
    quotes_generated = quotes_query.count()

    quotes_accepted = db.query(Quotation).join(Lead).filter(
        Lead.business_id == business_id,
        Quotation.created_at >= start_dt,
        Quotation.created_at <= end_dt,
        Quotation.status == "ACCEPTED"
    ).count()

    # 3. Bookings & Revenue
    bookings_count = db.query(Booking).join(Lead).filter(
        Lead.business_id == business_id,
        Booking.created_at >= start_dt,
        Booking.created_at <= end_dt
    ).count()

    revenue_sum = db.query(func.sum(Booking.booking_amount)).join(Lead).filter(
        Lead.business_id == business_id,
        Booking.created_at >= start_dt,
        Booking.created_at <= end_dt
    ).scalar() or 0.0

    # 4. Pending Follow-Ups & Failed Tasks
    pending_followups = db.query(FollowUp).join(Lead).filter(
        Lead.business_id == business_id,
        FollowUp.status == "SCHEDULED"
    ).count()

    failed_tasks = db.query(AgentTask).filter(
        AgentTask.created_at >= start_dt,
        AgentTask.created_at <= end_dt,
        AgentTask.status == "FAILED"
    ).count()

    # 5. Estimated AI Cost (Estimated based on ₹1.50 per customer enquiry process)
    estimated_ai_cost = round(enquiries_count * 1.50, 2)
    net_contribution = round(revenue_sum - estimated_ai_cost, 2)

    return DailyReportResponse(
        date=target_date.isoformat(),
        enquiries_count=enquiries_count,
        qualified_leads=qualified_leads,
        quotes_generated=quotes_generated,
        quotes_accepted=quotes_accepted,
        bookings_count=bookings_count,
        revenue_amount=round(revenue_sum, 2),
        pending_followups=pending_followups,
        failed_tasks=failed_tasks,
        estimated_ai_cost=estimated_ai_cost,
        net_contribution=net_contribution
    )
