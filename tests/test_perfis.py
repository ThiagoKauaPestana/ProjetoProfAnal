"""Administração de perfis e efeito imediato das permissões."""

from conftest import EMAIL_ORGANIZADOR


def test_listagem_restrita_sem_senhas(client, anonimo, criar_participante):
    headers, _ = criar_participante()
    assert anonimo.get('/auth/usuarios').status_code == 401
    assert anonimo.get('/auth/usuarios', headers=headers).status_code == 403
    response = client.get('/auth/usuarios')
    assert response.status_code == 200
    assert len(response.json()) == 2
    assert all(set(u) == {'id','nome','email','papel','ativo'} for u in response.json())


def test_participante_nao_se_promove(client, anonimo, criar_participante):
    headers, user = criar_participante()
    route = f"/auth/usuarios/{user['id']}/perfil"
    assert anonimo.patch(route, json={'papel':'organizador'}).status_code == 401
    assert anonimo.patch(route, headers=headers, json={'papel':'organizador'}).status_code == 403
    assert anonimo.get('/auth/me', headers=headers).json()['papel'] == 'participante'


def test_promover_e_rebaixar_atualiza_token_existente(client, anonimo, criar_participante):
    headers, user = criar_participante()
    route = f"/auth/usuarios/{user['id']}/perfil"
    assert client.patch(route, json={'papel':'organizador'}).json()['papel'] == 'organizador'
    assert anonimo.get('/auth/usuarios', headers=headers).status_code == 200
    assert anonimo.get('/auth/me', headers=headers).json()['papel'] == 'organizador'
    assert client.patch(route, json={'papel':'participante'}).status_code == 200
    assert anonimo.get('/auth/usuarios', headers=headers).status_code == 403
    assert anonimo.get('/auth/me', headers=headers).json()['papel'] == 'participante'


def test_admin_nao_remove_proprio_acesso(client):
    user = client.get('/auth/me').json()
    route = f"/auth/usuarios/{user['id']}/perfil"
    assert client.patch(route, json={'papel':'participante'}).status_code == 409
    assert client.get('/auth/usuarios').status_code == 200


def test_valida_perfil_e_usuario(client, criar_participante):
    _, user = criar_participante()
    route = f"/auth/usuarios/{user['id']}/perfil"
    assert client.patch(route, json={'papel':'root'}).status_code == 422
    assert client.patch(route, json={'papel':'organizador','ativo':True}).status_code == 422
    assert client.patch('/auth/usuarios/999999/perfil', json={'papel':'organizador'}).status_code == 404


def test_organizador_inicial_nao_pode_ser_rebaixado(client, anonimo, criar_participante, monkeypatch):
    headers, user = criar_participante()
    client.patch(f"/auth/usuarios/{user['id']}/perfil", json={'papel':'organizador'})
    owner = client.get('/auth/me').json()
    monkeypatch.setenv('ORGANIZADOR_EMAIL', EMAIL_ORGANIZADOR)
    assert anonimo.patch(f"/auth/usuarios/{owner['id']}/perfil", headers=headers,
                         json={'papel':'participante'}).status_code == 409
