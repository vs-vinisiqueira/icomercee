from sqlalchemy import CheckConstraint, Column, ForeignKey, Integer, String, UniqueConstraint

from app.database import Base


class ProductChannelMapping(Base):
    __tablename__ = "product_channel_mapping"
    __table_args__ = (
        UniqueConstraint(
            "tenant_id", "canal", "item_id_externo", name="uq_mapping_tenant_canal_item"
        ),
        CheckConstraint("canal IN ('mercado_livre')", name="ck_mapping_canal_valid"),
    )

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False, index=True)
    canal = Column(String(30), nullable=False)
    item_id_externo = Column(String(60), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
