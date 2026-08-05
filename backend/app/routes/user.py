from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.deps import require_admin
from app.crud.user import criar_usuario, desativar_usuario, listar_usuarios
from app.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def criar(
    user: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    novo_usuario = criar_usuario(db, tenant_id=current_user.tenant_id, user=user)

    if not novo_usuario:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email já cadastrado",
        )

    return novo_usuario


@router.get("/", response_model=list[UserResponse])
def listar(
    limit: int = Query(default=100, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    return listar_usuarios(db, tenant_id=current_user.tenant_id, limit=limit, offset=offset)


@router.delete("/{user_id}", response_model=UserResponse)
def desativar(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    usuario = desativar_usuario(db, tenant_id=current_user.tenant_id, user_id=user_id)

    if not usuario:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado")

    return usuario
