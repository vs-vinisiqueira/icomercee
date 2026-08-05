"""Sobe um Postgres local descartável (via pgserver, binário portátil, sem instalação)
para desenvolvimento/teste manual. Não faz parte do runtime de produção -- em produção
usa-se um Postgres real (Railway/Render/RDS/etc). Mantém o processo vivo até ser
interrompido; escreve a DATABASE_URL em dev_pg_uri.txt para outros scripts lerem."""

import pathlib
import time

import pgserver

DATA_DIR = pathlib.Path(__file__).resolve().parent.parent / "pgdata_dev"
URI_FILE = pathlib.Path(__file__).resolve().parent.parent / "dev_pg_uri.txt"

server = pgserver.get_server(str(DATA_DIR))
uri = server.get_uri()
URI_FILE.write_text(uri)
print(f"Postgres de dev rodando em: {uri}")
print("Pressione Ctrl+C ou mate o processo para encerrar.")

try:
    while True:
        time.sleep(3600)
except KeyboardInterrupt:
    pass
finally:
    server.cleanup()
    URI_FILE.unlink(missing_ok=True)
