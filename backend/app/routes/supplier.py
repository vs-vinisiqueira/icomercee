from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.crud.supplier import (
    atualizar_fornecedor,
    criar_fornecedor,
    listar_fornecedores,
    obter_fornecedor,
)
from app.database import get_db
from app.models.user import User
from app.schemas.supplier import SupplierCreate, SupplierResponse, SupplierUpdate

router = APIRouter(prefix="/suppliers", tags=["Suppliers"])


@router.post("/", response_model=SupplierResponse, status_code=status.HTTP_201_CREATED)
def criar(
    supplier: SupplierCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return criar_fornecedor(db, tenant_id=current_user.tenant_id, supplier=supplier)


@router.get("/", response_model=list[SupplierResponse])
def listar(
    limit: int = Query(default=100, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return listar_fornecedores(db, tenant_id=current_user.tenant_id, limit=limit, offset=offset)


@router.get("/{supplier_id}", response_model=SupplierResponse)
def obter(
    supplier_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    fornecedor = obter_fornecedor(db, tenant_id=current_user.tenant_id, supplier_id=supplier_id)
    if not fornecedor:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Fornecedor não encontrado")
    return fornecedor


@router.patch("/{supplier_id}", response_model=SupplierResponse)
def atualizar(
    supplier_id: int,
    dados: SupplierUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    fornecedor = atualizar_fornecedor(
        db, tenant_id=current_user.tenant_id, supplier_id=supplier_id, dados=dados
    )
    if not fornecedor:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Fornecedor não encontrado")
    return fornecedor
