from sqlalchemy import JSON, CheckConstraint, Column, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import JSONB

from app.database import Base

# JSONB em produção (Postgres); cai para JSON genérico em outros dialetos (ex: SQLite nos testes).
JSON_VARIANT = JSON().with_variant(JSONB, "postgresql")


class WebhookEvent(Base):
    __tablename__ = "webhook_events"
    __table_args__ = (
        UniqueConstraint(
            "tenant_id", "ml_notification_id", name="uq_webhook_events_tenant_notification"
        ),
        CheckConstraint("canal IN ('mercado_livre')", name="ck_webhook_events_canal_valid"),
        CheckConstraint(
            "status IN ('recebido', 'processando', 'processado', 'erro', 'duplicado')",
            name="ck_webhook_events_status_valid",
        ),
    )

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=True, index=True)
    canal = Column(String(30), nullable=False, default="mercado_livre", server_default="mercado_livre")
    topic = Column(String(60), nullable=False)
    resource = Column(String(255), nullable=False)
    ml_notification_id = Column(String(120), nullable=True)
    payload_raw = Column(JSON_VARIANT, nullable=False)
    status = Column(String(20), nullable=False, default="recebido", server_default="recebido")
    tentativas = Column(Integer, nullable=False, default=0, server_default="0")
    erro_detalhe = Column(Text, nullable=True)
    recebido_em = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    processado_em = Column(DateTime(timezone=True), nullable=True)
