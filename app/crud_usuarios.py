import os

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app import models, schemas
from app.security import gerar_hash_senha, verificar_senha


class EmailJaCadastradoError(Exception):
    """Lançada quando já existe um usuário com o e-mail informado."""


def obter_usuario_por_email(db: Session, email: str) -> models.Usuario | None:
    return db.scalar(
        select(models.Usuario).where(models.Usuario.email == email.strip().lower())
    )


def criar_usuario(
    db: Session,
    dados: schemas.UsuarioCreate,
    papel: str = models.PAPEL_PARTICIPANTE,
) -> models.Usuario:
    if obter_usuario_por_email(db, dados.email):
        raise EmailJaCadastradoError(dados.email)

    usuario = models.Usuario(
        nome=dados.nome,
        email=dados.email,
        senha_hash=gerar_hash_senha(dados.senha),
        papel=papel,
    )
    db.add(usuario)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise EmailJaCadastradoError(dados.email)
    db.refresh(usuario)
    return usuario


def autenticar(db: Session, email: str, senha: str) -> models.Usuario | None:
    usuario = obter_usuario_por_email(db, email)
    if usuario is None or not usuario.ativo:
        return None
    if not verificar_senha(senha, usuario.senha_hash):
        return None
    return usuario


def garantir_organizador_inicial(
    db: Session,
    email: str | None = None,
    senha: str | None = None,
    nome: str | None = None,
) -> models.Usuario | None:
    """
    Cria (ou promove) o organizador inicial a partir das variáveis de ambiente
    ORGANIZADOR_EMAIL, ORGANIZADOR_SENHA e ORGANIZADOR_NOME. Sem e-mail e senha
    não faz nada. Se o usuário já existe, a senha NÃO é alterada.
    """
    email = email or os.getenv("ORGANIZADOR_EMAIL")
    senha = senha or os.getenv("ORGANIZADOR_SENHA")
    nome = nome or os.getenv("ORGANIZADOR_NOME", "Organizador")
    if not email or not senha:
        return None

    existente = obter_usuario_por_email(db, email)
    if existente:
        if existente.papel != models.PAPEL_ORGANIZADOR:
            existente.papel = models.PAPEL_ORGANIZADOR
            db.commit()
            db.refresh(existente)
        return existente

    dados = schemas.UsuarioCreate(nome=nome, email=email, senha=senha)
    return criar_usuario(db, dados, papel=models.PAPEL_ORGANIZADOR)
