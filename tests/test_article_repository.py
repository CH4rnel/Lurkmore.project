# inb4: just_for_lulz

import pytest
from datetime import datetime, timezone
from src.infrastructure.database import create_pool, run_migrations
from src.corpus.repository import ArticleRepository


@pytest.fixture
async def db_pool():
    """Creates a test database pool and runs migrations."""
    pool = await create_pool("postgresql://lurkmore:lurkmore_pass@localhost:5433/lurkmore_db")
    await run_migrations(pool)
    yield pool
    await pool.close()


@pytest.fixture
def repository(db_pool):
    """Creates an ArticleRepository instance."""
    return ArticleRepository(db_pool)


@pytest.mark.asyncio
async def test_upsert_article_insert(repository):
    """Test inserting a new article."""
    fetched_at = datetime(2026, 9, 28, 12, 0, 0, tzinfo=timezone.utc)
    
    await repository.upsert_article(
        title="Тестовая статья",
        source_url="https://lurkmore.to/Тестовая_статья",
        revision_id=12345,
        raw_wikitext="== Заголовок ==\nТекст статьи.",
        clean_text="Текст статьи.",
        fetched_at=fetched_at
    )
    
    article = await repository.load_article_by_title("Тестовая статья")
    
    assert article is not None
    assert article["title"] == "Тестовая статья"
    assert article["source_url"] == "https://lurkmore.to/Тестовая_статья"
    assert article["revision_id"] == 12345
    assert article["clean_text"] == "Текст статьи."
    assert article["fetched_at"] == fetched_at


@pytest.mark.asyncio
async def test_upsert_article_update(repository):
    """Test updating an existing article."""
    fetched_at1 = datetime(2026, 9, 28, 10, 0, 0, tzinfo=timezone.utc)
    await repository.upsert_article(
        title="Обновляемая статья",
        source_url="https://lurkmore.to/Обновляемая_статья",
        revision_id=100,
        raw_wikitext="Старый текст",
        clean_text="Старый текст",
        fetched_at=fetched_at1
    )
    
    fetched_at2 = datetime(2026, 9, 28, 12, 0, 0, tzinfo=timezone.utc)
    await repository.upsert_article(
        title="Обновляемая статья",
        source_url="https://lurkmore.to/Обновляемая_статья",
        revision_id=200,
        raw_wikitext="Новый текст",
        clean_text="Новый текст",
        fetched_at=fetched_at2
    )
    
    article = await repository.load_article_by_title("Обновляемая статья")
    
    assert article["revision_id"] == 200
    assert article["clean_text"] == "Новый текст"
    assert article["fetched_at"] == fetched_at2


@pytest.mark.asyncio
async def test_load_article_not_found(repository):
    """Test that loading non-existent article returns None."""
    article = await repository.load_article_by_title("Несуществующая статья")
    assert article is None