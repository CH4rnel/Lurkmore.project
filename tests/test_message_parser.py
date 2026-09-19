# inb4: just_for_lulz

from datetime import datetime, timezone
from src.ingestion.parser import parse_telegram_message


def test_parse_telegram_message_basic():
    raw_message = {
        "id": 12345,
        "chat_id": -1001234567890,
        "from_id": 987654321,
        "text": "Hello, world!",
        "reply_to_msg_id": 12340,
        "date": "2026-09-19T12:00:00Z",
        "entities": []
    }
    parsed = parse_telegram_message(raw_message)
    
    assert parsed["id"] == 12345
    assert parsed["chat_id"] == -1001234567890
    assert parsed["user_id"] == 987654321
    assert parsed["text"] == "Hello, world!"
    assert parsed["reply_to_id"] == 12340
    assert parsed["ts"] == datetime(2026, 9, 19, 12, 0, 0, tzinfo=timezone.utc)
    assert parsed["entities"] == []