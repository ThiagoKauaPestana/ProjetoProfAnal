"""Dependências de autenticação e permissão usadas pelos routers."""

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app import models, security
from app.database import get_db

# auto_error=False para devolvermos a mensagem de erro em português.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token", auto_error=False)


def get_usuario_atual(
    token: str | None = Depends(oauth2_scheme), db: Session = Depends(get_db)
) -> models.Usuario:
    erro = HTTPException(
        status_code=401,
        detail="Credenciais inválidas ou ausentes",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if not token:
        raise erro
    payload = security.decodificar_token(token)
    if not payload:
        raise erro
    try:
        usuario_id = int(payload["sub"])
    except (KeyError, ValueError, TypeError):
        raise erro

    usuario = db.get(models.Usuario, usuario_id)
    if usuario is None or not usuario.ativo:
        raise erro
    return usuario


def exigir_organizador(
    usuario: models.Usuario = Depends(get_usuario_atual),
) -> models.Usuario:
    if usuario.papel != models.PAPEL_ORGANIZADOR:
        raise HTTPException(
            status_code=403, detail="Apenas organizadores podem executar esta ação"
        )
    return usuario


def exigir_participante(
    usuario: models.Usuario = Depends(get_usuario_atual),
) -> models.Usuario:
    if usuario.papel != models.PAPEL_PARTICIPANTE:
        raise HTTPException(
            status_code=403, detail="Apenas participantes podem executar esta ação"
        )
    return usuario
