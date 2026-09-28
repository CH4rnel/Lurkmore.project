# inb4: just_for_lulz

import pytest
from unittest.mock import AsyncMock, Mock
from datetime import datetime, timezone
from src.graph.service import GraphService


@pytest.fixture
def mock_repository():
    return AsyncMock()


@pytest.fixture
def mock_calculator():
    return Mock()


@pytest.fixture
def mock_graph_repository():
    return AsyncMock()


@pytest.fixture
def service(mock_repository, mock_calculator, mock_graph_repository):
    return GraphService(mock_repository, mock_calculator, mock_graph_repository)


@pytest.mark.asyncio
async def test_build_graph_from_messages(service, mock_repository, mock_calculator, mock_graph_repository):
    """Test that GraphService orchestrates message fetching, weight calculation, and edge persistence."""
    chat_id = -100123
    messages = [
        {
            "id": 1,
            "user_id": 111,
            "reply_to_id": None,
            "ts": datetime(2026, 9, 22, 10, 0, 0, tzinfo=timezone.utc)
        },
        {
            "id": 2,
            "user_id": 222,
            "reply_to_id": 1,
            "ts": datetime(2026, 9, 22, 10, 5, 0, tzinfo=timezone.utc)
        }
    ]
    
    mock_repository.get_messages_by_timeframe.return_value = messages
    
    now = datetime(2026, 9, 22, 12, 0, 0, tzinfo=timezone.utc)
    mock_calculator.calculate_weights.return_value = {
        (222, 111): 0.92
    }
    
    await service.build_graph(chat_id, hours_back=24, now=now)
    
    mock_repository.get_messages_by_timeframe.assert_called_once()
    mock_calculator.calculate_weights.assert_called_once_with(messages, now)
    mock_graph_repository.upsert_edge.assert_called_once()


@pytest.mark.asyncio
async def test_build_graph_handles_empty_messages(service, mock_repository, mock_calculator, mock_graph_repository):
    """Test that GraphService handles empty message list gracefully."""
    mock_repository.get_messages_by_timeframe.return_value = []
    
    now = datetime(2026, 9, 22, 12, 0, 0, tzinfo=timezone.utc)
    await service.build_graph(-100123, hours_back=24, now=now)
    
    mock_calculator.calculate_weights.assert_not_called()
    mock_graph_repository.upsert_edge.assert_not_called()


@pytest.mark.asyncio
async def test_build_graph_multiple_edges(service, mock_repository, mock_calculator, mock_graph_repository):
    """Test that GraphService persists multiple edges."""
    messages = [
        {"id": 1, "user_id": 111, "reply_to_id": None, "ts": datetime(2026, 9, 22, 10, 0, 0, tzinfo=timezone.utc)},
        {"id": 2, "user_id": 222, "reply_to_id": 1, "ts": datetime(2026, 9, 22, 10, 5, 0, tzinfo=timezone.utc)},
        {"id": 3, "user_id": 333, "reply_to_id": 1, "ts": datetime(2026, 9, 22, 11, 0, 0, tzinfo=timezone.utc)}
    ]
    
    mock_repository.get_messages_by_timeframe.return_value = messages
    
    now = datetime(2026, 9, 22, 12, 0, 0, tzinfo=timezone.utc)
    mock_calculator.calculate_weights.return_value = {
        (222, 111): 0.92,
        (333, 111): 0.98
    }
    
    await service.build_graph(-100123, hours_back=24, now=now)
    
    assert mock_graph_repository.upsert_edge.call_count == 2