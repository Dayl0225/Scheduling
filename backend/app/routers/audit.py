from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database import get_db
from .. import models, schemas

router = APIRouter()

@router.get("/audit-logs/", response_model=list[schemas.AuditLog])
def read_audit_logs(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    logs = db.query(models.AuditLog).offset(skip).limit(limit).all()
    return logs

# Function to log actions (to be called from other places)
def log_action(db: Session, actor_id: str, action_type: str, entity_type: str, entity_id: int, payload: dict = None):
    log = models.AuditLog(
        actor_id=actor_id,
        action_type=action_type,
        entity_type=entity_type,
        entity_id=entity_id,
        payload_json=str(payload) if payload else None
    )
    db.add(log)
    db.commit()