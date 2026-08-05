from datetime import datetime

from sqlalchemy.orm import Session

from app.core.crypto import criptografar, descriptografar
from app.models.ml_credentials import MLCredentials


def salvar_credenciais(
    db: Session,
    tenant_id: int,
    ml_user_id: str,
    access_token: str,
    refresh_token: str,
    expires_at: datetime,
) -> MLCredentials:
    credenciais = db.query(MLCredentials).filter(MLCredentials.tenant_id == tenant_id).first()

    if credenciais is None:
        credenciais = MLCredentials(tenant_id=tenant_id)
        db.add(credenciais)

    credenciais.ml_user_id = ml_user_id
    credenciais.access_token = criptografar(access_token)
    credenciais.refresh_token = criptografar(refresh_token)
    credenciais.expires_at = expires_at

    db.commit()
    db.refresh(credenciais)
    return credenciais


def obter_credenciais_por_tenant(db: Session, tenant_id: int) -> MLCredentials | None:
    return db.query(MLCredentials).filter(MLCredentials.tenant_id == tenant_id).first()


def obter_credenciais_por_ml_user_id(db: Session, ml_user_id: str) -> MLCredentials | None:
    return db.query(MLCredentials).filter(MLCredentials.ml_user_id == ml_user_id).first()


def travar_credenciais_por_tenant(db: Session, tenant_id: int) -> MLCredentials | None:
    """SELECT ... FOR UPDATE: evita duas renovações concorrentes do mesmo refresh_token."""
    return (
        db.query(MLCredentials)
        .filter(MLCredentials.tenant_id == tenant_id)
        .with_for_update()
        .first()
    )


def access_token_em_claro(credenciais: MLCredentials) -> str:
    return descriptografar(credenciais.access_token)


def refresh_token_em_claro(credenciais: MLCredentials) -> str:
    return descriptografar(credenciais.refresh_token)
