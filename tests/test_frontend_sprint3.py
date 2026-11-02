"""Smoke tests for the Sprint 3 interface served by FastAPI."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_frontend_sections_and_scripts():
    html = (ROOT / 'frontend/index.html').read_text(encoding='utf-8')
    for anchor in ('catalogoView', 'minhasView', 'gestaoView', 'authDialog', 'catalogFilters', 'managementFilters'):
        assert f'id="{anchor}"' in html
    assert '/static/sprint3.js' in html


def test_frontend_uses_real_api_routes():
    js = (ROOT / 'frontend/sprint3.js').read_text(encoding='utf-8')
    for route in ('/auth/login', '/auth/registro', '/auth/me', '/inscricoes/minhas', '/inscricoes?', '/inscricao', '/sessoes'):
        assert route in js
    assert 'data-cancel-id' in js
    assert 'posicao_fila' in js


def test_admin_mutations_include_auth_token():
    js = (ROOT / 'frontend/app.js').read_text(encoding='utf-8')
    assert 'Authorization:' in js
    assert 'sessionStorage.getItem("g15_token")' in js
