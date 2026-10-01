# inb4: just_for_lulz

import asyncpg
import json
from datetime import datetime
from typing import Optional


class ArticleRepository:
    """Repository for persisting Lurkmore articles and their relations."""
    
    def __init__(self, pool: asyncpg.Pool, base_url: str = "https://lurkmore.to"):
        self.pool = pool
        self.base_url = base_url.rstrip("/")
    
    async def upsert_article(
        self,
        title: str,
        source_url: str,
        revision_id: Optional[int],
        raw_wikitext: Optional[str],
        clean_text: Optional[str],
        fetched_at: datetime
    ) -> int:
        """Inserts or updates an article and returns its ID."""
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                INSERT INTO articles (title, source_url, revision_id, raw_wikitext, clean_text, fetched_at)
                VALUES ($1, $2, $3, $4, $5, $6)
                ON CONFLICT (title) DO UPDATE
                SET source_url = EXCLUDED.source_url,
                    revision_id = EXCLUDED.revision_id,
                    raw_wikitext = EXCLUDED.raw_wikitext,
                    clean_text = EXCLUDED.clean_text,
                    fetched_at = EXCLUDED.fetched_at
                RETURNING id
                """,
                title, source_url, revision_id, raw_wikitext, clean_text, fetched_at
            )
            return row["id"]
    
    async def upsert_article_relations(
        self,
        article_id: int,
        links: list[dict],
        categories: list[str],
        templates: list[dict]
    ) -> None:
        """Inserts categories, templates, and links for a given article."""
        async with self.pool.acquire() as conn:
            # 1. Categories
            for cat_name in categories:
                cat_row = await conn.fetchrow(
                    "INSERT INTO categories (name) VALUES ($1) ON CONFLICT (name) DO NOTHING RETURNING id",
                    cat_name
                )
                cat_id = cat_row["id"] if cat_row else await conn.fetchval(
                    "SELECT id FROM categories WHERE name = $1", cat_name
                )
                await conn.execute(
                    "INSERT INTO article_categories (article_id, category_id) VALUES ($1, $2) ON CONFLICT DO NOTHING",
                    article_id, cat_id
                )
            
            # 2. Templates
            for tmpl in templates:
                tmpl_name = tmpl["name"]

                params_json = json.dumps(tmpl.get("params", {}))
                
                tmpl_row = await conn.fetchrow(
                    "INSERT INTO templates (name) VALUES ($1) ON CONFLICT (name) DO NOTHING RETURNING id",
                    tmpl_name
                )
                tmpl_id = tmpl_row["id"] if tmpl_row else await conn.fetchval(
                    "SELECT id FROM templates WHERE name = $1", tmpl_name
                )
                
                await conn.execute(
                    """
                    INSERT INTO article_templates (article_id, template_id, params) 
                    VALUES ($1, $2, $3::jsonb) 
                    ON CONFLICT (article_id, template_id) DO UPDATE SET params = EXCLUDED.params
                    """,
                    article_id, tmpl_id, params_json
                )
            
            # 3. Links
            for link in links:
                target_title = link["target"]
                anchor = link.get("anchor", target_title)
                
                dst_id = await conn.fetchval("SELECT id FROM articles WHERE title = $1", target_title)
                if dst_id is None:
                    stub_url = f"{self.base_url}/wiki/{target_title}"
                    dst_id = await conn.fetchval(
                        "INSERT INTO articles (title, source_url, fetched_at) VALUES ($1, $2, NOW()) ON CONFLICT (title) DO NOTHING RETURNING id",
                        target_title, stub_url
                    )
                    if dst_id is None:
                        dst_id = await conn.fetchval("SELECT id FROM articles WHERE title = $1", target_title)
                
                if dst_id is not None:
                    await conn.execute(
                        "INSERT INTO links (src_id, dst_id, anchor) VALUES ($1, $2, $3) ON CONFLICT DO NOTHING",
                        article_id, dst_id, anchor
                    )