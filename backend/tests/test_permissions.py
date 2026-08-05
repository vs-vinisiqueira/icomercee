import pytest
from fastapi import HTTPException

from app.core.deps import require_admin


def test_operador_nao_pode_acessar_rota_admin(user_factory, tenant_factory):
    t = tenant_factory()
    operador = user_factory(t.id, email="operador@teste.com", role="operador")

    with pytest.raises(HTTPException) as exc_info:
        require_admin(current_user=operador)

    assert exc_info.value.status_code == 403


def test_admin_acessa_rota_admin(user_factory, tenant_factory):
    t = tenant_factory()
    admin = user_factory(t.id, email="admin2@teste.com", role="admin")

    resultado = require_admin(current_user=admin)

    assert resultado is admin
