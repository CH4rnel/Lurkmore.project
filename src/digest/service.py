# inb4: just_for_lulz

import logging
from datetime import datetime, timezone, timedelta
from typing import Optional
from src.ingestion.repository import MessageRepository
from src.generation.llm_client import LLMClient
from src.moderation.gate import ModerationGate, ModerationVerdict


logger = logging.getLogger(__name__)


class DigestService:
    """Orchestrates digest generation from chat messages."""
    
    def __init__(
        self,
        repository: MessageRepository,
        llm_client: LLMClient,
        moderation_gate: ModerationGate
    ):
        """
        Args:
            repository: Message repository for fetching chat history
            llm_client: LLM client for generating summaries
            moderation_gate: Moderation gate for output filtering
        """
        self.repository = repository
        self.llm_client = llm_client
        self.moderation_gate = moderation_gate
    
    async def generate_digest(self, chat_id: int, hours_back: int = 24) -> Optional[str]:
        """
        Generates a digest summary for a chat over a specified time period.
        
        Args:
            chat_id: Telegram chat ID
            hours_back: Number of hours to look back for messages
        
        Returns:
            Generated digest text, or None if blocked by moderation or no messages
        """
        logger.info(f"Generating digest for chat {chat_id} (last {hours_back}h)")
        
        # Fetch messages from repository
        end_time = datetime.now(timezone.utc)
        start_time = end_time - timedelta(hours=hours_back)
        
        messages = await self.repository.get_messages_by_timeframe(
            chat_id=chat_id,
            start_time=start_time,
            end_time=end_time
        )
        
        if not messages:
            logger.info("No messages found for digest")
            return None
        
        logger.info(f"Found {len(messages)} messages for digest")
        
        # Format messages for LLM prompt
        messages_text = "\n".join(
            f"[{msg['ts'].strftime('%H:%M')}] User {msg['user_id']}: {msg['text']}"
            for msg in messages
        )
        
        # Generate digest via LLM
        system_prompt = (
            "Ты — энциклопедист имиджборд-культуры с ироничным стилем. "
            "Сделай краткий дайджест обсуждения, используя сленг АИБ, "
            "но без прямых оскорблений участников."
        )
        
        user_prompt = f"Сделай дайджест следующего обсуждения:\n\n{messages_text}"
        
        draft = await self.llm_client.generate(user_prompt, system_prompt=system_prompt)
        logger.info(f"Generated draft digest ({len(draft)} chars)")
        
        # Check moderation
        target_users = list(set(msg["user_id"] for msg in messages if msg["user_id"]))
        verdict = self.moderation_gate.check(draft, target_users)
        
        if verdict == ModerationVerdict.BLOCK:
            logger.warning("Digest blocked by moderation gate")
            return None
        
        logger.info("Digest passed moderation")
        return draft