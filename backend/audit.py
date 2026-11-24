from sqlalchemy.orm import Session

from backend.database.models import AuditLog


def log_action(
    db: Session,
    action: str,
    description: str,
    entity_type: str = None,
    entity_id: int = None
):
    audit_entry = AuditLog(
        action=action,
        description=description,
        entity_type=entity_type,
        entity_id=entity_id
    )

    db.add(audit_entry)
    db.commit()

    return audit_entry