# inb4: just_for_lulz

import logging
from src.ingestion.telegram_client import TelegramClient
from src.ingestion.repository import MessageRepository


logger = logging.getLogger(__name__)


class IngestionService:
    """Orchestrates chat history ingestion from Telegram to PostgreSQL."""
    
    def __init__(self, telegram_client: TelegramClient, repository: MessageRepository):
        """
        Args:
            telegram_client: Telegram client wrapper
            repository: Message repository for persistence
        """
        self.telegram_client = telegram_client
        self.repository = repository
    
    async def ingest_chat(self, chat_id: int, limit: int = 100) -> int:
        """
        Ingests message history from a Telegram chat into the database.
        
        Args:
            chat_id: Telegram chat ID to ingest
            limit: Maximum number of messages to fetch
        
        Returns:
            Number of messages successfully ingested
        """
        logger.info(f"Starting ingestion for chat {chat_id} (limit={limit})")
        
        # Fetch messages from Telegram
        messages = await self.telegram_client.get_chat_history(chat_id, limit)
        logger.info(f"Fetched {len(messages)} messages from Telegram")
        
        # Persist to database
        ingested_count = 0
        for msg in messages:
            try:
                # Upsert user first
                await self.repository.upsert_user(
                    user_id=msg["user_id"],
                    username=None,  # TODO: extract from message.sender
                    display_name=None
                )
                
                # Insert message
                await self.repository.insert_message(
                    message_id=msg["id"],
                    chat_id=msg["chat_id"],
                    user_id=msg["user_id"],
                    text=msg["text"],
                    ts=msg["ts"],
                    reply_to_id=msg["reply_to_id"],
                    entities=msg["entities"]
                )
                ingested_count += 1
                
            except Exception as e:
                logger.error(f"Failed to ingest message {msg['id']}: {e}")
                continue
        
        logger.info(f"Successfully ingested {ingested_count}/{len(messages)} messages")
        return ingested_count