from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.crud.order import listar_pendentes
from app.crud.product import listar_produtos
from app.database import get_db
from app.models.user import User
from app.schemas.dashboard import DashboardResponse

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/", response_model=DashboardResponse)
def resumo(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    pedidos_pendentes = listar_pendentes(db, tenant_id=current_user.tenant_id, limit=100)
    produtos_estoque_baixo = listar_produtos(
        db, tenant_id=current_user.tenant_id, apenas_estoque_baixo=True, limit=100
    )

    return DashboardResponse(
        pedidos_pendentes=pedidos_pendentes,
        produtos_estoque_baixo=produtos_estoque_baixo,
        total_pedidos_pendentes=len(pedidos_pendentes),
        total_produtos_estoque_baixo=len(produtos_estoque_baixo),
    )
