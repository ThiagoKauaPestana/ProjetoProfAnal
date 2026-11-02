"""
Regras de inscrição: capacidade, duplicidade, fila de espera e promoção.

Observação importante: a Session do projeto usa autoflush=False. Por isso,
sempre que uma contagem depende de alterações ainda não gravadas, o código
chama db.flush() antes de consultar.

Controle de concorrência no PostgreSQL: um advisory lock transacional
serializa inscrições, cancelamentos e promoções entre sessões; a sessão
também é travada com SELECT ... FOR UPDATE. Os testes SQLite verificam as
regras funcionais, mas não reproduzem os locks do PostgreSQL.
"""

from sqlalchemy import and_, case, func, or_, select, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app import models
from app.models import STATUS_CANCELADA, STATUS_CONFIRMADA, STATUS_LISTA_ESPERA
from app.tempo import agora

# Inscrições novas não são aceitas em eventos com esses status.
STATUS_EVENTO_SEM_INSCRICAO = {"cancelado", "encerrado"}


class InscricaoError(Exception):
    """Base das regras de negócio de inscrição."""

    def __init__(self, mensagem: str):
        self.mensagem = mensagem
        super().__init__(mensagem)


class SessaoNaoEncontradaError(InscricaoError):
    pass


class InscricaoDuplicadaError(InscricaoError):
    pass


class InscricaoNaoPermitidaError(InscricaoError):
    pass


class InscricaoJaCanceladaError(InscricaoError):
    pass


def _serializar_inscricoes(db: Session) -> None:
    """Serializa inscrições e promoções entre sessões no PostgreSQL até o commit.

    O lock transacional compartilhado evita que requisições simultâneas validem
    a mesma agenda antes de uma delas gravar a inscrição.
    """
    if db.get_bind().dialect.name == "postgresql":
        db.execute(text("SELECT pg_advisory_xact_lock(15032026)"))


def conflito_na_agenda(
    db: Session, usuario_id: int, sessao: models.Sessao
) -> models.Sessao | None:
    """Inscrições confirmadas e em espera reservam o intervalo [início, fim)."""
    return db.scalar(
        select(models.Sessao)
        .join(models.Inscricao, models.Inscricao.sessao_id == models.Sessao.id)
        .where(
            models.Inscricao.usuario_id == usuario_id,
            models.Inscricao.status.in_([STATUS_CONFIRMADA, STATUS_LISTA_ESPERA]),
            models.Sessao.id != sessao.id,
            models.Sessao.data_hora_inicio < sessao.data_hora_fim,
            models.Sessao.data_hora_fim > sessao.data_hora_inicio,
        )
        .order_by(models.Sessao.data_hora_inicio, models.Sessao.id)
        .limit(1)
    )


# --------------------------------------------------------------------------
# Consultas auxiliares
# --------------------------------------------------------------------------
def capacidade_total(sessao: models.Sessao) -> int:
    """Vagas da sessão: capacidade_prevista, ou a capacidade do espaço."""
    if sessao.capacidade_prevista is not None:
        return sessao.capacidade_prevista
    return sessao.espaco.capacidade


def contar(db: Session, sessao_id: int, status: str) -> int:
    return db.scalar(
        select(func.count(models.Inscricao.id)).where(
            models.Inscricao.sessao_id == sessao_id,
            models.Inscricao.status == status,
        )
    )


def contar_por_status(
    db: Session, sessao_ids: list[int]
) -> dict[int, dict[str, int]]:
    """Retorna {sessao_id: {"confirmada": n, "lista_espera": n}} (sem canceladas)."""
    resultado: dict[int, dict[str, int]] = {
        sid: {STATUS_CONFIRMADA: 0, STATUS_LISTA_ESPERA: 0} for sid in sessao_ids
    }
    if not sessao_ids:
        return resultado
    linhas = db.execute(
        select(
            models.Inscricao.sessao_id,
            models.Inscricao.status,
            func.count(models.Inscricao.id),
        )
        .where(
            models.Inscricao.sessao_id.in_(sessao_ids),
            models.Inscricao.status != STATUS_CANCELADA,
        )
        .group_by(models.Inscricao.sessao_id, models.Inscricao.status)
    ).all()
    for sessao_id, status, total in linhas:
        resultado[sessao_id][status] = total
    return resultado


def posicao_na_fila(db: Session, inscricao: models.Inscricao) -> int | None:
    """Posição na lista de espera (1 = próximo a ser promovido)."""
    if inscricao.status != STATUS_LISTA_ESPERA:
        return None
    anteriores = db.scalar(
        select(func.count(models.Inscricao.id)).where(
            models.Inscricao.sessao_id == inscricao.sessao_id,
            models.Inscricao.status == STATUS_LISTA_ESPERA,
            or_(
                models.Inscricao.entrou_em < inscricao.entrou_em,
                and_(
                    models.Inscricao.entrou_em == inscricao.entrou_em,
                    models.Inscricao.id < inscricao.id,
                ),
            ),
        )
    )
    return anteriores + 1


def _travar_sessao(db: Session, sessao_id: int) -> models.Sessao | None:
    return db.scalar(
        select(models.Sessao)
        .where(models.Sessao.id == sessao_id)
        .with_for_update()
        .execution_options(populate_existing=True)
    )


def obter_inscricao(db: Session, inscricao_id: int) -> models.Inscricao | None:
    return db.get(models.Inscricao, inscricao_id)


def obter_inscricao_ativa(
    db: Session, usuario_id: int, sessao_id: int
) -> models.Inscricao | None:
    """Inscrição do usuário na sessão que não esteja cancelada."""
    return db.scalar(
        select(models.Inscricao).where(
            models.Inscricao.usuario_id == usuario_id,
            models.Inscricao.sessao_id == sessao_id,
            models.Inscricao.status != STATUS_CANCELADA,
        )
    )


# --------------------------------------------------------------------------
# Fila de espera
# --------------------------------------------------------------------------
def promover_fila(db: Session, sessao: models.Sessao) -> list[models.Inscricao]:
    """
    Promove, na ordem de chegada, quem está na lista de espera enquanto
    houver vagas livres. Não faz commit (quem chama decide).
    """
    _serializar_inscricoes(db)
    db.flush()
    db.refresh(sessao)
    if sessao.data_hora_inicio <= agora() or sessao.evento.status in STATUS_EVENTO_SEM_INSCRICAO:
        return []
    vagas_livres = capacidade_total(sessao) - contar(db, sessao.id, STATUS_CONFIRMADA)
    if vagas_livres <= 0:
        return []

    fila = list(
        db.scalars(
            select(models.Inscricao)
            .where(
                models.Inscricao.sessao_id == sessao.id,
                models.Inscricao.status == STATUS_LISTA_ESPERA,
            )
            .order_by(models.Inscricao.entrou_em, models.Inscricao.id)
        ).all()
    )
    momento = agora()
    promovidas = []
    for inscricao in fila:
        if conflito_na_agenda(db, inscricao.usuario_id, sessao):
            continue
        inscricao.status = STATUS_CONFIRMADA
        inscricao.promovida_em = momento
        promovidas.append(inscricao)
        db.flush()
        if len(promovidas) == vagas_livres:
            break
    db.flush()
    return promovidas


# --------------------------------------------------------------------------
# Inscrever / cancelar
# --------------------------------------------------------------------------
def inscrever(db: Session, usuario: models.Usuario, sessao_id: int) -> models.Inscricao:
    _serializar_inscricoes(db)
    sessao = _travar_sessao(db, sessao_id)
    if sessao is None:
        raise SessaoNaoEncontradaError("Sessão não encontrada")

    if sessao.evento.status in STATUS_EVENTO_SEM_INSCRICAO:
        raise InscricaoNaoPermitidaError(
            f"Inscrições indisponíveis: o evento está {sessao.evento.status}"
        )
    if sessao.data_hora_inicio <= agora():
        raise InscricaoNaoPermitidaError(
            "Inscrições encerradas: a sessão já começou ou já terminou"
        )

    existente = db.scalar(
        select(models.Inscricao).where(
            models.Inscricao.usuario_id == usuario.id,
            models.Inscricao.sessao_id == sessao.id,
        )
    )
    if existente is not None and existente.status != STATUS_CANCELADA:
        rotulo = (
            "confirmado" if existente.status == STATUS_CONFIRMADA else "na lista de espera"
        )
        raise InscricaoDuplicadaError(f"Você já está {rotulo} nesta sessão")

    conflito = conflito_na_agenda(db, usuario.id, sessao)
    if conflito:
        raise InscricaoNaoPermitidaError(
            f'Conflito de horário: você já possui inscrição ativa na sessão '
            f'"{conflito.titulo}" ({conflito.data_hora_inicio:%d/%m/%Y %H:%M}'
            f' às {conflito.data_hora_fim:%H:%M}). Cancele a inscrição anterior para trocar de atividade.'
        )

    # Garante que vagas liberadas por mudança de capacidade já foram ocupadas
    # pela fila antes de decidir o status de quem está chegando.
    promover_fila(db, sessao)

    confirmadas = contar(db, sessao.id, STATUS_CONFIRMADA)
    tem_vaga = confirmadas < capacidade_total(sessao)
    status = STATUS_CONFIRMADA if tem_vaga else STATUS_LISTA_ESPERA

    if existente is not None:  # reativa a inscrição cancelada
        inscricao = existente
        inscricao.status = status
        inscricao.entrou_em = agora()
        inscricao.promovida_em = None
        inscricao.cancelada_em = None
    else:
        inscricao = models.Inscricao(
            usuario_id=usuario.id,
            sessao_id=sessao.id,
            status=status,
            entrou_em=agora(),
        )
        db.add(inscricao)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise InscricaoDuplicadaError("Você já está inscrito nesta sessão")
    db.refresh(inscricao)
    return inscricao


def cancelar(
    db: Session, inscricao: models.Inscricao, *, ignorar_inicio: bool = False
) -> tuple[models.Inscricao, list[models.Inscricao]]:
    """
    Cancela a inscrição e promove a fila. Retorna (inscricao, promovidas).
    `ignorar_inicio=True` permite cancelar depois que a sessão começou
    (usado pelo organizador).
    """
    _serializar_inscricoes(db)
    sessao = _travar_sessao(db, inscricao.sessao_id)
    db.refresh(inscricao)  # estado atual, depois do lock

    if inscricao.status == STATUS_CANCELADA:
        raise InscricaoJaCanceladaError("Esta inscrição já foi cancelada")
    if not ignorar_inicio and sessao.data_hora_inicio <= agora():
        raise InscricaoNaoPermitidaError(
            "Não é possível cancelar: a sessão já começou ou já terminou"
        )

    inscricao.status = STATUS_CANCELADA
    inscricao.cancelada_em = agora()
    promovidas = promover_fila(db, sessao)
    db.commit()
    db.refresh(inscricao)
    return inscricao, promovidas


# --------------------------------------------------------------------------
# Listagens
# --------------------------------------------------------------------------
def _filtrar_status(stmt, status: str | None, incluir_canceladas: bool):
    if status is not None:
        return stmt.where(models.Inscricao.status == status)
    if not incluir_canceladas:
        return stmt.where(models.Inscricao.status != STATUS_CANCELADA)
    return stmt


_ORDEM_STATUS = case(
    (models.Inscricao.status == STATUS_CONFIRMADA, 0),
    (models.Inscricao.status == STATUS_LISTA_ESPERA, 1),
    else_=2,
)


def listar_minhas(
    db: Session,
    usuario_id: int,
    status: str | None = None,
    incluir_canceladas: bool = False,
    evento_id: int | None = None,
    apenas_futuras: bool = False,
) -> list[models.Inscricao]:
    stmt = (
        select(models.Inscricao)
        .join(models.Sessao, models.Inscricao.sessao_id == models.Sessao.id)
        .where(models.Inscricao.usuario_id == usuario_id)
    )
    stmt = _filtrar_status(stmt, status, incluir_canceladas)
    if evento_id is not None:
        stmt = stmt.where(models.Sessao.evento_id == evento_id)
    if apenas_futuras:  # sessões que ainda não terminaram
        stmt = stmt.where(models.Sessao.data_hora_fim > agora())
    stmt = stmt.order_by(models.Sessao.data_hora_inicio, models.Inscricao.id)
    return list(db.scalars(stmt).all())


def listar_por_sessao(
    db: Session,
    sessao_id: int,
    status: str | None = None,
    incluir_canceladas: bool = False,
) -> list[models.Inscricao]:
    stmt = select(models.Inscricao).where(models.Inscricao.sessao_id == sessao_id)
    stmt = _filtrar_status(stmt, status, incluir_canceladas)
    stmt = stmt.order_by(_ORDEM_STATUS, models.Inscricao.entrou_em, models.Inscricao.id)
    return list(db.scalars(stmt).all())


def listar_por_evento(
    db: Session,
    evento_id: int,
    status: str | None = None,
    incluir_canceladas: bool = False,
    sessao_id: int | None = None,
) -> list[models.Inscricao]:
    stmt = (
        select(models.Inscricao)
        .join(models.Sessao, models.Inscricao.sessao_id == models.Sessao.id)
        .where(models.Sessao.evento_id == evento_id)
    )
    if sessao_id is not None:
        stmt = stmt.where(models.Inscricao.sessao_id == sessao_id)
    stmt = _filtrar_status(stmt, status, incluir_canceladas)
    stmt = stmt.order_by(
        models.Sessao.data_hora_inicio,
        models.Sessao.id,
        _ORDEM_STATUS,
        models.Inscricao.entrou_em,
        models.Inscricao.id,
    )
    return list(db.scalars(stmt).all())
