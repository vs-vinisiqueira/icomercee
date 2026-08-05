"""Wrapper HTTP para a API do Mercado Livre, com renovação automática de token."""

from datetime import datetime, timedelta, timezone

import httpx
from sqlalchemy.orm import Session

from app.crud.ml_credentials import (
    access_token_em_claro,
    refresh_token_em_claro,
    travar_credenciais_por_tenant,
)
from app.core.crypto import criptografar
from app.services.mercadolivre.oauth import MLOAuthError, renovar_tokens

ML_API_BASE = "https://api.mercadolibre.com"
REFRESH_MARGIN = timedelta(minutes=5)


class MLCredenciaisNaoEncontradasError(Exception):
    def __init__(self, tenant_id: int):
        self.tenant_id = tenant_id
        super().__init__(f"Tenant {tenant_id} não tem conta do Mercado Livre conectada")


def get_valid_token(db: Session, tenant_id: int) -> str:
    """Retorna um access_token válido, renovando via refresh_token se necessário.

    Usa SELECT ... FOR UPDATE na linha de ml_credentials: se duas requisições
    concorrentes precisarem renovar, a segunda espera a primeira commitar e reaproveita
    o token novo em vez de tentar renovar de novo com um refresh_token já invalidado.
    """
    credenciais = travar_credenciais_por_tenant(db, tenant_id)
    if not credenciais:
        raise MLCredenciaisNaoEncontradasError(tenant_id)

    agora = datetime.now(timezone.utc)
    expira_em = credenciais.expires_at
    if expira_em.tzinfo is None:
        expira_em = expira_em.replace(tzinfo=timezone.utc)

    if expira_em - REFRESH_MARGIN > agora:
        db.commit()  # libera o lock
        return access_token_em_claro(credenciais)

    tokens = renovar_tokens(refresh_token_em_claro(credenciais))

    credenciais.access_token = criptografar(tokens["access_token"])
    credenciais.refresh_token = criptografar(tokens["refresh_token"])
    credenciais.expires_at = agora + timedelta(seconds=tokens["expires_in"])
    db.commit()
    db.refresh(credenciais)

    return access_token_em_claro(credenciais)


def _headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def buscar_recurso(db: Session, tenant_id: int, resource_path: str) -> dict:
    """GET genérico usado pelo processamento de webhook (resource vem no payload)."""
    token = get_valid_token(db, tenant_id)
    url = resource_path if resource_path.startswith("http") else f"{ML_API_BASE}{resource_path}"

    resposta = httpx.get(url, headers=_headers(token), timeout=15)
    if resposta.status_code != 200:
        raise MLOAuthError(f"Falha ao buscar recurso {resource_path}: {resposta.status_code} {resposta.text}")

    return resposta.json()


def buscar_pedido(db: Session, tenant_id: int, order_id: str) -> dict:
    return buscar_recurso(db, tenant_id, f"/orders/{order_id}")


def buscar_shipment(db: Session, tenant_id: int, shipment_id: str) -> dict:
    return buscar_recurso(db, tenant_id, f"/shipments/{shipment_id}")


def baixar_etiqueta(db: Session, tenant_id: int, shipment_id: str) -> bytes:
    """Baixa o PDF/ZPL da etiqueta de envio (endpoint de shipping labels do ML)."""
    token = get_valid_token(db, tenant_id)
    url = f"{ML_API_BASE}/shipment_labels"

    resposta = httpx.get(
        url,
        headers=_headers(token),
        params={"shipment_ids": shipment_id, "response_type": "pdf"},
        timeout=30,
    )
    if resposta.status_code != 200:
        raise MLOAuthError(
            f"Falha ao gerar etiqueta do shipment {shipment_id}: {resposta.status_code} {resposta.text}"
        )

    return resposta.content
