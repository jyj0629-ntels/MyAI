CREATE EXTENSION IF NOT EXISTS vector;


CREATE TABLE IF NOT EXISTS users (
    user_id BIGSERIAL PRIMARY KEY,
    username VARCHAR(100) NOT NULL UNIQUE,
    display_name VARCHAR(200),
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);


CREATE TABLE IF NOT EXISTS personal_memory (
    memory_id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(user_id),

    memory_type VARCHAR(50) NOT NULL,
    memory_key VARCHAR(200) NOT NULL,
    memory_value TEXT NOT NULL,

    confidence NUMERIC(5,4) DEFAULT 0.0,
    evidence_count INTEGER DEFAULT 0,

    status VARCHAR(30) NOT NULL DEFAULT 'CANDIDATE',

    source_type VARCHAR(50),
    source_id VARCHAR(100),

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);


CREATE TABLE IF NOT EXISTS questions (
    question_id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(user_id),

    original_question TEXT NOT NULL,
    normalized_question TEXT,

    category VARCHAR(100),
    priority VARCHAR(30),

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);


CREATE TABLE IF NOT EXISTS ai_sessions (
    session_id BIGSERIAL PRIMARY KEY,
    question_id BIGINT NOT NULL REFERENCES questions(question_id),

    provider VARCHAR(50) NOT NULL,

    prompt TEXT NOT NULL,
    status VARCHAR(30) NOT NULL DEFAULT 'REQUESTED',

    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,

    error_message TEXT
);


CREATE TABLE IF NOT EXISTS ai_answers (
    answer_id BIGSERIAL PRIMARY KEY,
    session_id BIGINT NOT NULL REFERENCES ai_sessions(session_id),

    answer_text TEXT,
    normalized_answer TEXT,

    input_tokens INTEGER,
    output_tokens INTEGER,

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);


CREATE TABLE IF NOT EXISTS ai_comparisons (
    comparison_id BIGSERIAL PRIMARY KEY,
    question_id BIGINT NOT NULL REFERENCES questions(question_id),

    consensus_count INTEGER NOT NULL DEFAULT 0,
    provider_count INTEGER NOT NULL DEFAULT 0,

    consensus_status VARCHAR(30) NOT NULL,

    merged_answer TEXT,

    confidence NUMERIC(5,4),

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);


CREATE TABLE IF NOT EXISTS workflows (
    workflow_id BIGSERIAL PRIMARY KEY,

    workflow_name VARCHAR(200) NOT NULL,
    workflow_type VARCHAR(100),

    description TEXT,

    enabled BOOLEAN NOT NULL DEFAULT TRUE,

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);


CREATE TABLE IF NOT EXISTS workflow_runs (
    run_id BIGSERIAL PRIMARY KEY,

    workflow_id BIGINT NOT NULL REFERENCES workflows(workflow_id),

    status VARCHAR(30) NOT NULL DEFAULT 'RUNNING',

    input_data JSONB,
    output_data JSONB,

    started_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMPTZ,

    error_message TEXT
);
