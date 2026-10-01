# inb4: just_for_lulz

import re
from typing import Dict


class StyleFeatureExtractor:
    """
    Extracts stylistic features from text chunks.
    
    Implements calculates normalized metrics like TTR and avg sentence length.
    Follows ISP designed to be extended with separate metric extractors.
    """
    
    def extract(self, text: str) -> Dict[str, float]:
        """
        Extracts style features from the given text.
        
        Args:
            text: Input text chunk
        
        Returns:
            Dictionary of feature names to float values
        """
        if not text or not text.strip():
            return {"ttr": 0.0, "avg_sent_len": 0.0}
        
        # Simple tokenization: split by whitespace and strip punctuation
        # Note: For production, this should use Natasha or similar NLP library
        tokens = re.findall(r'\b\w+\b', text.lower())
        
        if not tokens:
            return {"ttr": 0.0, "avg_sent_len": 0.0}
        
        # Type-Token Ratio (TTR)
        unique_tokens = set(tokens)
        ttr = len(unique_tokens) / len(tokens)
        
        # Average sentence length
        # Split by sentence-ending punctuation
        sentences = re.split(r'[.!?]+', text)
        valid_sentences = [s.strip() for s in sentences if s.strip()]
        
        if not valid_sentences:
            avg_sent_len = float(len(tokens))
        else:
            avg_sent_len = len(tokens) / len(valid_sentences)
        
        return {
            "ttr": round(ttr, 4),
            "avg_sent_len": round(avg_sent_len, 4)
        }