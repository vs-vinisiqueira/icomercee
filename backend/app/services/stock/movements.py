"""Regra de negócio central do sistema: toda alteração de estoque passa por aqui.

Cada função grava um StockMovement (histórico append-only, nunca editado ou apagado)
e atualiza o cache `products.estoque_atual` na MESMA transação — ou tudo persiste, ou
nada persiste. `with_for_update()` trava a linha do produto durante a operação para que
duas baixas concorrentes do mesmo produto não ultrapassem o estoque disponível; o
CHECK (estoque_atual >= 0) no banco é a rede de segurança adicional caso o lock falhe.
"""

from decimal import Decimal

from sqlalchemy.orm import Session

from app.models.product import Product
from app.models.stock_movement import StockMovement


class EstoqueInsuficienteError(Exception):
    def __init__(self, product_id: int, disponivel: int, solicitado: int):
        self.product_id = product_id
        self.disponivel = disponivel
        self.solicitado = solicitado
        super().__init__(
            f"Estoque insuficiente para o produto {product_id}: "
            f"disponível={disponivel}, solicitado={solicitado}"
        )


class ProdutoNaoEncontradoError(Exception):
    def __init__(self, product_id: int):
        self.product_id = product_id
        super().__init__(f"Produto {product_id} não encontrado")


def _travar_produto(db: Session, tenant_id: int, product_id: int) -> Product:
    produto = (
        db.query(Product)
        .filter(Product.id == product_id, Product.tenant_id == tenant_id)
        .with_for_update()
        .first()
    )
    if not produto:
        raise ProdutoNaoEncontradoError(product_id)
    return produto


def registrar_entrada(
    db: Session,
    tenant_id: int,
    product_id: int,
    quantidade: int,
    motivo: str,
    criado_por: int,
    custo_unitario: Decimal | None = None,
    observacao: str | None = None,
) -> StockMovement:
    produto = _travar_produto(db, tenant_id, product_id)

    movimento = StockMovement(
        tenant_id=tenant_id,
        product_id=product_id,
        tipo="entrada",
        quantidade=quantidade,
        motivo=motivo,
        origem="manual",
        custo_unitario=custo_unitario,
        observacao=observacao,
        criado_por=criado_por,
    )
    db.add(movimento)

    produto.estoque_atual += quantidade
    if custo_unitario is not None:
        produto.custo_compra = custo_unitario

    db.commit()
    db.refresh(movimento)
    return movimento


def registrar_saida(
    db: Session,
    tenant_id: int,
    product_id: int,
    quantidade: int,
    motivo: str,
    criado_por: int,
    origem: str = "manual",
    referencia_pedido_id: int | None = None,
    observacao: str | None = None,
) -> StockMovement:
    produto = _travar_produto(db, tenant_id, product_id)

    if produto.estoque_atual < quantidade:
        db.rollback()
        raise EstoqueInsuficienteError(
            product_id=product_id, disponivel=produto.estoque_atual, solicitado=quantidade
        )

    movimento = StockMovement(
        tenant_id=tenant_id,
        product_id=product_id,
        tipo="saida",
        quantidade=quantidade,
        motivo=motivo,
        origem=origem,
        referencia_pedido_id=referencia_pedido_id,
        observacao=observacao,
        criado_por=criado_por,
    )
    db.add(movimento)

    produto.estoque_atual -= quantidade

    db.commit()
    db.refresh(movimento)
    return movimento


def historico_produto(
    db: Session, tenant_id: int, product_id: int, limit: int = 100, offset: int = 0
) -> list[StockMovement]:
    return (
        db.query(StockMovement)
        .filter(StockMovement.tenant_id == tenant_id, StockMovement.product_id == product_id)
        .order_by(StockMovement.criado_em.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )
