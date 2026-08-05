from datetime import datetime

from sqlalchemy.orm import Session

from app.models.order import Order


def upsert_pedido(
    db: Session,
    tenant_id: int,
    canal: str,
    pedido_id_externo: str,
    item_id_externo: str | None,
    quantidade: int,
    shipment_id_externo: str | None,
    data_pedido: datetime | None,
    product_id: int | None,
) -> Order:
    pedido = (
        db.query(Order)
        .filter(
            Order.tenant_id == tenant_id,
            Order.canal == canal,
            Order.pedido_id_externo == pedido_id_externo,
        )
        .first()
    )

    if pedido is None:
        pedido = Order(
            tenant_id=tenant_id,
            canal=canal,
            pedido_id_externo=pedido_id_externo,
        )
        db.add(pedido)

    pedido.item_id_externo = item_id_externo
    pedido.quantidade = quantidade
    pedido.shipment_id_externo = shipment_id_externo
    pedido.data_pedido = data_pedido
    if product_id is not None:
        pedido.product_id = product_id

    db.commit()
    db.refresh(pedido)
    return pedido


def listar_pendentes(db: Session, tenant_id: int, limit: int = 100, offset: int = 0) -> list[Order]:
    return (
        db.query(Order)
        .filter(Order.tenant_id == tenant_id, Order.status == "pendente_etiqueta")
        .order_by(Order.data_pedido.asc())
        .offset(offset)
        .limit(limit)
        .all()
    )


def obter_pedido(db: Session, tenant_id: int, order_id: int) -> Order | None:
    return db.query(Order).filter(Order.id == order_id, Order.tenant_id == tenant_id).first()


def vincular_produto(db: Session, tenant_id: int, order_id: int, product_id: int) -> Order | None:
    pedido = obter_pedido(db, tenant_id, order_id)
    if not pedido:
        return None
    pedido.product_id = product_id
    db.commit()
    db.refresh(pedido)
    return pedido
