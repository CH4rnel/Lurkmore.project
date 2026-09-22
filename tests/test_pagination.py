# inb4: just_for_lulz

import pytest
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime, timezone
from src.ingestion.telegram_client import TelegramClient


def _make_mock_message(msg_id: int) -> MagicMock:
    """Helper to create a mock Telethon message."""
    msg = MagicMock()
    msg.id = msg_id
    msg.chat_id = -100123
    msg.from_id = 111
    msg.text = f"message {msg_id}"
    msg.reply_to_msg_id = None
    msg.date = datetime(2026, 9, 20, 10, 0, 0, tzinfo=timezone.utc)
    msg.entities = []
    return msg


@pytest.fixture
def mock_telethon():
    return AsyncMock()


@pytest.fixture
def client(mock_telethon):
    return TelegramClient(mock_telethon)


@pytest.mark.asyncio
async def test_get_chat_history_single_page(client, mock_telethon):
    """When total messages <= limit, single fetch is enough."""
    mock_telethon.get_messages.return_value = [
        _make_mock_message(1), _make_mock_message(2)
    ]
    messages = await client.get_chat_history(-100123, limit=100)
    assert len(messages) == 2
    assert mock_telethon.get_messages.call_count == 1


@pytest.mark.asyncio
async def test_get_chat_history_with_offset(client, mock_telethon):
    """Pagination via offset_id fetches older messages."""
    mock_telethon.get_messages.return_value = [
        _make_mock_message(50), _make_mock_message(49)
    ]
    messages = await client.get_chat_history(-100123, limit=2, offset_id=100)
    assert len(messages) == 2
    mock_telethon.get_messages.assert_called_once_with(-100123, limit=2, offset_id=100)