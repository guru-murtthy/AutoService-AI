from datetime import date
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.all_schemas import DailyReportResponse
from app.services.analytics_service import generate_daily_report

router = APIRouter(prefix="/reports", tags=["reports"])

@router.get("/daily", response_model=DailyReportResponse)
def get_daily_report(
    business_id: str,
    target_date: Optional[str] = None,
    db: Session = Depends(get_db)
):
    d = date.today()
    if target_date:
        try:
            d = date.fromisoformat(target_date)
        except ValueError:
            pass
    return generate_daily_report(business_id, d, db)
