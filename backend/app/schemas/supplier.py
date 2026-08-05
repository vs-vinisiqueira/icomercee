from pydantic import BaseModel, ConfigDict, Field


class SupplierCreate(BaseModel):
    nome: str = Field(min_length=2, max_length=120)
    contato: str | None = Field(default=None, max_length=255)


class SupplierUpdate(BaseModel):
    nome: str | None = Field(default=None, min_length=2, max_length=120)
    contato: str | None = Field(default=None, max_length=255)


class SupplierResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    tenant_id: int
    nome: str
    contato: str | None
