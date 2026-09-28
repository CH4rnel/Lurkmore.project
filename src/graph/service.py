# inb4: just_for_lulz

import logging
from datetime import datetime, timezone, timedelta
from src.ingestion.repository import MessageRepository
from src.graph.calculator import RelationshipCalculator
from src.graph.repository import GraphRepository


logger = logging.getLogger(__name__)


class GraphService:
    """Orchestrates relationship graph construction from chat messages."""
    
    def __init__(
        self,
        repository: MessageRepository,
        calculator: RelationshipCalculator,
        graph_repository: GraphRepository
    ):
        """
        Args:
            repository: Message repository for fetching chat history
            calculator: Relationship calculator for computing edge weights
            graph_repository: Graph repository for persisting edges
        """
        self.repository = repository
        self.calculator = calculator
        self.graph_repository = graph_repository
    
    async def build_graph(
        self,
        chat_id: int,
        hours_back: int = 24,
        now: datetime = None
    ) -> None:
        """
        Builds relationship graph from recent chat messages.
        
        Args:
            chat_id: Telegram chat ID
            hours_back: Number of hours to look back for messages
            now: Current timestamp for decay calculation (defaults to UTC now)
        """
        if now is None:
            now = datetime.now(timezone.utc)
        
        logger.info(f"Building graph for chat {chat_id} (last {hours_back}h)")
        
        # Fetch messages from repository
        end_time = now
        start_time = now - timedelta(hours=hours_back)
        
        messages = await self.repository.get_messages_by_timeframe(
            chat_id=chat_id,
            start_time=start_time,
            end_time=end_time
        )
        
        if not messages:
            logger.info("No messages found for graph building")
            return
        
        logger.info(f"Found {len(messages)} messages for graph building")
        
        # Calculate edge weights
        weights = self.calculator.calculate_weights(messages, now)
        logger.info(f"Calculated {len(weights)} edges")
        
        # Build message ID -> timestamp mapping for last_ts
        msg_id_to_ts = {msg["id"]: msg["ts"] for msg in messages}
        
        # Persist edges
        for (src_user, dst_user), weight in weights.items():
            # Find the latest message timestamp for this edge
            # (simplified: use the latest reply timestamp)
            latest_ts = max(
                (msg["ts"] for msg in messages 
                 if msg["user_id"] == src_user and msg.get("reply_to_id") is not None),
                default=now
            )
            
            await self.graph_repository.upsert_edge(
                src_user_id=src_user,
                dst_user_id=dst_user,
                edge_type="reply",
                weight=weight,
                last_ts=latest_ts
            )
        
        logger.info(f"Graph building complete: {len(weights)} edges persisted")