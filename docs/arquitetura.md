# Arquitetura da Solução — Auditório Inteligente

## 1. Visão Geral

O sistema de Gestão de Eventos e Auditórios é uma aplicação web com back-end em
**API REST** e front-end desacoplado, seguindo uma arquitetura em camadas
(apresentação → API → serviço/regra de negócio → persistência).

```
[Cliente / Front-end]
        │  HTTP/JSON
        ▼
[API REST - FastAPI]
        │
   ┌────┴────┐
   │ Routers │  (espacos, eventos, sessoes, ...)
   └────┬────┘
        │
   [Camada de regra de negócio / CRUD]
        │  (SQLAlchemy ORM)
        ▼
[Banco de Dados - PostgreSQL]
```

## 2. Decisões de Arquitetura

### 2.1 Linguagem e Framework de back-end
- **Linguagem:** Python 3.12
- **Framework:** FastAPI
  - Escolhido pela produtividade (tipagem com Pydantic, documentação
    automática via OpenAPI/Swagger em `/docs`), facilidade de validação de
    dados de entrada e bom suporte a testes automatizados.
- **ORM:** SQLAlchemy 2.0 (Declarative + `Session`)
- **Migrações:** Alembic
- **Validação/serialização:** Pydantic v2 (schemas de entrada e saída)

### 2.2 Banco de Dados
- **SGBD:** PostgreSQL (versão 15+)
  - Escolhido por ser um banco relacional robusto, gratuito, com bom suporte
    a constraints, chaves estrangeiras e consultas de intervalo de tempo
    (necessárias para checagem de conflito de horário de uso dos espaços).
- **Driver:** `psycopg2-binary`
- O schema inicial (DDL) está versionado em `sql/init.sql` e as migrações
  incrementais ficam em `alembic/versions`.

### 2.3 Estrutura de dados (entidades principais)
- **Espaco** — representa um ambiente físico que pode sediar sessões
  (auditório, sala, laboratório): nome, tipo, capacidade, localização,
  recursos disponíveis, situação (ativo/inativo).
- **Evento** — agrupador de sessões (ex.: "Semana da FCI"): nome, descrição,
  data de início/fim, status.
- **Sessao** — atividade concreta dentro de um evento, associada a um espaço
  e a um intervalo de data/hora (ex.: "Palestra de Segurança"): título,
  tipo, responsável, capacidade prevista, `data_hora_inicio`,
  `data_hora_fim`, `evento_id` (FK), `espaco_id` (FK).

Relacionamentos:
- 1 Evento → N Sessões
- 1 Espaço → N Sessões
- Um Espaço não pode ter duas Sessões com horários sobrepostos (regra de
  negócio de conflito, validada na camada de serviço antes do INSERT/UPDATE).

### 2.4 Gestão de conflitos de uso do espaço físico
Antes de criar ou atualizar uma Sessão, o back-end verifica se já existe
outra sessão para o **mesmo espaço** cujo intervalo `[inicio, fim)` se
sobreponha ao novo intervalo:

```
existente.inicio < nova.fim  AND  existente.fim > nova.inicio
```

Se houver sobreposição, a API responde `409 Conflict` com os dados da(s)
sessão(ões) conflitante(s), impedindo a dupla reserva do mesmo ambiente.

### 2.5 Front-end
- A definir/registrado pelo(s) responsável(is) pela camada de apresentação
  do grupo (framework de front-end e forma de consumo da API REST).

### 2.6 Controle de versão
- Repositório Git único do grupo (GitLab/GitHub), com commits individuais
  por integrante para comprovar autoria/contribuição em cada sprint.
- Entregas de sprint marcadas com tags anotadas (ex.: `SPRINT1`, `SPRINT2`).

## 3. Justificativa das escolhas
- **FastAPI + PostgreSQL** oferece tipagem forte de ponta a ponta (Pydantic
  ↔ SQLAlchemy ↔ Postgres), documentação automática da API (facilita a
  integração com o front-end do grupo) e é leve o suficiente para o escopo
  acadêmico do projeto, sem abrir mão de boas práticas (migrações, testes,
  separação em camadas).
