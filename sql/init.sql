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
