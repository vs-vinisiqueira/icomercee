"""Cria o tenant inicial e o usuário admin da cliente.

Uso:
    python scripts/seed_admin.py --tenant "Nome da Loja" --nome "Fulana" --email fulana@exemplo.com --senha "senha-forte"
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.core.security import gerar_hash_senha  # noqa: E402
from app.database import SessionLocal  # noqa: E402
from app.models.tenant import Tenant  # noqa: E402
from app.models.user import User  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description="Seed do tenant e usuário admin inicial")
    parser.add_argument("--tenant", required=True, help="Nome da loja/tenant")
    parser.add_argument("--nome", required=True, help="Nome do usuário admin")
    parser.add_argument("--email", required=True, help="Email de login do admin")
    parser.add_argument("--senha", required=True, help="Senha do admin (mín. 8 caracteres)")
    args = parser.parse_args()

    if len(args.senha) < 8:
        raise SystemExit("A senha precisa ter no mínimo 8 caracteres")

    db = SessionLocal()
    try:
        existente = db.query(User).filter(User.email == args.email.lower()).first()
        if existente:
            raise SystemExit(f"Já existe um usuário com o email {args.email}")

        tenant = Tenant(nome=args.tenant)
        db.add(tenant)
        db.flush()

        admin = User(
            tenant_id=tenant.id,
            nome=args.nome,
            email=args.email.lower(),
            senha_hash=gerar_hash_senha(args.senha),
            role="admin",
        )
        db.add(admin)
        db.commit()

        print(f"Tenant '{tenant.nome}' (id={tenant.id}) criado.")
        print(f"Admin '{admin.nome}' <{admin.email}> (id={admin.id}) criado com sucesso.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
