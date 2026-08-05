from fastapi import APIRouter, BackgroundTasks, Request, status
from sqlalchemy.orm import Session

from app.crud.ml_credentials import obter_credenciais_por_ml_user_id
from app.crud.webhook_event import registrar_evento
from app.database import SessionLocal
from app.services.mercadolivre.webhook import processar_evento

router = APIRouter(prefix="/webhooks", tags=["Webhooks"])


@router.post("/mercadolivre", status_code=status.HTTP_200_OK)
async def receber_notificacao_ml(request: Request, background_tasks: BackgroundTasks):
    """Responde 200 o mais rápido possível (requisito do ML) e delega o processamento
    pesado para uma BackgroundTask. Idempotência é garantida em `registrar_evento`
    (UNIQUE tenant_id+ml_notification_id) — reentregas do ML não duplicam efeito."""
    payload = await request.json()

    topic = payload.get("topic", "")
    resource = payload.get("resource", "")
    ml_user_id = str(payload.get("user_id", ""))
    notification_id = payload.get("_id") or f"{resource}:{payload.get('sent', '')}"

    db: Session = SessionLocal()
    try:
        credenciais = obter_credenciais_por_ml_user_id(db, ml_user_id) if ml_user_id else None
        tenant_id = credenciais.tenant_id if credenciais else None

        evento, is_novo = registrar_evento(
            db,
            canal="mercado_livre",
            topic=topic,
            resource=resource,
            ml_notification_id=notification_id,
            payload_raw=payload,
            tenant_id=tenant_id,
        )
    finally:
        db.close()

    if is_novo:
        background_tasks.add_task(processar_evento, evento.id)

    return {"status": "recebido"}
