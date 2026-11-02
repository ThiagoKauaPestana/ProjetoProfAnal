from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud, schemas
from app.database import get_db
from app.deps import exigir_organizador

router = APIRouter(prefix="/eventos", tags=["Eventos"])


@router.post(
    "",
    response_model=schemas.EventoOut,
    status_code=201,
    dependencies=[Depends(exigir_organizador)],
)
def criar_evento(dados: schemas.EventoCreate, db: Session = Depends(get_db)):
    return crud.criar_evento(db, dados)


@router.get("", response_model=list[schemas.EventoOut])
def listar_eventos(
    status: str | None = None,
    busca: str | None = None,
    data_de: date | None = None,
    data_ate: date | None = None,
    db: Session = Depends(get_db),
):
    """Catálogo de eventos (público). Filtros: status, busca (nome/descrição) e
    período (`data_de`/`data_ate` retornam eventos que ocorrem nesse intervalo)."""
    return crud.listar_eventos(
        db, status=status, busca=busca, data_de=data_de, data_ate=data_ate
    )


@router.get("/{evento_id}", response_model=schemas.EventoOut)
def obter_evento(evento_id: int, db: Session = Depends(get_db)):
    evento = crud.obter_evento(db, evento_id)
    if not evento:
        raise HTTPException(status_code=404, detail="Evento não encontrado")
    return evento


@router.put(
    "/{evento_id}",
    response_model=schemas.EventoOut,
    dependencies=[Depends(exigir_organizador)],
)
def atualizar_evento(
    evento_id: int, dados: schemas.EventoUpdate, db: Session = Depends(get_db)
):
    evento = crud.obter_evento(db, evento_id)
    if not evento:
        raise HTTPException(status_code=404, detail="Evento não encontrado")
    try:
        return crud.atualizar_evento(db, evento, dados)
    except crud.PeriodoEventoInvalidoError as exc:
        raise HTTPException(status_code=422, detail=str(exc))


@router.delete(
    "/{evento_id}", status_code=204, dependencies=[Depends(exigir_organizador)]
)
def remover_evento(evento_id: int, db: Session = Depends(get_db)):
    evento = crud.obter_evento(db, evento_id)
    if not evento:
        raise HTTPException(status_code=404, detail="Evento não encontrado")
    crud.remover_evento(db, evento)
