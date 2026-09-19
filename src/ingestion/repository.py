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
        """
        Inserts or updates a user record.
        
        Args:
            user_id: Telegram user ID
            username: Telegram username (optional)
            display_name: Display name (optional)
        """
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
        """
        Inserts a message record.
        
        Args:
            message_id: Telegram message ID
            chat_id: Telegram chat ID
            user_id: Author user ID
            text: Message text
            ts: Timestamp as datetime object
            reply_to_id: ID of replied message (optional)
            entities: Message entities (mentions, links, etc.)
        """
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