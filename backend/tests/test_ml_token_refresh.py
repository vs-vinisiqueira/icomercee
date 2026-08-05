from datetime import datetime, timedelta, timezone

from app.crud.ml_credentials import salvar_credenciais
from app.services.mercadolivre import client as ml_client


def test_token_valido_nao_dispara_renovacao(db, tenant_factory, monkeypatch):
    t = tenant_factory()
    salvar_credenciais(
        db,
        tenant_id=t.id,
        ml_user_id="123",
        access_token="token-valido",
        refresh_token="refresh-valido",
        expires_at=datetime.now(timezone.utc) + timedelta(hours=1),
    )

    chamadas = {"n": 0}

    def renovar_tokens_fake(refresh_token: str):
        chamadas["n"] += 1
        raise AssertionError("não deveria renovar um token ainda válido")

    monkeypatch.setattr(ml_client, "renovar_tokens", renovar_tokens_fake)

    token = ml_client.get_valid_token(db, t.id)

    assert token == "token-valido"
    assert chamadas["n"] == 0


def test_token_expirado_dispara_renovacao_automatica(db, tenant_factory, monkeypatch):
    t = tenant_factory()
    salvar_credenciais(
        db,
        tenant_id=t.id,
        ml_user_id="123",
        access_token="token-antigo",
        refresh_token="refresh-antigo",
        expires_at=datetime.now(timezone.utc) - timedelta(minutes=1),
    )

    chamadas = {"n": 0}

    def renovar_tokens_fake(refresh_token: str):
        chamadas["n"] += 1
        assert refresh_token == "refresh-antigo"
        return {
            "access_token": "token-novo",
            "refresh_token": "refresh-novo",
            "expires_in": 21600,
        }

    monkeypatch.setattr(ml_client, "renovar_tokens", renovar_tokens_fake)

    token = ml_client.get_valid_token(db, t.id)

    assert token == "token-novo"
    assert chamadas["n"] == 1

    # Segunda chamada logo em seguida: token novo ainda válido, não renova de novo.
    token2 = ml_client.get_valid_token(db, t.id)
    assert token2 == "token-novo"
    assert chamadas["n"] == 1


def test_token_perto_de_expirar_renova_por_margem_de_seguranca(db, tenant_factory, monkeypatch):
    """expires_at daqui a 2 minutos deve renovar (margem de 5 min), não esperar expirar de fato."""
    t = tenant_factory()
    salvar_credenciais(
        db,
        tenant_id=t.id,
        ml_user_id="123",
        access_token="token-quase-expirando",
        refresh_token="refresh-x",
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=2),
    )

    def renovar_tokens_fake(refresh_token: str):
        return {"access_token": "token-renovado", "refresh_token": "refresh-y", "expires_in": 21600}

    monkeypatch.setattr(ml_client, "renovar_tokens", renovar_tokens_fake)

    token = ml_client.get_valid_token(db, t.id)
    assert token == "token-renovado"
