from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud, schemas
from app.database import get_db

router = APIRouter(prefix="/eventos", tags=["Eventos"])


@router.post("", response_model=schemas.EventoOut, status_code=201)
def criar_evento(dados: schemas.EventoCreate, db: Session = Depends(get_db)):
    return crud.criar_evento(db, dados)


@router.get("", response_model=list[schemas.EventoOut])
def listar_eventos(db: Session = Depends(get_db)):
    return crud.listar_eventos(db)


@router.get("/{evento_id}", response_model=schemas.EventoOut)
def obter_evento(evento_id: int, db: Session = Depends(get_db)):
    evento = crud.obter_evento(db, evento_id)
    if not evento:
        raise HTTPException(status_code=404, detail="Evento não encontrado")
    return evento


@router.put("/{evento_id}", response_model=schemas.EventoOut)
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


@router.delete("/{evento_id}", status_code=204)
def remover_evento(evento_id: int, db: Session = Depends(get_db)):
    evento = crud.obter_evento(db, evento_id)
    if not evento:
        raise HTTPException(status_code=404, detail="Evento não encontrado")
    crud.remover_evento(db, evento)
