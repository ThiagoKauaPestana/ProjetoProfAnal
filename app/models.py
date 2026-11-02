from datetime import datetime, date
from sqlalchemy import (
    String,
    Integer,
    Boolean,
    Text,
    Date,
    DateTime,
    ForeignKey,
    Index,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.tempo import agora

# Papéis de usuário
PAPEL_ORGANIZADOR = "organizador"
PAPEL_PARTICIPANTE = "participante"

# Status de inscrição
STATUS_CONFIRMADA = "confirmada"
STATUS_LISTA_ESPERA = "lista_espera"
STATUS_CANCELADA = "cancelada"


class Espaco(Base):
    __tablename__ = "espacos"

    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(String(120), nullable=False)
    tipo: Mapped[str] = mapped_column(String(50), nullable=False)
    capacidade: Mapped[int] = mapped_column(Integer, nullable=False)
    localizacao: Mapped[str | None] = mapped_column(String(150), nullable=True)
    recursos: Mapped[str | None] = mapped_column(Text, nullable=True)
    ativo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    criado_em: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    sessoes: Mapped[list["Sessao"]] = relationship(back_populates="espaco")


class Evento(Base):
    __tablename__ = "eventos"

    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(String(150), nullable=False)
    descricao: Mapped[str | None] = mapped_column(Text, nullable=True)
    data_inicio: Mapped[date] = mapped_column(Date, nullable=False)
    data_fim: Mapped[date] = mapped_column(Date, nullable=False)
    status: Mapped[str] = mapped_column(String(30), default="planejado", nullable=False)
    criado_em: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    sessoes: Mapped[list["Sessao"]] = relationship(
        back_populates="evento", cascade="all, delete-orphan"
    )


class Sessao(Base):
    __tablename__ = "sessoes"

    id: Mapped[int] = mapped_column(primary_key=True)
    evento_id: Mapped[int] = mapped_column(ForeignKey("eventos.id", ondelete="CASCADE"))
    espaco_id: Mapped[int] = mapped_column(ForeignKey("espacos.id", ondelete="RESTRICT"))
    titulo: Mapped[str] = mapped_column(String(150), nullable=False)
    descricao: Mapped[str | None] = mapped_column(Text, nullable=True)
    tipo: Mapped[str | None] = mapped_column(String(50), nullable=True)
    responsavel: Mapped[str | None] = mapped_column(String(120), nullable=True)
    capacidade_prevista: Mapped[int | None] = mapped_column(Integer, nullable=True)
    data_hora_inicio: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    data_hora_fim: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    criado_em: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    evento: Mapped["Evento"] = relationship(back_populates="sessoes")
    espaco: Mapped["Espaco"] = relationship(back_populates="sessoes")
    inscricoes: Mapped[list["Inscricao"]] = relationship(
        back_populates="sessao", cascade="all, delete-orphan"
    )


class Usuario(Base):
    __tablename__ = "usuarios"

    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(String(120), nullable=False)
    email: Mapped[str] = mapped_column(String(150), nullable=False, unique=True)
    senha_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    papel: Mapped[str] = mapped_column(
        String(20), default=PAPEL_PARTICIPANTE, nullable=False
    )
    ativo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    criado_em: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    inscricoes: Mapped[list["Inscricao"]] = relationship(
        back_populates="usuario", cascade="all, delete-orphan"
    )


class Inscricao(Base):
    """
    Inscrição de um usuário em uma sessão.

    Existe no máximo UMA linha por (usuario, sessao) — garantido pela
    constraint única. Cancelar não apaga a linha: muda o status para
    "cancelada". Se o usuário se inscrever de novo, a mesma linha é
    reativada (com `entrou_em` renovado, ou seja, ele volta ao fim da fila).
    """

    __tablename__ = "inscricoes"
    __table_args__ = (
        UniqueConstraint("usuario_id", "sessao_id", name="uq_inscricao_usuario_sessao"),
        Index("idx_inscricoes_sessao_status", "sessao_id", "status", "entrou_em"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    usuario_id: Mapped[int] = mapped_column(
        ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False
    )
    sessao_id: Mapped[int] = mapped_column(
        ForeignKey("sessoes.id", ondelete="CASCADE"), nullable=False
    )
    status: Mapped[str] = mapped_column(
        String(20), default=STATUS_CONFIRMADA, nullable=False
    )
    # Momento em que entrou (ou reentrou) na sessão; define a ordem da fila.
    entrou_em: Mapped[datetime] = mapped_column(DateTime, default=agora, nullable=False)
    promovida_em: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    cancelada_em: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    criado_em: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    usuario: Mapped["Usuario"] = relationship(back_populates="inscricoes")
    sessao: Mapped["Sessao"] = relationship(back_populates="inscricoes")
