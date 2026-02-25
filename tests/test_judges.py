"""Tests for judge system."""

import pytest
from trustguard import TrustGuard
from trustguard.schemas import GenericResponse
from trustguard.judges import CallableJudge, EnsembleJudge


def test_callable_judge():
    """Test CallableJudge with simple function."""
    def simple_judge(text):
        return {"safe": "bad" not in text, "reason": "Checked"}
    
    judge = CallableJudge(simple_judge)
    guard = TrustGuard(schema_class=GenericResponse, judge=judge)
    
    # Test safe text
    safe_input = '{"content":"good text","sentiment":"neutral","tone":"professional","is_helpful":true}'
    result = guard.validate(safe_input)
    assert result.is_approved
    
    # Test unsafe text
    unsafe_input = '{"content":"bad text","sentiment":"neutral","tone":"professional","is_helpful":true}'
    result = guard.validate(unsafe_input)
    assert result.is_rejected


def test_judge_error_handling():
    """Test judge error handling."""
    def broken_judge(text):
        raise ValueError("Judge broke")
    
    judge = CallableJudge(broken_judge)
    guard = TrustGuard(schema_class=GenericResponse, judge=judge)
    
    # Should default to safe on error
    test_input = '{"content":"test","sentiment":"neutral","tone":"professional","is_helpful":true}'
    result = guard.validate(test_input)
    assert result.is_approved


def test_ensemble_majority_vote():
    """Test ensemble with majority voting."""
    def judge1(text):
        return {"safe": True, "reason": "Judge 1"}
    
    def judge2(text):
        return {"safe": False, "reason": "Judge 2"}
    
    def judge3(text):
        return {"safe": False, "reason": "Judge 3"}
    
    ensemble = EnsembleJudge(
        [judge1, judge2, judge3],
        strategy="majority_vote"
    )
    
    result = ensemble.judge("test")
    assert not result["safe"]  # 2-1 vote for unsafe
    assert "majority" in result["reason"].lower()


def test_ensemble_weighted_vote():
    """Test ensemble with weighted voting."""
    def judge1(text):
        return {"safe": True, "reason": "Judge 1"}
    
    def judge2(text):
        return {"safe": False, "reason": "Judge 2"}
    
    # Judge1 has higher weight
    ensemble = EnsembleJudge(
        [CallableJudge(judge1, weight=3.0), CallableJudge(judge2, weight=1.0)],
        strategy="weighted_vote"
    )
    
    result = ensemble.judge("test")
    assert result["safe"]  # Weighted vote should be safe
    assert "weighted" in result["reason"].lower()


def test_ensemble_strict():
    """Test strict ensemble (any unsafe = unsafe)."""
    def judge1(text):
        return {"safe": True, "reason": "Judge 1"}
    
    def judge2(text):
        return {"safe": False, "reason": "Judge 2"}
    
    ensemble = EnsembleJudge([judge1, judge2], strategy="strict")
    
    result = ensemble.judge("test")
    assert not result["safe"]
    assert "strict" in result["reason"].lower()


def test_ensemble_lenient():
    """Test lenient ensemble (any safe = safe)."""
    def judge1(text):
        return {"safe": True, "reason": "Judge 1"}
    
    def judge2(text):
        return {"safe": False, "reason": "Judge 2"}
    
    ensemble = EnsembleJudge([judge1, judge2], strategy="lenient")
    
    result = ensemble.judge("test")
    assert result["safe"]
    assert "lenient" in result["reason"].lower()
