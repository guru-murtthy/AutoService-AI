from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.all_models import FollowUp
from app.services.followup_service import schedule_default_followups, process_due_followups

router = APIRouter(prefix="/followups", tags=["followups"])

@router.post("/schedule/{lead_id}")
def schedule_lead_followups(lead_id: str, db: Session = Depends(get_db)):
    followups = schedule_default_followups(lead_id, db)
    return {"status": "scheduled", "count": len(followups)}

@router.post("/trigger-due")
def trigger_due_followups(db: Session = Depends(get_db)):
    executed_count = process_due_followups(db)
    return {"status": "processed", "executed_count": executed_count}
