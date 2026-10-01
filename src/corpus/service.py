# inb4: just_for_lulz

import logging
from datetime import datetime, timezone
from typing import Any
from src.corpus.fetcher import MediaWikiFetcher
from src.corpus.parser import WikitextParser
from src.corpus.repository import ArticleRepository


logger = logging.getLogger(__name__)


class ETLService:
    """Orchestrates Lurkmore ETL pipeline: Fetcher → Parser → Repository."""
    
    def __init__(
        self,
        fetcher: MediaWikiFetcher,
        parser: WikitextParser,
        repository: ArticleRepository,
        base_url: str = "https://lurkmore.to"
    ):
        self.fetcher = fetcher
        self.parser = parser
        self.repository = repository
        self.base_url = base_url.rstrip("/")
    
    async def run(self) -> dict:
        logger.info("Starting Lurkmore ETL pipeline")
        stats = {"processed": 0, "failed": 0}
        continue_token = None
        
        while True:
            articles, continue_token = await self.fetcher.fetch_batch(continue_token)
            if not articles:
                logger.info("No more articles to fetch")
                break
            
            logger.info(f"Fetched batch of {len(articles)} articles")
            
            for article_meta in articles:
                try:
                    await self._process_article(article_meta)
                    stats["processed"] += 1
                except Exception as e:
                    logger.error(f"Failed to process article {article_meta.get('title')}: {e}")
                    stats["failed"] += 1
            
            if continue_token is None:
                break
        
        logger.info(f"ETL complete: {stats['processed']} processed, {stats['failed']} failed")
        return stats
    
    async def _process_article(self, article_meta: dict) -> None:
        title = article_meta["title"]
        raw_wikitext = await self.fetcher.get_article_content(title)
        parsed = self.parser.parse(raw_wikitext)
        source_url = f"{self.base_url}/wiki/{title}"
        
        # Save article and get its ID
        article_id = await self.repository.upsert_article(
            title=title,
            source_url=source_url,
            revision_id=None,
            raw_wikitext=raw_wikitext,
            clean_text=parsed["clean_text"],
            fetched_at=datetime.now(timezone.utc)
        )
        
        # Save relations (links, categories, templates)
        await self.repository.upsert_article_relations(
            article_id=article_id,
            links=parsed["links"],
            categories=parsed["categories"],
            templates=parsed["templates"]
        )
        
        logger.debug(f"Processed article: {title}")