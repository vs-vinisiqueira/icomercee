from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.crud.product import (
    atualizar_produto,
    criar_produto,
    inativar_produto,
    listar_produtos,
    obter_produto,
)
from app.database import get_db
from app.models.user import User
from app.schemas.product import ProductCreate, ProductResponse, ProductUpdate

router = APIRouter(prefix="/products", tags=["Products"])


@router.post("/", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
def criar(
    product: ProductCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    novo = criar_produto(db, tenant_id=current_user.tenant_id, product=product)
    if not novo:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="SKU já cadastrado")
    return novo


@router.get("/", response_model=list[ProductResponse])
def listar(
    apenas_ativos: bool = Query(default=True),
    apenas_estoque_baixo: bool = Query(default=False),
    limit: int = Query(default=100, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return listar_produtos(
        db,
        tenant_id=current_user.tenant_id,
        apenas_ativos=apenas_ativos,
        apenas_estoque_baixo=apenas_estoque_baixo,
        limit=limit,
        offset=offset,
    )


@router.get("/{product_id}", response_model=ProductResponse)
def obter(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    produto = obter_produto(db, tenant_id=current_user.tenant_id, product_id=product_id)
    if not produto:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Produto não encontrado")
    return produto


@router.patch("/{product_id}", response_model=ProductResponse)
def atualizar(
    product_id: int,
    dados: ProductUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    produto = atualizar_produto(
        db, tenant_id=current_user.tenant_id, product_id=product_id, dados=dados
    )
    if not produto:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Produto não encontrado")
    return produto


@router.delete("/{product_id}", response_model=ProductResponse)
def inativar(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    produto = inativar_produto(db, tenant_id=current_user.tenant_id, product_id=product_id)
    if not produto:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Produto não encontrado")
    return produto
