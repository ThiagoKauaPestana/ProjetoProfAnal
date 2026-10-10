from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.database import Base, engine
from app.routers import espacos, eventos, sessoes

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Auditório Inteligente API",
    description="Gestão de espaços, eventos e sessões",
    version="0.1.0",
)

app.include_router(espacos.router)
app.include_router(eventos.router)
app.include_router(sessoes.router)

frontend_dir = Path(__file__).resolve().parent.parent / "frontend"
app.mount("/static", StaticFiles(directory=frontend_dir), name="static")


@app.get("/", include_in_schema=False)
def frontend():
    return FileResponse(frontend_dir / "index.html")


@app.get("/api/status", tags=["Status"])
def status():
    return {"status": "ok", "servico": "auditorio-inteligente-api"}
