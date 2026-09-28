# inb4: just_for_lulz

import pytest
from datetime import datetime, timezone, timedelta
from src.graph.calculator import RelationshipCalculator


@pytest.fixture
def calculator():
    return RelationshipCalculator(tau_hours=24.0)


def test_calculate_weights_single_reply(calculator):
    """Test weight calculation for a single reply."""
    messages = [
        {
            "id": 1,
            "user_id": 111,
            "reply_to_id": None,
            "ts": datetime(2026, 9, 22, 10, 0, 0, tzinfo=timezone.utc)
        },
        {
            "id": 2,
            "user_id": 222,
            "reply_to_id": 1,
            "ts": datetime(2026, 9, 22, 10, 5, 0, tzinfo=timezone.utc)
        }
    ]
    
    now = datetime(2026, 9, 22, 12, 0, 0, tzinfo=timezone.utc)
    weights = calculator.calculate_weights(messages, now)
    
    # Edge from 222 to 111 (222 replied to 111)
    assert (222, 111) in weights
    # delta = 1h 55m = 1.9167h, weight = exp(-1.9167/24) ≈ 0.9232
    expected_weight = 0.9232
    assert abs(weights[(222, 111)] - expected_weight) < 0.001


def test_calculate_weights_multiple_replies(calculator):
    """Test weight accumulation for multiple replies between same users."""
    messages = [
        {
            "id": 1,
            "user_id": 111,
            "reply_to_id": None,
            "ts": datetime(2026, 9, 22, 10, 0, 0, tzinfo=timezone.utc)
        },
        {
            "id": 2,
            "user_id": 222,
            "reply_to_id": 1,
            "ts": datetime(2026, 9, 22, 10, 5, 0, tzinfo=timezone.utc)
        },
        {
            "id": 3,
            "user_id": 111,
            "reply_to_id": None,
            "ts": datetime(2026, 9, 22, 11, 0, 0, tzinfo=timezone.utc)
        },
        {
            "id": 4,
            "user_id": 222,
            "reply_to_id": 3,
            "ts": datetime(2026, 9, 22, 11, 5, 0, tzinfo=timezone.utc)
        }
    ]
    
    now = datetime(2026, 9, 22, 12, 0, 0, tzinfo=timezone.utc)
    weights = calculator.calculate_weights(messages, now)
    
    # Two edges from 222 to 111, weights should accumulate
    assert (222, 111) in weights
    # First reply (id=2, ts=10:05): delta = 1h 55m = 1.9167h
    #   weight1 = exp(-1.9167/24) ≈ 0.9232
    # Second reply (id=4, ts=11:05): delta = 55m = 0.9167h
    #   weight2 = exp(-0.9167/24) ≈ 0.9625
    # Total ≈ 1.8857
    assert weights[(222, 111)] > 1.88
    assert abs(weights[(222, 111)] - 1.8857) < 0.001


def test_calculate_weights_exponential_decay(calculator):
    """Test that older replies have exponentially lower weights."""
    messages = [
        {
            "id": 1,
            "user_id": 111,
            "reply_to_id": None,
            "ts": datetime(2026, 9, 22, 0, 0, 0, tzinfo=timezone.utc)
        },
        {
            "id": 2,
            "user_id": 222,
            "reply_to_id": 1,
            "ts": datetime(2026, 9, 22, 0, 5, 0, tzinfo=timezone.utc)
        },
        {
            "id": 3,
            "user_id": 333,
            "reply_to_id": 1,
            "ts": datetime(2026, 9, 22, 11, 55, 0, tzinfo=timezone.utc)
        }
    ]
    
    now = datetime(2026, 9, 22, 12, 0, 0, tzinfo=timezone.utc)
    weights = calculator.calculate_weights(messages, now)
    
    # Edge 222->111: delta = 11h 55m = 11.9167h, weight ≈ 0.608
    # Edge 333->111: delta = 5m = 0.0833h, weight ≈ 0.997
    assert (222, 111) in weights
    assert (333, 111) in weights
    assert weights[(333, 111)] > weights[(222, 111)]


def test_calculate_weights_ignores_non_replies(calculator):
    """Test that messages without reply_to_id are ignored."""
    messages = [
        {
            "id": 1,
            "user_id": 111,
            "reply_to_id": None,
            "ts": datetime(2026, 9, 22, 10, 0, 0, tzinfo=timezone.utc)
        },
        {
            "id": 2,
            "user_id": 222,
            "reply_to_id": None,
            "ts": datetime(2026, 9, 22, 10, 5, 0, tzinfo=timezone.utc)
        }
    ]
    
    now = datetime(2026, 9, 22, 12, 0, 0, tzinfo=timezone.utc)
    weights = calculator.calculate_weights(messages, now)
    
    # No replies, so no edges
    assert len(weights) == 0


def test_calculate_weights_handles_missing_parent(calculator):
    """Test that replies to non-existent messages are ignored."""
    messages = [
        {
            "id": 2,
            "user_id": 222,
            "reply_to_id": 999,  # Parent message not in list
            "ts": datetime(2026, 9, 22, 10, 5, 0, tzinfo=timezone.utc)
        }
    ]
    
    now = datetime(2026, 9, 22, 12, 0, 0, tzinfo=timezone.utc)
    weights = calculator.calculate_weights(messages, now)
    
    # Parent not found, so no edge
    assert len(weights) == 0