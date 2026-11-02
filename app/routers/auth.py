import os

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy import select

from app import crud_usuarios, models, schemas, security
from app.database import get_db
from app.deps import exigir_organizador, get_usuario_atual

router = APIRouter(prefix="/auth", tags=["Autenticação"])


def _token_para(usuario: models.Usuario) -> schemas.TokenOut:
    return schemas.TokenOut(
        access_token=security.criar_token(usuario.id, usuario.papel),
        usuario=schemas.UsuarioOut.model_validate(usuario),
    )


@router.post("/registro", response_model=schemas.UsuarioOut, status_code=201)
def registrar_participante(dados: schemas.UsuarioCreate, db: Session = Depends(get_db)):
    """Cadastro público: sempre cria um usuário com papel *participante*."""
    try:
        return crud_usuarios.criar_usuario(db, dados, papel=models.PAPEL_PARTICIPANTE)
    except crud_usuarios.EmailJaCadastradoError:
        raise HTTPException(status_code=409, detail="E-mail já cadastrado")


@router.post("/login", response_model=schemas.TokenOut)
def login(dados: schemas.LoginIn, db: Session = Depends(get_db)):
    usuario = crud_usuarios.autenticar(db, dados.email, dados.senha)
    if usuario is None:
        raise HTTPException(
            status_code=401,
            detail="E-mail ou senha incorretos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return _token_para(usuario)


@router.post("/token", response_model=schemas.TokenOut, include_in_schema=True)
def login_formulario(
    form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    """Mesmo login, no formato de formulário OAuth2 (botão *Authorize* do /docs).
    Use o e-mail no campo *username*."""
    usuario = crud_usuarios.autenticar(db, form.username, form.password)
    if usuario is None:
        raise HTTPException(
            status_code=401,
            detail="E-mail ou senha incorretos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return _token_para(usuario)


@router.get("/me", response_model=schemas.UsuarioOut)
def meus_dados(usuario: models.Usuario = Depends(get_usuario_atual)):
    return usuario


@router.post(
    "/organizadores",
    response_model=schemas.UsuarioOut,
    status_code=201,
    dependencies=[Depends(exigir_organizador)],
)
def criar_organizador(dados: schemas.UsuarioCreate, db: Session = Depends(get_db)):
    """Somente um organizador já existente pode criar outro organizador."""
    try:
        return crud_usuarios.criar_usuario(db, dados, papel=models.PAPEL_ORGANIZADOR)
    except crud_usuarios.EmailJaCadastradoError:
        raise HTTPException(status_code=409, detail="E-mail já cadastrado")


@router.get("/usuarios", response_model=list[schemas.UsuarioOut])
def listar_usuarios(
    _: models.Usuario = Depends(exigir_organizador), db: Session = Depends(get_db)
):
    """Lista as contas para gestão de perfis pelo organizador."""
    return list(db.scalars(select(models.Usuario).order_by(models.Usuario.nome, models.Usuario.id)))


@router.patch("/usuarios/{usuario_id}/perfil", response_model=schemas.UsuarioOut)
def alterar_perfil(
    usuario_id: int,
    dados: schemas.PerfilUpdate,
    autor: models.Usuario = Depends(exigir_organizador),
    db: Session = Depends(get_db),
):
    """Altera o perfil de outra conta, preservando o acesso administrativo atual."""
    usuarios = list(db.scalars(
        select(models.Usuario).order_by(models.Usuario.id).with_for_update()
        .execution_options(populate_existing=True)
    ))
    if autor.papel != models.PAPEL_ORGANIZADOR or not autor.ativo:
        raise HTTPException(status_code=403, detail="Apenas organizadores podem alterar perfis")
    alvo = next((u for u in usuarios if u.id == usuario_id), None)
    if alvo is None:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    if alvo.id == autor.id and dados.papel != autor.papel:
        raise HTTPException(status_code=409, detail="Peça a outro administrador para alterar seu perfil")
    email_inicial = os.getenv("ORGANIZADOR_EMAIL", "").strip().lower()
    if alvo.email == email_inicial and dados.papel != models.PAPEL_ORGANIZADOR:
        raise HTTPException(status_code=409, detail="O organizador inicial deve manter acesso administrativo")
    alvo.papel = dados.papel
    db.commit()
    db.refresh(alvo)
    return alvo
