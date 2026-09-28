from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud, schemas
from app.database import get_db

router = APIRouter(prefix="/espacos", tags=["Espaços"])


@router.post("", response_model=schemas.EspacoOut, status_code=201)
def criar_espaco(dados: schemas.EspacoCreate, db: Session = Depends(get_db)):
    return crud.criar_espaco(db, dados)


@router.get("", response_model=list[schemas.EspacoOut])
def listar_espacos(apenas_ativos: bool = False, db: Session = Depends(get_db)):
    return crud.listar_espacos(db, apenas_ativos=apenas_ativos)


@router.get("/{espaco_id}", response_model=schemas.EspacoOut)
def obter_espaco(espaco_id: int, db: Session = Depends(get_db)):
    espaco = crud.obter_espaco(db, espaco_id)
    if not espaco:
        raise HTTPException(status_code=404, detail="Espaço não encontrado")
    return espaco


@router.put("/{espaco_id}", response_model=schemas.EspacoOut)
def atualizar_espaco(
    espaco_id: int, dados: schemas.EspacoUpdate, db: Session = Depends(get_db)
):
    espaco = crud.obter_espaco(db, espaco_id)
    if not espaco:
        raise HTTPException(status_code=404, detail="Espaço não encontrado")
    return crud.atualizar_espaco(db, espaco, dados)


@router.delete("/{espaco_id}", status_code=204)
def remover_espaco(espaco_id: int, db: Session = Depends(get_db)):
    espaco = crud.obter_espaco(db, espaco_id)
    if not espaco:
        raise HTTPException(status_code=404, detail="Espaço não encontrado")
    crud.remover_espaco(db, espaco)
