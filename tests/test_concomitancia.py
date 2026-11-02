"""Conflitos na agenda do participante, inclusive na promoção de filas."""

from datetime import datetime, timedelta

import pytest

from test_sprint3 import (
    cancelar, criar_espaco, criar_evento, criar_sessao, inscrever, minhas,
)


def duas_sessoes(client, *, deslocamento=30, capacidade=2):
    evento = criar_evento(client)
    sala_a = criar_espaco(client, nome="Sala A")
    sala_b = criar_espaco(client, nome="Sala B")
    a = criar_sessao(client, evento, sala_a, dias=3, hora=10, capacidade=capacidade)
    b = criar_sessao(client, evento, sala_b, dias=3, hora=10, capacidade=capacidade)
    inicio = datetime.fromisoformat(a["data_hora_inicio"]) + timedelta(minutes=deslocamento)
    resposta = client.put(f"/sessoes/{b['id']}", json={
        "data_hora_inicio": inicio.isoformat(),
        "data_hora_fim": (inicio + timedelta(hours=1)).isoformat(),
    })
    assert resposta.status_code == 200, resposta.text
    return a, resposta.json()


@pytest.mark.parametrize("deslocamento", [0, 30, -30])
def test_bloqueia_inscricao_em_sessoes_sobrepostas(
    client, anonimo, criar_participante, deslocamento
):
    a, b = duas_sessoes(client, deslocamento=deslocamento)
    aluno, _ = criar_participante()
    assert inscrever(anonimo, aluno, a).status_code == 201
    resposta = inscrever(anonimo, aluno, b)
    assert resposta.status_code == 409
    assert "Conflito de horário" in resposta.json()["detail"]
    assert len(minhas(anonimo, aluno)) == 1


@pytest.mark.parametrize("deslocamento", [60, -60])
def test_permite_sessoes_consecutivas(client, anonimo, criar_participante, deslocamento):
    a, b = duas_sessoes(client, deslocamento=deslocamento)
    aluno, _ = criar_participante()
    assert inscrever(anonimo, aluno, a).status_code == 201
    assert inscrever(anonimo, aluno, b).status_code == 201


def test_cancelar_libera_agenda_para_outra_sessao(client, anonimo, criar_participante):
    a, b = duas_sessoes(client)
    aluno, _ = criar_participante()
    inscrever(anonimo, aluno, a)
    assert cancelar(anonimo, aluno, a).status_code == 200
    assert inscrever(anonimo, aluno, b).status_code == 201
    assert inscrever(anonimo, aluno, a).status_code == 409


def test_inscricao_em_espera_tambem_reserva_agenda(client, anonimo, criar_participante):
    a, b = duas_sessoes(client, capacidade=1)
    primeiro, _ = criar_participante()
    aluno, _ = criar_participante()
    inscrever(anonimo, primeiro, a)
    assert inscrever(anonimo, aluno, a).json()["status"] == "lista_espera"
    assert inscrever(anonimo, aluno, b).status_code == 409


def test_promocao_pula_conflito_criado_por_mudanca_de_horario(
    client, anonimo, criar_participante
):
    a, b = duas_sessoes(client, deslocamento=120, capacidade=1)
    titular, _ = criar_participante()
    primeiro_fila, _ = criar_participante()
    segundo_fila, _ = criar_participante()
    inscrever(anonimo, titular, a)
    inscrever(anonimo, primeiro_fila, a)
    inscrever(anonimo, segundo_fila, a)
    inscrever(anonimo, primeiro_fila, b)
    assert client.put(f"/sessoes/{b['id']}", json={
        "data_hora_inicio": a["data_hora_inicio"],
        "data_hora_fim": a["data_hora_fim"],
    }).status_code == 200
    resposta = cancelar(anonimo, titular, a)
    assert resposta.json()["promovidas_total"] == 1
    status_primeiro = {i["sessao_id"]: i["status"] for i in minhas(anonimo, primeiro_fila)}
    assert status_primeiro[a["id"]] == "lista_espera"
    assert minhas(anonimo, segundo_fila)[0]["status"] == "confirmada"


def test_conflito_entre_eventos_diferentes(client, anonimo, criar_participante):
    a, _ = duas_sessoes(client)
    evento = criar_evento(client, nome="Outro evento")
    sala = criar_espaco(client, nome="Sala C")
    b = criar_sessao(client, evento, sala, dias=3, hora=10)
    aluno, _ = criar_participante()
    inscrever(anonimo, aluno, a)
    assert inscrever(anonimo, aluno, b).status_code == 409
