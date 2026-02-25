"""Tests for core validation engine."""

import pytest
import json
from trustguard import TrustGuard
from trustguard.schemas import GenericResponse


def test_basic_validation():
    """Test basic validation passes."""
    guard = TrustGuard(schema_class=GenericResponse)
    
    valid_input = json.dumps({
        "content": "Test content that is long enough to pass quality checks",
        "sentiment": "neutral",
        "tone": "professional",
        "is_helpful": True
    })
    
    result = guard.validate(valid_input)
    assert result.status == "APPROVED"
    assert result.data["content"] == "Test content that is long enough to pass quality checks"


def test_invalid_json():
    """Test invalid JSON handling."""
    guard = TrustGuard(schema_class=GenericResponse)
    
    result = guard.validate("Not JSON")
    assert result.status == "REJECTED"
    assert "JSON Extraction Error" in result.log


def test_schema_validation():
    """Test schema validation failures."""
    guard = TrustGuard(schema_class=GenericResponse)
    
    # Missing required field - but content is long enough to pass quality check
    invalid_input = json.dumps({
        "content": "This is a test content that is long enough to pass the quality check",
        # Missing sentiment, tone, is_helpful
    })
    
    result = guard.validate(invalid_input)
    assert result.status == "REJECTED"
    assert "Schema Error" in result.log


def test_quality_rule_vs_schema():
    """Test that quality rule doesn't interfere with schema validation."""
    guard = TrustGuard(schema_class=GenericResponse)
    
    # Content is short but has all required fields - should pass
    valid_short_input = json.dumps({
        "content": "Short",
        "sentiment": "neutral",
        "tone": "professional",
        "is_helpful": True
    })
    
    result = guard.validate(valid_short_input)
    assert result.status == "APPROVED"  # Quality rule is lenient enough
    
    # Content is long enough but missing required fields - should fail
    invalid_input = json.dumps({
        "content": "This is a long enough content but missing required fields",
        # Missing sentiment, tone, is_helpful
    })
    
    result = guard.validate(invalid_input)
    assert result.status == "REJECTED"
    assert "Schema Error" in result.log


def test_custom_rule():
    """Test custom rule execution."""
    def always_fail(data, raw_text, context=None):
        return "Custom rule failed"
    
    guard = TrustGuard(
        schema_class=GenericResponse,
        custom_rules=[always_fail]
    )
    
    valid_input = json.dumps({
        "content": "Test content that is long enough to pass quality checks",
        "sentiment": "neutral",
        "tone": "professional",
        "is_helpful": True
    })
    
    result = guard.validate(valid_input)
    assert result.status == "REJECTED"
    assert result.log == "Custom rule failed"


def test_batch_validation():
    """Test batch validation."""
    guard = TrustGuard(schema_class=GenericResponse)
    
    inputs = [
        json.dumps({"content": "Good response that is long enough", "sentiment": "positive", "tone": "professional", "is_helpful": True}),
        "Invalid JSON",
        json.dumps({"content": "Also good and long enough", "sentiment": "neutral", "tone": "professional", "is_helpful": True}),
    ]
    
    report = guard.validate_batch(inputs)
    assert report.total == 3
    assert report.passed == 2
    assert report.failed == 1


def test_stats():
    """Test statistics tracking."""
    guard = TrustGuard(schema_class=GenericResponse)
    
    valid_input = json.dumps({
        "content": "Test content that is long enough to pass quality checks",
        "sentiment": "neutral",
        "tone": "professional",
        "is_helpful": True
    })
    
    guard.validate(valid_input)
    guard.validate("Invalid")
    
    stats = guard.get_stats()
    assert stats["total_validations"] == 2
    assert stats["approved"] == 1
    assert stats["rejected"] == 1
