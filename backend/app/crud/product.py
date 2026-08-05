from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.product import Product
from app.schemas.product import ProductCreate, ProductUpdate


def criar_produto(db: Session, tenant_id: int, product: ProductCreate) -> Product | None:
    novo = Product(tenant_id=tenant_id, **product.model_dump())

    try:
        db.add(novo)
        db.commit()
        db.refresh(novo)
    except IntegrityError:
        db.rollback()
        return None

    return novo


def listar_produtos(
    db: Session,
    tenant_id: int,
    apenas_ativos: bool = True,
    apenas_estoque_baixo: bool = False,
    limit: int = 100,
    offset: int = 0,
) -> list[Product]:
    query = db.query(Product).filter(Product.tenant_id == tenant_id)

    if apenas_ativos:
        query = query.filter(Product.ativo.is_(True))

    if apenas_estoque_baixo:
        query = query.filter(Product.estoque_atual <= Product.estoque_minimo)

    return query.offset(offset).limit(limit).all()


def obter_produto(db: Session, tenant_id: int, product_id: int) -> Product | None:
    return (
        db.query(Product)
        .filter(Product.id == product_id, Product.tenant_id == tenant_id)
        .first()
    )


def atualizar_produto(
    db: Session, tenant_id: int, product_id: int, dados: ProductUpdate
) -> Product | None:
    produto = obter_produto(db, tenant_id, product_id)
    if not produto:
        return None

    for campo, valor in dados.model_dump(exclude_unset=True).items():
        setattr(produto, campo, valor)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        return None

    db.refresh(produto)
    return produto


def inativar_produto(db: Session, tenant_id: int, product_id: int) -> Product | None:
    produto = obter_produto(db, tenant_id, product_id)
    if not produto:
        return None

    produto.ativo = False
    db.commit()
    db.refresh(produto)
    return produto
