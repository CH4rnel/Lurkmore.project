# inb4: just_for_lulz

import pytest
from unittest.mock import AsyncMock, Mock
from src.corpus.service import ETLService


@pytest.fixture
def mock_fetcher():
    return AsyncMock()


@pytest.fixture
def mock_parser():
    return Mock()


@pytest.fixture
def mock_repository():
    return AsyncMock()


@pytest.fixture
def service(mock_fetcher, mock_parser, mock_repository):
    return ETLService(mock_fetcher, mock_parser, mock_repository)


@pytest.mark.asyncio
async def test_etl_service_processes_single_batch(service, mock_fetcher, mock_parser, mock_repository):
    """Test that ETL service processes a single batch of articles."""
    mock_fetcher.fetch_batch.side_effect = [
        (
            [
                {"pageid": 1, "title": "Статья1"},
                {"pageid": 2, "title": "Статья2"}
            ],
            None
        )
    ]
    
    mock_fetcher.get_article_content = AsyncMock(side_effect=[
        "== Заголовок ==\nТекст статьи 1",
        "== Заголовок ==\nТекст статьи 2"
    ])
    
    mock_parser.parse.side_effect = [
        {"clean_text": "Текст статьи 1", "links": [], "categories": [], "templates": []},
        {"clean_text": "Текст статьи 2", "links": [], "categories": [], "templates": []}
    ]
    
    stats = await service.run()
    
    assert stats["processed"] == 2
    assert stats["failed"] == 0
    assert mock_repository.upsert_article.call_count == 2


@pytest.mark.asyncio
async def test_etl_service_handles_multiple_batches(service, mock_fetcher, mock_parser, mock_repository):
    """Test that ETL service handles continuation tokens across batches."""
    mock_fetcher.fetch_batch.side_effect = [
        (
            [{"pageid": 1, "title": "Статья1"}],
            "continue_token_1"
        ),
        (
            [{"pageid": 2, "title": "Статья2"}],
            None
        )
    ]
    
    mock_fetcher.get_article_content = AsyncMock(side_effect=[
        "Текст 1",
        "Текст 2"
    ])
    
    mock_parser.parse.side_effect = [
        {"clean_text": "Текст 1", "links": [], "categories": [], "templates": []},
        {"clean_text": "Текст 2", "links": [], "categories": [], "templates": []}
    ]
    
    stats = await service.run()
    
    assert stats["processed"] == 2
    assert mock_fetcher.fetch_batch.call_count == 2


@pytest.mark.asyncio
async def test_etl_service_handles_parser_error(service, mock_fetcher, mock_parser, mock_repository):
    """Test that ETL service continues processing even if parser fails on one article."""
    mock_fetcher.fetch_batch.side_effect = [
        (
            [
                {"pageid": 1, "title": "Статья1"},
                {"pageid": 2, "title": "Статья2"}
            ],
            None
        )
    ]
    
    mock_fetcher.get_article_content = AsyncMock(side_effect=[
        "Текст 1",
        "Текст 2"
    ])
    
    mock_parser.parse.side_effect = [
        {"clean_text": "Текст 1", "links": [], "categories": [], "templates": []},
        Exception("Parser error")
    ]
    
    stats = await service.run()
    
    assert stats["processed"] == 1
    assert stats["failed"] == 1
    assert mock_repository.upsert_article.call_count == 1


@pytest.mark.asyncio
async def test_etl_service_handles_empty_corpus(service, mock_fetcher, mock_parser, mock_repository):
    """Test that ETL service handles empty corpus gracefully."""
    mock_fetcher.fetch_batch.side_effect = [
        ([], None)
    ]
    
    stats = await service.run()
    
    assert stats["processed"] == 0
    assert stats["failed"] == 0
    mock_repository.upsert_article.assert_not_called()


@pytest.mark.asyncio
async def test_etl_service_constructs_source_url(service, mock_fetcher, mock_parser, mock_repository):
    """Test that ETL service constructs source_url from base_url and title."""
    mock_fetcher.fetch_batch.side_effect = [
        ([{"pageid": 1, "title": "Тестовая_статья"}], None)
    ]
    
    mock_fetcher.get_article_content = AsyncMock(return_value="Текст")
    mock_parser.parse.return_value = {
        "clean_text": "Текст", "links": [], "categories": [], "templates": []
    }
    
    await service.run()
    
    call_args = mock_repository.upsert_article.call_args
    assert call_args.kwargs["source_url"] == "https://lurkmore.to/wiki/Тестовая_статья"