"""Tests for built-in rules.

Modified March 2026 to match the new validate_pii(text) single-input API.
"""

import pytest
from trustguard.rules import validate_pii, validate_blocklist, validate_toxicity


def test_pii_detection():
    """Test PII detection rule."""
    # Email detection
    result = validate_pii("Contact me at test@example.com")
    assert result is not None
    assert "Email" in result
    
    # Phone detection
    result = validate_pii("Call me at 555-123-4567")
    assert result is not None
    assert "Phone" in result
    
    # Safe text
    result = validate_pii( "Just regular text")
    assert result is None


def test_pii_detection():
    """Test PII detection rule."""
    
    result = validate_pii("Contact me at test@example.com")
    assert result is not None
    assert "email" in result.lower()

    result = validate_pii("Call me at 555-123-4567")
    assert result is not None
    assert "phone" in result.lower()

    result = validate_pii("Just regular text")
    assert result is None


def test_blocklist():
    """Test blocklist rule."""

    result = validate_blocklist({}, "This contains secret_code")
    assert result is not None
    assert "secret_code" in result

    result = validate_blocklist({}, "This is safe")
    assert result is None

    context = {"blocklist": ["custom_term"]}
    result = validate_blocklist({}, "This has custom_term", context=context)

    assert result is not None
    assert "custom_term" in result


def test_toxicity():
    """Test toxicity detection."""
    # Toxic content
    result = validate_toxicity({}, "You are so stupid")
    assert result is not None
    assert "stupid" in result
    
    # Safe content
    result = validate_toxicity({}, "I appreciate your help")
    assert result is None
    
    # Different sensitivity levels
    mild_text = "I don't like this"
    
    result_low = validate_toxicity({}, mild_text, context={"toxicity_sensitivity": 3})
    result_high = validate_toxicity({}, mild_text, context={"toxicity_sensitivity": 8})
    
    # High sensitivity might catch more
    assert result_low is None
