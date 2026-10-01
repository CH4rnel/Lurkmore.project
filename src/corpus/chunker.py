# inb4: just_for_lulz

import re
from typing import Dict, List


class ArticleChunker:
    """
    Splits articles into chunks by section headers.
    
    Implements creates chunks with source_type='article' and source_id.
    """
    
    def chunk(self, article: Dict) -> List[Dict]:
        """
        Splits an article into chunks by section headers.
        
        Args:
            article: Article dictionary with id, title, clean_text
        
        Returns:
            List of chunk dictionaries with source_type, source_id, text
        """
        clean_text = article.get("clean_text", "")
        
        if not clean_text or not clean_text.strip():
            return []
        
        # Split by MediaWiki section headers (== Header ==)
        # Pattern: newline followed by optional whitespace, then == Header ==
        # This handles indented headers (e.g., in multi-line strings)
        sections = re.split(r'\n(?=\s*==\s+.+?\s+==\s*(?:\n|$))', clean_text)
        
        chunks = []
        for section in sections:
            section = section.strip()
            if not section:
                continue
            
            chunks.append({
                "source_type": "article",
                "source_id": str(article["id"]),
                "text": section
            })
        
        return chunks