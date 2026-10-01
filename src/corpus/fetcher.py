# inb4: just_for_lulz

import asyncio
import logging
from typing import Any, Optional
from datetime import datetime, timezone


logger = logging.getLogger(__name__)


class MediaWikiFetcher:
    """
    Fetches articles from MediaWiki API with rate limiting and retry logic.
    
    Implements MediaWiki Action API with continuation tokens.
    Implements Rate limiting (~1 req/sec) with exponential backoff on 429/5xx.
    """
    
    def __init__(
        self,
        base_url: str,
        http_client: Any,
        rate_limit: float = 1.0,
        max_retries: int = 3
    ):
        """
        Args:
            base_url: MediaWiki base URL (e.g., "https://lurkmore.to")
            http_client: aiohttp.ClientSession or mock
            rate_limit: Minimum seconds between requests
            max_retries: Maximum number of retries on 429/5xx
        """
        self.base_url = base_url.rstrip("/")
        self.http_client = http_client
        self.rate_limit = rate_limit
        self.max_retries = max_retries
        self._last_request_time = 0.0
    
    async def fetch_batch(
        self,
        continue_token: Optional[str] = None
    ) -> tuple[list[dict], Optional[str]]:
        """
        Fetches a batch of articles from MediaWiki API.
        
        Args:
            continue_token: Continuation token from previous batch (None for first batch)
        
        Returns:
            Tuple of (list of article dicts, next continuation token or None)
        """
        # Rate limiting
        current_time = asyncio.get_event_loop().time()
        time_since_last = current_time - self._last_request_time
        if time_since_last < self.rate_limit:
            await asyncio.sleep(self.rate_limit - time_since_last)
        
        # Build API URL
        params = {
            "action": "query",
            "list": "allpages",
            "aplimit": "50",
            "format": "json"
        }
        
        if continue_token:
            params["apcontinue"] = continue_token
        
        url = f"{self.base_url}/w/api.php"
        
        # Retry logic with exponential backoff
        for attempt in range(self.max_retries):
            try:
                async with self.http_client.get(url, params=params) as response:
                    self._last_request_time = asyncio.get_event_loop().time()
                    
                    if response.status == 200:
                        data = await response.json()
                        
                        # Extract articles
                        articles = data.get("query", {}).get("allpages", [])
                        
                        # Extract continuation token
                        continue_data = data.get("continue", {})
                        next_token = continue_data.get("apcontinue")
                        
                        logger.info(f"Fetched {len(articles)} articles")
                        return articles, next_token
                    
                    elif response.status == 429:
                        # Rate limited
                        retry_after = int(response.headers.get("Retry-After", 2 ** attempt))
                        logger.warning(f"Rate limited (429), retrying after {retry_after}s")
                        await asyncio.sleep(retry_after)
                        continue
                    
                    elif response.status >= 500:
                        # Server error
                        retry_delay = 2 ** attempt
                        logger.warning(f"Server error ({response.status}), retrying after {retry_delay}s")
                        await asyncio.sleep(retry_delay)
                        continue
                    
                    else:
                        # Other error
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