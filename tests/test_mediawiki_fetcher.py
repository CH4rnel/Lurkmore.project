# inb4: just_for_lulz

import pytest
from unittest.mock import AsyncMock, MagicMock
from src.corpus.fetcher import MediaWikiFetcher


@pytest.fixture
def mock_http_client():
    """MagicMock (не AsyncMock!) для корректной эмуляции async context manager."""
    return MagicMock()


@pytest.fixture
def fetcher(mock_http_client):
    """MediaWikiFetcher с rate_limit=0 для скорости тестов."""
    return MediaWikiFetcher(
        base_url="https://lurkmore.to",
        http_client=mock_http_client,
        rate_limit=0.0,
        max_retries=3
    )


def _make_context_manager(response):
    """Создаёт объект-контекстный менеджер, эмулирующий aiohttp response."""
    cm = MagicMock()
    cm.__aenter__.return_value = response
    cm.__aexit__.return_value = None
    return cm


def _make_response(status: int, json_data: dict = None, headers: dict = None):
    """Создаёт mock response объект."""
    response = MagicMock()
    response.status = status
    response.json = AsyncMock(return_value=json_data or {})
    response.headers = headers or {}
    return response


@pytest.mark.asyncio
async def test_fetch_batch_single_page(fetcher, mock_http_client):
    """Test fetching a single batch of articles."""
    response = _make_response(200, {
        "query": {
            "allpages": [
                {"pageid": 1, "title": "Статья1"},
                {"pageid": 2, "title": "Статья2"}
            ]
        },
        "continue": {
            "apcontinue": "Статья3",
            "continue": "-||"
        }
    })
    
    mock_http_client.get.return_value = _make_context_manager(response)
    
    articles, continue_token = await fetcher.fetch_batch(continue_token=None)
    
    assert len(articles) == 2
    assert articles[0]["title"] == "Статья1"
    assert articles[1]["title"] == "Статья2"
    assert continue_token == "Статья3"


@pytest.mark.asyncio
async def test_fetch_batch_last_page(fetcher, mock_http_client):
    """Test fetching the last batch (no continuation)."""
    response = _make_response(200, {
        "query": {
            "allpages": [
                {"pageid": 10, "title": "ПоследняяСтатья"}
            ]
        }
    })
    
    mock_http_client.get.return_value = _make_context_manager(response)
    
    articles, continue_token = await fetcher.fetch_batch(continue_token="Предыдущая")
    
    assert len(articles) == 1
    assert continue_token is None


@pytest.mark.asyncio
async def test_fetch_batch_handles_rate_limit(fetcher, mock_http_client):
    """Test that fetcher respects rate limiting."""
    response = _make_response(200, {"query": {"allpages": []}})
    mock_http_client.get.return_value = _make_context_manager(response)
    
    await fetcher.fetch_batch(continue_token=None)
    await fetcher.fetch_batch(continue_token="next")
    
    assert mock_http_client.get.call_count == 2


@pytest.mark.asyncio
async def test_fetch_batch_retries_on_429(fetcher, mock_http_client):
    """Test exponential backoff on 429 Too Many Requests."""
    response_429 = _make_response(429, headers={"Retry-After": "1"})
    response_200 = _make_response(200, {
        "query": {"allpages": [{"pageid": 1, "title": "Статья"}]}
    })
    
    mock_http_client.get.side_effect = [
        _make_context_manager(response_429),
        _make_context_manager(response_200)
    ]
    
    articles, _ = await fetcher.fetch_batch(continue_token=None)
    
    assert len(articles) == 1
    assert mock_http_client.get.call_count == 2


@pytest.mark.asyncio
async def test_fetch_batch_retries_on_5xx(fetcher, mock_http_client):
    """Test exponential backoff on 5xx errors."""
    response_503 = _make_response(503)
    response_200 = _make_response(200, {"query": {"allpages": []}})
    
    mock_http_client.get.side_effect = [
        _make_context_manager(response_503),
        _make_context_manager(response_200)
    ]
    
    articles, _ = await fetcher.fetch_batch(continue_token=None)
    
    assert mock_http_client.get.call_count == 2