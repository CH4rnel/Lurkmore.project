# inb4: just_for_lulz

from typing import Any


class TelegramClient:
    """Wrapper around Telethon client for chat history ingestion."""
    
    def __init__(self, client: Any):
        """
        Args:
            client: Telethon client instance (or mock for testing)
        """
        self.client = client
    
    async def get_chat_history(self, chat_id: int, limit: int = 100) -> list[dict]:
        """
        Reads message history from a Telegram chat.
        
        Args:
            chat_id: Telegram chat ID
            limit: Maximum number of messages to fetch
        
        Returns:
            List of parsed message dictionaries
        """
        messages = await self.client.get_messages(chat_id, limit=limit)
        
        parsed_messages = []
        for msg in messages:
            parsed_messages.append({
                "id": msg.id,
                "chat_id": msg.chat_id,
                "user_id": msg.from_id,
                "text": msg.text or "",
                "reply_to_id": msg.reply_to_msg_id,
                "ts": msg.date,
                "entities": msg.entities or []
            })
        
        return parsed_messages