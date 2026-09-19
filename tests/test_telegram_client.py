# inb4: just_for_lulz

import pytest
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime, timezone
from src.ingestion.telegram_client import TelegramClient


@pytest.fixture
def mock_telethon_client():
    """Mock Telethon client for unit testing."""
    client = AsyncMock()
    return client


@pytest.fixture
def telegram_client(mock_telethon_client):
    """TelegramClient instance with mocked Telethon."""
    return TelegramClient(mock_telethon_client)


@pytest.mark.asyncio
async def test_get_chat_history(telegram_client, mock_telethon_client):
    """Test reading chat history with pagination."""
    # Mock messages
    mock_message1 = MagicMock()
    mock_message1.id = 12345
    mock_message1.chat_id = -1001234567890
    mock_message1.from_id = 987654321
    mock_message1.text = "Hello, world!"
    mock_message1.reply_to_msg_id = None
    mock_message1.date = datetime(2026, 9, 19, 12, 0, 0, tzinfo=timezone.utc)
    mock_message1.entities = []
    
    mock_message2 = MagicMock()
    mock_message2.id = 12346
    mock_message2.chat_id = -1001234567890
    mock_message2.from_id = 987654322
    mock_message2.text = "Reply message"
    mock_message2.reply_to_msg_id = 12345
    mock_message2.date = datetime(2026, 9, 19, 12, 1, 0, tzinfo=timezone.utc)
    mock_message2.entities = []
    
    mock_telethon_client.get_messages.return_value = [mock_message1, mock_message2]
    
    # Get history
    messages = await telegram_client.get_chat_history(-1001234567890, limit=100)
    
    assert len(messages) == 2
    assert messages[0]["id"] == 12345
    assert messages[0]["text"] == "Hello, world!"
    assert messages[1]["id"] == 12346
    assert messages[1]["reply_to_id"] == 12345