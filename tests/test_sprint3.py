"""Testes da Sprint 3: autenticação, catálogo com filtros e inscrições."""

import itertools
from datetime import timedelta

import pytest
from sqlalchemy.exc import IntegrityError

from app import crud_usuarios, models, security
from app.tempo import agora

# ---------------------------------------------------------------------------
# Auxiliares
# ---------------------------------------------------------------------------
_proximo_dia = itertools.count(1)


def _iso(momento):
    return momento.replace(microsecond=0).isoformat()


def criar_espaco(client, nome="Auditorio Principal", capacidade=120):
    resposta = client.post(
        "/espacos",
        json={"nome": nome, "tipo": "auditorio", "capacidade": capacidade},
    )
    assert resposta.status_code == 201, resposta.text
    return resposta.json()


def criar_evento(client, nome="Semana da FCI", **extra):
    payload = {"nome": nome, "data_inicio": "2026-10-01", "data_fim": "2026-10-03"}
    payload.update(extra)
    resposta = client.post("/eventos", json=payload)
    assert resposta.status_code == 201, resposta.text
    return resposta.json()


def criar_sessao(
    client, evento, espaco, *, dias=None, hora=9, horas=1, capacidade=None, **extra
):
    """Cria uma sessão no futuro. Sem `dias`, cada chamada usa um dia novo,
    então sessões do mesmo espaço nunca entram em conflito de horário."""
    dias = next(_proximo_dia) if dias is None else dias
    inicio = (agora() + timedelta(days=dias)).replace(
        hour=hora, minute=0, second=0, microsecond=0
    )
    payload = {
        "evento_id": evento["id"],
        "espaco_id": espaco["id"],
        "titulo": f"Sessao {dias}",
        "data_hora_inicio": _iso(inicio),
        "data_hora_fim": _iso(inicio + timedelta(hours=horas)),
    }
    if capacidade is not None:
        payload["capacidade_prevista"] = capacidade
    payload.update(extra)
    resposta = client.post("/sessoes", json=payload)
    assert resposta.status_code == 201, resposta.text
    return resposta.json()


def cenario(client, capacidade=2):
    espaco = criar_espaco(client)
    evento = criar_evento(client)
    sessao = criar_sessao(client, evento, espaco, capacidade=capacidade)
    return evento, espaco, sessao


def inscrever(anonimo, headers, sessao):
    return anonimo.post(f"/sessoes/{sessao['id']}/inscricao", headers=headers)


def cancelar(anonimo, headers, sessao):
    return anonimo.delete(f"/sessoes/{sessao['id']}/inscricao", headers=headers)


def ids(itens):
    return [i["id"] for i in itens]


def minhas(anonimo, headers, **params):
    resposta = anonimo.get("/inscricoes/minhas", headers=headers, params=params)
    assert resposta.status_code == 200, resposta.text
    return resposta.json()


# ---------------------------------------------------------------------------
# Segurança (hash e token)
# ---------------------------------------------------------------------------
def test_hash_de_senha():
    senha_hash = security.gerar_hash_senha("abc12345")

    assert senha_hash != "abc12345"
    assert security.verificar_senha("abc12345", senha_hash)
    assert not security.verificar_senha("outra-senha", senha_hash)
    assert senha_hash != security.gerar_hash_senha("abc12345")  # salt aleatório
    assert not security.verificar_senha("abc12345", "hash-invalido")


def test_token_jwt(monkeypatch):
    token = security.criar_token(7, "participante")
    payload = security.decodificar_token(token)

    assert payload["sub"] == "7"
    assert payload["papel"] == "participante"
    assert security.decodificar_token("token-lixo") is None

    monkeypatch.setattr(security, "TOKEN_EXPIRA_MINUTOS", -1)
    expirado = security.criar_token(7, "participante")
    assert security.decodificar_token(expirado) is None


# ---------------------------------------------------------------------------
# Autenticação
# ---------------------------------------------------------------------------
def test_registro_cria_participante(anonimo):
    resposta = anonimo.post(
        "/auth/registro",
        json={"nome": "Maria", "email": "Maria@Mackenzista.com.br", "senha": "senha123"},
    )

    assert resposta.status_code == 201
    corpo = resposta.json()
    assert corpo["papel"] == "participante"
    assert corpo["email"] == "maria@mackenzista.com.br"
    assert "senha" not in corpo and "senha_hash" not in corpo


def test_registro_nao_permite_escolher_papel(anonimo):
    resposta = anonimo.post(
        "/auth/registro",
        json={
            "nome": "Espertinho",
            "email": "esperto@mackenzista.com.br",
            "senha": "senha123",
            "papel": "organizador",
        },
    )

    assert resposta.status_code == 201
    assert resposta.json()["papel"] == "participante"


def test_registro_rejeita_email_repetido(anonimo):
    dados = {"nome": "Maria", "email": "maria@mackenzista.com.br", "senha": "senha123"}

    assert anonimo.post("/auth/registro", json=dados).status_code == 201
    repetido = anonimo.post("/auth/registro", json=dados)

    assert repetido.status_code == 409


@pytest.mark.parametrize(
    "dados",
    [
        {"nome": "Maria", "email": "maria@x.com", "senha": "123"},  # senha curta
        {"nome": "Maria", "email": "sem-arroba", "senha": "senha123"},  # e-mail ruim
        {"nome": "   ", "email": "maria@x.com", "senha": "senha123"},  # nome vazio
    ],
)
def test_registro_valida_dados(anonimo, dados):
    assert anonimo.post("/auth/registro", json=dados).status_code == 422


def test_login_e_dados_do_usuario_logado(anonimo, criar_participante):
    headers, usuario = criar_participante("Joana")

    eu = anonimo.get("/auth/me", headers=headers)

    assert eu.status_code == 200
    assert eu.json()["id"] == usuario["id"]
    assert eu.json()["nome"] == "Joana"


def test_login_com_senha_errada(anonimo, criar_participante):
    _, usuario = criar_participante()

    resposta = anonimo.post(
        "/auth/login", json={"email": usuario["email"], "senha": "errada123"}
    )

    assert resposta.status_code == 401


def test_login_formulario_oauth2_do_swagger(anonimo, criar_participante):
    _, usuario = criar_participante()

    resposta = anonimo.post(
        "/auth/token", data={"username": usuario["email"], "password": "senha123"}
    )

    assert resposta.status_code == 200
    assert resposta.json()["token_type"] == "bearer"


def test_token_invalido_ou_ausente_retorna_401(anonimo):
    assert anonimo.get("/auth/me").status_code == 401
    ruim = anonimo.get("/auth/me", headers={"Authorization": "Bearer lixo"})
    assert ruim.status_code == 401


# ---------------------------------------------------------------------------
# Permissões
# ---------------------------------------------------------------------------
def test_visitante_nao_cadastra_nada(anonimo):
    assert anonimo.post("/espacos", json={"nome": "x", "tipo": "sala", "capacidade": 5}).status_code == 401
    assert anonimo.post("/eventos", json={}).status_code == 401
    assert anonimo.post("/sessoes", json={}).status_code == 401


def test_participante_nao_altera_espacos_eventos_sessoes(
    client, anonimo, criar_participante
):
    evento, espaco, sessao = cenario(client)
    headers, _ = criar_participante()

    assert anonimo.post("/espacos", headers=headers, json={"nome": "x", "tipo": "sala", "capacidade": 5}).status_code == 403
    assert anonimo.post("/eventos", headers=headers, json={}).status_code == 403
    assert anonimo.post("/sessoes", headers=headers, json={}).status_code == 403
    assert anonimo.put(f"/espacos/{espaco['id']}", headers=headers, json={"nome": "y"}).status_code == 403
    assert anonimo.put(f"/eventos/{evento['id']}", headers=headers, json={"nome": "y"}).status_code == 403
    assert anonimo.put(f"/sessoes/{sessao['id']}", headers=headers, json={"titulo": "y"}).status_code == 403
    assert anonimo.delete(f"/sessoes/{sessao['id']}", headers=headers).status_code == 403
    assert anonimo.delete(f"/eventos/{evento['id']}", headers=headers).status_code == 403
    assert anonimo.delete(f"/espacos/{espaco['id']}", headers=headers).status_code == 403


def test_catalogo_e_publico(client, anonimo):
    evento, espaco, sessao = cenario(client)

    assert anonimo.get("/eventos").status_code == 200
    assert anonimo.get(f"/eventos/{evento['id']}").status_code == 200
    assert anonimo.get("/espacos").status_code == 200
    assert anonimo.get("/sessoes").status_code == 200
    assert anonimo.get(f"/sessoes/{sessao['id']}").status_code == 200


def test_organizador_cria_outro_organizador(client, anonimo, criar_participante):
    novo = {"nome": "Org 2", "email": "org2@mackenzista.com.br", "senha": "organizador2"}

    criado = client.post("/auth/organizadores", json=novo)
    assert criado.status_code == 201
    assert criado.json()["papel"] == "organizador"

    login = anonimo.post(
        "/auth/login", json={"email": novo["email"], "senha": novo["senha"]}
    )
    headers = {"Authorization": f"Bearer {login.json()['access_token']}"}
    assert anonimo.post("/espacos", headers=headers, json={"nome": "Sala", "tipo": "sala", "capacidade": 10}).status_code == 201

    participante, _ = criar_participante()
    assert anonimo.post("/auth/organizadores", headers=participante, json=novo).status_code == 403
    assert anonimo.post("/auth/organizadores", json=novo).status_code == 401


def test_organizador_inicial_a_partir_do_ambiente(session_factory, monkeypatch):
    monkeypatch.delenv("ORGANIZADOR_EMAIL", raising=False)
    monkeypatch.delenv("ORGANIZADOR_SENHA", raising=False)
    db = session_factory()

    assert crud_usuarios.garantir_organizador_inicial(db) is None

    admin = crud_usuarios.garantir_organizador_inicial(
        db, email="Admin@Mackenzista.com.br", senha="admin123", nome="Admin"
    )
    assert admin.papel == models.PAPEL_ORGANIZADOR
    assert admin.email == "admin@mackenzista.com.br"

    de_novo = crud_usuarios.garantir_organizador_inicial(
        db, email="admin@mackenzista.com.br", senha="outra-senha", nome="Admin"
    )
    assert de_novo.id == admin.id
    assert crud_usuarios.autenticar(db, "admin@mackenzista.com.br", "admin123")
    db.close()


# ---------------------------------------------------------------------------
# Catálogo com filtros
# ---------------------------------------------------------------------------
def test_filtros_do_catalogo_de_sessoes(client, anonimo):
    espaco1 = criar_espaco(client, "Auditorio A")
    espaco2 = criar_espaco(client, "Sala B", capacidade=30)
    evento1 = criar_evento(client, "Semana da FCI")
    evento2 = criar_evento(client, "Semana de IA")

    s1 = criar_sessao(client, evento1, espaco1, dias=1, hora=9, tipo="palestra",
                      titulo="Seguranca da Informacao", responsavel="Ana Silva")
    s2 = criar_sessao(client, evento1, espaco1, dias=1, hora=14, tipo="workshop",
                      titulo="Introducao ao Docker", responsavel="Bruno")
    s3 = criar_sessao(client, evento2, espaco2, dias=3, hora=10, tipo="palestra",
                      titulo="Inteligencia Artificial")
    dia1 = (agora() + timedelta(days=1)).date().isoformat()
    dia2 = (agora() + timedelta(days=2)).date().isoformat()
    dia3 = (agora() + timedelta(days=3)).date().isoformat()

    def buscar(**params):
        resposta = anonimo.get("/sessoes", params=params)
        assert resposta.status_code == 200, resposta.text
        return ids(resposta.json())

    assert buscar() == [s1["id"], s2["id"], s3["id"]]  # ordenado por horário
    assert buscar(tipo="palestra") == [s1["id"], s3["id"]]
    assert buscar(tipo="PALESTRA") == [s1["id"], s3["id"]]
    assert buscar(busca="docker") == [s2["id"]]
    assert buscar(busca="silva") == [s1["id"]]  # procura também no responsável
    assert buscar(busca="%") == []  # % é tratado como texto comum
    assert buscar(evento_id=evento2["id"]) == [s3["id"]]
    assert buscar(espaco_id=espaco2["id"]) == [s3["id"]]
    assert buscar(data=dia1) == [s1["id"], s2["id"]]
    assert buscar(data_de=dia2) == [s3["id"]]
    assert buscar(data_ate=dia1) == [s1["id"], s2["id"]]
    assert buscar(data_de=dia2, data_ate=dia3) == [s3["id"]]
    assert buscar(tipo="palestra", data=dia1) == [s1["id"]]


def test_filtros_do_catalogo_de_eventos(client, anonimo):
    e1 = criar_evento(client, "Semana da FCI")
    e2 = criar_evento(
        client,
        "Hackathon",
        descricao="Maratona de programacao",
        data_inicio="2026-11-10",
        data_fim="2026-11-11",
        status="em_andamento",
    )

    def buscar(**params):
        resposta = anonimo.get("/eventos", params=params)
        assert resposta.status_code == 200, resposta.text
        return ids(resposta.json())

    assert buscar() == [e1["id"], e2["id"]]
    assert buscar(status="em_andamento") == [e2["id"]]
    assert buscar(busca="fci") == [e1["id"]]
    assert buscar(busca="maratona") == [e2["id"]]  # procura na descrição
    assert buscar(data_de="2026-11-01") == [e2["id"]]
    assert buscar(data_ate="2026-10-31") == [e1["id"]]
    assert buscar(data_de="2026-10-02", data_ate="2026-10-02") == [e1["id"]]


def test_catalogo_mostra_vagas_e_filtra_sessoes_lotadas(
    client, anonimo, criar_participante
):
    espaco = criar_espaco(client)
    evento = criar_evento(client)
    lotada = criar_sessao(client, evento, espaco, capacidade=1)
    livre = criar_sessao(client, evento, espaco, capacidade=3)
    ana, _ = criar_participante()
    bia, _ = criar_participante()
    inscrever(anonimo, ana, lotada)
    inscrever(anonimo, bia, lotada)  # vai para a fila

    detalhe = anonimo.get(f"/sessoes/{lotada['id']}").json()
    assert detalhe["capacidade_total"] == 1
    assert detalhe["vagas_ocupadas"] == 1
    assert detalhe["vagas_disponiveis"] == 0
    assert detalhe["lista_espera"] == 1
    assert detalhe["evento_nome"] == "Semana da FCI"
    assert detalhe["espaco_nome"] == "Auditorio Principal"

    com_vagas = anonimo.get("/sessoes", params={"apenas_com_vagas": True}).json()
    assert ids(com_vagas) == [livre["id"]]


def test_capacidade_usa_a_do_espaco_quando_a_sessao_nao_define(client, anonimo):
    espaco = criar_espaco(client, capacidade=5)
    evento = criar_evento(client)
    sessao = criar_sessao(client, evento, espaco)  # sem capacidade_prevista

    assert anonimo.get(f"/sessoes/{sessao['id']}").json()["capacidade_total"] == 5


# ---------------------------------------------------------------------------
# Inscrição, capacidade e duplicidade
# ---------------------------------------------------------------------------
def test_inscricao_confirmada_ocupa_uma_vaga(client, anonimo, criar_participante):
    _, _, sessao = cenario(client, capacidade=2)
    ana, usuario = criar_participante()

    resposta = inscrever(anonimo, ana, sessao)

    assert resposta.status_code == 201
    corpo = resposta.json()
    assert corpo["status"] == "confirmada"
    assert corpo["usuario_id"] == usuario["id"]
    assert corpo["sessao_id"] == sessao["id"]
    assert corpo["posicao_fila"] is None
    detalhe = anonimo.get(f"/sessoes/{sessao['id']}").json()
    assert detalhe["vagas_ocupadas"] == 1
    assert detalhe["vagas_disponiveis"] == 1


def test_inscricao_duplicada_retorna_409(client, anonimo, criar_participante):
    _, _, sessao = cenario(client, capacidade=2)
    ana, _ = criar_participante()

    assert inscrever(anonimo, ana, sessao).status_code == 201
    repetida = inscrever(anonimo, ana, sessao)

    assert repetida.status_code == 409
    assert anonimo.get(f"/sessoes/{sessao['id']}").json()["vagas_ocupadas"] == 1


def test_inscricao_duplicada_na_fila_tambem_retorna_409(
    client, anonimo, criar_participante
):
    _, _, sessao = cenario(client, capacidade=1)
    ana, _ = criar_participante()
    bia, _ = criar_participante()
    inscrever(anonimo, ana, sessao)

    assert inscrever(anonimo, bia, sessao).json()["status"] == "lista_espera"
    assert inscrever(anonimo, bia, sessao).status_code == 409
    assert anonimo.get(f"/sessoes/{sessao['id']}").json()["lista_espera"] == 1


def test_banco_impede_inscricao_duplicada(session_factory):
    db = session_factory()
    db.add(models.Inscricao(usuario_id=1, sessao_id=1, status="confirmada"))
    db.commit()
    db.add(models.Inscricao(usuario_id=1, sessao_id=1, status="confirmada"))

    with pytest.raises(IntegrityError):
        db.commit()
    db.rollback()
    db.close()


def test_lotacao_envia_para_lista_de_espera(client, anonimo, criar_participante):
    _, _, sessao = cenario(client, capacidade=1)
    ana, _ = criar_participante()
    bia, _ = criar_participante()
    caio, _ = criar_participante()

    assert inscrever(anonimo, ana, sessao).json()["status"] == "confirmada"
    fila_bia = inscrever(anonimo, bia, sessao).json()
    fila_caio = inscrever(anonimo, caio, sessao).json()

    assert fila_bia["status"] == "lista_espera"
    assert fila_bia["posicao_fila"] == 1
    assert fila_caio["status"] == "lista_espera"
    assert fila_caio["posicao_fila"] == 2
    detalhe = anonimo.get(f"/sessoes/{sessao['id']}").json()
    assert detalhe["vagas_ocupadas"] == 1
    assert detalhe["vagas_disponiveis"] == 0
    assert detalhe["lista_espera"] == 2


def test_inscricao_exige_login_e_perfil_participante(client, anonimo):
    _, _, sessao = cenario(client)

    assert anonimo.post(f"/sessoes/{sessao['id']}/inscricao").status_code == 401
    assert client.post(f"/sessoes/{sessao['id']}/inscricao").status_code == 403  # organizador


def test_inscricao_em_sessao_inexistente(anonimo, criar_participante):
    ana, _ = criar_participante()

    assert anonimo.post("/sessoes/9999/inscricao", headers=ana).status_code == 404


def test_sessao_que_ja_comecou_nao_aceita_inscricao(client, anonimo, criar_participante):
    espaco = criar_espaco(client)
    evento = criar_evento(client)
    passada = criar_sessao(client, evento, espaco, dias=-1)
    ana, _ = criar_participante()

    assert inscrever(anonimo, ana, passada).status_code == 409


def test_evento_cancelado_nao_aceita_inscricao(client, anonimo, criar_participante):
    evento, _, sessao = cenario(client)
    client.put(f"/eventos/{evento['id']}", json={"status": "cancelado"})
    ana, _ = criar_participante()

    assert inscrever(anonimo, ana, sessao).status_code == 409


# ---------------------------------------------------------------------------
# Cancelamento e promoção automática
# ---------------------------------------------------------------------------
def test_cancelamento_promove_o_primeiro_da_fila(client, anonimo, criar_participante):
    _, _, sessao = cenario(client, capacidade=1)
    ana, _ = criar_participante()
    bia, _ = criar_participante()
    caio, _ = criar_participante()
    inscrever(anonimo, ana, sessao)
    inscrever(anonimo, bia, sessao)
    inscrever(anonimo, caio, sessao)

    resposta = cancelar(anonimo, ana, sessao)

    assert resposta.status_code == 200
    assert resposta.json()["inscricao"]["status"] == "cancelada"
    assert resposta.json()["promovidas_total"] == 1
    [da_bia] = minhas(anonimo, bia)
    assert da_bia["status"] == "confirmada"
    assert da_bia["promovida_em"] is not None
    [do_caio] = minhas(anonimo, caio)
    assert do_caio["status"] == "lista_espera"
    assert do_caio["posicao_fila"] == 1  # andou uma posição na fila
    assert minhas(anonimo, ana) == []  # cancelada some da listagem padrão


def test_sair_da_fila_nao_promove_ninguem(client, anonimo, criar_participante):
    _, _, sessao = cenario(client, capacidade=1)
    ana, _ = criar_participante()
    bia, _ = criar_participante()
    caio, _ = criar_participante()
    inscrever(anonimo, ana, sessao)
    inscrever(anonimo, bia, sessao)
    inscrever(anonimo, caio, sessao)

    resposta = cancelar(anonimo, bia, sessao)

    assert resposta.json()["promovidas_total"] == 0
    assert minhas(anonimo, ana)[0]["status"] == "confirmada"
    assert minhas(anonimo, caio)[0]["posicao_fila"] == 1


def test_quem_cancela_e_volta_entra_no_fim_da_fila(client, anonimo, criar_participante):
    _, _, sessao = cenario(client, capacidade=1)
    ana, _ = criar_participante()
    bia, _ = criar_participante()
    inscrever(anonimo, ana, sessao)
    inscrever(anonimo, bia, sessao)
    cancelar(anonimo, ana, sessao)  # a Bia é promovida

    de_volta = inscrever(anonimo, ana, sessao)

    assert de_volta.status_code == 201
    assert de_volta.json()["status"] == "lista_espera"
    assert de_volta.json()["posicao_fila"] == 1
    historico = minhas(anonimo, ana, incluir_canceladas=True)
    assert len(historico) == 1  # a mesma inscrição foi reativada, sem duplicar


def test_cancelar_sem_inscricao_ativa_retorna_404(client, anonimo, criar_participante):
    _, _, sessao = cenario(client)
    ana, _ = criar_participante()

    assert cancelar(anonimo, ana, sessao).status_code == 404
    inscrever(anonimo, ana, sessao)
    assert cancelar(anonimo, ana, sessao).status_code == 200
    assert cancelar(anonimo, ana, sessao).status_code == 404


def test_participante_cancela_por_id_so_a_propria(client, anonimo, criar_participante):
    _, _, sessao = cenario(client, capacidade=2)
    ana, _ = criar_participante()
    bia, _ = criar_participante()
    [da_ana] = [inscrever(anonimo, ana, sessao).json()]

    outro = anonimo.delete(f"/inscricoes/{da_ana['id']}", headers=bia)
    assert outro.status_code == 403

    propria = anonimo.delete(f"/inscricoes/{da_ana['id']}", headers=ana)
    assert propria.status_code == 200
    assert anonimo.delete(f"/inscricoes/{da_ana['id']}", headers=ana).status_code == 409
    assert anonimo.delete("/inscricoes/9999", headers=ana).status_code == 404


def test_nao_cancela_sessao_iniciada_mas_organizador_pode(
    client, anonimo, criar_participante
):
    _, _, sessao = cenario(client, capacidade=2)
    ana, _ = criar_participante()
    inscricao = inscrever(anonimo, ana, sessao).json()
    agora_ = agora()
    client.put(
        f"/sessoes/{sessao['id']}",
        json={
            "data_hora_inicio": _iso(agora_ - timedelta(hours=3)),
            "data_hora_fim": _iso(agora_ - timedelta(hours=2)),
        },
    )

    assert cancelar(anonimo, ana, sessao).status_code == 409
    assert len(minhas(anonimo, ana)) == 1
    assert minhas(anonimo, ana, apenas_futuras=True) == []  # a sessão já terminou

    pelo_organizador = client.delete(f"/inscricoes/{inscricao['id']}")
    assert pelo_organizador.status_code == 200
    assert pelo_organizador.json()["inscricao"]["status"] == "cancelada"


# ---------------------------------------------------------------------------
# Mudança de capacidade
# ---------------------------------------------------------------------------
def test_aumentar_capacidade_da_sessao_promove_a_fila(client, anonimo, criar_participante):
    _, _, sessao = cenario(client, capacidade=1)
    ana, _ = criar_participante()
    bia, _ = criar_participante()
    caio, _ = criar_participante()
    for headers in (ana, bia, caio):
        inscrever(anonimo, headers, sessao)

    assert client.put(f"/sessoes/{sessao['id']}", json={"capacidade_prevista": 2}).status_code == 200
    assert minhas(anonimo, bia)[0]["status"] == "confirmada"
    assert minhas(anonimo, caio)[0]["status"] == "lista_espera"
    assert minhas(anonimo, caio)[0]["posicao_fila"] == 1

    client.put(f"/sessoes/{sessao['id']}", json={"capacidade_prevista": 3})
    assert minhas(anonimo, caio)[0]["status"] == "confirmada"


def test_reduzir_capacidade_mantem_confirmados_e_bloqueia_novas_promocoes(
    client, anonimo, criar_participante
):
    _, _, sessao = cenario(client, capacidade=2)
    ana, _ = criar_participante()
    bia, _ = criar_participante()
    caio, _ = criar_participante()
    inscrever(anonimo, ana, sessao)
    inscrever(anonimo, bia, sessao)
    client.put(f"/sessoes/{sessao['id']}", json={"capacidade_prevista": 1})

    assert minhas(anonimo, ana)[0]["status"] == "confirmada"
    assert minhas(anonimo, bia)[0]["status"] == "confirmada"
    assert inscrever(anonimo, caio, sessao).json()["status"] == "lista_espera"

    cancelar(anonimo, ana, sessao)  # sobra 1 confirmado para 1 vaga: ninguém é promovido
    assert minhas(anonimo, caio)[0]["status"] == "lista_espera"


def test_aumentar_capacidade_do_espaco_promove_a_fila(client, anonimo, criar_participante):
    espaco = criar_espaco(client, capacidade=1)
    evento = criar_evento(client)
    sessao = criar_sessao(client, evento, espaco)  # usa a capacidade do espaço
    ana, _ = criar_participante()
    bia, _ = criar_participante()
    inscrever(anonimo, ana, sessao)
    assert inscrever(anonimo, bia, sessao).json()["status"] == "lista_espera"

    client.put(f"/espacos/{espaco['id']}", json={"capacidade": 2})

    assert minhas(anonimo, bia)[0]["status"] == "confirmada"


# ---------------------------------------------------------------------------
# Minhas inscrições
# ---------------------------------------------------------------------------
def test_minhas_inscricoes(client, anonimo, criar_participante):
    espaco = criar_espaco(client)
    evento = criar_evento(client, "Semana da FCI")
    outro_evento = criar_evento(client, "Hackathon")
    s1 = criar_sessao(client, evento, espaco, dias=1, capacidade=5, titulo="Primeira")
    s2 = criar_sessao(client, evento, espaco, dias=2, capacidade=1, titulo="Lotada")
    s3 = criar_sessao(client, evento, espaco, dias=3, capacidade=5, titulo="Cancelada")
    s4 = criar_sessao(client, outro_evento, espaco, dias=4, capacidade=5, titulo="Outro evento")
    ana, _ = criar_participante()
    bia, _ = criar_participante()
    inscrever(anonimo, bia, s2)  # ocupa a única vaga da s2
    for sessao in (s1, s2, s3, s4):
        inscrever(anonimo, ana, sessao)
    cancelar(anonimo, ana, s3)

    padrao = minhas(anonimo, ana)
    assert [i["sessao"]["titulo"] for i in padrao] == ["Primeira", "Lotada", "Outro evento"]
    assert [i["status"] for i in padrao] == ["confirmada", "lista_espera", "confirmada"]
    assert padrao[1]["posicao_fila"] == 1
    assert padrao[0]["sessao"]["evento_nome"] == "Semana da FCI"
    assert padrao[0]["sessao"]["espaco_nome"] == "Auditorio Principal"

    assert [i["sessao"]["titulo"] for i in minhas(anonimo, ana, status="lista_espera")] == ["Lotada"]
    assert [i["sessao"]["titulo"] for i in minhas(anonimo, ana, status="cancelada")] == ["Cancelada"]
    assert len(minhas(anonimo, ana, incluir_canceladas=True)) == 4
    assert [i["sessao"]["titulo"] for i in minhas(anonimo, ana, evento_id=outro_evento["id"])] == ["Outro evento"]
    assert len(minhas(anonimo, ana, apenas_futuras=True)) == 3
    # cada participante só vê as próprias
    assert [i["sessao"]["titulo"] for i in minhas(anonimo, bia)] == ["Lotada"]


def test_minhas_inscricoes_exige_login(anonimo):
    assert anonimo.get("/inscricoes/minhas").status_code == 401


# ---------------------------------------------------------------------------
# Gerenciamento pelo organizador
# ---------------------------------------------------------------------------
def test_organizador_lista_inscricoes_da_sessao(client, anonimo, criar_participante):
    _, _, sessao = cenario(client, capacidade=1)
    ana, _ = criar_participante("Ana")
    bia, _ = criar_participante("Bia")
    caio, _ = criar_participante("Caio")
    inscrever(anonimo, ana, sessao)
    inscrever(anonimo, bia, sessao)
    inscrever(anonimo, caio, sessao)

    todas = client.get(f"/sessoes/{sessao['id']}/inscricoes").json()
    assert [i["usuario"]["nome"] for i in todas] == ["Ana", "Bia", "Caio"]
    assert [i["status"] for i in todas] == ["confirmada", "lista_espera", "lista_espera"]
    assert [i["posicao_fila"] for i in todas] == [None, 1, 2]
    assert todas[0]["usuario"]["email"].endswith("@mackenzista.com.br")

    fila = client.get(f"/sessoes/{sessao['id']}/inscricoes", params={"status": "lista_espera"}).json()
    assert [i["usuario"]["nome"] for i in fila] == ["Bia", "Caio"]

    cancelar(anonimo, ana, sessao)
    sem_canceladas = client.get(f"/sessoes/{sessao['id']}/inscricoes").json()
    com_canceladas = client.get(
        f"/sessoes/{sessao['id']}/inscricoes", params={"incluir_canceladas": True}
    ).json()
    assert len(sem_canceladas) == 2
    assert len(com_canceladas) == 3


def test_listagens_do_organizador_exigem_perfil_organizador(
    client, anonimo, criar_participante
):
    evento, _, sessao = cenario(client)
    ana, _ = criar_participante()

    assert anonimo.get(f"/sessoes/{sessao['id']}/inscricoes").status_code == 401
    assert anonimo.get(f"/sessoes/{sessao['id']}/inscricoes", headers=ana).status_code == 403
    assert anonimo.get(f"/eventos/{evento['id']}/inscricoes", headers=ana).status_code == 403
    assert client.get("/sessoes/9999/inscricoes").status_code == 404
    assert client.get("/eventos/9999/inscricoes").status_code == 404


def test_organizador_lista_inscricoes_do_evento(client, anonimo, criar_participante):
    espaco = criar_espaco(client)
    evento = criar_evento(client)
    outro_evento = criar_evento(client, "Outro")
    s1 = criar_sessao(client, evento, espaco, dias=1, capacidade=1, titulo="S1")
    s2 = criar_sessao(client, evento, espaco, dias=2, capacidade=5, titulo="S2")
    s3 = criar_sessao(client, outro_evento, espaco, dias=3, capacidade=5, titulo="S3")
    ana, _ = criar_participante("Ana")
    bia, _ = criar_participante("Bia")
    inscrever(anonimo, ana, s1)
    inscrever(anonimo, bia, s1)  # fila
    inscrever(anonimo, ana, s2)
    inscrever(anonimo, ana, s3)

    todas = client.get(f"/eventos/{evento['id']}/inscricoes").json()
    assert [(i["sessao"]["titulo"], i["usuario"]["nome"]) for i in todas] == [
        ("S1", "Ana"), ("S1", "Bia"), ("S2", "Ana"),
    ]  # S3 é de outro evento
    so_s2 = client.get(
        f"/eventos/{evento['id']}/inscricoes", params={"sessao_id": s2["id"]}
    ).json()
    assert [i["sessao"]["titulo"] for i in so_s2] == ["S2"]
    fila = client.get(
        f"/eventos/{evento['id']}/inscricoes", params={"status": "lista_espera"}
    ).json()
    assert [i["usuario"]["nome"] for i in fila] == ["Bia"]


def test_organizador_cancela_inscricao_e_a_fila_anda(client, anonimo, criar_participante):
    _, _, sessao = cenario(client, capacidade=1)
    ana, _ = criar_participante()
    bia, _ = criar_participante()
    da_ana = inscrever(anonimo, ana, sessao).json()
    inscrever(anonimo, bia, sessao)

    resposta = client.delete(f"/inscricoes/{da_ana['id']}")

    assert resposta.status_code == 200
    assert resposta.json()["promovidas_total"] == 1
    assert minhas(anonimo, bia)[0]["status"] == "confirmada"


def test_excluir_sessao_remove_as_inscricoes(client, anonimo, criar_participante):
    _, _, sessao = cenario(client)
    ana, _ = criar_participante()
    inscrever(anonimo, ana, sessao)

    assert client.delete(f"/sessoes/{sessao['id']}").status_code == 204
    assert minhas(anonimo, ana, incluir_canceladas=True) == []
