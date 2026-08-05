from app.crud.product import listar_produtos
from app.crud.user import listar_usuarios


def test_listar_produtos_so_retorna_do_proprio_tenant(db, tenant_factory, product_factory):
    tenant_a = tenant_factory("Loja A")
    tenant_b = tenant_factory("Loja B")
    product_factory(tenant_a.id, sku="A-1")
    product_factory(tenant_a.id, sku="A-2")
    product_factory(tenant_b.id, sku="B-1")

    produtos_a = listar_produtos(db, tenant_id=tenant_a.id, apenas_ativos=False)
    produtos_b = listar_produtos(db, tenant_id=tenant_b.id, apenas_ativos=False)

    assert {p.sku for p in produtos_a} == {"A-1", "A-2"}
    assert {p.sku for p in produtos_b} == {"B-1"}


def test_listar_usuarios_so_retorna_do_proprio_tenant(db, tenant_factory, user_factory):
    tenant_a = tenant_factory("Loja A")
    tenant_b = tenant_factory("Loja B")
    user_factory(tenant_a.id, email="a1@teste.com")
    user_factory(tenant_a.id, email="a2@teste.com")
    user_factory(tenant_b.id, email="b1@teste.com")

    usuarios_a = listar_usuarios(db, tenant_id=tenant_a.id)
    usuarios_b = listar_usuarios(db, tenant_id=tenant_b.id)

    assert {u.email for u in usuarios_a} == {"a1@teste.com", "a2@teste.com"}
    assert {u.email for u in usuarios_b} == {"b1@teste.com"}
