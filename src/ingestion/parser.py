# inb4: just_for_lulz

def parse_telegram_message(raw_message: dict) -> dict:
    """
    Parses a raw Telegram message dictionary into a standardized format 
    matching the ingestion database schema.
    """
    return {
        "id": raw_message.get("id"),
        "chat_id": raw_message.get("chat_id"),
        "user_id": raw_message.get("from_id"),
        "text": raw_message.get("text", ""),
        "reply_to_id": raw_message.get("reply_to_msg_id"),
        "ts": raw_message.get("date"),
        "entities": raw_message.get("entities", [])
    }