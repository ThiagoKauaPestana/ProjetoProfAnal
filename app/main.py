from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app import crud_usuarios
from app.database import Base, SessionLocal, engine
from app.routers import auth, espacos, eventos, inscricoes, sessoes

Base.metadata.create_all(bind=engine)


@asynccontextmanager
async def lifespan(_: FastAPI):
    # Cria o organizador inicial se ORGANIZADOR_EMAIL e ORGANIZADOR_SENHA
    # estiverem definidos no ambiente (ver .env.example). Sem elas, não faz nada.
    db = SessionLocal()
    try:
        crud_usuarios.garantir_organizador_inicial(db)
    finally:
        db.close()
    yield


app = FastAPI(
    title="Auditório Inteligente API",
    description="Gestão de espaços, eventos e sessões, com inscrições de participantes",
    version="0.3.0",
    lifespan=lifespan,
)

app.include_router(auth.router)
app.include_router(espacos.router)
app.include_router(eventos.router)
app.include_router(sessoes.router)
app.include_router(inscricoes.router)

frontend_dir = Path(__file__).resolve().parent.parent / "frontend"
app.mount("/static", StaticFiles(directory=frontend_dir), name="static")


@app.get("/", include_in_schema=False)
def frontend():
    return FileResponse(frontend_dir / "index.html")


@app.get("/api/status", tags=["Status"])
def status():
    return {"status": "ok", "servico": "auditorio-inteligente-api"}


from fastapi.staticfiles import StaticFiles

app.mount(
    "/painel",
    StaticFiles(directory="frontend", html=True),
    name="painel"
)

