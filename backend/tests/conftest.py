"""Testes rodam contra um SQLite em arquivo (não :memory:, para que múltiplas
conexões/sessões enxerguem os mesmos dados — vários serviços abrem sua própria
SessionLocal()). As variáveis de ambiente precisam existir ANTES de qualquer
import de app.* para que app.database crie o engine já apontando pro SQLite
de teste em vez do Postgres do .env."""

import os
import sys
from pathlib import Path

TEST_DB_PATH = Path(__file__).parent / "test_sistema_dri.db"

os.environ["DATABASE_URL"] = f"sqlite:///{TEST_DB_PATH}"
os.environ["JWT_SECRET_KEY"] = "test-secret-key"
os.environ["JWT_ALGORITHM"] = "HS256"
os.environ["ACCESS_TOKEN_EXPIRE_MINUTES"] = "480"
os.environ["ML_TOKEN_ENCRYPTION_KEY"] = "Uu8x0y2A4B6c8D0e2F4g6H8i0J2k4L6m8N0o2P4q6R8="
os.environ["ML_CLIENT_ID"] = "test-client-id"
os.environ["ML_CLIENT_SECRET"] = "test-client-secret"
os.environ["ML_REDIRECT_URI"] = "http://localhost:8000/integrations/ml/callback"

sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest  # noqa: E402

from app.database import Base, SessionLocal, engine  # noqa: E402
from app.models import (  # noqa: E402, F401
    ml_credentials,
    order,
    product,
    product_channel_mapping,
    stock_movement,
    supplier,
    tenant,
    user,
    webhook_event,
)
from app.core.security import gerar_hash_senha  # noqa: E402


@pytest.fixture(scope="session", autouse=True)
def _setup_database():
    if TEST_DB_PATH.exists():
        TEST_DB_PATH.unlink()

    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)
    engine.dispose()
    if TEST_DB_PATH.exists():
        TEST_DB_PATH.unlink()


@pytest.fixture
def db():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.rollback()
        session.close()

    # Limpa todas as tabelas entre testes (services abrem sua própria SessionLocal(),
    # então rollback() sozinho não é suficiente — dados já commitados persistiriam).
    cleanup = SessionLocal()
    try:
        for table in reversed(Base.metadata.sorted_tables):
            cleanup.execute(table.delete())
        cleanup.commit()
    finally:
        cleanup.close()


@pytest.fixture
def tenant_factory(db):
    def _criar(nome: str = "Loja Teste"):
        t = tenant.Tenant(nome=nome)
        db.add(t)
        db.commit()
        db.refresh(t)
        return t

    return _criar


@pytest.fixture
def user_factory(db):
    def _criar(tenant_id: int, email: str = "admin@teste.com", role: str = "admin"):
        u = user.User(
            tenant_id=tenant_id,
            nome="Usuário Teste",
            email=email,
            senha_hash=gerar_hash_senha("senha12345"),
            role=role,
        )
        db.add(u)
        db.commit()
        db.refresh(u)
        return u

    return _criar


@pytest.fixture
def product_factory(db):
    def _criar(tenant_id: int, sku: str = "SKU-1", estoque_atual: int = 0, estoque_minimo: int = 0):
        p = product.Product(
            tenant_id=tenant_id,
            sku=sku,
            nome=f"Produto {sku}",
            estoque_atual=estoque_atual,
            estoque_minimo=estoque_minimo,
        )
        db.add(p)
        db.commit()
        db.refresh(p)
        return p

    return _criar
