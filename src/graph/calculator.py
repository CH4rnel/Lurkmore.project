# inb4: just_for_lulz

import math
from datetime import datetime, timezone
from typing import Dict, Tuple


class RelationshipCalculator:
    """
    Calculates relationship weights between users based on reply interactions.
    
    Uses exponential decay formula: w(u,v) = Σ exp(-(t_now - t_msg) / τ)
    where τ is the decay parameter (tau_hours).
    """
    
    def __init__(self, tau_hours: float = 24.0):
        """
        Args:
            tau_hours: Decay parameter in hours. Controls how quickly old interactions lose weight.
        """
        self.tau_hours = tau_hours
    
    def calculate_weights(
        self,
        messages: list[dict],
        now: datetime
    ) -> Dict[Tuple[int, int], float]:
        """
        Calculates edge weights from reply interactions.
        
        Args:
            messages: List of message dictionaries with id, user_id, reply_to_id, ts
            now: Current timestamp for decay calculation
        
        Returns:
            Dictionary mapping (from_user, to_user) -> weight
        """
        # Build message ID -> user_id mapping
        msg_to_user = {msg["id"]: msg["user_id"] for msg in messages}
        
        weights: Dict[Tuple[int, int], float] = {}
        
        for msg in messages:
            reply_to_id = msg.get("reply_to_id")
            if reply_to_id is None:
                continue
            
            # Find parent message author
            parent_user_id = msg_to_user.get(reply_to_id)
            if parent_user_id is None:
                continue
            
            from_user = msg["user_id"]
            to_user = parent_user_id
            
            # Skip self-replies
            if from_user == to_user:
                continue
            
            # Calculate time delta in hours
            msg_time = msg["ts"]
            if msg_time.tzinfo is None:
                msg_time = msg_time.replace(tzinfo=timezone.utc)
            
            if now.tzinfo is None:
                now = now.replace(tzinfo=timezone.utc)
            
            delta_hours = (now - msg_time).total_seconds() / 3600.0
            
            # Exponential decay: exp(-Δt / τ)
            weight = math.exp(-delta_hours / self.tau_hours)
            
            # Accumulate weights for same edge
            edge = (from_user, to_user)
            weights[edge] = weights.get(edge, 0.0) + weight
        
        return weights