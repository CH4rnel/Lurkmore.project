# inb4: just_for_lulz

import json
import pytest
from datetime import datetime, timezone
from src.infrastructure.database import create_pool, run_migrations
from src.corpus.repository import ArticleRepository


@pytest.fixture
async def db_pool():
    pool = await create_pool("postgresql://lurkmore:lurkmore_pass@localhost:5433/lurkmore_db")
    await run_migrations(pool)
    yield pool
    await pool.close()


@pytest.fixture
def repository(db_pool):
    return ArticleRepository(db_pool, base_url="https://lurkmore.to")


@pytest.mark.asyncio
async def test_upsert_article_returns_id(repository):
    """Test that upsert_article returns the article ID."""
    fetched_at = datetime(2026, 9, 28, 12, 0, 0, tzinfo=timezone.utc)
    article_id = await repository.upsert_article(
        title="Тестовая статья с ID",
        source_url="https://lurkmore.to/Тестовая_статья_с_ID",
        revision_id=12345,
        raw_wikitext="Текст",
        clean_text="Текст",
        fetched_at=fetched_at
    )
    assert isinstance(article_id, int)
    assert article_id > 0


@pytest.mark.asyncio
async def test_upsert_article_relations(repository):
    """Test saving categories, templates, and links for an article."""
    fetched_at = datetime(2026, 9, 28, 12, 0, 0, tzinfo=timezone.utc)
    article_id = await repository.upsert_article(
        title="Статья со связями",
        source_url="https://lurkmore.to/Статья_со_связями",
        revision_id=1,
        raw_wikitext="Текст",
        clean_text="Текст",
        fetched_at=fetched_at
    )
    
    links = [{"target": "Другая статья", "anchor": "ссылка"}]
    categories = ["Мемы", "Сленг"]
    templates = [{"name": "stub", "params": {"reason": "недописано"}}]
    
    await repository.upsert_article_relations(article_id, links, categories, templates)
    
    async with repository.pool.acquire() as conn:
        # Check categories
        cats = await conn.fetch(
            "SELECT c.name FROM categories c JOIN article_categories ac ON c.id = ac.category_id WHERE ac.article_id = $1",
            article_id
        )
        assert len(cats) == 2
        assert "Мемы" in [c["name"] for c in cats]
        
        tmpls = await conn.fetch(
            "SELECT t.name, at.params::jsonb AS params FROM templates t JOIN article_templates at ON t.id = at.template_id WHERE at.article_id = $1",
            article_id
        )
        assert len(tmpls) == 1
        assert tmpls[0]["name"] == "stub"
        
        params = tmpls[0]["params"]
        if isinstance(params, str):
            params = json.loads(params)
            
        assert params["reason"] == "недописано"
        
        # Check links
        links_db = await conn.fetch(
            "SELECT dst.title as dst_title, l.anchor FROM links l JOIN articles dst ON l.dst_id = dst.id WHERE l.src_id = $1",
            article_id
        )
        assert len(links_db) == 1
        assert links_db[0]["dst_title"] == "Другая статья"
        assert links_db[0]["anchor"] == "ссылка"