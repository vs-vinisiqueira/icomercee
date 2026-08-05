from sqlalchemy import Boolean, Column, DateTime, Integer, String, func

from app.database import Base


class Tenant(Base):
    __tablename__ = "tenants"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(120), nullable=False)
    ativo = Column(Boolean, nullable=False, default=True, server_default="true")
    criado_em = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
