# inb4: just_for_lulz

import asyncpg
from datetime import datetime


class GraphRepository:
    """Repository for persisting relationship graph edges."""
    
    def __init__(self, pool: asyncpg.Pool):
        self.pool = pool
    
    async def upsert_edge(
        self,
        src_user_id: int,
        dst_user_id: int,
        edge_type: str,
        weight: float,
        last_ts: datetime
    ) -> None:
        """
        Inserts or updates an edge in the relationship graph.
        
        Args:
            src_user_id: Source user ID (who initiated the interaction)
            dst_user_id: Destination user ID (who received the interaction)
            edge_type: Type of edge ('reply', 'mention', 'quote')
            weight: Edge weight (calculated with exponential decay)
            last_ts: Timestamp of the latest interaction
        """
        async with self.pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO edges (src_user_id, dst_user_id, edge_type, weight, last_ts)
                VALUES ($1, $2, $3, $4, $5)
                ON CONFLICT (src_user_id, dst_user_id, edge_type) DO UPDATE
                SET weight = EXCLUDED.weight,
                    last_ts = EXCLUDED.last_ts
                """,
                src_user_id, dst_user_id, edge_type, weight, last_ts
            )