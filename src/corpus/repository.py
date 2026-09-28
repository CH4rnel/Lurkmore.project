# inb4: just_for_lulz

import asyncpg
from datetime import datetime
from typing import Optional


class ArticleRepository:
    """Repository for persisting Lurkmore articles."""
    
    def __init__(self, pool: asyncpg.Pool):
        self.pool = pool
    
    async def upsert_article(
        self,
        title: str,
        source_url: str,
        revision_id: Optional[int],
        raw_wikitext: Optional[str],
        clean_text: Optional[str],
        fetched_at: datetime
    ) -> None:
        """
        Inserts or updates an article.
        
        Args:
            title: Article title (unique identifier)
            source_url: Original URL of the article
            revision_id: MediaWiki revision ID
            raw_wikitext: Raw wikitext content
            clean_text: Parsed and cleaned text
            fetched_at: Timestamp of fetch
        """
        async with self.pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO articles (title, source_url, revision_id, raw_wikitext, clean_text, fetched_at)
                VALUES ($1, $2, $3, $4, $5, $6)
                ON CONFLICT (title) DO UPDATE
                SET source_url = EXCLUDED.source_url,
                    revision_id = EXCLUDED.revision_id,
                    raw_wikitext = EXCLUDED.raw_wikitext,
                    clean_text = EXCLUDED.clean_text,
                    fetched_at = EXCLUDED.fetched_at
                """,
                title, source_url, revision_id, raw_wikitext, clean_text, fetched_at
            )
    
    async def load_article_by_title(self, title: str) -> Optional[dict]:
        """
        Loads an article by title.
        
        Args:
            title: Article title
        
        Returns:
            Article dictionary or None if not found
        """
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT * FROM articles WHERE title = $1",
                title
            )
            
            if row is None:
                return None
            
            return dict(row)