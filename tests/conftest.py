import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

os.environ["DATABASE_URL"] = "sqlite://"

from app import crud_usuarios, models, schemas
from app.database import Base, get_db
from app.main import app

SENHA_ORGANIZADOR = "organizador123"
EMAIL_ORGANIZADOR = "organizador@mackenzista.com.br"


@pytest.fixture()
def session_factory():
    """Banco SQLite em memória, isolado por teste."""
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    testing_session = sessionmaker(
        bind=engine,
        autoflush=False,
        autocommit=False,
    )
    Base.metadata.create_all(bind=engine)
    yield testing_session
    Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def anonimo(session_factory):
    """Cliente SEM login (visitante)."""

    def override_get_db():
        db = session_factory()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture()
def client(anonimo, session_factory):
    """
    Cliente já autenticado como ORGANIZADOR. É o cliente usado pelos testes
    originais (test_api.py), que cadastram espaços, eventos e sessões.
    """
    db = session_factory()
    crud_usuarios.criar_usuario(
        db,
        schemas.UsuarioCreate(
            nome="Organizador", email=EMAIL_ORGANIZADOR, senha=SENHA_ORGANIZADOR
        ),
        papel=models.PAPEL_ORGANIZADOR,
    )
    db.close()

    login = anonimo.post(
        "/auth/login",
        json={"email": EMAIL_ORGANIZADOR, "senha": SENHA_ORGANIZADOR},
    )
    assert login.status_code == 200
    token = login.json()["access_token"]
    return TestClient(app, headers={"Authorization": f"Bearer {token}"})


@pytest.fixture()
def criar_participante(anonimo):
    """
    Fábrica de participantes: cada chamada registra um aluno novo e devolve
    (headers_de_autenticacao, dados_do_usuario).
    """
    contador = {"n": 0}

    def _criar(nome: str | None = None):
        contador["n"] += 1
        n = contador["n"]
        email = f"aluno{n}@mackenzista.com.br"
        registro = anonimo.post(
            "/auth/registro",
            json={"nome": nome or f"Aluno {n}", "email": email, "senha": "senha123"},
        )
        assert registro.status_code == 201
        login = anonimo.post("/auth/login", json={"email": email, "senha": "senha123"})
        assert login.status_code == 200
        headers = {"Authorization": f"Bearer {login.json()['access_token']}"}
        return headers, registro.json()

    return _criar
