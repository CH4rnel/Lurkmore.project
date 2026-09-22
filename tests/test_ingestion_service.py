# inb4: just_for_lulz

import pytest
from unittest.mock import AsyncMock
from datetime import datetime, timezone
from src.ingestion.service import IngestionService


@pytest.fixture
def mock_telegram_client():
    return AsyncMock()


@pytest.fixture
def mock_repository():
    return AsyncMock()


@pytest.fixture
def service(mock_telegram_client, mock_repository):
    return IngestionService(mock_telegram_client, mock_repository)


@pytest.mark.asyncio
async def test_ingest_chat_success(service, mock_telegram_client, mock_repository):
    """Test successful ingestion of chat messages."""
    messages = [
        {
            "id": 12345, "chat_id": -100123, "user_id": 111,
            "text": "Hello", "reply_to_id": None,
            "ts": datetime(2026, 9, 19, 12, 0, 0, tzinfo=timezone.utc),
            "entities": []
        },
        {
            "id": 12346, "chat_id": -100123, "user_id": 222,
            "text": "Reply", "reply_to_id": 12345,
            "ts": datetime(2026, 9, 19, 12, 1, 0, tzinfo=timezone.utc),
            "entities": []
        }
    ]
    # First call returns messages, second returns empty (end of history)
    mock_telegram_client.get_chat_history.side_effect = [messages, []]
    
    ingested = await service.ingest_chat(-100123, limit=100)
    assert ingested == 2


@pytest.mark.asyncio
async def test_ingest_chat_handles_errors(service, mock_telegram_client, mock_repository):
    """Test that ingestion continues even if some messages fail."""
    messages = [
        {
            "id": 1, "chat_id": -100123, "user_id": 111,
            "text": "OK", "reply_to_id": None,
            "ts": datetime(2026, 9, 19, 12, 0, 0, tzinfo=timezone.utc),
            "entities": []
        },
        {
            "id": 2, "chat_id": -100123, "user_id": 222,
            "text": "Fail", "reply_to_id": None,
            "ts": datetime(2026, 9, 19, 12, 1, 0, tzinfo=timezone.utc),
            "entities": []
        }
    ]
    mock_telegram_client.get_chat_history.side_effect = [messages, []]
    mock_repository.insert_message.side_effect = [None, Exception("DB error")]
    ingested = await service.ingest_chat(-100123, limit=100)
    assert ingested == 1


@pytest.mark.asyncio
async def test_ingest_chat_pagination(service, mock_telegram_client, mock_repository):
    """Test that ingestion paginates through multiple batches."""
    batch1 = [
        {
            "id": 100, "chat_id": -100123, "user_id": 111,
            "text": "msg 100", "reply_to_id": None,
            "ts": datetime(2026, 9, 19, 12, 0, 0, tzinfo=timezone.utc),
            "entities": []
        }
    ]
    batch2 = [
        {
            "id": 99, "chat_id": -100123, "user_id": 222,
            "text": "msg 99", "reply_to_id": 100,
            "ts": datetime(2026, 9, 19, 11, 59, 0, tzinfo=timezone.utc),
            "entities": []
        }
    ]
    # First call returns batch1, second returns batch2, third returns empty
    mock_telegram_client.get_chat_history.side_effect = [batch1, batch2, []]

    ingested = await service.ingest_chat(-100123, limit=10, batch_size=1)

    assert ingested == 2
    assert mock_telegram_client.get_chat_history.call_count == 3


@pytest.mark.asyncio
async def test_ingest_skips_service_messages(service, mock_telegram_client, mock_repository):
    """Test that messages with no user_id (service messages) are skipped."""
    messages = [
        {
            "id": 500, "chat_id": -100123, "user_id": None,
            "text": "User joined", "reply_to_id": None,
            "ts": datetime(2026, 9, 19, 12, 0, 0, tzinfo=timezone.utc),
            "entities": []
        }
    ]
    mock_telegram_client.get_chat_history.side_effect = [messages, []]
    ingested = await service.ingest_chat(-100123, limit=100)
    assert ingested == 0
    mock_repository.insert_message.assert_not_called()