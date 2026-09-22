from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.all_models import AuditLog, SystemHealth
from app.schemas.all_schemas import EmergencyStopRequest, EmergencyStopStatus
from app.services.emergency_stop import activate_emergency_stop, deactivate_emergency_stop, is_emergency_stop_active

router = APIRouter(prefix="/admin", tags=["admin"])

@router.post("/emergency-stop", response_model=EmergencyStopStatus)
def trigger_emergency_stop(req: EmergencyStopRequest, db: Session = Depends(get_db)):
    """
    POST /api/v1/admin/emergency-stop
    Instantly halts all outbound communication, autonomous agent tools, and payment actions.
    Preserves audit logs and dashboard access.
    """
    config = activate_emergency_stop(req.reason, actor="admin_user", db=db)
    return EmergencyStopStatus(
        is_active=config.is_active,
        activated_by=config.activated_by,
        activated_at=config.activated_at,
        reason=config.reason
    )

@router.post("/emergency-stop/deactivate", response_model=EmergencyStopStatus)
def resume_normal_operations(db: Session = Depends(get_db)):
    config = deactivate_emergency_stop(actor="admin_user", db=db)
    return EmergencyStopStatus(
        is_active=config.is_active,
        activated_by=config.activated_by,
        activated_at=config.activated_at,
        reason=config.reason
    )

@router.get("/emergency-stop/status", response_model=EmergencyStopStatus)
def get_emergency_status(db: Session = Depends(get_db)):
    from app.models.all_models import EmergencyStopConfig
    config = db.query(EmergencyStopConfig).filter(EmergencyStopConfig.id == "default_config").first()
    if not config:
        return EmergencyStopStatus(is_active=False, activated_by=None, activated_at=None, reason=None)
    return EmergencyStopStatus(
        is_active=config.is_active,
        activated_by=config.activated_by,
        activated_at=config.activated_at,
        reason=config.reason
    )

@router.get("/audit-logs")
def get_audit_logs(limit: int = 50, db: Session = Depends(get_db)):
    logs = db.query(AuditLog).order_by(AuditLog.created_at.desc()).limit(limit).all()
    return logs

@router.get("/system-health")
def get_system_health(db: Session = Depends(get_db)):
    health_entries = db.query(SystemHealth).order_by(SystemHealth.checked_at.desc()).limit(10).all()
    return health_entries
