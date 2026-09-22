# inb4: just_for_lulz

import logging
from src.ingestion.telegram_client import TelegramClient
from src.ingestion.repository import MessageRepository


logger = logging.getLogger(__name__)


class IngestionService:
    """Orchestrates chat history ingestion from Telegram to PostgreSQL."""

    def __init__(self, telegram_client: TelegramClient, repository: MessageRepository):
        self.telegram_client = telegram_client
        self.repository = repository

    async def ingest_chat(
        self,
        chat_id: int,
        limit: int = 100,
        batch_size: int = 100
    ) -> int:
        """
        Ingests message history with automatic pagination.

        Args:
            chat_id: Telegram chat ID to ingest
            limit: Total maximum number of messages to fetch
            batch_size: Number of messages per API call

        Returns:
            Number of messages successfully ingested
        """
        logger.info(f"Starting ingestion for chat {chat_id} (limit={limit})")

        ingested_count = 0
        offset_id = None
        remaining = limit

        while remaining > 0:
            fetch_count = min(batch_size, remaining)
            messages = await self.telegram_client.get_chat_history(
                chat_id, limit=fetch_count, offset_id=offset_id
            )

            if not messages:
                logger.info("No more messages to fetch")
                break

            for msg in messages:
                if msg["user_id"] is None:
                    logger.debug(f"Skipping service message {msg['id']}")
                    continue

                try:
                    await self.repository.upsert_user(
                        user_id=msg["user_id"],
                        username=None,
                        display_name=None
                    )
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

            offset_id = messages[-1]["id"]
            remaining -= len(messages)
            logger.info(f"Progress: {ingested_count} ingested, offset={offset_id}")

        logger.info(f"Ingestion complete: {ingested_count} messages")
        return ingested_count