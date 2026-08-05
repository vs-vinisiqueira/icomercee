from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

Role = Literal["admin", "operador"]


class UserCreate(BaseModel):
    nome: str = Field(min_length=2, max_length=120)
    email: EmailStr
    senha: str = Field(min_length=8, max_length=72)
    role: Role = "operador"

    @field_validator("email")
    @classmethod
    def normalizar_email(cls, email: str) -> str:
        return email.lower()


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    tenant_id: int
    nome: str
    email: str
    role: str
    ativo: bool
