# Sprint 3 v2 — Inscrições

## Alterações

A API existente já implementava autenticação, autorização e regras de inscrições. A interface principal em `frontend/` foi conectada aos endpoints da Sprint 3.

- Login e cadastro público de participante; organizador pode ser criado por outro organizador na API e pode ser inicializado via variáveis de ambiente (instruções em `README-setup.md`).
- Catálogo público de sessões com filtros por título, tipo, evento, intervalo de datas e disponibilidade; exibição de vagas e fila.
- Inscrição individual, cancelamento e visualização do resultado (confirmada ou fila de espera).
- Área *Minhas inscrições* com histórico opcional e posição na fila.
- Consulta de inscrições por evento e sessão para organizadores, filtros de status e cancelamento administrativo.
- Menus administrativos somente para organizadores autenticados; backend continua sendo a proteção real de todas as operações.

## Testes

```bash
pip install -r requirements-dev.txt
pytest -q
```

## Executar

Configure o banco e o organizador inicial conforme `README-setup.md` e rode a aplicação FastAPI. Acesse `/` para visualizar a interface, `/docs` para conferir a API.

**Observação:** o token de acesso fica apenas na sessão da aba do navegador (`sessionStorage`). É necessário entrar novamente ao abrir uma nova sessão. Para testar a fila de espera, crie sessões com capacidade pequena e entre com contas de participantes diferentes.

Não compartilhe `.env` com credenciais nem faça commit desse arquivo.
