from datetime import datetime, date
from sqlalchemy import String, Integer, Boolean, Text, Date, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


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
