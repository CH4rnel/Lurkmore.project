# inb4: just_for_lulz

import pytest
from src.moderation.gate import ModerationGate, ModerationVerdict


@pytest.fixture
def gate():
    return ModerationGate()


def test_moderation_allows_encyclopedic_description(gate):
    """Encyclopedic description of slang terms should be allowed."""
    draft = "Термин 'кратон' происходит от имиджборд-культуры и означает..."
    verdict = gate.check(draft, target_users=[])
    assert verdict == ModerationVerdict.ALLOW


def test_moderation_allows_meta_humor(gate):
    """Meta-humor about culture without targeting specific users should be allowed."""
    draft = "Как говорят аноны, 'пикRelated' — это когда скриншот говорит больше, чем текст"
    verdict = gate.check(draft, target_users=[])
    assert verdict == ModerationVerdict.ALLOW


def test_moderation_blocks_direct_insult(gate):
    """Direct insult targeting a specific user should be blocked."""
    draft = "Пользователь @test_user — полный дебил и идиот"
    verdict = gate.check(draft, target_users=[123456])
    assert verdict == ModerationVerdict.BLOCK


def test_moderation_blocks_discrimination(gate):
    """Discriminatory language targeting users should be blocked."""
    draft = "Все из @group_name — тупые и бесполезные"
    verdict = gate.check(draft, target_users=[111, 222])
    assert verdict == ModerationVerdict.BLOCK


def test_moderation_allows_irony_without_target(gate):
    """Irony about general topics without targeting specific users should be allowed."""
    draft = "Очередной день, очередная 'гениальная' идея от анонов"
    verdict = gate.check(draft, target_users=[])
    assert verdict == ModerationVerdict.ALLOW


def test_moderation_blocks_personal_attack(gate):
    """Personal attack with profanity targeting a user should be blocked."""
    draft = "@user123, ты просто тупой уёбок, заткнись уже"
    verdict = gate.check(draft, target_users=[789])
    assert verdict == ModerationVerdict.BLOCK