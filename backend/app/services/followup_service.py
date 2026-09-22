import re
from datetime import datetime, timedelta
from typing import List
from sqlalchemy.orm import Session

from app.models.all_models import FollowUp, Lead, Conversation, Message, Customer, AuditLog

OPT_OUT_KEYWORDS = ["stop", "unsubscribe", "opt out", "opt-out", "do not contact", "dont contact", "don't contact", "remove me"]

def check_customer_opt_out(message_text: str) -> bool:
    text_lower = message_text.lower()
    for kw in OPT_OUT_KEYWORDS:
        if re.search(r"\b" + re.escape(kw) + r"\b", text_lower):
            return True
    return False

def handle_customer_opt_out(lead_id: str, db: Session) -> bool:
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        return False

    customer = db.query(Customer).filter(Customer.id == lead.customer_id).first()
    if customer:
        customer.is_opted_out = True

    lead.status = "OPTED_OUT"

    followups = db.query(FollowUp).filter(FollowUp.lead_id == lead_id, FollowUp.status == "SCHEDULED").all()
    for f in followups:
        f.status = "OPTED_OUT"

    db.commit()

    audit = AuditLog(
        actor_type="customer",
        action="CUSTOMER_OPTED_OUT",
        resource_type="lead",
        resource_id=lead_id
    )
    db.add(audit)
    db.commit()

    return True

def schedule_default_followups(lead_id: str, db: Session) -> List[FollowUp]:
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead or lead.status == "OPTED_OUT":
        return []

    customer = db.query(Customer).filter(Customer.id == lead.customer_id).first()
    if customer and customer.is_opted_out:
        return []

    # Cancel any existing scheduled follow-ups for this lead
    existing = db.query(FollowUp).filter(FollowUp.lead_id == lead_id, FollowUp.status == "SCHEDULED").all()
    for f in existing:
        f.status = "CANCELLED"
    db.commit()

    now = datetime.utcnow()
    f1 = FollowUp(
        lead_id=lead_id,
        scheduled_at=now + timedelta(hours=24),
        attempt_number=1,
        message="Hi! Checking in to see if you had any questions regarding your travel quotation?",
        status="SCHEDULED"
    )
    f2 = FollowUp(
        lead_id=lead_id,
        scheduled_at=now + timedelta(hours=48),
        attempt_number=2,
        message="Hi! We have excellent driver availability for your requested travel dates. Would you like to lock in your booking?",
        status="SCHEDULED"
    )
    f3 = FollowUp(
        lead_id=lead_id,
        scheduled_at=now + timedelta(hours=72),
        attempt_number=3,
        message="Hi! This is our final check regarding your trip enquiry. Reply STOP anytime to unsubscribe.",
        status="SCHEDULED"
    )

    db.add_all([f1, f2, f3])
    db.commit()

    lead.status = "FOLLOW_UP"
    db.commit()

    return [f1, f2, f3]

def process_due_followups(db: Session) -> int:
    now = datetime.utcnow()
    due = db.query(FollowUp).filter(
        FollowUp.status == "SCHEDULED",
        FollowUp.scheduled_at <= now
    ).all()

    executed_count = 0
    for f in due:
        lead = db.query(Lead).filter(Lead.id == f.lead_id).first()
        if not lead or lead.status in ["BOOKED", "LOST", "OPTED_OUT", "CANCELLED"]:
            f.status = "CANCELLED" if lead and lead.status != "OPTED_OUT" else "OPTED_OUT"
            db.commit()
            continue

        customer = db.query(Customer).filter(Customer.id == lead.customer_id).first()
        if customer and customer.is_opted_out:
            f.status = "OPTED_OUT"
            db.commit()
            continue

        conv = db.query(Conversation).filter(
            Conversation.business_id == lead.business_id,
            Conversation.customer_id == lead.customer_id
        ).first()

        if conv and conv.last_message_at > f.scheduled_at - timedelta(hours=20):
            f.status = "CANCELLED"
            db.commit()
            continue

        f.status = "EXECUTED"
        f.executed_at = datetime.utcnow()
        db.commit()
        executed_count += 1

        audit = AuditLog(
            actor_type="system",
            action="FOLLOWUP_EXECUTED",
            resource_type="followup",
            resource_id=f.id,
            metadata_json={"lead_id": lead.id, "attempt": f.attempt_number}
        )
        db.add(audit)
        db.commit()

    return executed_count
