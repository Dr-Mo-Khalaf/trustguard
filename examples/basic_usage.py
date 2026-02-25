#!/usr/bin/env python3
"""
Basic usage examples for trustguard.
"""

import json
from trustguard import TrustGuard
from trustguard.schemas import GenericResponse
from trustguard.rules import DEFAULT_RULES


def basic_validation():
    """Basic validation example."""
    print("=" * 50)
    print("Basic Validation Example")
    print("=" * 50)
    
    # Create validator
    guard = TrustGuard(schema_class=GenericResponse)
    
    # Test a valid response
    valid_response = json.dumps({
        "content": "I can help you reset your password. Please check your email.",
        "sentiment": "positive",
        "tone": "helpful",
        "is_helpful": True
    })
    
    print("\n📝 Validating safe response...")
    result = guard.validate(valid_response)
    print(f"Status: {result.status}")
    print(f"Log: {result.log}")
    if result.is_approved:
        print(f"Data: {json.dumps(result.data, indent=2)}")
    
    # Test an invalid response
    invalid_response = "This is not JSON"
    
    print("\n📝 Validating invalid JSON...")
    result = guard.validate(invalid_response)
    print(f"Status: {result.status}")
    print(f"Log: {result.log}")


def custom_rules():
    """Custom rules example."""
    print("\n" + "=" * 50)
    print("Custom Rules Example")
    print("=" * 50)
    
    # Define a custom rule
    def check_length(data, raw_text, context=None):
        content = data.get("content", "")
        if len(content) < 20:
            return "Content too short (minimum 20 characters)"
        if len(content) > 500:
            return "Content too long (maximum 500 characters)"
        return None
    
    # Create validator with custom rule
    guard = TrustGuard(
        schema_class=GenericResponse,
        custom_rules=[check_length] + DEFAULT_RULES
    )
    
    # Test with short content
    short_response = json.dumps({
        "content": "Too short",
        "sentiment": "neutral",
        "tone": "professional",
        "is_helpful": True
    })
    
    print("\n📝 Testing short content...")
    result = guard.validate(short_response)
    print(f"Status: {result.status}")
    print(f"Log: {result.log}")
    
    # Test with good content
    good_response = json.dumps({
        "content": "I'd be happy to help you with your account. What specific issue are you having?",
        "sentiment": "positive",
        "tone": "helpful",
        "is_helpful": True
    })
    
    print("\n📝 Testing good content...")
    result = guard.validate(good_response)
    print(f"Status: {result.status}")
    print(f"Log: {result.log}")


def batch_validation():
    """Batch validation example."""
    print("\n" + "=" * 50)
    print("Batch Validation Example")
    print("=" * 50)
    
    guard = TrustGuard(schema_class=GenericResponse)
    
    # Create multiple responses
    responses = [
        json.dumps({"content": "Good response 1", "sentiment": "positive", "tone": "professional", "is_helpful": True}),
        json.dumps({"content": "Bad response with email@example.com", "sentiment": "neutral", "tone": "professional", "is_helpful": True}),
        json.dumps({"content": "This is a very long response that goes on and on and on...", "sentiment": "neutral", "tone": "professional", "is_helpful": True}),
        json.dumps({"content": "Good response 2", "sentiment": "positive", "tone": "helpful", "is_helpful": True}),
    ]
    
    print(f"\n📝 Validating {len(responses)} responses...")
    report = guard.validate_batch(responses)
    
    print(f"\n{report.summary()}")


if __name__ == "__main__":
    basic_validation()
    custom_rules()
    batch_validation()
