# inb4: just_for_lulz

import asyncpg
import json
from datetime import datetime
from typing import Optional


class MessageRepository:
    """Repository for persisting Telegram messages and users."""
    
    def __init__(self, pool: asyncpg.Pool):
        self.pool = pool
    
    async def upsert_user(self, user_id: int, username: Optional[str], display_name: Optional[str]) -> None:
        """Inserts or updates a user record."""
        async with self.pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO users (id, username, display_name)
                VALUES ($1, $2, $3)
                ON CONFLICT (id) DO UPDATE
                SET username = EXCLUDED.username,
                    display_name = EXCLUDED.display_name
                """,
                user_id, username, display_name
            )
    
    async def insert_message(
        self,
        message_id: int,
        chat_id: int,
        user_id: int,
        text: str,
        ts: datetime,
        reply_to_id: Optional[int] = None,
        entities: Optional[list] = None
    ) -> None:
        """Inserts a message record."""
        entities_json = json.dumps(entities) if entities else None
        
        async with self.pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO messages (id, chat_id, user_id, reply_to_id, text, entities, ts)
                VALUES ($1, $2, $3, $4, $5, $6, $7)
                ON CONFLICT (id) DO NOTHING
                """,
                message_id, chat_id, user_id, reply_to_id, text, entities_json, ts
            )
    
    async def get_messages_by_timeframe(
        self,
        chat_id: int,
        start_time: datetime,
        end_time: datetime
    ) -> list[dict]:
        """
        Fetches messages within a time range.
        
        Args:
            chat_id: Telegram chat ID
            start_time: Start of time range
            end_time: End of time range
        
        Returns:
            List of message dictionaries
        """
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT id, chat_id, user_id, text, ts, reply_to_id, entities
                FROM messages
                WHERE chat_id = $1 AND ts >= $2 AND ts <= $3
                ORDER BY ts ASC
                """,
                chat_id, start_time, end_time
            )
            
            return [
                {
                    "id": row["id"],
                    "chat_id": row["chat_id"],
                    "user_id": row["user_id"],
                    "text": row["text"],
                    "ts": row["ts"],
                    "reply_to_id": row["reply_to_id"],
                    "entities": json.loads(row["entities"]) if row["entities"] else []
                }
                for row in rows
            ]