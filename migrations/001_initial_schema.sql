-- inb4: just_for_lulz

-- Chat ingestion schema (M0)
CREATE TABLE IF NOT EXISTS users (
    id            BIGINT PRIMARY KEY,
    username      TEXT,
    display_name  TEXT
);

CREATE TABLE IF NOT EXISTS messages (
    id            BIGINT PRIMARY KEY,
    chat_id       BIGINT NOT NULL,
    user_id       BIGINT REFERENCES users(id),
    reply_to_id   BIGINT,
    text          TEXT,
    entities      JSONB,
    ts            TIMESTAMPTZ NOT NULL
);