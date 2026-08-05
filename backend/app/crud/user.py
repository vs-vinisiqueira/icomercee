from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.security import gerar_hash_senha
from app.models.user import User
from app.schemas.user import UserCreate


def criar_usuario(db: Session, tenant_id: int, user: UserCreate) -> User | None:
    usuario_existente = db.query(User).filter(User.email == user.email).first()

    if usuario_existente:
        return None

    novo_usuario = User(
        tenant_id=tenant_id,
        nome=user.nome,
        email=user.email,
        senha_hash=gerar_hash_senha(user.senha),
        role=user.role,
    )

    try:
        db.add(novo_usuario)
        db.commit()
        db.refresh(novo_usuario)
    except IntegrityError:
        db.rollback()
        return None

    return novo_usuario


def listar_usuarios(db: Session, tenant_id: int, limit: int = 100, offset: int = 0) -> list[User]:
    return (
        db.query(User)
        .filter(User.tenant_id == tenant_id)
        .offset(offset)
        .limit(limit)
        .all()
    )


def obter_usuario_por_email(db: Session, email: str) -> User | None:
    return db.query(User).filter(User.email == email).first()


def desativar_usuario(db: Session, tenant_id: int, user_id: int) -> User | None:
    usuario = (
        db.query(User)
        .filter(User.id == user_id, User.tenant_id == tenant_id)
        .first()
    )
    if not usuario:
        return None

    usuario.ativo = False
    db.commit()
    db.refresh(usuario)
    return usuario
