from pydantic import BaseModel

from app.schemas.order import OrderResponse
from app.schemas.product import ProductResponse


class DashboardResponse(BaseModel):
    pedidos_pendentes: list[OrderResponse]
    produtos_estoque_baixo: list[ProductResponse]
    total_pedidos_pendentes: int
    total_produtos_estoque_baixo: int
