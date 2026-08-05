from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.crud.product_channel_mapping import criar_vinculo, listar_vinculos
from app.database import get_db
from app.models.user import User
from app.schemas.product_mapping import ProductMappingCreate, ProductMappingResponse

router = APIRouter(prefix="/product-mappings", tags=["Product Mappings"])


@router.post("/", response_model=ProductMappingResponse, status_code=status.HTTP_201_CREATED)
def criar(
    dados: ProductMappingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    vinculo = criar_vinculo(
        db,
        tenant_id=current_user.tenant_id,
        canal=dados.canal,
        item_id_externo=dados.item_id_externo,
        product_id=dados.product_id,
    )
    if not vinculo:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Este anúncio já está vinculado a um produto",
        )
    return vinculo


@router.get("/", response_model=list[ProductMappingResponse])
def listar(
    limit: int = Query(default=100, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return listar_vinculos(db, tenant_id=current_user.tenant_id, limit=limit, offset=offset)
