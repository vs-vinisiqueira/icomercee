from app.crud.webhook_event import registrar_evento
from app.models.webhook_event import WebhookEvent


def test_notificacao_duplicada_nao_processa_duas_vezes(db, tenant_factory):
    t = tenant_factory()
    payload = {"topic": "orders_v2", "resource": "/orders/123", "user_id": "999"}

    evento1, is_novo1 = registrar_evento(
        db,
        canal="mercado_livre",
        topic="orders_v2",
        resource="/orders/123",
        ml_notification_id="notif-abc",
        payload_raw=payload,
        tenant_id=t.id,
    )
    evento2, is_novo2 = registrar_evento(
        db,
        canal="mercado_livre",
        topic="orders_v2",
        resource="/orders/123",
        ml_notification_id="notif-abc",
        payload_raw=payload,
        tenant_id=t.id,
    )

    assert is_novo1 is True
    assert is_novo2 is False
    assert evento2.id == evento1.id
    assert evento2.status == "duplicado"

    total = db.query(WebhookEvent).filter(WebhookEvent.ml_notification_id == "notif-abc").count()
    assert total == 1


def test_notificacoes_diferentes_geram_eventos_separados(db, tenant_factory):
    t = tenant_factory()
    payload = {"topic": "orders_v2", "resource": "/orders/456", "user_id": "999"}

    evento1, is_novo1 = registrar_evento(
        db,
        canal="mercado_livre",
        topic="orders_v2",
        resource="/orders/456",
        ml_notification_id="notif-1",
        payload_raw=payload,
        tenant_id=t.id,
    )
    evento2, is_novo2 = registrar_evento(
        db,
        canal="mercado_livre",
        topic="orders_v2",
        resource="/orders/457",
        ml_notification_id="notif-2",
        payload_raw=payload,
        tenant_id=t.id,
    )

    assert is_novo1 is True
    assert is_novo2 is True
    assert evento1.id != evento2.id
