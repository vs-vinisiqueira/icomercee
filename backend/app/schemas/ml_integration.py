from datetime import datetime

from pydantic import BaseModel, ConfigDict


class MLConnectResponse(BaseModel):
    authorization_url: str


class MLCredentialsStatus(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    conectado: bool
    ml_user_id: str | None = None
    expires_at: datetime | None = None
