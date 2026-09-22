# inb4: just_for_lulz

from datetime import datetime, timezone
from src.ingestion.parser import parse_telegram_message


def test_parse_reply_chain():
    """Test parsing a message that is a reply to another message."""
    raw = {
        "id": 200,
        "chat_id": -100123,
        "from_id": 111,
        "text": "согласен",
        "reply_to_msg_id": 199,
        "date": datetime(2026, 9, 20, 10, 0, 0, tzinfo=timezone.utc),
        "entities": []
    }
    parsed = parse_telegram_message(raw)
    assert parsed["reply_to_id"] == 199
    assert parsed["id"] == 200


def test_parse_deep_reply_chain():
    """Test that reply_to_id only points to direct parent, not chain root."""
    raw = {
        "id": 300,
        "chat_id": -100123,
        "from_id": 222,
        "text": "а я нет",
        "reply_to_msg_id": 200,
        "date": datetime(2026, 9, 20, 10, 5, 0, tzinfo=timezone.utc),
        "entities": []
    }
    parsed = parse_telegram_message(raw)
    assert parsed["reply_to_id"] == 200


def test_parse_message_without_reply():
    """Test that non-reply messages have reply_to_id as None."""
    raw = {
        "id": 100,
        "chat_id": -100123,
        "from_id": 333,
        "text": "новая тема",
        "reply_to_msg_id": None,
        "date": datetime(2026, 9, 20, 9, 0, 0, tzinfo=timezone.utc),
        "entities": []
    }
    parsed = parse_telegram_message(raw)
    assert parsed["reply_to_id"] is None