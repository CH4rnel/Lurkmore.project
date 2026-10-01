# inb4: just_for_lulz

import pytest
from src.corpus.chunker import ArticleChunker


@pytest.fixture
def chunker():
    return ArticleChunker()


def test_chunk_simple_article(chunker):
    """Test chunking a simple article with one section."""
    article = {
        "id": 1,
        "title": "Тестовая статья",
        "clean_text": """== Заголовок ==
Первый параграф текста.

Второй параграф текста.
"""
    }
    
    chunks = chunker.chunk(article)
    
    assert len(chunks) == 1
    assert chunks[0]["source_id"] == "1"
    assert "Заголовок" in chunks[0]["text"]
    assert "Первый параграф" in chunks[0]["text"]


def test_chunk_article_with_multiple_sections(chunker):
    """Test chunking article with multiple sections."""
    article = {
        "id": 2,
        "title": "Многосекционная статья",
        "clean_text": """== Секция 1 ==
Текст секции 1.

== Секция 2 ==
Текст секции 2.

== Секция 3 ==
Текст секции 3.
"""
    }
    
    chunks = chunker.chunk(article)
    
    assert len(chunks) == 3
    assert "Секция 1" in chunks[0]["text"]
    assert "Секция 2" in chunks[1]["text"]
    assert "Секция 3" in chunks[2]["text"]


def test_chunk_article_without_headers(chunker):
    """Test chunking article without section headers."""
    article = {
        "id": 3,
        "title": "Статья без заголовков",
        "clean_text": """Просто текст без заголовков.
Много параграфов.
"""
    }
    
    chunks = chunker.chunk(article)
    
    # Should return single chunk with full text
    assert len(chunks) == 1
    assert "Просто текст" in chunks[0]["text"]


def test_chunk_empty_article(chunker):
    """Test chunking empty article."""
    article = {
        "id": 4,
        "title": "Пустая статья",
        "clean_text": ""
    }
    
    chunks = chunker.chunk(article)
    
    assert len(chunks) == 0


def test_chunk_preserves_source_metadata(chunker):
    """Test that chunks preserve source article metadata."""
    article = {
        "id": 5,
        "title": "Метаданные",
        "clean_text": "== Заголовок ==\nТекст."
    }
    
    chunks = chunker.chunk(article)
    
    assert chunks[0]["source_type"] == "article"
    assert chunks[0]["source_id"] == "5"