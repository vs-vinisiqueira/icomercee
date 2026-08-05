from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.database import get_db
from app.models.user import User
from app.schemas.stock_movement import (
    StockEntradaCreate,
    StockMovementResponse,
    StockSaidaCreate,
)
from app.services.stock.movements import (
    EstoqueInsuficienteError,
    ProdutoNaoEncontradoError,
    historico_produto,
    registrar_entrada,
    registrar_saida,
)

router = APIRouter(prefix="/stock", tags=["Stock"])


@router.post("/entrada", response_model=StockMovementResponse, status_code=status.HTTP_201_CREATED)
def entrada(
    dados: StockEntradaCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return registrar_entrada(
            db,
            tenant_id=current_user.tenant_id,
            product_id=dados.product_id,
            quantidade=dados.quantidade,
            motivo=dados.motivo,
            criado_por=current_user.id,
            custo_unitario=dados.custo_unitario,
            observacao=dados.observacao,
        )
    except ProdutoNaoEncontradoError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.post("/saida", response_model=StockMovementResponse, status_code=status.HTTP_201_CREATED)
def saida(
    dados: StockSaidaCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return registrar_saida(
            db,
            tenant_id=current_user.tenant_id,
            product_id=dados.product_id,
            quantidade=dados.quantidade,
            motivo=dados.motivo,
            criado_por=current_user.id,
            origem="manual",
            observacao=dados.observacao,
        )
    except ProdutoNaoEncontradoError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except EstoqueInsuficienteError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.get("/produtos/{product_id}/historico", response_model=list[StockMovementResponse])
def historico(
    product_id: int,
    limit: int = Query(default=100, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return historico_produto(
        db, tenant_id=current_user.tenant_id, product_id=product_id, limit=limit, offset=offset
    )
