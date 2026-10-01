# inb4: just_for_lulz

import pytest
from src.retrieval.style_extractor import StyleFeatureExtractor


@pytest.fixture
def extractor():
    return StyleFeatureExtractor()


def test_extract_ttr(extractor):
    """Test Type-Token Ratio calculation."""
    # "Слово слово слово другое" -> 4 токена, 2 уникальных (слово, другое)
    # TTR = 2 / 4 = 0.5
    text = "Слово слово слово другое."
    features = extractor.extract(text)
    assert "ttr" in features
    assert features["ttr"] == pytest.approx(0.5, rel=1e-2)


def test_extract_avg_sentence_length(extractor):
    """Test average sentence length calculation."""
    # "Один два три. Четыре пять." -> 2 предложения, 5 токенов
    # Avg len = 5 / 2 = 2.5
    text = "Один два три. Четыре пять."
    features = extractor.extract(text)
    assert "avg_sent_len" in features
    assert features["avg_sent_len"] == pytest.approx(2.5, rel=1e-2)


def test_extract_empty_text(extractor):
    """Test that empty text returns zeroed features."""
    features = extractor.extract("")
    assert features["ttr"] == 0.0
    assert features["avg_sent_len"] == 0.0


def test_extract_punctuation_only(extractor):
    """Test that text with only punctuation returns zeroed features."""
    features = extractor.extract("... !!!")
    assert features["ttr"] == 0.0
    assert features["avg_sent_len"] == 0.0