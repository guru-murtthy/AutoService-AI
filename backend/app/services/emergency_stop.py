from datetime import datetime
from sqlalchemy.orm import Session
from app.models.all_models import EmergencyStopConfig, AuditLog

def is_emergency_stop_active(db: Session) -> bool:
    config = db.query(EmergencyStopConfig).filter(EmergencyStopConfig.id == "default_config").first()
    if config:
        return config.is_active
    return False

def activate_emergency_stop(reason: str, actor: str, db: Session) -> EmergencyStopConfig:
    config = db.query(EmergencyStopConfig).filter(EmergencyStopConfig.id == "default_config").first()
    if not config:
        config = EmergencyStopConfig(id="default_config")
        db.add(config)
    
    config.is_active = True
    config.activated_by = actor
    config.activated_at = datetime.utcnow()
    config.reason = reason
    db.commit()
    db.refresh(config)

    # Log critical audit entry
    audit = AuditLog(
        actor_type="user",
        actor_id=actor,
        action="EMERGENCY_STOP_ACTIVATED",
        resource_type="system",
        resource_id="emergency_stop",
        metadata_json={"reason": reason}
    )
    db.add(audit)
    db.commit()

    return config

def deactivate_emergency_stop(actor: str, db: Session) -> EmergencyStopConfig:
    config = db.query(EmergencyStopConfig).filter(EmergencyStopConfig.id == "default_config").first()
    if config:
        config.is_active = False
        db.commit()
        db.refresh(config)

        audit = AuditLog(
            actor_type="user",
            actor_id=actor,
            action="EMERGENCY_STOP_DEACTIVATED",
            resource_type="system",
            resource_id="emergency_stop"
        )
        db.add(audit)
        db.commit()
    return config
