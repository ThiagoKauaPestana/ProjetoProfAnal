from fastapi import FastAPI

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


@app.get("/", tags=["Status"])
def status():
    return {"status": "ok", "servico": "auditorio-inteligente-api"}
