# inb4: just_for_lulz

import pytest
from src.generation.llm_client import LLMClient, MockLLMClient


@pytest.fixture
def llm_client():
    return MockLLMClient()


@pytest.mark.asyncio
async def test_llm_client_generates_response(llm_client):
    """Test that LLM client generates a response for a given prompt."""
    prompt = "Сделай дайджест чата за последние 24 часа"
    response = await llm_client.generate(prompt)
    assert isinstance(response, str)
    assert len(response) > 0


@pytest.mark.asyncio
async def test_llm_client_handles_system_prompt(llm_client):
    """Test that LLM client accepts system prompt for style control."""
    system_prompt = "Ты — энциклопедист имиджборд-культуры с ироничным стилем"
    user_prompt = "Объясни термин 'кратон'"
    response = await llm_client.generate(user_prompt, system_prompt=system_prompt)
    assert isinstance(response, str)
    assert len(response) > 0


@pytest.mark.asyncio
async def test_llm_client_handles_empty_prompt(llm_client):
    """Test that LLM client handles empty prompt gracefully."""
    response = await llm_client.generate("")
    assert isinstance(response, str)


@pytest.mark.asyncio
async def test_mock_llm_client_returns_deterministic_response(llm_client):
    """Test that mock client returns predictable response for testing."""
    prompt = "test prompt"
    response1 = await llm_client.generate(prompt)
    response2 = await llm_client.generate(prompt)
    assert response1 == response2