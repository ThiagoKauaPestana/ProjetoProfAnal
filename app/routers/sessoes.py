from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud, crud_inscricoes, models, schemas
from app.database import get_db
from app.deps import exigir_organizador

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


def montar_catalogo(
    db: Session, sessoes: list[models.Sessao]
) -> list[schemas.SessaoCatalogoOut]:
    """Anexa a cada sessão a situação das vagas (ocupadas, livres, fila)."""
    contagens = crud_inscricoes.contar_por_status(db, [s.id for s in sessoes])
    itens = []
    for sessao in sessoes:
        total = crud_inscricoes.capacidade_total(sessao)
        ocupadas = contagens[sessao.id][models.STATUS_CONFIRMADA]
        base = schemas.SessaoOut.model_validate(sessao).model_dump()
        itens.append(
            schemas.SessaoCatalogoOut(
                **base,
                evento_nome=sessao.evento.nome,
                espaco_nome=sessao.espaco.nome,
                capacidade_total=total,
                vagas_ocupadas=ocupadas,
                vagas_disponiveis=max(total - ocupadas, 0),
                lista_espera=contagens[sessao.id][models.STATUS_LISTA_ESPERA],
            )
        )
    return itens


@router.post(
    "",
    response_model=schemas.SessaoOut,
    status_code=201,
    dependencies=[Depends(exigir_organizador)],
)
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


@router.get("", response_model=list[schemas.SessaoCatalogoOut])
def listar_sessoes(
    evento_id: int | None = None,
    espaco_id: int | None = None,
    tipo: str | None = None,
    busca: str | None = None,
    data: date | None = None,
    data_de: date | None = None,
    data_ate: date | None = None,
    apenas_com_vagas: bool = False,
    db: Session = Depends(get_db),
):
    """
    Catálogo de sessões (público), ordenado por horário de início.

    Filtros: evento_id, espaco_id, tipo (palestra, workshop...), busca
    (título, descrição ou responsável), data (um dia), data_de/data_ate
    (sessões que começam no intervalo) e apenas_com_vagas.
    """
    sessoes = crud.listar_sessoes(
        db,
        evento_id=evento_id,
        espaco_id=espaco_id,
        tipo=tipo,
        busca=busca,
        data=data,
        data_de=data_de,
        data_ate=data_ate,
        apenas_com_vagas=apenas_com_vagas,
    )
    return montar_catalogo(db, sessoes)


@router.get("/{sessao_id}", response_model=schemas.SessaoCatalogoOut)
def obter_sessao(sessao_id: int, db: Session = Depends(get_db)):
    sessao = crud.obter_sessao(db, sessao_id)
    if not sessao:
        raise HTTPException(status_code=404, detail="Sessão não encontrada")
    return montar_catalogo(db, [sessao])[0]


@router.put(
    "/{sessao_id}",
    response_model=schemas.SessaoOut,
    dependencies=[Depends(exigir_organizador)],
)
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


@router.delete(
    "/{sessao_id}", status_code=204, dependencies=[Depends(exigir_organizador)]
)
def remover_sessao(sessao_id: int, db: Session = Depends(get_db)):
    sessao = crud.obter_sessao(db, sessao_id)
    if not sessao:
        raise HTTPException(status_code=404, detail="Sessão não encontrada")
    crud.remover_sessao(db, sessao)
