# inb4: just_for_lulz

from enum import Enum
from typing import Optional


class ModerationVerdict(Enum):
    """Result of moderation check."""
    ALLOW = "allow"
    BLOCK = "block"


class ModerationGate:
    """
    Moderation gate that filters output before sending to Telegram.
    
    Distinguishes between:
    - Encyclopedic/ironic description of slang (ALLOW)
    - Direct insults/discrimination targeting specific users (BLOCK)
    """
    
    def check(self, draft: str, target_users: list[int]) -> ModerationVerdict:
        """
        Checks if draft message should be allowed or blocked.
        
        Args:
            draft: Draft message text
            target_users: List of user IDs mentioned or targeted in the message
        
        Returns:
            ModerationVerdict.ALLOW if message is acceptable
            ModerationVerdict.BLOCK if message targets users with insults/discrimination
        """
        if not target_users:
            return ModerationVerdict.ALLOW
        
        draft_lower = draft.lower()
        
        # Check for direct targeting with insult keywords (including morphological variants)
        insult_keywords = [
            # Singular forms
            "дебил", "идиот", "тупой", "уёбок", "ублюдок",
            "дурак", "кретин", "мудак", "придурок",
            # Plural/adjective forms
            "тупые", "тупая", "тупое", "тупого", "тупому", "тупым", "тупых",
            "дебилы", "идиоты", "дураки", "кретины", "мудаки", "придурки",
            # Derogatory adjectives
            "бесполезные", "бесполезный", "бесполезная", "бесполезное",
            "ненужные", "ненужный", "ненужная", "ненужное"
        ]
        
        has_insult = any(keyword in draft_lower for keyword in insult_keywords)
        
        # Check for discrimination patterns (generalized attacks on groups)
        discrimination_patterns = [
            "все из", "все эти", "все вы", "каждый из",
            "группа", "толпа", "банда"
        ]
        
        has_discrimination_pattern = any(
            pattern in draft_lower for pattern in discrimination_patterns
        )
        
        # Block if: (insult + target users) OR (discrimination pattern + insult + target users)
        if has_insult and target_users:
            return ModerationVerdict.BLOCK
        
        if has_discrimination_pattern and has_insult and target_users:
            return ModerationVerdict.BLOCK
        
        return ModerationVerdict.ALLOW