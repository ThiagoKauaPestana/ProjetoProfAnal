"""Hash de senha (scrypt, só biblioteca padrão) e tokens JWT."""

import hashlib
import hmac
import os
import secrets
from datetime import datetime, timedelta, timezone

import jwt

# Em produção defina SECRET_KEY no ambiente (Render: variável de ambiente).
SECRET_KEY = os.getenv(
    "SECRET_KEY", "dev-only-chave-insegura-troque-em-producao-0123456789"
)
ALGORITHM = "HS256"
TOKEN_EXPIRA_MINUTOS = int(os.getenv("TOKEN_EXPIRA_MINUTOS", "60"))

_SCRYPT_N = 2**14
_SCRYPT_R = 8
_SCRYPT_P = 1


def gerar_hash_senha(senha: str) -> str:
    salt = secrets.token_bytes(16)
    derivada = hashlib.scrypt(
        senha.encode("utf-8"),
        salt=salt,
        n=_SCRYPT_N,
        r=_SCRYPT_R,
        p=_SCRYPT_P,
        dklen=32,
    )
    return f"scrypt${_SCRYPT_N}${_SCRYPT_R}${_SCRYPT_P}${salt.hex()}${derivada.hex()}"


def verificar_senha(senha: str, hash_armazenado: str) -> bool:
    try:
        algoritmo, n, r, p, salt_hex, hash_hex = hash_armazenado.split("$")
        if algoritmo != "scrypt":
            return False
        esperado = bytes.fromhex(hash_hex)
        derivada = hashlib.scrypt(
            senha.encode("utf-8"),
            salt=bytes.fromhex(salt_hex),
            n=int(n),
            r=int(r),
            p=int(p),
            dklen=len(esperado),
        )
    except (ValueError, TypeError):
        return False
    return hmac.compare_digest(derivada, esperado)


def criar_token(usuario_id: int, papel: str) -> str:
    agora = datetime.now(timezone.utc)
    payload = {
        "sub": str(usuario_id),
        "papel": papel,
        "iat": agora,
        "exp": agora + timedelta(minutes=TOKEN_EXPIRA_MINUTOS),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decodificar_token(token: str) -> dict | None:
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.PyJWTError:
        return None
