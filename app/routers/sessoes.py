from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud, schemas
from app.database import get_db

router = APIRouter(prefix="/sessoes", tags=["Sessões"])


def _formatar_conflitos(conflitos):
    return [
        {
            "id": s.id,
            "titulo": s.titulo,
            "espaco_id": s.espaco_id,
            "data_hora_inicio": s.data_hora_inicio.isoformat(),
            "data_hora_fim": s.data_hora_fim.isoformat(),
        }
        for s in conflitos
    ]


@router.post("", response_model=schemas.SessaoOut, status_code=201)
def criar_sessao(dados: schemas.SessaoCreate, db: Session = Depends(get_db)):
    if not crud.obter_evento(db, dados.evento_id):
        raise HTTPException(status_code=404, detail="Evento não encontrado")
    if not crud.obter_espaco(db, dados.espaco_id):
        raise HTTPException(status_code=404, detail="Espaço não encontrado")
    try:
        return crud.criar_sessao(db, dados)
    except crud.ConflitoDeHorarioError as exc:
        raise HTTPException(
            status_code=409,
            detail={
                "mensagem": "O espaço já está reservado nesse horário.",
                "conflitos": _formatar_conflitos(exc.conflitos),
            },
        )


@router.get("", response_model=list[schemas.SessaoOut])
def listar_sessoes(
    evento_id: int | None = None,
    espaco_id: int | None = None,
    db: Session = Depends(get_db),
):
    return crud.listar_sessoes(db, evento_id=evento_id, espaco_id=espaco_id)


@router.get("/{sessao_id}", response_model=schemas.SessaoOut)
def obter_sessao(sessao_id: int, db: Session = Depends(get_db)):
    sessao = crud.obter_sessao(db, sessao_id)
    if not sessao:
        raise HTTPException(status_code=404, detail="Sessão não encontrada")
    return sessao


@router.put("/{sessao_id}", response_model=schemas.SessaoOut)
def atualizar_sessao(
    sessao_id: int, dados: schemas.SessaoUpdate, db: Session = Depends(get_db)
):
    sessao = crud.obter_sessao(db, sessao_id)
    if not sessao:
        raise HTTPException(status_code=404, detail="Sessão não encontrada")
    try:
        return crud.atualizar_sessao(db, sessao, dados)
    except crud.ConflitoDeHorarioError as exc:
        raise HTTPException(
            status_code=409,
            detail={
                "mensagem": "O espaço já está reservado nesse horário.",
                "conflitos": _formatar_conflitos(exc.conflitos),
            },
        )


@router.delete("/{sessao_id}", status_code=204)
def remover_sessao(sessao_id: int, db: Session = Depends(get_db)):
    sessao = crud.obter_sessao(db, sessao_id)
    if not sessao:
        raise HTTPException(status_code=404, detail="Sessão não encontrada")
    crud.remover_sessao(db, sessao)
