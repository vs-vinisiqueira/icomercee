import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("A variável DATABASE_URL não foi definida no arquivo .env")

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Garante que todo módulo de modelo é importado assim que o app.database é importado
# por qualquer entrypoint (main.py, scripts/, testes) — sem isso, uma FK referenciada só
# por string (ex: ForeignKey("tenants.id")) falha em runtime se a classe dona da tabela
# nunca foi importada por nenhuma rota. Fica no fim do arquivo porque depende de Base
# já estar definida acima.
from app import models  # noqa: E402,F401
