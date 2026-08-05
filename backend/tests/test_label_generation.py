import pytest

from app.models.order import Order
from app.models.stock_movement import StockMovement
from app.services.mercadolivre import labels


def test_gerar_etiqueta_com_sucesso_baixa_estoque_e_atualiza_pedido(
    db, tenant_factory, user_factory, product_factory, order_factory, monkeypatch, tmp_path
):
    t = tenant_factory()
    u = user_factory(t.id)
    p = product_factory(t.id, estoque_atual=10)
    pedido = order_factory(t.id, product_id=p.id, quantidade=3)

    monkeypatch.setattr(labels, "LABELS_DIR", tmp_path)
    monkeypatch.setattr(labels, "baixar_etiqueta", lambda db, tenant_id, shipment_id: b"%PDF-fake-content")

    resultado = labels.gerar_etiqueta_pedido(db, tenant_id=t.id, order_id=pedido.id, usuario_id=u.id)

    assert resultado.etiqueta_gerada is True
    assert resultado.status == "etiqueta_gerada"

    db.refresh(p)
    assert p.estoque_atual == 7

    movimentos = db.query(StockMovement).filter(StockMovement.referencia_pedido_id == pedido.id).all()
    assert len(movimentos) == 1
    assert movimentos[0].motivo == "baixa_pedido"
    assert movimentos[0].origem == "pedido"

    arquivo = tmp_path / f"{t.id}_{pedido.id}.pdf"
    assert arquivo.exists()
    assert arquivo.read_bytes() == b"%PDF-fake-content"


def test_falha_ao_baixar_etiqueta_nao_altera_estoque_nem_pedido(
    db, tenant_factory, user_factory, product_factory, order_factory, monkeypatch, tmp_path
):
    """Regra crítica: se a chamada à API do ML falhar, nada é persistido — nem
    baixa de estoque, nem status do pedido."""
    t = tenant_factory()
    u = user_factory(t.id)
    p = product_factory(t.id, estoque_atual=10)
    pedido = order_factory(t.id, product_id=p.id, quantidade=3)

    monkeypatch.setattr(labels, "LABELS_DIR", tmp_path)

    def baixar_etiqueta_com_falha(db, tenant_id, shipment_id):
        raise RuntimeError("Falha simulada na API do Mercado Livre")

    monkeypatch.setattr(labels, "baixar_etiqueta", baixar_etiqueta_com_falha)

    with pytest.raises(RuntimeError):
        labels.gerar_etiqueta_pedido(db, tenant_id=t.id, order_id=pedido.id, usuario_id=u.id)

    db.refresh(p)
    assert p.estoque_atual == 10

    pedido_recarregado = db.query(Order).filter(Order.id == pedido.id).first()
    assert pedido_recarregado.status == "pendente_etiqueta"
    assert pedido_recarregado.etiqueta_gerada is False

    movimentos = db.query(StockMovement).filter(StockMovement.referencia_pedido_id == pedido.id).all()
    assert len(movimentos) == 0


def test_pedido_sem_produto_vinculado_nao_gera_etiqueta(
    db, tenant_factory, user_factory, order_factory, monkeypatch
):
    t = tenant_factory()
    u = user_factory(t.id)
    pedido = order_factory(t.id, product_id=None)

    chamou_ml = {"sim": False}
    monkeypatch.setattr(
        labels, "baixar_etiqueta", lambda *a, **kw: chamou_ml.update(sim=True) or b""
    )

    with pytest.raises(labels.ProdutoNaoVinculadoError):
        labels.gerar_etiqueta_pedido(db, tenant_id=t.id, order_id=pedido.id, usuario_id=u.id)

    assert chamou_ml["sim"] is False


def test_pedido_sem_shipment_nao_gera_etiqueta(
    db, tenant_factory, user_factory, product_factory, order_factory
):
    t = tenant_factory()
    u = user_factory(t.id)
    p = product_factory(t.id, estoque_atual=10)
    pedido = order_factory(t.id, product_id=p.id, shipment_id_externo=None)

    with pytest.raises(labels.PedidoSemShipmentError):
        labels.gerar_etiqueta_pedido(db, tenant_id=t.id, order_id=pedido.id, usuario_id=u.id)


def test_lote_uma_falha_nao_trava_os_demais_pedidos(
    db, tenant_factory, user_factory, product_factory, order_factory, monkeypatch, tmp_path
):
    t = tenant_factory()
    u = user_factory(t.id)
    produto_com_estoque = product_factory(t.id, sku="OK-1", estoque_atual=10)
    produto_sem_estoque = product_factory(t.id, sku="SEM-1", estoque_atual=1)

    pedido_ok = order_factory(
        t.id, product_id=produto_com_estoque.id, quantidade=2, pedido_id_externo="pedido-ok"
    )
    pedido_falha = order_factory(
        t.id, product_id=produto_sem_estoque.id, quantidade=5, pedido_id_externo="pedido-falha"
    )

    monkeypatch.setattr(labels, "LABELS_DIR", tmp_path)
    monkeypatch.setattr(labels, "baixar_etiqueta", lambda db, tenant_id, shipment_id: b"fake")

    sucesso, falhas = labels.gerar_etiquetas_lote(
        db, tenant_id=t.id, order_ids=[pedido_ok.id, pedido_falha.id], usuario_id=u.id
    )

    assert len(sucesso) == 1
    assert sucesso[0].id == pedido_ok.id
    assert len(falhas) == 1
    assert falhas[0]["order_id"] == pedido_falha.id
    assert isinstance(falhas[0]["erro"], str)

    db.refresh(produto_com_estoque)
    db.refresh(produto_sem_estoque)
    assert produto_com_estoque.estoque_atual == 8
    assert produto_sem_estoque.estoque_atual == 1
