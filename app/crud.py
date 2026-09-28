from sqlalchemy import select, and_
from sqlalchemy.orm import Session

from app import models, schemas


def criar_espaco(db: Session, dados: schemas.EspacoCreate) -> models.Espaco:
    espaco = models.Espaco(**dados.model_dump())
    db.add(espaco)
    db.commit()
    db.refresh(espaco)
    return espaco


def listar_espacos(db: Session, apenas_ativos: bool = False) -> list[models.Espaco]:
    stmt = select(models.Espaco)
    if apenas_ativos:
        stmt = stmt.where(models.Espaco.ativo.is_(True))
    return list(db.scalars(stmt).all())


def obter_espaco(db: Session, espaco_id: int) -> models.Espaco | None:
    return db.get(models.Espaco, espaco_id)


def atualizar_espaco(
    db: Session, espaco: models.Espaco, dados: schemas.EspacoUpdate
) -> models.Espaco:
    for campo, valor in dados.model_dump(exclude_unset=True).items():
        setattr(espaco, campo, valor)
    db.commit()
    db.refresh(espaco)
    return espaco


def remover_espaco(db: Session, espaco: models.Espaco) -> None:
    db.delete(espaco)
    db.commit()


def criar_evento(db: Session, dados: schemas.EventoCreate) -> models.Evento:
    evento = models.Evento(**dados.model_dump())
    db.add(evento)
    db.commit()
    db.refresh(evento)
    return evento


def listar_eventos(db: Session) -> list[models.Evento]:
    return list(db.scalars(select(models.Evento)).all())


def obter_evento(db: Session, evento_id: int) -> models.Evento | None:
    return db.get(models.Evento, evento_id)


class PeriodoEventoInvalidoError(ValueError):
    """Lancada quando a data final do evento antecede a data inicial."""


def atualizar_evento(
    db: Session, evento: models.Evento, dados: schemas.EventoUpdate
) -> models.Evento:
    atualizacoes = dados.model_dump(exclude_unset=True)
    novo_inicio = atualizacoes.get("data_inicio", evento.data_inicio)
    novo_fim = atualizacoes.get("data_fim", evento.data_fim)

    if novo_fim < novo_inicio:
        raise PeriodoEventoInvalidoError(
            "data_fim nao pode ser anterior a data_inicio"
        )

    for campo, valor in atualizacoes.items():
        setattr(evento, campo, valor)
    db.commit()
    db.refresh(evento)
    return evento


def remover_evento(db: Session, evento: models.Evento) -> None:
    db.delete(evento)
    db.commit()


class ConflitoDeHorarioError(Exception):
    """Lançada quando uma sessão conflita com outra no mesmo espaço."""

    def __init__(self, conflitos: list[models.Sessao]):
        self.conflitos = conflitos
        super().__init__("Conflito de horário para o espaço informado.")


def _buscar_conflitos(
    db: Session,
    espaco_id: int,
    inicio,
    fim,
    ignorar_sessao_id: int | None = None,
) -> list[models.Sessao]:
    """
    Duas sessões conflitam quando seus intervalos [inicio, fim) se sobrepõem
    no MESMO espaço:  existente.inicio < nova.fim  AND  existente.fim > nova.inicio
    """
    stmt = select(models.Sessao).where(
        and_(
            models.Sessao.espaco_id == espaco_id,
            models.Sessao.data_hora_inicio < fim,
            models.Sessao.data_hora_fim > inicio,
        )
    )
    if ignorar_sessao_id is not None:
        stmt = stmt.where(models.Sessao.id != ignorar_sessao_id)
    return list(db.scalars(stmt).all())


def criar_sessao(db: Session, dados: schemas.SessaoCreate) -> models.Sessao:
    conflitos = _buscar_conflitos(
        db, dados.espaco_id, dados.data_hora_inicio, dados.data_hora_fim
    )
    if conflitos:
        raise ConflitoDeHorarioError(conflitos)

    sessao = models.Sessao(**dados.model_dump())
    db.add(sessao)
    db.commit()
    db.refresh(sessao)
    return sessao


def atualizar_sessao(
    db: Session, sessao: models.Sessao, dados: schemas.SessaoUpdate
) -> models.Sessao:
    atualizacoes = dados.model_dump(exclude_unset=True)

    novo_espaco_id = atualizacoes.get("espaco_id", sessao.espaco_id)
    novo_inicio = atualizacoes.get("data_hora_inicio", sessao.data_hora_inicio)
    novo_fim = atualizacoes.get("data_hora_fim", sessao.data_hora_fim)

    conflitos = _buscar_conflitos(
        db, novo_espaco_id, novo_inicio, novo_fim, ignorar_sessao_id=sessao.id
    )
    if conflitos:
        raise ConflitoDeHorarioError(conflitos)

    for campo, valor in atualizacoes.items():
        setattr(sessao, campo, valor)
    db.commit()
    db.refresh(sessao)
    return sessao


def listar_sessoes(
    db: Session, evento_id: int | None = None, espaco_id: int | None = None
) -> list[models.Sessao]:
    stmt = select(models.Sessao)
    if evento_id is not None:
        stmt = stmt.where(models.Sessao.evento_id == evento_id)
    if espaco_id is not None:
        stmt = stmt.where(models.Sessao.espaco_id == espaco_id)
    return list(db.scalars(stmt).all())


def obter_sessao(db: Session, sessao_id: int) -> models.Sessao | None:
    return db.get(models.Sessao, sessao_id)


def remover_sessao(db: Session, sessao: models.Sessao) -> None:
    db.delete(sessao)
    db.commit()
