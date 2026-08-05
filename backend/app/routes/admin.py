from fastapi import APIRouter, BackgroundTasks, Depends
from sqlalchemy.orm import Session

from app.core.deps import require_admin
from app.crud.webhook_event import listar_travados_ou_com_erro
from app.database import get_db
from app.models.user import User
from app.services.mercadolivre.webhook import processar_evento

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.post("/webhooks/reprocess")
def reprocessar_webhooks_travados(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Varre webhook_events com status 'recebido' (nunca processados, ex: processo caiu)
    ou 'erro' (falha anterior) e agenda reprocessamento. Cobre a lacuna de não ter fila
    dedicada no MVP — ver decisão de arquitetura sobre BackgroundTasks vs Celery."""
    eventos = listar_travados_ou_com_erro(db)
    for evento in eventos:
        background_tasks.add_task(processar_evento, evento.id)

    return {"eventos_agendados": len(eventos)}
