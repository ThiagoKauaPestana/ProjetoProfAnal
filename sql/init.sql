-- Schema inicial do sistema Auditório Inteligente
-- SGBD: PostgreSQL 15+

CREATE TABLE IF NOT EXISTS espacos (
    id              SERIAL PRIMARY KEY,
    nome            VARCHAR(120) NOT NULL,
    tipo            VARCHAR(50)  NOT NULL,          -- ex: auditorio, sala, laboratorio
    capacidade      INTEGER      NOT NULL CHECK (capacidade > 0),
    localizacao     VARCHAR(150),
    recursos        TEXT,                           -- ex: "projetor, som, ar-condicionado"
    ativo           BOOLEAN      NOT NULL DEFAULT TRUE,
    criado_em       TIMESTAMP    NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS eventos (
    id              SERIAL PRIMARY KEY,
    nome            VARCHAR(150) NOT NULL,          -- ex: "Semana da FCI"
    descricao       TEXT,
    data_inicio     DATE         NOT NULL,
    data_fim        DATE         NOT NULL,
    status          VARCHAR(30)  NOT NULL DEFAULT 'planejado', -- planejado, em_andamento, encerrado, cancelado
    criado_em       TIMESTAMP    NOT NULL DEFAULT NOW(),
    CHECK (data_fim >= data_inicio)
);

CREATE TABLE IF NOT EXISTS sessoes (
    id                  SERIAL PRIMARY KEY,
    evento_id           INTEGER NOT NULL REFERENCES eventos(id) ON DELETE CASCADE,
    espaco_id           INTEGER NOT NULL REFERENCES espacos(id) ON DELETE RESTRICT,
    titulo              VARCHAR(150) NOT NULL,       -- ex: "Palestra de Segurança"
    descricao           TEXT,
    tipo                VARCHAR(50),                 -- ex: palestra, workshop, minicurso
    responsavel         VARCHAR(120),
    capacidade_prevista INTEGER CHECK (capacidade_prevista IS NULL OR capacidade_prevista > 0),
    data_hora_inicio    TIMESTAMP NOT NULL,
    data_hora_fim       TIMESTAMP NOT NULL,
    criado_em           TIMESTAMP NOT NULL DEFAULT NOW(),
    CHECK (data_hora_fim > data_hora_inicio)
);

-- Índice para acelerar a checagem de conflito de horário por espaço
CREATE INDEX IF NOT EXISTS idx_sessoes_espaco_horario
    ON sessoes (espaco_id, data_hora_inicio, data_hora_fim);

-- ---------------------------------------------------------------------------
-- Sprint 3: usuários e inscrições
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS usuarios (
    id              SERIAL PRIMARY KEY,
    nome            VARCHAR(120) NOT NULL,
    email           VARCHAR(150) NOT NULL UNIQUE,   -- sempre em minúsculas
    senha_hash      VARCHAR(255) NOT NULL,          -- scrypt; nunca a senha em texto
    papel           VARCHAR(20)  NOT NULL DEFAULT 'participante'
                    CHECK (papel IN ('organizador', 'participante')),
    ativo           BOOLEAN      NOT NULL DEFAULT TRUE,
    criado_em       TIMESTAMP    NOT NULL DEFAULT NOW()
);

-- Uma linha por (usuário, sessão). Cancelar muda o status; reinscrever
-- reativa a mesma linha. A constraint UNIQUE é a trava final contra duplicidade.
CREATE TABLE IF NOT EXISTS inscricoes (
    id              SERIAL PRIMARY KEY,
    usuario_id      INTEGER NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
    sessao_id       INTEGER NOT NULL REFERENCES sessoes(id)  ON DELETE CASCADE,
    status          VARCHAR(20) NOT NULL DEFAULT 'confirmada'
                    CHECK (status IN ('confirmada', 'lista_espera', 'cancelada')),
    entrou_em       TIMESTAMP NOT NULL DEFAULT NOW(),  -- define a ordem da fila de espera
    promovida_em    TIMESTAMP,                         -- quando saiu da fila para confirmada
    cancelada_em    TIMESTAMP,
    criado_em       TIMESTAMP NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_inscricao_usuario_sessao UNIQUE (usuario_id, sessao_id)
);

-- Contagem de vagas e ordem da fila por sessão
CREATE INDEX IF NOT EXISTS idx_inscricoes_sessao_status
    ON inscricoes (sessao_id, status, entrou_em);
