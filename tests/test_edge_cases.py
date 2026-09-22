# inb4: just_for_lulz

from datetime import datetime, timezone
from src.ingestion.parser import parse_telegram_message


def test_parse_sticker_message():
    """Sticker messages have no text — should default to empty string."""
    raw = {
        "id": 400,
        "chat_id": -100123,
        "from_id": 111,
        "text": None,
        "reply_to_msg_id": None,
        "date": datetime(2026, 9, 20, 11, 0, 0, tzinfo=timezone.utc),
        "entities": []
    }
    parsed = parse_telegram_message(raw)
    assert parsed["text"] == ""


def test_parse_service_message_no_sender():
    """Service messages (join/leave) may have no from_id."""
    raw = {
        "id": 500,
        "chat_id": -100123,
        "from_id": None,
        "text": "User joined the group",
        "reply_to_msg_id": None,
        "date": datetime(2026, 9, 20, 12, 0, 0, tzinfo=timezone.utc),
        "entities": []
    }
    parsed = parse_telegram_message(raw)
    assert parsed["user_id"] is None


def test_parse_empty_entities():
    """Messages without entities should have empty list."""
    raw = {
        "id": 600,
        "chat_id": -100123,
        "from_id": 111,
        "text": "plain text",
        "reply_to_msg_id": None,
        "date": datetime(2026, 9, 20, 13, 0, 0, tzinfo=timezone.utc),
    }
    parsed = parse_telegram_message(raw)
    assert parsed["entities"] == []


def test_parse_explicit_none_entities():
    """Messages with explicit None entities should default to empty list."""
    raw = {
        "id": 700,
        "chat_id": -100123,
        "from_id": 111,
        "text": "plain text",
        "reply_to_msg_id": None,
        "date": datetime(2026, 9, 20, 14, 0, 0, tzinfo=timezone.utc),
        "entities": None
    }
    parsed = parse_telegram_message(raw)
    assert parsed["entities"] == []