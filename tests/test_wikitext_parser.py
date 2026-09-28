# inb4: just_for_lulz

import pytest
from src.corpus.parser import WikitextParser


@pytest.fixture
def parser():
    return WikitextParser()


def test_parse_simple_article(parser):
    """Test parsing a simple article with basic wikitext."""
    raw_wikitext = """== Заголовок ==
Это простой текст статьи.

=== Подзаголовок ===
Ещё немного текста.
"""
    
    result = parser.parse(raw_wikitext)
    
    assert "Заголовок" in result["clean_text"]
    assert "Это простой текст статьи" in result["clean_text"]
    assert "Подзаголовок" in result["clean_text"]


def test_parse_article_with_links(parser):
    """Test parsing article with internal links."""
    raw_wikitext = """См. также [[Другая статья]] и [[Ещё одна|текст ссылки]]."""
    
    result = parser.parse(raw_wikitext)
    
    assert "Другая статья" in result["clean_text"]
    assert "текст ссылки" in result["clean_text"]
    assert len(result["links"]) == 2
    assert result["links"][0]["target"] == "Другая статья"
    assert result["links"][1]["target"] == "Ещё одна"
    assert result["links"][1]["anchor"] == "текст ссылки"


def test_parse_article_with_categories(parser):
    """Test parsing article with categories."""
    raw_wikitext = """Текст статьи.

[[Категория:Мемы]]
[[Категория:Сленг]]
"""
    
    result = parser.parse(raw_wikitext)
    
    assert len(result["categories"]) == 2
    assert "Мемы" in result["categories"]
    assert "Сленг" in result["categories"]


def test_parse_article_with_templates(parser):
    """Test parsing article with templates."""
    raw_wikitext = """{{stub}}
Текст статьи.
{{cite web|url=http://example.com|title=Пример}}
"""
    
    result = parser.parse(raw_wikitext)
    
    assert len(result["templates"]) >= 1
    template_names = [t["name"] for t in result["templates"]]
    assert "stub" in template_names or "cite web" in template_names


def test_parse_article_with_infobox(parser):
    """Test parsing article with infobox template."""
    raw_wikitext = """{{Карточка
|название = Тест
|изображение = test.png
|подпись = Подпись к изображению
}}

Текст статьи.
"""
    
    result = parser.parse(raw_wikitext)
    
    # Infobox should be removed from clean_text
    assert "Карточка" not in result["clean_text"]
    assert "Текст статьи" in result["clean_text"]


def test_parse_article_with_external_links(parser):
    """Test parsing article with external links."""
    raw_wikitext = """См. [http://example.com внешний сайт]."""
    
    result = parser.parse(raw_wikitext)
    
    assert "внешний сайт" in result["clean_text"]


def test_parse_article_with_html_tags(parser):
    """Test parsing article with HTML tags."""
    raw_wikitext = """Текст с <b>жирным</b> и <i>курсивом</i>.

<ref>Сноска</ref>
"""
    
    result = parser.parse(raw_wikitext)
    
    assert "жирным" in result["clean_text"]
    assert "курсивом" in result["clean_text"]


def test_parse_article_with_nested_templates(parser):
    """Test parsing article with nested templates."""
    raw_wikitext = """{{lang|en|{{link|en|Example}}}}"""
    
    result = parser.parse(raw_wikitext)
    
    # Should handle nested templates without crashing
    assert result["clean_text"] is not None


def test_parse_empty_article(parser):
    """Test parsing empty article."""
    raw_wikitext = ""
    
    result = parser.parse(raw_wikitext)
    
    assert result["clean_text"] == ""
    assert result["links"] == []
    assert result["categories"] == []
    assert result["templates"] == []