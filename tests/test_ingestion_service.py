# inb4: just_for_lulz

import pytest
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime, timezone
from src.ingestion.service import IngestionService


@pytest.fixture
def mock_telegram_client():
    """Mock Telegram client."""
    client = AsyncMock()
    return client


@pytest.fixture
def mock_repository():
    """Mock message repository."""
    repository = AsyncMock()
    return repository


@pytest.fixture
def service(mock_telegram_client, mock_repository):
    """IngestionService with mocked dependencies."""
    return IngestionService(mock_telegram_client, mock_repository)


@pytest.mark.asyncio
async def test_ingest_chat_success(service, mock_telegram_client, mock_repository):
    """Test successful ingestion of chat messages."""
    # Mock messages
    mock_telegram_client.get_chat_history.return_value = [
        {
            "id": 12345,
            "chat_id": -1001234567890,
            "user_id": 987654321,
            "text": "Hello, world!",
            "reply_to_id": None,
            "ts": datetime(2026, 9, 19, 12, 0, 0, tzinfo=timezone.utc),
            "entities": []
        },
        {
            "id": 12346,
            "chat_id": -1001234567890,
            "user_id": 987654322,
            "text": "Reply message",
            "reply_to_id": 12345,
            "ts": datetime(2026, 9, 19, 12, 1, 0, tzinfo=timezone.utc),
            "entities": []
        }
    ]
    
    # Run ingestion
    ingested = await service.ingest_chat(-1001234567890, limit=100)
    
    # Assertions
    assert ingested == 2
    assert mock_telegram_client.get_chat_history.called
    assert mock_repository.upsert_user.call_count == 2
    assert mock_repository.insert_message.call_count == 2


@pytest.mark.asyncio
async def test_ingest_chat_handles_errors(service, mock_telegram_client, mock_repository):
    """Test that ingestion continues even if some messages fail."""
    # Mock messages
    mock_telegram_client.get_chat_history.return_value = [
        {
            "id": 12345,
            "chat_id": -1001234567890,
            "user_id": 987654321,
            "text": "Success message",
            "reply_to_id": None,
            "ts": datetime(2026, 9, 19, 12, 0, 0, tzinfo=timezone.utc),
            "entities": []
        },
        {
            "id": 12346,
            "chat_id": -1001234567890,
            "user_id": 987654322,
            "text": "Failed message",
            "reply_to_id": None,
            "ts": datetime(2026, 9, 19, 12, 1, 0, tzinfo=timezone.utc),
            "entities": []
        }
    ]
    
    # Make second message fail
    mock_repository.insert_message.side_effect = [None, Exception("DB error")]
    
    # Run ingestion
    ingested = await service.ingest_chat(-1001234567890, limit=100)
    
    # Should still count first message as successful
    assert ingested == 1