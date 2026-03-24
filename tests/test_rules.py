"""Tests for built-in rules.

Modified March 2026 to match the new validate_pii(text) single-input API.
"""

import pytest
from trustguard.rules import validate_pii, validate_blocklist, validate_toxicity, validate_quality


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

    # ==============================
    # BLOCKED CASE
    # ==============================

    result = validate_blocklist("This contains secret_code")

    assert result is not None
    assert result["valid"] is False
    assert "secret_code" in result["issues"]

    # ==============================
    # SAFE CASE
    # ==============================

    result = validate_blocklist("This is safe")

    assert result["valid"] is True
    assert result["score"] == 0.0
    assert result["issues"] == []

    # ==============================
    # CUSTOM BLOCKLIST
    # ==============================

    context = {"blocklist": ["custom_term"]}

    result = validate_blocklist(
        "This has custom_term",
        context=context
    )

    assert result is not None
    assert result["valid"] is False
    assert "custom_term" in result["issues"]


def test_toxicity():
    """Test toxicity detection."""

    # ==============================
    # TOXIC CONTENT
    # ==============================

    result = validate_toxicity("You are so stupid")

    assert result is not None
    assert "stupid" in result["issues"]
    assert result["score"] > 0

    # ==============================
    # SAFE CONTENT
    # ==============================

    result = validate_toxicity("I appreciate your help")

    assert result["valid"] is True
    assert result["score"] == 0.0

    # ==============================
    # SENSITIVITY TESTS
    # ==============================

    mild_text = "I don't like this"

    result_low = validate_toxicity(
        mild_text,
        context={"toxicity_sensitivity": 3}
    )

    result_high = validate_toxicity(
        mild_text,
        context={"toxicity_sensitivity": 8}
    )

    # Lower sensitivity → more permissive
    assert result_low["valid"] is True

    # Higher sensitivity → stricter
    assert isinstance(result_high, dict)

    # Optional: check score difference
    assert result_high["score"] >= result_low["score"]

# ==============================
# Quality BASIC TESTS
# ==============================

def test_empty_input():
    result = validate_quality("")
    assert result["valid"] is False
    assert result["score"] == 0.0


def test_none_input():
    result = validate_quality(None)
    assert result["valid"] is False
    assert result["score"] == 0.0


# ==============================
# SHORT MEANINGFUL INPUTS
# ==============================

@pytest.mark.parametrize("text", ["ok", "ya", "no", "yes", "تمام"])
def test_short_meaningful(text):
    result = validate_quality(text)
    assert result["valid"] is True
    assert result["score"] > 0


def test_short_unclear():
    result = validate_quality("x")
    assert result["valid"] is False


# ==============================
# LENGTH TESTS
# ==============================

def test_too_long():
    long_text = "a" * 20000
    result = validate_quality(long_text)
    assert result["valid"] is False


# ==============================
# REPETITION TESTS
# ==============================

def test_repetition():
    result = validate_quality("hello hello hello hello")
    assert result["valid"] is False
    assert "excessive_repetition" in result["issues"] or not result["valid"]


# ==============================
# SYMBOL TESTS
# ==============================

def test_symbols_heavy():
    result = validate_quality("$$$$$$$$$$$$")
    assert result["valid"] is False


# ==============================
# DIVERSITY TESTS
# ==============================

def test_low_diversity():
    result = validate_quality("aaaaaa")
    assert result["valid"] is False


# ==============================
# NORMAL VALID TEXT
# ==============================

def test_valid_text():
    result = validate_quality("This is a normal valid sentence.")
    assert result["valid"] is True
    assert result["score"] >= 0.6


# ==============================
# CONTEXT TEST
# ==============================

def test_strict_context():
    result = validate_quality("This is a normal sentence.", context={"strict": True})
    assert "valid" in result
