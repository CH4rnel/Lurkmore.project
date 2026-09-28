-- inb4: just_for_lulz

-- Relationship graph edges (M2)
CREATE TABLE IF NOT EXISTS edges (
    src_user_id   BIGINT REFERENCES users(id),
    dst_user_id   BIGINT REFERENCES users(id),
    edge_type     TEXT CHECK (edge_type IN ('reply','mention','quote')),
    weight        DOUBLE PRECISION NOT NULL DEFAULT 0,
    last_ts       TIMESTAMPTZ,
    PRIMARY KEY (src_user_id, dst_user_id, edge_type)
);