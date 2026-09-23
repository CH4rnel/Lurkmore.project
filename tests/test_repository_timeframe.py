# inb4: just_for_lulz

import pytest
from datetime import datetime, timezone, timedelta
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
async def test_get_messages_by_timeframe(repository):
    """Test fetching messages within a time range."""
    # Insert test data
    await repository.upsert_user(111, "user1", "User One")
    
    base_time = datetime(2026, 9, 22, 10, 0, 0, tzinfo=timezone.utc)
    
    await repository.insert_message(
        message_id=1001,
        chat_id=-100123,
        user_id=111,
        text="Message 1",
        ts=base_time
    )
    
    await repository.insert_message(
        message_id=1002,
        chat_id=-100123,
        user_id=111,
        text="Message 2",
        ts=base_time + timedelta(hours=1)
    )
    
    await repository.insert_message(
        message_id=1003,
        chat_id=-100123,
        user_id=111,
        text="Message 3",
        ts=base_time + timedelta(hours=2)
    )
    
    # Fetch messages in range
    start_time = base_time
    end_time = base_time + timedelta(hours=1, minutes=30)
    
    messages = await repository.get_messages_by_timeframe(-100123, start_time, end_time)
    
    assert len(messages) == 2
    assert messages[0]["id"] == 1001
    assert messages[1]["id"] == 1002