# inb4: just_for_lulz

from datetime import datetime


def parse_telegram_message(raw_message: dict) -> dict:
    """
    Parses a raw Telegram message dictionary into a standardized format 
    matching the ingestion database schema.
    """
    # Convert date to datetime if it's a string
    ts = raw_message.get("date")
    if isinstance(ts, str):
        # Handle ISO 8601 format with 'Z' suffix
        ts = ts.replace("Z", "+00:00")
        ts = datetime.fromisoformat(ts)
    
    return {
        "id": raw_message.get("id"),
        "chat_id": raw_message.get("chat_id"),
        "user_id": raw_message.get("from_id"),
        "text": raw_message.get("text", ""),
        "reply_to_id": raw_message.get("reply_to_msg_id"),
        "ts": ts,
        "entities": raw_message.get("entities", [])
    }