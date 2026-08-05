"""Fluxo OAuth2 com o Mercado Livre.

`state` é um JWT de vida curta assinado com o mesmo segredo do resto da aplicação,
carregando o tenant_id — evita CSRF no callback e amarra a autorização ao tenant certo
sem precisar de tabela de sessão à parte.
"""

import os
from datetime import datetime, timedelta, timezone
from typing import Any
from urllib.parse import urlencode

import httpx
import jwt

from app.core.security import JWT_ALGORITHM, JWT_SECRET_KEY

ML_AUTH_URL = "https://auth.mercadolivre.com.br/authorization"
ML_TOKEN_URL = "https://api.mercadolibre.com/oauth/token"
ML_STATE_PURPOSE = "ml_oauth_state"
ML_STATE_EXPIRE_MINUTES = 10


class MLConfigError(Exception):
    pass


class MLOAuthError(Exception):
    pass


def _client_id() -> str:
    valor = os.getenv("ML_CLIENT_ID")
    if not valor:
        raise MLConfigError("ML_CLIENT_ID não configurado no .env")
    return valor


def _client_secret() -> str:
    valor = os.getenv("ML_CLIENT_SECRET")
    if not valor:
        raise MLConfigError("ML_CLIENT_SECRET não configurado no .env")
    return valor


def _redirect_uri() -> str:
    valor = os.getenv("ML_REDIRECT_URI")
    if not valor:
        raise MLConfigError("ML_REDIRECT_URI não configurado no .env")
    return valor


def gerar_state(tenant_id: int) -> str:
    payload = {
        "purpose": ML_STATE_PURPOSE,
        "tenant_id": tenant_id,
        "exp": datetime.now(timezone.utc) + timedelta(minutes=ML_STATE_EXPIRE_MINUTES),
    }
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)


def validar_state(state: str) -> int:
    """Retorna o tenant_id embutido no state, ou levanta MLOAuthError se inválido/expirado."""
    try:
        payload: dict[str, Any] = jwt.decode(state, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
    except jwt.PyJWTError as exc:
        raise MLOAuthError("state inválido ou expirado") from exc

    if payload.get("purpose") != ML_STATE_PURPOSE:
        raise MLOAuthError("state com propósito inválido")

    tenant_id = payload.get("tenant_id")
    if tenant_id is None:
        raise MLOAuthError("state sem tenant_id")

    return int(tenant_id)


def montar_url_autorizacao(tenant_id: int) -> str:
    params = {
        "response_type": "code",
        "client_id": _client_id(),
        "redirect_uri": _redirect_uri(),
        "state": gerar_state(tenant_id),
    }
    return f"{ML_AUTH_URL}?{urlencode(params)}"


def trocar_code_por_tokens(code: str) -> dict[str, Any]:
    dados = {
        "grant_type": "authorization_code",
        "client_id": _client_id(),
        "client_secret": _client_secret(),
        "code": code,
        "redirect_uri": _redirect_uri(),
    }

    resposta = httpx.post(ML_TOKEN_URL, data=dados, timeout=15)
    if resposta.status_code != 200:
        raise MLOAuthError(f"Falha ao trocar code por tokens: {resposta.status_code} {resposta.text}")

    return resposta.json()


def renovar_tokens(refresh_token: str) -> dict[str, Any]:
    dados = {
        "grant_type": "refresh_token",
        "client_id": _client_id(),
        "client_secret": _client_secret(),
        "refresh_token": refresh_token,
    }

    resposta = httpx.post(ML_TOKEN_URL, data=dados, timeout=15)
    if resposta.status_code != 200:
        raise MLOAuthError(f"Falha ao renovar tokens: {resposta.status_code} {resposta.text}")

    return resposta.json()
