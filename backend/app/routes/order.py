from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.crud.order import listar_pendentes, obter_pedido, vincular_produto
from app.database import get_db
from app.models.user import User
from app.schemas.label import LabelBatchRequest, LabelBatchResponse
from app.schemas.order import OrderResponse, OrderVincularProduto
from app.services.mercadolivre.labels import (
    LABELS_DIR,
    PedidoNaoEncontradoError,
    PedidoSemShipmentError,
    ProdutoNaoVinculadoError,
    gerar_etiqueta_pedido,
    gerar_etiquetas_lote,
)
from app.services.stock.movements import EstoqueInsuficienteError

router = APIRouter(prefix="/orders", tags=["Orders"])

_ERROS_NEGOCIO = (
    PedidoNaoEncontradoError,
    ProdutoNaoVinculadoError,
    PedidoSemShipmentError,
    EstoqueInsuficienteError,
)


@router.get("/pending", response_model=list[OrderResponse])
def listar_pendentes_etiqueta(
    limit: int = Query(default=100, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return listar_pendentes(db, tenant_id=current_user.tenant_id, limit=limit, offset=offset)


@router.post("/labels/batch", response_model=LabelBatchResponse)
def gerar_etiquetas_em_lote(
    dados: LabelBatchRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    sucesso, falhas = gerar_etiquetas_lote(
        db, tenant_id=current_user.tenant_id, order_ids=dados.order_ids, usuario_id=current_user.id
    )
    return LabelBatchResponse(sucesso=sucesso, falhas=falhas)


@router.get("/{order_id}", response_model=OrderResponse)
def obter(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    pedido = obter_pedido(db, tenant_id=current_user.tenant_id, order_id=order_id)
    if not pedido:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pedido não encontrado")
    return pedido


@router.post("/{order_id}/vincular-produto", response_model=OrderResponse)
def vincular(
    order_id: int,
    dados: OrderVincularProduto,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    pedido = vincular_produto(
        db, tenant_id=current_user.tenant_id, order_id=order_id, product_id=dados.product_id
    )
    if not pedido:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pedido não encontrado")
    return pedido


@router.post("/{order_id}/label", response_model=OrderResponse)
def gerar_etiqueta(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return gerar_etiqueta_pedido(
            db, tenant_id=current_user.tenant_id, order_id=order_id, usuario_id=current_user.id
        )
    except _ERROS_NEGOCIO as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.get("/{order_id}/label/download")
def baixar_etiqueta_gerada(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    pedido = obter_pedido(db, tenant_id=current_user.tenant_id, order_id=order_id)
    if not pedido or not pedido.etiqueta_gerada:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Etiqueta ainda não gerada")

    caminho = Path(LABELS_DIR) / f"{current_user.tenant_id}_{order_id}.pdf"
    if not caminho.exists():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Arquivo da etiqueta não encontrado")

    return FileResponse(caminho, media_type="application/pdf", filename=f"etiqueta-pedido-{order_id}.pdf")
