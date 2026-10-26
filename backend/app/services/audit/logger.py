from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any, Optional
from app.db.models.core import AuditLog

class AuditLogger:
    @staticmethod
    async def log(
        session: AsyncSession,
        actor: str,
        action: str,
        entity_type: str,
        entity_id: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> AuditLog:
        audit_event = AuditLog(
            actor=actor,
            action=action,
            entity_type=entity_type,
            entity_id=str(entity_id),
            metadata_=metadata or {}
        )
        session.add(audit_event)
        # We don't commit here to allow the caller to group the audit log within their own transaction
        # If the outer transaction rolls back, the audit log won't be saved (which is usually desired for failed transactions)
        return audit_event

audit_logger = AuditLogger()
