"""Utilitário de data/hora.

As colunas de data/hora do banco são "ingênuas" (sem fuso) e guardam o horário
local informado pelo organizador. Por isso "agora" é calculado no fuso do
evento (padrão: America/Sao_Paulo) e devolvido sem tzinfo, para poder ser
comparado diretamente com `Sessao.data_hora_inicio`.
"""

import os
from datetime import datetime
from zoneinfo import ZoneInfo

FUSO_HORARIO = ZoneInfo(os.getenv("FUSO_HORARIO", "America/Sao_Paulo"))


def agora() -> datetime:
    return datetime.now(FUSO_HORARIO).replace(tzinfo=None)
