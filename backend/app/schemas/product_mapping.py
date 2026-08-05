from typing import Literal

from pydantic import BaseModel, ConfigDict


class ProductMappingCreate(BaseModel):
    canal: Literal["mercado_livre"] = "mercado_livre"
    item_id_externo: str
    product_id: int


class ProductMappingResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    tenant_id: int
    canal: str
    item_id_externo: str
    product_id: int
