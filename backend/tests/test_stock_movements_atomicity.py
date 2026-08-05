from app.models.product import Product
from app.models.stock_movement import StockMovement
from app.services.stock.movements import registrar_entrada


def test_commit_falho_causa_rollback_completo(db, tenant_factory, user_factory, product_factory, monkeypatch):
    """Simula uma falha exatamente no commit da movimentação (ex: queda de conexão) e
    confirma que nem o StockMovement nem a alteração em products.estoque_atual
    sobrevivem — a movimentação é uma unidade atômica, não dois passos separados."""
    t = tenant_factory()
    u = user_factory(t.id)
    p = product_factory(t.id, estoque_atual=10)

    original_commit = db.commit
    chamadas = {"n": 0}

    def commit_que_falha_uma_vez():
        chamadas["n"] += 1
        if chamadas["n"] == 1:
            db.rollback()
            raise RuntimeError("falha simulada de commit")
        return original_commit()

    monkeypatch.setattr(db, "commit", commit_que_falha_uma_vez)

    try:
        registrar_entrada(
            db, tenant_id=t.id, product_id=p.id, quantidade=5, motivo="ajuste_manual", criado_por=u.id
        )
    except RuntimeError:
        pass

    monkeypatch.undo()

    produto_recarregado = db.query(Product).filter(Product.id == p.id).first()
    assert produto_recarregado.estoque_atual == 10

    movimentos = db.query(StockMovement).filter(StockMovement.product_id == p.id).all()
    assert len(movimentos) == 0
