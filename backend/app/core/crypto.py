"""Criptografia simétrica dos tokens do ML em repouso (nunca gravar em texto plano)."""

import os

from cryptography.fernet import Fernet, InvalidToken
from dotenv import load_dotenv

load_dotenv()

_ENCRYPTION_KEY = os.getenv("ML_TOKEN_ENCRYPTION_KEY")

if not _ENCRYPTION_KEY:
    raise ValueError("A variável ML_TOKEN_ENCRYPTION_KEY não foi definida no arquivo .env")

_fernet = Fernet(_ENCRYPTION_KEY.encode())


def criptografar(valor: str) -> str:
    return _fernet.encrypt(valor.encode()).decode()


def descriptografar(valor: str) -> str:
    try:
        return _fernet.decrypt(valor.encode()).decode()
    except InvalidToken as exc:
        raise ValueError("Token armazenado é inválido ou a chave de criptografia mudou") from exc
