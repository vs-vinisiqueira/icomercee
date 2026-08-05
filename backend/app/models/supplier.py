from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, func

from app.database import Base


class Supplier(Base):
    __tablename__ = "suppliers"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False, index=True)
    nome = Column(String(120), nullable=False)
    contato = Column(String(255), nullable=True)
    criado_em = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
