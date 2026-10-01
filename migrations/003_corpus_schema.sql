-- inb4: just_for_lulz

CREATE TABLE IF NOT EXISTS articles (
    id            SERIAL PRIMARY KEY,
    title         TEXT UNIQUE NOT NULL,
    source_url    TEXT NOT NULL,
    revision_id   BIGINT,
    raw_wikitext  TEXT,
    clean_text    TEXT,
    fetched_at    TIMESTAMPTZ NOT NULL
);

CREATE TABLE IF NOT EXISTS categories (
    id SERIAL PRIMARY KEY,
    name TEXT UNIQUE
);

CREATE TABLE IF NOT EXISTS article_categories (
    article_id INT REFERENCES articles(id),
    category_id INT REFERENCES categories(id),
    PRIMARY KEY (article_id, category_id)
);

CREATE TABLE IF NOT EXISTS links (
    src_id INT REFERENCES articles(id),
    dst_id INT REFERENCES articles(id),
    anchor TEXT,
    PRIMARY KEY (src_id, dst_id, anchor)
);

CREATE TABLE IF NOT EXISTS templates (
    id SERIAL PRIMARY KEY,
    name TEXT UNIQUE
);

CREATE TABLE IF NOT EXISTS article_templates (
    article_id INT REFERENCES articles(id),
    template_id INT REFERENCES templates(id),
    params JSONB,
    PRIMARY KEY (article_id, template_id)
);

CREATE TABLE IF NOT EXISTS lexicon (
    term        TEXT PRIMARY KEY,
    definition  TEXT,
    register    TEXT CHECK (register IN ('слэнг', 'мем', 'аббревиатура', 'эвфемизм')),
    examples    JSONB,
    llr_score   DOUBLE PRECISION,
    freq        INT
);