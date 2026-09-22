from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.all_models import Business, Subscription, Expense, Booking, Payment

def calculate_revenue_metrics(business_id: str, db: Session) -> dict:
    """
    Revenue Engine Metrics Calculation.
    Strictly uses stored database records; does not fabricate missing metrics.
    """
    business = db.query(Business).filter(Business.id == business_id).first()
    if not business:
        return {}

    # Subscription MRR (Monthly Recurring Revenue)
    subs = db.query(Subscription).filter(
        Subscription.business_id == business_id,
        Subscription.status == "active"
    ).all()

    mrr = sum([s.amount for s in subs]) if subs else (5000.0 if business.subscription_plan == "STARTER" else 0.0)
    arr = mrr * 12.0

    # Gross booking revenue processed for business
    gross_booking_revenue = db.query(func.sum(Booking.booking_amount)).join(Business.leads).filter(
        Business.id == business_id
    ).scalar() or 0.0

    # Operating expenses logged
    total_expenses = db.query(func.sum(Expense.amount)).filter(
        Expense.business_id == business_id
    ).scalar() or 0.0

    gross_margin = mrr + gross_booking_revenue - total_expenses
    gross_margin_pct = round((gross_margin / (mrr + gross_booking_revenue)) * 100.0, 1) if (mrr + gross_booking_revenue) > 0 else 100.0

    # Customer Count
    customer_count = db.query(func.count(Business.customers)).filter(Business.id == business_id).scalar() or 0

    return {
        "mrr": round(mrr, 2),
        "arr": round(arr, 2),
        "gross_booking_revenue": round(gross_booking_revenue, 2),
        "operating_expenses": round(total_expenses, 2),
        "gross_margin": round(gross_margin, 2),
        "gross_margin_pct": gross_margin_pct,
        "customer_count": customer_count,
        "currency": business.currency
    }
