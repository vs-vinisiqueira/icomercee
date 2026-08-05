from pydantic import BaseModel

from app.schemas.order import OrderResponse


class LabelBatchRequest(BaseModel):
    order_ids: list[int]


class LabelBatchResponse(BaseModel):
    sucesso: list[OrderResponse]
    falhas: list[dict]
