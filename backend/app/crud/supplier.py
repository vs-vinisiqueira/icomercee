from sqlalchemy.orm import Session

from app.models.supplier import Supplier
from app.schemas.supplier import SupplierCreate, SupplierUpdate


def criar_fornecedor(db: Session, tenant_id: int, supplier: SupplierCreate) -> Supplier:
    novo = Supplier(tenant_id=tenant_id, nome=supplier.nome, contato=supplier.contato)
    db.add(novo)
    db.commit()
    db.refresh(novo)
    return novo


def listar_fornecedores(db: Session, tenant_id: int, limit: int = 100, offset: int = 0) -> list[Supplier]:
    return (
        db.query(Supplier)
        .filter(Supplier.tenant_id == tenant_id)
        .offset(offset)
        .limit(limit)
        .all()
    )


def obter_fornecedor(db: Session, tenant_id: int, supplier_id: int) -> Supplier | None:
    return (
        db.query(Supplier)
        .filter(Supplier.id == supplier_id, Supplier.tenant_id == tenant_id)
        .first()
    )


def atualizar_fornecedor(
    db: Session, tenant_id: int, supplier_id: int, dados: SupplierUpdate
) -> Supplier | None:
    fornecedor = obter_fornecedor(db, tenant_id, supplier_id)
    if not fornecedor:
        return None

    for campo, valor in dados.model_dump(exclude_unset=True).items():
        setattr(fornecedor, campo, valor)

    db.commit()
    db.refresh(fornecedor)
    return fornecedor
