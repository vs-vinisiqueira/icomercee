"""Regressão: em produção, só `app.main` é importado (é isso que o uvicorn faz) — não
o conjunto de imports manuais que `conftest.py` faz para montar as fixtures de teste.
Um bug real escapou dos testes unitários porque `app.models.tenant` nunca era
importado por nenhuma rota; `suppliers.tenant_id` referencia `tenants.id` só por
string, e o SQLAlchemy só resolve isso ao configurar os mappers (no primeiro insert).
Rodar `import app.main` num subprocesso limpo, do jeito que o uvicorn importa,
reproduz exatamente esse cenário sem a rede de segurança dos imports do conftest."""

import subprocess
import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent

TABELAS_ESPERADAS = {
    "tenants",
    "users",
    "suppliers",
    "products",
    "stock_movements",
    "orders",
    "product_channel_mapping",
    "ml_credentials",
    "webhook_events",
}


def test_importar_app_main_isoladamente_registra_todas_as_tabelas(monkeypatch):
    script = (
        "import app.main\n"
        "from app.database import Base\n"
        "from sqlalchemy.orm import configure_mappers\n"
        "configure_mappers()\n"
        "tabelas = set(Base.metadata.tables.keys())\n"
        f"esperado = {sorted(TABELAS_ESPERADAS)!r}\n"
        "faltando = set(esperado) - tabelas\n"
        "assert not faltando, f'tabelas nao registradas: {faltando}'\n"
        "print('OK')\n"
    )

    resultado = subprocess.run(
        [sys.executable, "-c", script],
        cwd=str(BACKEND_DIR),
        capture_output=True,
        text=True,
        timeout=30,
    )

    assert resultado.returncode == 0, resultado.stdout + resultado.stderr
    assert "OK" in resultado.stdout
