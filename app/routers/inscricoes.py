from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud, crud_inscricoes, models, schemas
from app.database import get_db
from app.deps import exigir_organizador, exigir_participante, get_usuario_atual

router = APIRouter(tags=["Inscrições"])


# --------------------------------------------------------------------------
# Conversões para os schemas de resposta
# --------------------------------------------------------------------------
def _inscricao_out(db: Session, inscricao: models.Inscricao) -> schemas.InscricaoOut:
    saida = schemas.InscricaoOut.model_validate(inscricao)
    saida.posicao_fila = crud_inscricoes.posicao_na_fila(db, inscricao)
    return saida


def _resumo_sessao(sessao: models.Sessao) -> schemas.SessaoResumoOut:
    return schemas.SessaoResumoOut(
        id=sessao.id,
        titulo=sessao.titulo,
        tipo=sessao.tipo,
        evento_id=sessao.evento_id,
        evento_nome=sessao.evento.nome,
        espaco_id=sessao.espaco_id,
        espaco_nome=sessao.espaco.nome,
        data_hora_inicio=sessao.data_hora_inicio,
        data_hora_fim=sessao.data_hora_fim,
    )


def _inscricao_minha_out(
    db: Session, inscricao: models.Inscricao
) -> schemas.InscricaoMinhaOut:
    base = _inscricao_out(db, inscricao).model_dump()
    return schemas.InscricaoMinhaOut(**base, sessao=_resumo_sessao(inscricao.sessao))


def _inscricao_gestao_out(
    db: Session, inscricao: models.Inscricao
) -> schemas.InscricaoGestaoOut:
    base = _inscricao_out(db, inscricao).model_dump()
    return schemas.InscricaoGestaoOut(
        **base,
        usuario=schemas.UsuarioResumoOut.model_validate(inscricao.usuario),
        sessao=_resumo_sessao(inscricao.sessao),
    )


def _erro_http(exc: crud_inscricoes.InscricaoError) -> HTTPException:
    if isinstance(exc, crud_inscricoes.SessaoNaoEncontradaError):
        return HTTPException(status_code=404, detail=exc.mensagem)
    # duplicada, fora do prazo, já cancelada...
    return HTTPException(status_code=409, detail=exc.mensagem)


def _cancelamento_out(
    db: Session, inscricao: models.Inscricao, promovidas: list[models.Inscricao]
) -> schemas.CancelamentoOut:
    return schemas.CancelamentoOut(
        inscricao=_inscricao_out(db, inscricao), promovidas_total=len(promovidas)
    )


# --------------------------------------------------------------------------
# Participante: inscrever-se e cancelar por sessão
# --------------------------------------------------------------------------
@router.post(
    "/sessoes/{sessao_id}/inscricao",
    response_model=schemas.InscricaoOut,
    status_code=201,
)
def inscrever_na_sessao(
    sessao_id: int,
    usuario: models.Usuario = Depends(exigir_participante),
    db: Session = Depends(get_db),
):
    """
    Inscreve o participante logado. Se houver vaga, o status é `confirmada`;
    se a sessão estiver lotada, entra na fila (`lista_espera`) e a resposta
    traz a `posicao_fila`. Inscrição duplicada retorna 409.
    """
    try:
        inscricao = crud_inscricoes.inscrever(db, usuario, sessao_id)
    except crud_inscricoes.InscricaoError as exc:
        raise _erro_http(exc)
    return _inscricao_out(db, inscricao)


@router.delete(
    "/sessoes/{sessao_id}/inscricao", response_model=schemas.CancelamentoOut
)
def cancelar_inscricao_na_sessao(
    sessao_id: int,
    usuario: models.Usuario = Depends(exigir_participante),
    db: Session = Depends(get_db),
):
    """Cancela a inscrição do participante logado nesta sessão (confirmada ou
    na fila). Se liberar vaga, o primeiro da fila é promovido automaticamente."""
    inscricao = crud_inscricoes.obter_inscricao_ativa(db, usuario.id, sessao_id)
    if inscricao is None:
        raise HTTPException(
            status_code=404, detail="Você não possui inscrição ativa nesta sessão"
        )
    try:
        inscricao, promovidas = crud_inscricoes.cancelar(db, inscricao)
    except crud_inscricoes.InscricaoError as exc:
        raise _erro_http(exc)
    return _cancelamento_out(db, inscricao, promovidas)


# --------------------------------------------------------------------------
# Participante: "Minhas inscrições"
# --------------------------------------------------------------------------
@router.get("/inscricoes/minhas", response_model=list[schemas.InscricaoMinhaOut])
def minhas_inscricoes(
    status: schemas.StatusInscricao | None = None,
    incluir_canceladas: bool = False,
    evento_id: int | None = None,
    apenas_futuras: bool = False,
    usuario: models.Usuario = Depends(get_usuario_atual),
    db: Session = Depends(get_db),
):
    """
    Inscrições do usuário logado, ordenadas pelo horário da sessão.
    Por padrão mostra confirmadas e em lista de espera; use `status` para
    filtrar um status específico ou `incluir_canceladas=true` para o histórico.
    """
    inscricoes = crud_inscricoes.listar_minhas(
        db,
        usuario.id,
        status=status,
        incluir_canceladas=incluir_canceladas,
        evento_id=evento_id,
        apenas_futuras=apenas_futuras,
    )
    return [_inscricao_minha_out(db, i) for i in inscricoes]


# --------------------------------------------------------------------------
# Cancelamento por id (dono da inscrição ou organizador)
# --------------------------------------------------------------------------
@router.delete("/inscricoes/{inscricao_id}", response_model=schemas.CancelamentoOut)
def cancelar_inscricao(
    inscricao_id: int,
    usuario: models.Usuario = Depends(get_usuario_atual),
    db: Session = Depends(get_db),
):
    """O participante cancela a própria inscrição; o organizador cancela
    qualquer uma (inclusive depois do início da sessão)."""
    inscricao = crud_inscricoes.obter_inscricao(db, inscricao_id)
    if inscricao is None:
        raise HTTPException(status_code=404, detail="Inscrição não encontrada")

    organizador = usuario.papel == models.PAPEL_ORGANIZADOR
    if not organizador and inscricao.usuario_id != usuario.id:
        raise HTTPException(
            status_code=403, detail="Você só pode cancelar as suas próprias inscrições"
        )
    try:
        inscricao, promovidas = crud_inscricoes.cancelar(
            db, inscricao, ignorar_inicio=organizador
        )
    except crud_inscricoes.InscricaoError as exc:
        raise _erro_http(exc)
    return _cancelamento_out(db, inscricao, promovidas)


# --------------------------------------------------------------------------
# Organizador: gerenciamento por sessão e por evento
# --------------------------------------------------------------------------
@router.get(
    "/sessoes/{sessao_id}/inscricoes",
    response_model=list[schemas.InscricaoGestaoOut],
    dependencies=[Depends(exigir_organizador)],
)
def listar_inscricoes_da_sessao(
    sessao_id: int,
    status: schemas.StatusInscricao | None = None,
    incluir_canceladas: bool = False,
    db: Session = Depends(get_db),
):
    """Inscritos da sessão: confirmados primeiro, depois a fila em ordem de chegada."""
    if not crud.obter_sessao(db, sessao_id):
        raise HTTPException(status_code=404, detail="Sessão não encontrada")
    inscricoes = crud_inscricoes.listar_por_sessao(
        db, sessao_id, status=status, incluir_canceladas=incluir_canceladas
    )
    return [_inscricao_gestao_out(db, i) for i in inscricoes]


@router.get(
    "/eventos/{evento_id}/inscricoes",
    response_model=list[schemas.InscricaoGestaoOut],
    dependencies=[Depends(exigir_organizador)],
)
def listar_inscricoes_do_evento(
    evento_id: int,
    status: schemas.StatusInscricao | None = None,
    incluir_canceladas: bool = False,
    sessao_id: int | None = None,
    db: Session = Depends(get_db),
):
    """Inscrições de todas as sessões do evento (filtráveis por sessão e status)."""
    if not crud.obter_evento(db, evento_id):
        raise HTTPException(status_code=404, detail="Evento não encontrado")
    inscricoes = crud_inscricoes.listar_por_evento(
        db,
        evento_id,
        status=status,
        incluir_canceladas=incluir_canceladas,
        sessao_id=sessao_id,
    )
    return [_inscricao_gestao_out(db, i) for i in inscricoes]
