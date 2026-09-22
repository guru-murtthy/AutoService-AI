from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy.orm import Session
from app.models.all_models import AuditLog

def check_and_store_idempotency_key(
    idempotency_key: str,
    action: str,
    db: Session,
    ttl_hours: int = 24
) -> bool:
    """
    Validates if an idempotency key has already been processed.
    Returns True if unique (key accepted and recorded), False if duplicate.
    """
    if not idempotency_key:
        return True  # If no idempotency key passed, proceed normally

    existing = db.query(AuditLog).filter(
        AuditLog.action == f"IDEMPOTENCY:{action}",
        AuditLog.resource_id == idempotency_key
    ).first()

    if existing:
        return False  # Duplicate request detected!

    # Record idempotency token
    record = AuditLog(
        actor_type="system",
        action=f"IDEMPOTENCY:{action}",
        resource_type="idempotency_key",
        resource_id=idempotency_key,
        created_at=datetime.utcnow()
    )
    db.add(record)
    db.commit()
    return True
