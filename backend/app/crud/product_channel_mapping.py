from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.product_channel_mapping import ProductChannelMapping


def criar_vinculo(
    db: Session, tenant_id: int, canal: str, item_id_externo: str, product_id: int
) -> ProductChannelMapping | None:
    vinculo = ProductChannelMapping(
        tenant_id=tenant_id, canal=canal, item_id_externo=item_id_externo, product_id=product_id
    )
    try:
        db.add(vinculo)
        db.commit()
        db.refresh(vinculo)
    except IntegrityError:
        db.rollback()
        return None
    return vinculo


def obter_product_id_por_item(
    db: Session, tenant_id: int, canal: str, item_id_externo: str
) -> int | None:
    vinculo = (
        db.query(ProductChannelMapping)
        .filter(
            ProductChannelMapping.tenant_id == tenant_id,
            ProductChannelMapping.canal == canal,
            ProductChannelMapping.item_id_externo == item_id_externo,
        )
        .first()
    )
    return vinculo.product_id if vinculo else None


def listar_vinculos(db: Session, tenant_id: int, limit: int = 100, offset: int = 0) -> list[ProductChannelMapping]:
    return (
        db.query(ProductChannelMapping)
        .filter(ProductChannelMapping.tenant_id == tenant_id)
        .offset(offset)
        .limit(limit)
        .all()
    )
