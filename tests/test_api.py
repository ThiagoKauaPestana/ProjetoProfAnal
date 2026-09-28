def criar_espaco(client, nome="Auditorio Principal"):
    return client.post(
        "/espacos",
        json={
            "nome": nome,
            "tipo": "auditorio",
            "capacidade": 120,
            "localizacao": "Bloco A",
            "recursos": "projetor, som",
        },
    )


def criar_evento(client):
    return client.post(
        "/eventos",
        json={
            "nome": "Semana da FCI",
            "data_inicio": "2026-10-01",
            "data_fim": "2026-10-03",
        },
    )


def test_status_da_api(client):
    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "servico": "auditorio-inteligente-api",
    }


def test_cria_e_lista_espaco(client):
    criado = criar_espaco(client)

    assert criado.status_code == 201
    assert criado.json()["id"] == 1
    assert criado.json()["nome"] == "Auditorio Principal"

    lista = client.get("/espacos")
    assert lista.status_code == 200
    assert len(lista.json()) == 1


def test_rejeita_capacidade_invalida(client):
    response = client.post(
        "/espacos",
        json={"nome": "Sala invalida", "tipo": "sala", "capacidade": 0},
    )

    assert response.status_code == 422


def test_rejeita_evento_com_datas_invertidas(client):
    response = client.post(
        "/eventos",
        json={
            "nome": "Evento invalido",
            "data_inicio": "2026-10-03",
            "data_fim": "2026-10-01",
        },
    )

    assert response.status_code == 422


def test_atualiza_evento(client):
    evento = criar_evento(client).json()

    response = client.put(
        f"/eventos/{evento['id']}",
        json={"nome": "Semana de Tecnologia", "status": "em_andamento"},
    )

    assert response.status_code == 200
    assert response.json()["nome"] == "Semana de Tecnologia"
    assert response.json()["status"] == "em_andamento"
    assert response.json()["data_inicio"] == "2026-10-01"


def test_rejeita_periodo_invalido_ao_atualizar_evento(client):
    evento = criar_evento(client).json()

    response = client.put(
        f"/eventos/{evento['id']}",
        json={"data_inicio": "2026-10-04"},
    )

    assert response.status_code == 422
    assert response.json()["detail"] == (
        "data_fim nao pode ser anterior a data_inicio"
    )


def test_exclui_evento_e_suas_sessoes(client):
    espaco = criar_espaco(client).json()
    evento = criar_evento(client).json()
    sessao = client.post(
        "/sessoes",
        json={
            "evento_id": evento["id"],
            "espaco_id": espaco["id"],
            "titulo": "Sessao do evento",
            "data_hora_inicio": "2026-10-01T09:00:00",
            "data_hora_fim": "2026-10-01T10:00:00",
        },
    ).json()

    exclusao = client.delete(f"/eventos/{evento['id']}")

    assert exclusao.status_code == 204
    assert client.get(f"/eventos/{evento['id']}").status_code == 404
    assert client.get(f"/sessoes/{sessao['id']}").status_code == 404


def test_impede_sessoes_sobrepostas_no_mesmo_espaco(client):
    espaco = criar_espaco(client).json()
    evento = criar_evento(client).json()

    primeira = client.post(
        "/sessoes",
        json={
            "evento_id": evento["id"],
            "espaco_id": espaco["id"],
            "titulo": "Palestra de abertura",
            "data_hora_inicio": "2026-10-01T09:00:00",
            "data_hora_fim": "2026-10-01T10:00:00",
        },
    )
    assert primeira.status_code == 201

    conflito = client.post(
        "/sessoes",
        json={
            "evento_id": evento["id"],
            "espaco_id": espaco["id"],
            "titulo": "Sessao conflitante",
            "data_hora_inicio": "2026-10-01T09:30:00",
            "data_hora_fim": "2026-10-01T10:30:00",
        },
    )

    assert conflito.status_code == 409
    assert conflito.json()["detail"]["conflitos"][0]["id"] == primeira.json()["id"]


def test_permite_sessoes_em_horarios_consecutivos(client):
    espaco = criar_espaco(client).json()
    evento = criar_evento(client).json()

    primeira = client.post(
        "/sessoes",
        json={
            "evento_id": evento["id"],
            "espaco_id": espaco["id"],
            "titulo": "Primeira sessao",
            "data_hora_inicio": "2026-10-01T09:00:00",
            "data_hora_fim": "2026-10-01T10:00:00",
        },
    )
    segunda = client.post(
        "/sessoes",
        json={
            "evento_id": evento["id"],
            "espaco_id": espaco["id"],
            "titulo": "Segunda sessao",
            "data_hora_inicio": "2026-10-01T10:00:00",
            "data_hora_fim": "2026-10-01T11:00:00",
        },
    )

    assert primeira.status_code == 201
    assert segunda.status_code == 201
