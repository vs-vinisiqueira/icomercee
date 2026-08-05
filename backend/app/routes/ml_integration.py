from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.deps import require_admin
from app.crud.ml_credentials import obter_credenciais_por_tenant, salvar_credenciais
from app.database import get_db
from app.models.user import User
from app.schemas.ml_integration import MLConnectResponse, MLCredentialsStatus
from app.services.mercadolivre.oauth import (
    MLConfigError,
    MLOAuthError,
    montar_url_autorizacao,
    trocar_code_por_tokens,
    validar_state,
)
from datetime import datetime, timedelta, timezone

router = APIRouter(prefix="/integrations/ml", tags=["Mercado Livre"])


@router.get("/connect", response_model=MLConnectResponse)
def connect(current_user: User = Depends(require_admin)):
    try:
        url = montar_url_autorizacao(current_user.tenant_id)
    except MLConfigError as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)) from exc

    return MLConnectResponse(authorization_url=url)


@router.get("/callback")
def callback(
    code: str = Query(...),
    state: str = Query(...),
    db: Session = Depends(get_db),
):
    try:
        tenant_id = validar_state(state)
        tokens = trocar_code_por_tokens(code)
    except (MLOAuthError, MLConfigError) as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    expires_at = datetime.now(timezone.utc) + timedelta(seconds=tokens["expires_in"])

    salvar_credenciais(
        db,
        tenant_id=tenant_id,
        ml_user_id=str(tokens["user_id"]),
        access_token=tokens["access_token"],
        refresh_token=tokens["refresh_token"],
        expires_at=expires_at,
    )

    return {"mensagem": "Conta do Mercado Livre conectada com sucesso"}


@router.get("/status", response_model=MLCredentialsStatus)
def status_conexao(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    credenciais = obter_credenciais_por_tenant(db, tenant_id=current_user.tenant_id)
    if not credenciais:
        return MLCredentialsStatus(conectado=False)

    return MLCredentialsStatus(
        conectado=True,
        ml_user_id=credenciais.ml_user_id,
        expires_at=credenciais.expires_at,
    )
