from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.webhook_event import WebhookEvent


def registrar_evento(
    db: Session,
    canal: str,
    topic: str,
    resource: str,
    ml_notification_id: str | None,
    payload_raw: dict,
    tenant_id: int | None = None,
) -> tuple[WebhookEvent, bool]:
    """Grava o evento; retorna (evento, is_novo). Se já existir (mesmo tenant+notification_id),
    retorna o registro existente marcado como duplicado em vez de levantar erro — o endpoint
    de webhook sempre responde 200, mesmo em reentrega do ML."""
    evento = WebhookEvent(
        tenant_id=tenant_id,
        canal=canal,
        topic=topic,
        resource=resource,
        ml_notification_id=ml_notification_id,
        payload_raw=payload_raw,
    )

    try:
        db.add(evento)
        db.commit()
        db.refresh(evento)
        return evento, True
    except IntegrityError:
        db.rollback()
        existente = (
            db.query(WebhookEvent)
            .filter(
                WebhookEvent.tenant_id == tenant_id,
                WebhookEvent.ml_notification_id == ml_notification_id,
            )
            .first()
        )
        if existente:
            existente.status = "duplicado"
            db.commit()
            db.refresh(existente)
            return existente, False
        raise


def marcar_processando(db: Session, evento: WebhookEvent) -> None:
    evento.status = "processando"
    evento.tentativas += 1
    db.commit()


def marcar_processado(db: Session, evento: WebhookEvent) -> None:
    from datetime import datetime, timezone

    evento.status = "processado"
    evento.processado_em = datetime.now(timezone.utc)
    db.commit()


def marcar_erro(db: Session, evento: WebhookEvent, erro_detalhe: str) -> None:
    evento.status = "erro"
    evento.erro_detalhe = erro_detalhe[:2000]
    db.commit()


def listar_travados_ou_com_erro(db: Session, limit: int = 100) -> list[WebhookEvent]:
    return (
        db.query(WebhookEvent)
        .filter(WebhookEvent.status.in_(["recebido", "erro"]))
        .order_by(WebhookEvent.recebido_em.asc())
        .limit(limit)
        .all()
    )
