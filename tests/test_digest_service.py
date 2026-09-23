# inb4: just_for_lulz

import pytest
from unittest.mock import AsyncMock, Mock
from datetime import datetime, timezone, timedelta
from src.digest.service import DigestService
from src.moderation.gate import ModerationVerdict


@pytest.fixture
def mock_repository():
    return AsyncMock()


@pytest.fixture
def mock_llm_client():
    return AsyncMock()


@pytest.fixture
def mock_moderation_gate():
    return Mock()


@pytest.fixture
def digest_service(mock_repository, mock_llm_client, mock_moderation_gate):
    return DigestService(mock_repository, mock_llm_client, mock_moderation_gate)


@pytest.mark.asyncio
async def test_digest_service_generates_summary(digest_service, mock_repository, mock_llm_client, mock_moderation_gate):
    """Test that digest service generates a summary from chat messages."""
    mock_repository.get_messages_by_timeframe.return_value = [
        {
            "id": 1, "user_id": 111, "text": "Привет всем",
            "ts": datetime(2026, 9, 22, 10, 0, 0, tzinfo=timezone.utc)
        },
        {
            "id": 2, "user_id": 222, "text": "Здарова",
            "ts": datetime(2026, 9, 22, 10, 5, 0, tzinfo=timezone.utc)
        }
    ]
    
    mock_llm_client.generate.return_value = "Вчера аноны обсуждали приветствия"
    mock_moderation_gate.check.return_value = ModerationVerdict.ALLOW
    
    result = await digest_service.generate_digest(-100123, 24)
    
    assert result is not None
    assert "анон" in result.lower()
    mock_repository.get_messages_by_timeframe.assert_called_once()
    mock_llm_client.generate.assert_called_once()
    mock_moderation_gate.check.assert_called_once()


@pytest.mark.asyncio
async def test_digest_service_blocks_insulting_content(digest_service, mock_repository, mock_llm_client, mock_moderation_gate):
    """Test that digest service blocks insulting content via moderation gate."""
    mock_repository.get_messages_by_timeframe.return_value = [
        {
            "id": 1, "user_id": 111, "text": "Тест",
            "ts": datetime(2026, 9, 22, 10, 0, 0, tzinfo=timezone.utc)
        }
    ]
    
    mock_llm_client.generate.return_value = "@user123 — ты дебил"
    mock_moderation_gate.check.return_value = ModerationVerdict.BLOCK
    
    result = await digest_service.generate_digest(-100123, 24)
    
    assert result is None  # Blocked by moderation
    mock_moderation_gate.check.assert_called_once()


@pytest.mark.asyncio
async def test_digest_service_handles_empty_chat(digest_service, mock_repository, mock_llm_client, mock_moderation_gate):
    """Test that digest service handles empty chat gracefully."""
    mock_repository.get_messages_by_timeframe.return_value = []
    
    result = await digest_service.generate_digest(-100123, 24)
    
    assert result is None
    mock_llm_client.generate.assert_not_called()