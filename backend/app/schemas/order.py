from datetime import datetime

from pydantic import BaseModel, ConfigDict


class OrderResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    tenant_id: int
    canal: str
    pedido_id_externo: str
    item_id_externo: str | None
    product_id: int | None
    quantidade: int
    status: str
    etiqueta_gerada: bool
    etiqueta_url: str | None
    shipment_id_externo: str | None
    data_pedido: datetime | None


class OrderVincularProduto(BaseModel):
    product_id: int
