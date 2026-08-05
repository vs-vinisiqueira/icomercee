from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

MotivoEntrada = Literal["compra_fornecedor", "ajuste_manual"]
MotivoSaida = Literal["ajuste_manual", "perda"]


class StockEntradaCreate(BaseModel):
    product_id: int
    quantidade: int = Field(gt=0)
    motivo: MotivoEntrada = "compra_fornecedor"
    custo_unitario: Decimal | None = Field(default=None, ge=0)
    observacao: str | None = None


class StockSaidaCreate(BaseModel):
    product_id: int
    quantidade: int = Field(gt=0)
    motivo: MotivoSaida = "ajuste_manual"
    observacao: str | None = None


class StockMovementResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    tenant_id: int
    product_id: int
    tipo: str
    quantidade: int
    motivo: str
    origem: str
    referencia_pedido_id: int | None
    custo_unitario: Decimal | None
    observacao: str | None
    criado_por: int
    criado_em: datetime
