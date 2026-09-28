from datetime import datetime, date
from pydantic import BaseModel, ConfigDict, field_validator


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


class SessaoOut(SessaoBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
