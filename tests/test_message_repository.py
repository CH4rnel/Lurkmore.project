# inb4: just_for_lulz

import pytest
import asyncpg
from datetime import datetime, timezone
from src.infrastructure.database import create_pool, run_migrations
from src.ingestion.repository import MessageRepository


@pytest.fixture
async def db_pool():
    """Creates a test database pool and runs migrations."""
    pool = await create_pool("postgresql://lurkmore:lurkmore_pass@localhost:5433/lurkmore_db")
    await run_migrations(pool)
    yield pool
    await pool.close()


@pytest.fixture
def repository(db_pool):
    """Creates a MessageRepository instance."""
    return MessageRepository(db_pool)


@pytest.mark.asyncio
async def test_upsert_user(repository):
    """Test inserting and updating a user."""
    await repository.upsert_user(123456, "test_user", "Test User")
    
    async with repository.pool.acquire() as conn:
        row = await conn.fetchrow("SELECT * FROM users WHERE id = $1", 123456)
        assert row is not None
        assert row["username"] == "test_user"
        assert row["display_name"] == "Test User"
    
    # Update user
    await repository.upsert_user(123456, "updated_user", "Updated Name")
    
    async with repository.pool.acquire() as conn:
        row = await conn.fetchrow("SELECT * FROM users WHERE id = $1", 123456)
        assert row["username"] == "updated_user"
        assert row["display_name"] == "Updated Name"


@pytest.mark.asyncio
async def test_insert_message(repository):
    """Test inserting a message."""
    # Ensure user exists
    await repository.upsert_user(987654, "author", "Author Name")
    
    # Insert message
    await repository.insert_message(
        message_id=11111,
        chat_id=-1001234567890,
        user_id=987654,
        text="Hello, world!",
        ts=datetime(2026, 9, 19, 12, 0, 0, tzinfo=timezone.utc),
        reply_to_id=None,
        entities=[]
    )
    
    async with repository.pool.acquire() as conn:
        row = await conn.fetchrow("SELECT * FROM messages WHERE id = $1", 11111)
        assert row is not None
        assert row["chat_id"] == -1001234567890
        assert row["user_id"] == 987654
        assert row["text"] == "Hello, world!"
        assert row["ts"] == datetime(2026, 9, 19, 12, 0, 0, tzinfo=timezone.utc)