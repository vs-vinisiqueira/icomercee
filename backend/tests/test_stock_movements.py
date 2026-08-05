import pytest

from app.models.stock_movement import StockMovement
from app.services.stock.movements import (
    EstoqueInsuficienteError,
    ProdutoNaoEncontradoError,
    registrar_entrada,
    registrar_saida,
)


def test_entrada_incrementa_estoque_e_grava_movimento(db, tenant_factory, user_factory, product_factory):
    t = tenant_factory()
    u = user_factory(t.id)
    p = product_factory(t.id, estoque_atual=10)

    movimento = registrar_entrada(
        db,
        tenant_id=t.id,
        product_id=p.id,
        quantidade=5,
        motivo="compra_fornecedor",
        criado_por=u.id,
    )

    db.refresh(p)
    assert p.estoque_atual == 15
    assert movimento.tipo == "entrada"
    assert movimento.quantidade == 5


def test_saida_decrementa_estoque_quando_ha_saldo(db, tenant_factory, user_factory, product_factory):
    t = tenant_factory()
    u = user_factory(t.id)
    p = product_factory(t.id, estoque_atual=10)

    registrar_saida(
        db, tenant_id=t.id, product_id=p.id, quantidade=4, motivo="ajuste_manual", criado_por=u.id
    )

    db.refresh(p)
    assert p.estoque_atual == 6


def test_estoque_nunca_fica_negativo(db, tenant_factory, user_factory, product_factory):
    """Regra crítica: baixa maior que o saldo disponível é rejeitada, sem gravar
    movimento nem alterar o cache de estoque."""
    t = tenant_factory()
    u = user_factory(t.id)
    p = product_factory(t.id, estoque_atual=3)

    with pytest.raises(EstoqueInsuficienteError):
        registrar_saida(
            db, tenant_id=t.id, product_id=p.id, quantidade=10, motivo="ajuste_manual", criado_por=u.id
        )

    db.refresh(p)
    assert p.estoque_atual == 3

    movimentos = db.query(StockMovement).filter(StockMovement.product_id == p.id).all()
    assert len(movimentos) == 0


def test_saida_por_pedido_registra_origem_e_referencia(
    db, tenant_factory, user_factory, product_factory
):
    t = tenant_factory()
    u = user_factory(t.id)
    p = product_factory(t.id, estoque_atual=10)

    movimento = registrar_saida(
        db,
        tenant_id=t.id,
        product_id=p.id,
        quantidade=2,
        motivo="baixa_pedido",
        criado_por=u.id,
        origem="pedido",
        referencia_pedido_id=None,
    )

    assert movimento.origem == "pedido"
    assert movimento.motivo == "baixa_pedido"


def test_movimento_produto_inexistente_levanta_erro(db, tenant_factory, user_factory):
    t = tenant_factory()
    u = user_factory(t.id)

    with pytest.raises(ProdutoNaoEncontradoError):
        registrar_entrada(
            db, tenant_id=t.id, product_id=99999, quantidade=1, motivo="ajuste_manual", criado_por=u.id
        )


def test_produto_de_outro_tenant_nao_e_visivel(db, tenant_factory, user_factory, product_factory):
    """Isolamento por tenant: um produto criado no tenant A não pode ser movimentado
    informando o tenant_id de B."""
    tenant_a = tenant_factory("Loja A")
    tenant_b = tenant_factory("Loja B")
    user_b = user_factory(tenant_b.id, email="admin.b@teste.com")
    produto_a = product_factory(tenant_a.id, sku="SKU-A", estoque_atual=10)

    with pytest.raises(ProdutoNaoEncontradoError):
        registrar_entrada(
            db,
            tenant_id=tenant_b.id,
            product_id=produto_a.id,
            quantidade=1,
            motivo="ajuste_manual",
            criado_por=user_b.id,
        )
