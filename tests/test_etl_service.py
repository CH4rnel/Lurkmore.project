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
async def test_etl_service_saves_relations(service, mock_fetcher, mock_parser, mock_repository):
    """Test that ETL service saves parsed links, categories, and templates."""
    mock_fetcher.fetch_batch.side_effect = [
        ([{"pageid": 1, "title": "Статья1"}], None)
    ]
    mock_fetcher.get_article_content = AsyncMock(return_value="Текст")
    
    parsed_data = {
        "clean_text": "Текст",
        "links": [{"target": "Цель", "anchor": "ссылка"}],
        "categories": ["Тест"],
        "templates": [{"name": "stub", "params": {}}]
    }
    mock_parser.parse.return_value = parsed_data
    mock_repository.upsert_article.return_value = 123
    
    await service.run()
    
    mock_repository.upsert_article.assert_called_once()
    
    mock_repository.upsert_article_relations.assert_called_once_with(
        article_id=123,
        links=parsed_data["links"],
        categories=parsed_data["categories"],
        templates=parsed_data["templates"]
    )