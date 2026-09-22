# inb4: just_for_lulz

from typing import Protocol, Optional


class LLMClient(Protocol):
    """Abstract interface for LLM interaction."""
    
    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None
    ) -> str:
        """
        Generates a response from the LLM.
        
        Args:
            prompt: User prompt / instruction
            system_prompt: Optional system prompt for style/context control
        
        Returns:
            Generated text response
        """
        ...


class MockLLMClient:
    """
    Mock LLM client for testing without real API calls.
    
    Returns deterministic responses based on input for predictable testing.
    """
    
    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None
    ) -> str:
        """
        Generates a mock response for testing.
        
        Args:
            prompt: User prompt
            system_prompt: Optional system prompt (ignored in mock)
        
        Returns:
            Deterministic mock response
        """
        if not prompt:
            return "[Пустой запрос]"
        
        # Simple deterministic response for testing
        return f"[Mock LLM Response] Получен запрос: {prompt[:50]}..."