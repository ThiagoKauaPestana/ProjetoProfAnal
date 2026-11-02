import re
from datetime import datetime, date
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

StatusInscricao = Literal["confirmada", "lista_espera", "cancelada"]


# --------------------------------------------------------------------------
# Espaços
# --------------------------------------------------------------------------
class EspacoBase(BaseModel):
    nome: str
    tipo: str
    capacidade: int
    localizacao: str | None = None
    recursos: str | None = None
    ativo: bool = True

    @field_validator("capacidade")
    @classmethod
    def capacidade_positiva(cls, v: int) -> int:
        if v <= 0:
            raise ValueError("capacidade deve ser maior que zero")
        return v


class EspacoCreate(EspacoBase):
    pass


class EspacoUpdate(BaseModel):
    nome: str | None = None
    tipo: str | None = None
    capacidade: int | None = None
    localizacao: str | None = None
    recursos: str | None = None
    ativo: bool | None = None


class EspacoOut(EspacoBase):
    model_config = ConfigDict(from_attributes=True)
    id: int


# --------------------------------------------------------------------------
# Eventos
# --------------------------------------------------------------------------
class EventoBase(BaseModel):
    nome: str
    descricao: str | None = None
    data_inicio: date
    data_fim: date
    status: str = "planejado"

    @field_validator("data_fim")
    @classmethod
    def fim_apos_inicio(cls, v: date, info):
        inicio = info.data.get("data_inicio")
        if inicio and v < inicio:
            raise ValueError("data_fim não pode ser anterior a data_inicio")
        return v


class EventoCreate(EventoBase):
    pass


class EventoUpdate(BaseModel):
    nome: str | None = None
    descricao: str | None = None
    data_inicio: date | None = None
    data_fim: date | None = None
    status: str | None = None


class EventoOut(EventoBase):
    model_config = ConfigDict(from_attributes=True)
    id: int


# --------------------------------------------------------------------------
# Sessões
# --------------------------------------------------------------------------
class SessaoBase(BaseModel):
    evento_id: int
    espaco_id: int
    titulo: str
    descricao: str | None = None
    tipo: str | None = None
    responsavel: str | None = None
    capacidade_prevista: int | None = None
    data_hora_inicio: datetime
    data_hora_fim: datetime

    @field_validator("capacidade_prevista")
    @classmethod
    def capacidade_prevista_positiva(cls, v: int | None) -> int | None:
        if v is not None and v <= 0:
            raise ValueError("capacidade_prevista deve ser maior que zero")
        return v

    @field_validator("data_hora_fim")
    @classmethod
    def fim_apos_inicio(cls, v: datetime, info):
        inicio = info.data.get("data_hora_inicio")
        if inicio and v <= inicio:
            raise ValueError("data_hora_fim deve ser posterior a data_hora_inicio")
        return v


class SessaoCreate(SessaoBase):
    pass


class SessaoUpdate(BaseModel):
    titulo: str | None = None
    descricao: str | None = None
    tipo: str | None = None
    responsavel: str | None = None
    capacidade_prevista: int | None = None
    espaco_id: int | None = None
    data_hora_inicio: datetime | None = None
    data_hora_fim: datetime | None = None

    @field_validator("capacidade_prevista")
    @classmethod
    def capacidade_prevista_positiva(cls, v: int | None) -> int | None:
        if v is not None and v <= 0:
            raise ValueError("capacidade_prevista deve ser maior que zero")
        return v


class SessaoOut(SessaoBase):
    model_config = ConfigDict(from_attributes=True)
    id: int


class SessaoCatalogoOut(SessaoOut):
    """Sessão como aparece no catálogo: inclui a situação das vagas."""

    evento_nome: str | None = None
    espaco_nome: str | None = None
    capacidade_total: int
    vagas_ocupadas: int
    vagas_disponiveis: int
    lista_espera: int


# --------------------------------------------------------------------------
# Usuários / autenticação
# --------------------------------------------------------------------------
class UsuarioCreate(BaseModel):
    nome: str = Field(min_length=1, max_length=120)
    email: str = Field(max_length=150)
    senha: str = Field(min_length=6, max_length=128)

    @field_validator("nome")
    @classmethod
    def nome_nao_vazio(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("nome não pode ser vazio")
        return v

    @field_validator("email")
    @classmethod
    def email_valido(cls, v: str) -> str:
        v = v.strip().lower()
        if not _EMAIL_RE.match(v):
            raise ValueError("e-mail inválido")
        return v


class LoginIn(BaseModel):
    email: str
    senha: str


class PerfilUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    papel: Literal["organizador", "participante"]


class UsuarioOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    nome: str
    email: str
    papel: str
    ativo: bool


class UsuarioResumoOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    nome: str
    email: str


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    usuario: UsuarioOut


# --------------------------------------------------------------------------
# Inscrições
# --------------------------------------------------------------------------
class InscricaoOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    usuario_id: int
    sessao_id: int
    status: StatusInscricao
    entrou_em: datetime
    promovida_em: datetime | None = None
    cancelada_em: datetime | None = None
    # Só preenchido quando status == "lista_espera" (1 = próximo a ser promovido)
    posicao_fila: int | None = None


class SessaoResumoOut(BaseModel):
    id: int
    titulo: str
    tipo: str | None = None
    evento_id: int
    evento_nome: str
    espaco_id: int
    espaco_nome: str
    data_hora_inicio: datetime
    data_hora_fim: datetime


class InscricaoMinhaOut(InscricaoOut):
    """Item da área "Minhas inscrições"."""

    sessao: SessaoResumoOut


class InscricaoGestaoOut(InscricaoOut):
    """Item das listagens do organizador."""

    usuario: UsuarioResumoOut
    sessao: SessaoResumoOut


class CancelamentoOut(BaseModel):
    inscricao: InscricaoOut
    # Quantas pessoas da lista de espera foram promovidas por causa do cancelamento
    promovidas_total: int
