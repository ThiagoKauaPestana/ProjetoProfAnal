# Como integrar estes arquivos ao repositório do grupo

## 1. Onde colocar cada arquivo
Copie mantendo a mesma estrutura de pastas para a raiz do repositório clonado:

```
docs/arquitetura.md
sql/init.sql
app/__init__.py
app/main.py
app/database.py
app/models.py
app/schemas.py
app/crud.py
app/routers/__init__.py
app/routers/espacos.py
app/routers/eventos.py
app/routers/sessoes.py
requirements.txt
.env.example
```

## 2. Rodando localmente
O projeto usa **Python 3.12**. Nesta maquina, use o `uv` no
Windows/PowerShell:

```powershell
uv python install 3.12
uv venv --python 3.12 --seed .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
```

Se voce tiver o Python Launcher instalado, `py -3.12 -m venv .venv` também
funciona no lugar dos dois primeiros comandos.

Os comandos usam o Python da `.venv` diretamente. Assim, nao e necessario
executar `Activate.ps1` nem alterar a politica de seguranca do PowerShell.

Para experimentar a API sem instalar um banco, use no VS Code
**Executar e Depurar > API FastAPI (teste local)**. Essa opcao usa um arquivo
SQLite apenas para desenvolvimento. Depois acesse `http://localhost:8000/docs`.

Para executar com a arquitetura final em PostgreSQL, inicie o Docker Desktop e
rode:

```powershell
Copy-Item .env.example .env
docker compose up -d
docker compose ps

# opcao A: deixar o FastAPI criar as tabelas (SQLAlchemy metadata)
python -m uvicorn app.main:app --reload

# opção B: aplicar o DDL manualmente
psql -U postgres -d auditorio_inteligente -f sql/init.sql
```

O `docker-compose.yml` cria o banco `auditorio_inteligente`, aplica
`sql/init.sql` na primeira inicializacao e publica o PostgreSQL na porta 5432.
Para encerrar o banco sem apagar os dados, use `docker compose stop`.

### Passo a passo completo apos clonar o repositorio

```powershell
uv python install 3.12
uv venv --python 3.12 --seed .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
Copy-Item .env.example .env
docker compose up -d
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

Depois, acesse `http://localhost:8000/docs`. Quem ja possui Python 3.12 pode
criar a `.venv` com o proprio Python, sem usar `uv`. Quem ja possui PostgreSQL
15+ pode dispensar o Docker e ajustar `DATABASE_URL` no arquivo `.env`.
A documentação interativa fica disponível em `http://localhost:8000/docs`.

No VS Code, abra a pasta `g15` (nao a pasta acima dela). As configuracoes em
`.vscode` selecionam o ambiente `.venv`. Para PostgreSQL, use **Executar e
Depurar > API FastAPI (PostgreSQL)**. Nao execute `app/main.py` diretamente.

## 3. Rodando os testes

Os testes usam um banco SQLite isolado e nao precisam do PostgreSQL:

```powershell
.\.venv\Scripts\python.exe -m pytest tests -q
```

Também é possível usar o painel **Testing** do VS Code ou a configuração
**Executar e Depurar > Testes pytest**.

## 4. Endpoints principais
- `POST/GET/PUT/DELETE /espacos` — cadastro de ambientes físicos
- `POST/GET/PUT/DELETE /eventos` — cadastro de eventos
- `POST/GET/PUT/DELETE /sessoes` — cadastro de sessões, com checagem
  automática de conflito de horário por espaço (retorna `409 Conflict`
  quando já existe sessão sobreposta no mesmo espaço)

## 5. Commit individual de cada integrante (obrigatório na entrega)
Cada membro deve fazer commit(s) com **seu próprio usuário/e-mail do
Git configurado**, por exemplo:

```bash
git config user.name "Seu Nome"
git config user.email "seu-email@mackenzista.com.br"

git add <arquivos que você implementou>
git commit -m "feat: cadastro de espaços físicos com regra de conflito"
git push origin <sua-branch-ou-main>
```

## 6. Criar e enviar a tag SPRINT2
Depois que todos os commits da sprint estiverem na branch principal:

```bash
git checkout main
git pull origin main

git tag -a SPRINT2 -m "Entrega Sprint 2 - cadastro de espaços, eventos e sessões"
git push origin SPRINT2
```

A URL a entregar na tarefa é a do repositório apontando para a tag, por
exemplo:
```
https://github.com/ppads-2026s2/g15/releases/tag/SPRINT2
```
(ou, se preferir, o link direto da tag:
`https://github.com/ppads-2026s2/g15/tree/SPRINT2`)

## 7. Publicar para apresentacao

O arquivo `render.yaml` configura automaticamente uma API FastAPI e um banco
PostgreSQL 15 no Render.

1. Envie o projeto para o GitHub.
2. Acesse `https://dashboard.render.com/blueprints`.
3. Selecione **New Blueprint Instance**.
4. Conecte o repositorio do grupo.
5. Confirme a criacao dos dois recursos descritos no `render.yaml`.
6. Aguarde o deploy e abra a URL terminada em `.onrender.com/docs`.

No plano gratuito, a API pode suspender depois de 15 minutos sem acessos e
demorar cerca de um minuto na primeira abertura. O PostgreSQL gratuito expira
30 dias depois da criacao, portanto deve ser criado proximo da apresentacao.
