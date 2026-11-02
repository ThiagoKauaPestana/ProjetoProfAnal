from datetime import date, datetime, time, timedelta

from sqlalchemy import select, and_, func, or_
from sqlalchemy.orm import Session

from app import crud_inscricoes, models, schemas


def _padrao_busca(termo: str) -> str:
    """Padrão LIKE que trata %, _ e \\ digitados pelo usuário como texto comum."""
    escapado = termo.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
    return f"%{escapado}%"


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

    # Se a capacidade do espaço aumentou, sessões que usam essa capacidade
    # podem ter ganhado vagas: promove a lista de espera.
    for sessao in espaco.sessoes:
        crud_inscricoes.promover_fila(db, sessao)
    db.commit()
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


def listar_eventos(
    db: Session,
    status: str | None = None,
    busca: str | None = None,
    data_de: date | None = None,
    data_ate: date | None = None,
) -> list[models.Evento]:
    """
    Catálogo de eventos. `data_de`/`data_ate` retornam os eventos que
    acontecem (total ou parcialmente) dentro do intervalo informado.
    """
    stmt = select(models.Evento)
    if status:
        stmt = stmt.where(models.Evento.status == status)
    if busca and busca.strip():
        padrao = _padrao_busca(busca.strip())
        stmt = stmt.where(
            or_(
                models.Evento.nome.ilike(padrao, escape="\\"),
                models.Evento.descricao.ilike(padrao, escape="\\"),
            )
        )
    if data_de is not None:
        stmt = stmt.where(models.Evento.data_fim >= data_de)
    if data_ate is not None:
        stmt = stmt.where(models.Evento.data_inicio <= data_ate)
    stmt = stmt.order_by(models.Evento.data_inicio, models.Evento.id)
    return list(db.scalars(stmt).all())


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

    # Se a capacidade aumentou (ou o espaço mudou para um maior), quem estava
    # na lista de espera é promovido automaticamente. Se a capacidade diminuiu,
    # os já confirmados são mantidos e apenas novas promoções deixam de ocorrer.
    crud_inscricoes.promover_fila(db, sessao)
    db.commit()
    db.refresh(sessao)
    return sessao


def _inicio_do_dia(dia: date) -> datetime:
    return datetime.combine(dia, time.min)


def listar_sessoes(
    db: Session,
    evento_id: int | None = None,
    espaco_id: int | None = None,
    tipo: str | None = None,
    busca: str | None = None,
    data: date | None = None,
    data_de: date | None = None,
    data_ate: date | None = None,
    apenas_com_vagas: bool = False,
) -> list[models.Sessao]:
    """
    Catálogo de sessões. `data` filtra um dia específico; `data_de`/`data_ate`
    filtram sessões que COMEÇAM dentro do intervalo (inclusive).
    """
    stmt = select(models.Sessao).join(
        models.Espaco, models.Sessao.espaco_id == models.Espaco.id
    )
    if evento_id is not None:
        stmt = stmt.where(models.Sessao.evento_id == evento_id)
    if espaco_id is not None:
        stmt = stmt.where(models.Sessao.espaco_id == espaco_id)
    if tipo and tipo.strip():
        stmt = stmt.where(func.lower(models.Sessao.tipo) == tipo.strip().lower())
    if busca and busca.strip():
        padrao = _padrao_busca(busca.strip())
        stmt = stmt.where(
            or_(
                models.Sessao.titulo.ilike(padrao, escape="\\"),
                models.Sessao.descricao.ilike(padrao, escape="\\"),
                models.Sessao.responsavel.ilike(padrao, escape="\\"),
            )
        )
    if data is not None:
        data_de = data_ate = data
    if data_de is not None:
        stmt = stmt.where(models.Sessao.data_hora_inicio >= _inicio_do_dia(data_de))
    if data_ate is not None:
        stmt = stmt.where(
            models.Sessao.data_hora_inicio < _inicio_do_dia(data_ate + timedelta(days=1))
        )
    if apenas_com_vagas:
        confirmadas = (
            select(func.count(models.Inscricao.id))
            .where(
                models.Inscricao.sessao_id == models.Sessao.id,
                models.Inscricao.status == models.STATUS_CONFIRMADA,
            )
            .correlate(models.Sessao)
            .scalar_subquery()
        )
        capacidade = func.coalesce(
            models.Sessao.capacidade_prevista, models.Espaco.capacidade
        )
        stmt = stmt.where(capacidade > confirmadas)

    stmt = stmt.order_by(models.Sessao.data_hora_inicio, models.Sessao.id)
    return list(db.scalars(stmt).all())


def obter_sessao(db: Session, sessao_id: int) -> models.Sessao | None:
    return db.get(models.Sessao, sessao_id)


def remover_sessao(db: Session, sessao: models.Sessao) -> None:
    db.delete(sessao)
    db.commit()
