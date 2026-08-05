"""Processamento das notificações de webhook do Mercado Livre.

Roda fora do ciclo de request (via BackgroundTasks) com sua própria sessão de banco,
por isso recebe `webhook_event_id` (não o objeto ORM) e reabre tudo a partir do id —
é a mesma função que, se o volume crescer, vira um `celery_task.delay(webhook_event_id)`
sem precisar mudar a lógica interna.
"""

from datetime import datetime

from app.crud.order import upsert_pedido
from app.crud.product_channel_mapping import obter_product_id_por_item
from app.crud.webhook_event import marcar_erro, marcar_processado, marcar_processando
from app.database import SessionLocal
from app.models.webhook_event import WebhookEvent
from app.services.mercadolivre.client import buscar_pedido


def processar_evento(webhook_event_id: int) -> None:
    db = SessionLocal()
    try:
        evento = db.query(WebhookEvent).filter(WebhookEvent.id == webhook_event_id).first()
        if not evento or evento.status not in ("recebido", "erro"):
            return

        if evento.tenant_id is None:
            marcar_erro(db, evento, "tenant não resolvido a partir do ml_user_id da notificação")
            return

        marcar_processando(db, evento)

        try:
            if evento.topic in ("orders_v2", "orders"):
                _processar_pedido(db, evento)

            marcar_processado(db, evento)
        except Exception as exc:  # noqa: BLE001 — qualquer falha vira status='erro' para retry manual
            db.rollback()
            evento_recarregado = db.query(WebhookEvent).filter(WebhookEvent.id == webhook_event_id).first()
            marcar_erro(db, evento_recarregado, str(exc))
    finally:
        db.close()


def _processar_pedido(db, evento: WebhookEvent) -> None:
    pedido_ml = buscar_pedido(db, evento.tenant_id, _extrair_order_id(evento.resource))

    item_id_externo = None
    itens = pedido_ml.get("order_items") or []
    if itens:
        item_id_externo = itens[0].get("item", {}).get("id")

    quantidade = sum(item.get("quantity", 1) for item in itens) or 1

    shipping = pedido_ml.get("shipping") or {}
    shipment_id_externo = str(shipping["id"]) if shipping.get("id") else None

    product_id = None
    if item_id_externo:
        product_id = obter_product_id_por_item(
            db, tenant_id=evento.tenant_id, canal="mercado_livre", item_id_externo=item_id_externo
        )

    upsert_pedido(
        db,
        tenant_id=evento.tenant_id,
        canal="mercado_livre",
        pedido_id_externo=str(pedido_ml["id"]),
        item_id_externo=item_id_externo,
        quantidade=quantidade,
        shipment_id_externo=shipment_id_externo,
        data_pedido=_parse_data_ml(pedido_ml.get("date_created")),
        product_id=product_id,
    )


def _extrair_order_id(resource: str) -> str:
    # resource vem como "/orders/123456789"
    return resource.rstrip("/").split("/")[-1]


def _parse_data_ml(valor: str | None) -> datetime | None:
    if not valor:
        return None
    try:
        return datetime.fromisoformat(valor)
    except ValueError:
        return None
