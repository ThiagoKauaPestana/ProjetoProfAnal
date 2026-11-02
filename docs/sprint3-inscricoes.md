# Sprint 3 — Inscrições (back-end)

## Arquivos novos e alterados

| Arquivo | O que mudou |
|---|---|
| `app/models.py` | + `Usuario`, + `Inscricao`; `Sessao.inscricoes` (cascade) |
| `app/schemas.py` | + schemas de usuário, token, inscrição e `SessaoCatalogoOut`; validação de `capacidade_prevista` |
| `app/security.py` | **novo** — hash de senha (scrypt) e JWT |
| `app/deps.py` | **novo** — `get_usuario_atual`, `exigir_organizador`, `exigir_participante` |
| `app/tempo.py` | **novo** — `agora()` no fuso do evento (padrão America/Sao_Paulo) |
| `app/crud_usuarios.py` | **novo** — cadastro, login e organizador inicial |
| `app/crud_inscricoes.py` | **novo** — capacidade, duplicidade, fila e promoção |
| `app/crud.py` | filtros de eventos/sessões; promoção da fila ao mudar capacidade |
| `app/routers/auth.py` | **novo** — registro, login, `/auth/me`, criar organizador |
| `app/routers/inscricoes.py` | **novo** — inscrever, cancelar, "minhas", gestão |
| `app/routers/espacos.py`, `eventos.py`, `sessoes.py` | escrita só para organizador; filtros no catálogo |
| `app/main.py` | registra os novos routers; cria organizador inicial |
| `sql/init.sql` | + tabelas `usuarios` e `inscricoes` |
| `requirements.txt` | + `PyJWT`, `python-multipart`, `tzdata` |
| `tests/conftest.py`, `tests/test_sprint3.py` | fixtures com login e testes da sprint |

## Configuração (variáveis de ambiente)

Acrescente ao `.env` / `.env.example`:

```
SECRET_KEY=troque-por-um-valor-longo-e-aleatorio
ORGANIZADOR_EMAIL=organizador@mackenzista.com.br
ORGANIZADOR_SENHA=troque-esta-senha
ORGANIZADOR_NOME=Organizador
```

* `SECRET_KEY` assina os tokens. Em produção (Render) use um valor aleatório.
* `ORGANIZADOR_*` criam o primeiro organizador quando a API sobe. Sem eles,
  ninguém consegue cadastrar espaços/eventos/sessões, pois o cadastro público
  (`/auth/registro`) só cria participantes.
* Opcionais: `TOKEN_EXPIRA_MINUTOS` (padrão 60) e `FUSO_HORARIO`
  (padrão `America/Sao_Paulo`).

Nenhuma migração é necessária: as tabelas novas são criadas na subida da API
(`create_all`) e nenhuma coluna de tabela existente foi alterada.

## Como usar no `/docs`

1. `POST /auth/registro` cria um participante (ou entre como organizador).
2. Clique em **Authorize** e informe o e-mail em *username* e a senha.
3. Os endpoints protegidos passam a funcionar.

## Endpoints

### Autenticação
| Método | Rota | Quem | Descrição |
|---|---|---|---|
| POST | `/auth/registro` | público | cria participante |
| POST | `/auth/login` | público | JSON `{email, senha}` → token |
| POST | `/auth/token` | público | mesmo login em formulário (botão Authorize) |
| GET | `/auth/me` | logado | dados do usuário |
| POST | `/auth/organizadores` | organizador | cria outro organizador |
| GET | `/auth/usuarios` | organizador | lista usuários, sem senhas |
| PATCH | `/auth/usuarios/{id}/perfil` | organizador | altera o papel de outra conta |

No painel, **Usuários e perfis** permite buscar contas por nome/e-mail e
selecionar **Administrador (organizador)** ou **Usuário (participante)**.
O cadastro público continua criando participantes. A API consulta o papel
atual no banco a cada requisição, inclusive para tokens emitidos antes da
troca. Atualizar a página recarrega os menus da pessoa afetada.
O administrador não pode remover o próprio acesso; o organizador inicial
configurado no ambiente mantém o perfil administrativo após reinicializações.

### Catálogo (leitura pública; escrita só organizador)
| Rota | Filtros |
|---|---|
| `GET /eventos` | `status`, `busca`, `data_de`, `data_ate` |
| `GET /sessoes` | `evento_id`, `espaco_id`, `tipo`, `busca`, `data`, `data_de`, `data_ate`, `apenas_com_vagas` |
| `GET /sessoes/{id}` | detalhe com `capacidade_total`, `vagas_ocupadas`, `vagas_disponiveis`, `lista_espera` |

### Inscrições
| Método | Rota | Quem | Descrição |
|---|---|---|---|
| POST | `/sessoes/{id}/inscricao` | participante | `confirmada` ou `lista_espera` (com `posicao_fila`) |
| DELETE | `/sessoes/{id}/inscricao` | participante | cancela a própria e promove a fila |
| GET | `/inscricoes/minhas` | logado | "Minhas inscrições" (`status`, `incluir_canceladas`, `evento_id`, `apenas_futuras`) |
| DELETE | `/inscricoes/{id}` | dono ou organizador | cancela por id |
| GET | `/sessoes/{id}/inscricoes` | organizador | inscritos da sessão (`status`, `incluir_canceladas`) |
| GET | `/eventos/{id}/inscricoes` | organizador | inscritos do evento (`status`, `incluir_canceladas`, `sessao_id`) |

## Regras de negócio

* **Vagas**: `capacidade_prevista` da sessão; se não houver, a capacidade do espaço.
* **Duplicidade**: não pode haver duas inscrições ativas do mesmo usuário na
  mesma sessão (409). Reforçado no banco por `UNIQUE (usuario_id, sessao_id)`.
  Cancelar e se inscrever de novo reativa a mesma linha.
* **Lotação**: sem vaga, a pessoa entra na `lista_espera`, ordenada por chegada.
* **Promoção automática**: ao cancelar uma inscrição confirmada, o primeiro da
  fila vira `confirmada` na mesma transação (`promovida_em` registra quando).
  Aumentar a capacidade da sessão ou do espaço também promove a fila.
  Reduzir a capacidade não remove quem já está confirmado.
* **Concorrência**: a sessão é travada (`SELECT ... FOR UPDATE`) enquanto a
  vaga é decidida, para duas pessoas não pegarem a última vaga juntas.
* **Prazo**: não é possível se inscrever (nem o participante cancelar) depois
  que a sessão começou; o organizador pode cancelar a qualquer momento.
  Eventos `cancelado` ou `encerrado` não aceitam novas inscrições.
* Organizadores não se inscrevem em sessões (403); só participantes.
* **Sessões concomitantes**: uma inscrição confirmada ou em espera impede
  outra inscrição com horário sobreposto, mesmo em salas ou eventos diferentes
  (409). Sessões consecutivas são permitidas: o término de uma pode coincidir
  com o início da próxima. Inscrições canceladas não bloqueiam a agenda.
* **Elegibilidade da fila**: a promoção verifica novamente a agenda. Quem
  ganhou um conflito após uma alteração de horário permanece em espera,
  preservando sua ordem, enquanto o próximo participante elegível ocupa a vaga.
  Não há promoção em sessão já iniciada ou evento cancelado/encerrado.
* No PostgreSQL, inscrições e promoções usam um advisory lock transacional
  compartilhado para impedir confirmações concomitantes por requisições paralelas.

## Rodando os testes

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe -m pytest tests -q
```

O fixture `client` dos testes agora já vem autenticado como organizador, então
`tests/test_api.py` continua funcionando sem alterações.
