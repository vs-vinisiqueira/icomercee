from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class ProductCreate(BaseModel):
    sku: str = Field(min_length=1, max_length=60)
    nome: str = Field(min_length=2, max_length=200)
    categoria: str | None = Field(default=None, max_length=100)
    supplier_id: int | None = None
    custo_compra: Decimal = Field(default=Decimal("0"), ge=0)
    preco_venda: Decimal = Field(default=Decimal("0"), ge=0)
    estoque_minimo: int = Field(default=0, ge=0)


class ProductUpdate(BaseModel):
    sku: str | None = Field(default=None, min_length=1, max_length=60)
    nome: str | None = Field(default=None, min_length=2, max_length=200)
    categoria: str | None = Field(default=None, max_length=100)
    supplier_id: int | None = None
    custo_compra: Decimal | None = Field(default=None, ge=0)
    preco_venda: Decimal | None = Field(default=None, ge=0)
    estoque_minimo: int | None = Field(default=None, ge=0)
    ativo: bool | None = None


class ProductResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    tenant_id: int
    sku: str
    nome: str
    categoria: str | None
    supplier_id: int | None
    custo_compra: Decimal
    preco_venda: Decimal
    estoque_minimo: int
    estoque_atual: int
    ativo: bool
