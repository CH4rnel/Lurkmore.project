# inb4: just_for_lulz

import asyncio
import logging
from typing import Any, Optional


logger = logging.getLogger(__name__)


class MediaWikiFetcher:
    """
    Fetches articles from MediaWiki API with rate limiting and retry logic.
    """
    
    def __init__(
        self,
        base_url: str,
        http_client: Any,
        rate_limit: float = 1.0,
        max_retries: int = 3
    ):
        self.base_url = base_url.rstrip("/")
        self.http_client = http_client
        self.rate_limit = rate_limit
        self.max_retries = max_retries
        self._last_request_time = 0.0
    
    async def fetch_batch(
        self,
        continue_token: Optional[str] = None
    ) -> tuple[list[dict], Optional[str]]:
        """Fetches a batch of articles from MediaWiki API."""
        # Rate limiting
        current_time = asyncio.get_event_loop().time()
        time_since_last = current_time - self._last_request_time
        if time_since_last < self.rate_limit:
            await asyncio.sleep(self.rate_limit - time_since_last)
        
        params = {
            "action": "query",
            "list": "allpages",
            "aplimit": "50",
            "format": "json"
        }
        
        if continue_token:
            params["apcontinue"] = continue_token
        
        url = f"{self.base_url}/w/api.php"
        
        for attempt in range(self.max_retries):
            try:
                async with self.http_client.get(url, params=params) as response:
                    self._last_request_time = asyncio.get_event_loop().time()
                    
                    if response.status == 200:
                        data = await response.json()
                        articles = data.get("query", {}).get("allpages", [])
                        continue_data = data.get("continue", {})
                        next_token = continue_data.get("apcontinue")
                        
                        logger.info(f"Fetched {len(articles)} articles")
                        return articles, next_token
                    
                    elif response.status == 429:
                        retry_after = int(response.headers.get("Retry-After", 2 ** attempt))
                        logger.warning(f"Rate limited (429), retrying after {retry_after}s")
                        await asyncio.sleep(retry_after)
                        continue
                    
                    elif response.status >= 500:
                        retry_delay = 2 ** attempt
                        logger.warning(f"Server error ({response.status}), retrying after {retry_delay}s")
                        await asyncio.sleep(retry_delay)
                        continue
                    
                    else:
                        logger.error(f"HTTP error {response.status}")
                        return [], None
            
            except Exception as e:
                logger.error(f"Request failed: {e}")
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(2 ** attempt)
                    continue
                return [], None
        
        logger.error("Max retries exceeded")
        return [], None
    
    async def get_article_content(self, title: str) -> str:
        """
        Fetches raw wikitext content for a specific article.
        
        Args:
            title: Article title
        
        Returns:
            Raw wikitext content
        """
        # Rate limiting
        current_time = asyncio.get_event_loop().time()
        time_since_last = current_time - self._last_request_time
        if time_since_last < self.rate_limit:
            await asyncio.sleep(self.rate_limit - time_since_last)
        
        params = {
            "action": "parse",
            "page": title,
            "prop": "wikitext",
            "format": "json"
        }
        
        url = f"{self.base_url}/w/api.php"
        
        for attempt in range(self.max_retries):
            try:
                async with self.http_client.get(url, params=params) as response:
                    self._last_request_time = asyncio.get_event_loop().time()
                    
                    if response.status == 200:
                        data = await response.json()
                        wikitext = data.get("parse", {}).get("wikitext", {}).get("*", "")
                        return wikitext
                    
                    elif response.status == 429:
                        retry_after = int(response.headers.get("Retry-After", 2 ** attempt))
                        await asyncio.sleep(retry_after)
                        continue
                    
                    elif response.status >= 500:
                        retry_delay = 2 ** attempt
                        await asyncio.sleep(retry_delay)
                        continue
                    
                    else:
                        logger.error(f"HTTP error {response.status} for article {title}")
                        return ""
            
            except Exception as e:
                logger.error(f"Request failed for article {title}: {e}")
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(2 ** attempt)
                    continue
                return ""
        
        logger.error(f"Max retries exceeded for article {title}")
        return ""