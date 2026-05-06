from typing import Any

from django.core.exceptions import ValidationError
from django.db import models

from apps.audit.models import AuditActorType, AuditEvent


def _entity_identity(entity: models.Model | None) -> tuple[str, str]:
    if entity is None:
        return "", ""
    return entity._meta.label_lower, str(entity.pk)


def log_audit_event(
    *,
    action: str,
    actor=None,
    actor_type: str | None = None,
    entity: models.Model | None = None,
    entity_type: str = "",
    entity_id: str = "",
    car=None,
    context: dict[str, Any] | None = None,
    metadata: dict[str, Any] | None = None,
) -> AuditEvent:
    action = action.strip()
    if not action:
        raise ValidationError("Audit action is required.")

    derived_entity_type, derived_entity_id = _entity_identity(entity)
    resolved_actor_type = actor_type or (AuditActorType.USER if actor is not None else AuditActorType.SYSTEM)

    return AuditEvent.objects.create(
        actor=actor,
        actor_type=resolved_actor_type,
        action=action,
        entity_type=entity_type.strip() or derived_entity_type,
        entity_id=str(entity_id).strip() or derived_entity_id,
        car=car,
        context=context or {},
        metadata=metadata or {},
    )
