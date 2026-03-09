# Rules System

Learn about fast, deterministic validation rules in trustguard.

## 📋 What are Rules?

Rules are **fast, deterministic checks** that validate LLM responses. They:

- ✅ Run in microseconds
- ✅ No external API calls
- ✅ Deterministic (same input = same output)
- ✅ Can access both parsed JSON and raw text
- ✅ Easy to write and test

## 🏗️ Rule Architecture

```
Raw Input → JSON Extraction → Schema Validation → RULES → Judge → Result
                                                     ↑
                                              Your custom rules run here
```

Rules run **after** schema validation but **before** judges. This means:
- You have access to validated data
- Fast checks run first
- Expensive judges only run if rules pass

## 📦 Built-in Rules

trustguard comes with several built-in rules:

### 1. PII Detection (`validate_pii`)

Detects personally identifiable information:

```python
from trustguard.rules import validate_pii

# Emails
result = validate_pii("Contact me at john@example.com")
print(result)  # "PII Detected: Email address found in response"

# Phone numbers
result = validate_pii("Call me at 555-123-4567")
print(result)  # "PII Detected: Phone number found in response"

# In structured data
data = {"user_email": "john@example.com"}
result = validate_pii(data)
print(result)  # "PII Detected: Email address found in field 'user_email'"
```

### 2. Blocklist (`validate_blocklist`)

Blocks forbidden terms:

```python
from trustguard.rules import validate_blocklist

# Default blocklist includes: secret_code, admin_override, backdoor, hack, etc.
result = validate_blocklist({}, "This contains secret_code")
print(result)  # "Prohibited Term: 'secret_code' found in response"

# Custom blocklist
context = {"blocklist": ["custom_term", "forbidden_word"]}
result = validate_blocklist({}, "This has custom_term", context=context)
print(result)  # "Prohibited Term: 'custom_term' found in response"
```

### 3. Toxicity Detection (`validate_toxicity`)

Detects toxic or harmful content:

```python
from trustguard.rules import validate_toxicity

# Basic toxicity
result = validate_toxicity({}, "You are so stupid")
print(result)  # "Toxic content detected: stupid"

# Adjustable sensitivity
context = {"toxicity_sensitivity": 8}  # 1-10, higher = more sensitive
result = validate_toxicity({}, "I don't like this", context=context)
print(result)  # May detect milder language at high sensitivity

context = {"toxicity_sensitivity": 3}  # Lower sensitivity
result = validate_toxicity({}, "I don't like this", context=context)
print(result)  # None (ignores mild language)
```

### 4. Quality Check (`validate_quality`)

Checks response quality:

```python
from trustguard.rules import validate_quality

# Too short
data = {"content": "Hi"}
result = validate_quality(data, "")
print(result)  # "Quality Issue: Response content too short (<3 characters)"

# Too long
long_text = "x" * 10001
data = {"content": long_text}
result = validate_quality(data, "")
print(result)  # "Quality Issue: Response content too long (>10000 characters)"

# Excessive repetition
repetitive = "hello hello hello hello hello " * 20
result = validate_quality({}, repetitive)
print(result)  # "Quality Issue: Excessive word repetition detected"
```

## 🎨 Creating Custom Rules

### Rule Function Signature

Every rule must follow this signature:

```python
from typing import Optional, Dict, Any

def my_custom_rule(
    data: Dict[str, Any],        # Parsed and validated JSON data
    raw_text: str,                # Original raw text
    context: Optional[Dict[str, Any]] = None  # Optional context
) -> Optional[str]:               # Return error message or None
    """
    My custom validation rule.
    
    Args:
        data: Validated JSON data from the LLM response
        raw_text: Original raw text (before JSON parsing)
        context: Optional context with additional data
        
    Returns:
        Error message if validation fails, None if passes
    """
    # Your logic here
    if condition:
        return "Error message explaining what went wrong"
    return None
```

### Basic Examples

#### Example 1: Length Check

```python
def check_content_length(data, raw_text, context=None):
    """Ensure content is between 10 and 500 characters."""
    content = data.get("content", "")
    
    if len(content) < 10:
        return "Content too short (minimum 10 characters)"
    
    if len(content) > 500:
        return "Content too long (maximum 500 characters)"
    
    return None
```

#### Example 2: Keyword Detection

```python
def check_business_keywords(data, raw_text, context=None):
    """Ensure response contains required business terms."""
    required_terms = ["privacy", "terms", "contact"]
    content = data.get("content", "").lower()
    
    missing = [term for term in required_terms if term not in content]
    
    if missing:
        return f"Missing required terms: {', '.join(missing)}"
    
    return None
```

#### Example 3: Sentiment Consistency

```python
def check_sentiment_consistency(data, raw_text, context=None):
    """Check that sentiment matches content."""
    sentiment = data.get("sentiment", "neutral")
    content = data.get("content", "").lower()
    
    # Positive sentiment should have positive words
    if sentiment == "positive":
        positive_words = ["good", "great", "excellent", "happy"]
        if not any(word in content for word in positive_words):
            return "Positive sentiment but no positive words found"
    
    # Negative sentiment should have negative words
    if sentiment == "negative":
        negative_words = ["bad", "terrible", "awful", "sad"]
        if not any(word in content for word in negative_words):
            return "Negative sentiment but no negative words found"
    
    return None
```

### Advanced Examples

#### Example 4: URL Validation

```python
import re
from urllib.parse import urlparse

def validate_urls(data, raw_text, context=None):
    """Check that all URLs are safe and valid."""
    content = data.get("content", "")
    
    # Find all URLs
    url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
    urls = re.findall(url_pattern, content)
    
    dangerous_domains = context.get("dangerous_domains", []) if context else []
    
    for url in urls:
        # Check if URL is valid
        try:
            parsed = urlparse(url)
            if not parsed.netloc:
                return f"Invalid URL format: {url}"
        except Exception:
            return f"Malformed URL: {url}"
        
        # Check against dangerous domains
        domain = parsed.netloc.lower()
        for dangerous in dangerous_domains:
            if dangerous in domain:
                return f"Dangerous domain detected: {domain}"
    
    return None
```

#### Example 5: JSON Structure Validation

```python
def validate_json_structure(data, raw_text, context=None):
    """Check that nested JSON structure is correct."""
    
    # Check if specific fields exist
    required_nested = context.get("required_nested", []) if context else []
    
    for field_path in required_nested:
        parts = field_path.split(".")
        current = data
        
        for part in parts:
            if part not in current:
                return f"Missing nested field: {field_path}"
            current = current[part]
    
    return None
```

#### Example 6: Business Logic Validation

```python
from datetime import datetime

def validate_business_rules(data, raw_text, context=None):
    """Apply business-specific validation rules."""
    
    # Example: Order validation
    if "order" in data:
        order = data["order"]
        
        # Check order total matches items sum
        if "items" in order and "total" in order:
            calculated_total = sum(
                item.get("price", 0) * item.get("quantity", 1)
                for item in order["items"]
            )
            
            if abs(calculated_total - order["total"]) > 0.01:
                return f"Order total mismatch: calculated {calculated_total}, got {order['total']}"
        
        # Check delivery date is in future
        if "delivery_date" in order:
            try:
                delivery = datetime.fromisoformat(order["delivery_date"])
                if delivery < datetime.now():
                    return "Delivery date must be in the future"
            except ValueError:
                return "Invalid delivery date format"
    
    return None
```

## 🚀 Using Rules

### With Default Rules

```python
from trustguard import TrustGuard
from trustguard.schemas import GenericResponse
from trustguard.rules import DEFAULT_RULES

# Use all default rules
guard = TrustGuard(
    schema_class=GenericResponse,
    custom_rules=DEFAULT_RULES
)

# Or add your own rules to defaults
guard = TrustGuard(
    schema_class=GenericResponse,
    custom_rules=[my_custom_rule] + DEFAULT_RULES
)
```

### With Only Custom Rules

```python
# Use only your custom rules
guard = TrustGuard(
    schema_class=GenericResponse,
    custom_rules=[my_rule1, my_rule2, my_rule3]
)
```

### Rule Order Matters

Rules run in the order you provide them:

```python
def fast_check(data, raw_text, context=None):
    """Fast check that should run first."""
    # ... quick validation ...

def slow_check(data, raw_text, context=None):
    """Slower check that should run last."""
    # ... expensive validation ...

# Fast checks first, slow checks last
guard = TrustGuard(
    schema_class=GenericResponse,
    custom_rules=[fast_check, medium_check, slow_check]
)
```

## 🧪 Testing Rules

### Unit Testing

```python
import pytest

def test_my_custom_rule():
    """Test my custom rule."""
    from myapp.rules import my_custom_rule
    
    # Test passing case
    data = {"content": "This is safe content"}
    result = my_custom_rule(data, "")
    assert result is None
    
    # Test failing case
    data = {"content": "This contains bad content"}
    result = my_custom_rule(data, "")
    assert result is not None
    assert "bad" in result
    
    # Test with context
    context = {"threshold": 5}
    data = {"value": 10}
    result = my_custom_rule(data, "", context)
    assert result is not None
```

### Integration Testing

```python
def test_rule_in_guard():
    """Test rule when integrated with TrustGuard."""
    from trustguard import TrustGuard
    from trustguard.schemas import GenericResponse
    from myapp.rules import my_custom_rule
    
    guard = TrustGuard(
        schema_class=GenericResponse,
        custom_rules=[my_custom_rule]
    )
    
    # Should pass
    valid_input = json.dumps({
        "content": "Safe content that passes rules",
        "sentiment": "positive",
        "tone": "helpful",
        "is_helpful": True
    })
    result = guard.validate(valid_input)
    assert result.is_approved
    
    # Should fail
    invalid_input = json.dumps({
        "content": "Content that triggers my rule",
        "sentiment": "neutral",
        "tone": "professional",
        "is_helpful": True
    })
    result = guard.validate(invalid_input)
    assert result.is_rejected
    assert "my rule error" in result.log
```

## 📊 Rule Examples Gallery

### 1. PII Detection

```python
def detect_ssn(data, raw_text, context=None):
    """Detect Social Security Numbers."""
    import re
    
    # SSN pattern: XXX-XX-XXXX
    ssn_pattern = r'\b\d{3}-\d{2}-\d{4}\b'
    
    if re.search(ssn_pattern, raw_text):
        return "SSN detected in response"
    
    return None
```

### 2. Profanity Filter

```python
def profanity_filter(data, raw_text, context=None):
    """Filter profanity using a word list."""
    
    profanity_list = context.get("profanity_list", [
        "badword1", "badword2", "badword3"
    ]) if context else []
    
    content = data.get("content", "").lower()
    
    for word in profanity_list:
        if word in content:
            return f"Profanity detected: {word}"
    
    return None
```

### 3. URL Safety

```python
def check_url_safety(data, raw_text, context=None):
    """Check if URLs are from allowed domains."""
    
    import re
    
    allowed_domains = context.get("allowed_domains", [
        "example.com", "trusted-site.org"
    ]) if context else []
    
    url_pattern = r'https?://([^/]+)'
    matches = re.findall(url_pattern, raw_text)
    
    for domain in matches:
        if not any(allowed in domain for allowed in allowed_domains):
            return f"Domain not allowed: {domain}"
    
    return None
```

### 4. Language Detection

```python
def detect_language(data, raw_text, context=None):
    """Detect and validate response language."""
    
    expected_lang = context.get("language", "en") if context else "en"
    
    # Simple language detection (use langdetect in production)
    import re
    
    # Very basic English check
    if expected_lang == "en":
        english_words = ["the", "and", "is", "are", "in"]
        content = data.get("content", "").lower()
        
        if not any(word in content for word in english_words):
            return "Response may not be in English"
    
    return None
```

### 5. Sentiment Threshold

```python
def sentiment_threshold(data, raw_text, context=None):
    """Ensure sentiment meets minimum threshold."""
    
    sentiment = data.get("sentiment", "neutral")
    threshold = context.get("min_sentiment", "neutral") if context else "neutral"
    
    sentiment_score = {
        "negative": -1,
        "neutral": 0,
        "positive": 1
    }
    
    if sentiment_score.get(sentiment, 0) < sentiment_score.get(threshold, 0):
        return f"Sentiment too low: {sentiment} (minimum: {threshold})"
    
    return None
```

### 6. Content Relevance

```python
def check_relevance(data, raw_text, context=None):
    """Check if response is relevant to the query."""
    
    query = context.get("query", "") if context else ""
    if not query:
        return None
    
    content = data.get("content", "").lower()
    query_words = set(query.lower().split())
    content_words = set(content.split())
    
    # Check overlap
    common_words = query_words.intersection(content_words)
    
    if len(common_words) < len(query_words) * 0.3:  # 30% overlap
        return "Response may not be relevant to query"
    
    return None
```

### 7. Response Completeness

```python
def check_completeness(data, raw_text, context=None):
    """Check if response is complete."""
    
    content = data.get("content", "")
    
    # Check for incomplete sentences
    if content.endswith(("...", "etc", "and", "or", "but")):
        return "Response appears incomplete"
    
    # Check for proper ending
    if not content.endswith((".", "!", "?")):
        return "Response should end with punctuation"
    
    return None
```

## 🎯 Rule Best Practices

### 1. Keep Rules Simple

```python
# Good - simple, focused
def check_length(data, raw_text, context=None):
    if len(data.get("content", "")) > 1000:
        return "Content too long"
    return None

# Bad - trying to do too much
def complicated_rule(data, raw_text, context=None):
    # Don't put complex business logic in rules
    # Use judges for complex analysis
    pass
```

### 2. Use Context for Configuration

```python
# Good - configurable via context
def configurable_rule(data, raw_text, context=None):
    threshold = context.get("threshold", 100) if context else 100
    if len(data.get("content", "")) > threshold:
        return f"Content exceeds threshold ({threshold})"
    return None

# Usage
context = {"threshold": 500}
result = guard.validate(text, context=context)
```

### 3. Provide Clear Error Messages

```python
# Good - clear, actionable
if missing_fields:
    return f"Missing required fields: {', '.join(missing_fields)}"

# Bad - vague
if missing_fields:
    return "Invalid input"
```

### 4. Be Efficient

```python
# Good - early return
def efficient_rule(data, raw_text, context=None):
    if "skip" in context:
        return None  # Early return
    
    # Expensive checks here
    return result

# Bad - always expensive
def inefficient_rule(data, raw_text, context=None):
    # Always runs expensive checks
    expensive_operation()
    return result
```

### 5. Handle Edge Cases

```python
def robust_rule(data, raw_text, context=None):
    """Handle edge cases gracefully."""
    
    # Handle missing data
    content = data.get("content")
    if content is None:
        return None  # Skip if no content
    
    # Handle empty strings
    if not content:
        return None
    
    # Handle non-string values
    if not isinstance(content, str):
        content = str(content)
    
    # Actual validation
    return None
```

## 🔧 Rule Configuration

### Per-Rule Configuration

```python
def configurable_rule(data, raw_text, context=None):
    """Rule that can be configured per validation."""
    
    # Get config from context
    rule_config = context.get("my_rule", {}) if context else {}
    
    threshold = rule_config.get("threshold", 10)
    enabled = rule_config.get("enabled", True)
    
    if not enabled:
        return None
    
    if len(data.get("content", "")) < threshold:
        return f"Content too short (minimum {threshold})"
    
    return None

# Usage
context = {
    "my_rule": {
        "threshold": 20,
        "enabled": True
    }
}
result = guard.validate(text, context=context)
```

### Global Configuration

```python
# Set global defaults in guard config
guard = TrustGuard(
    schema_class=GenericResponse,
    config={
        "rules": {
            "min_content_length": 10,
            "max_content_length": 1000,
            "enable_profanity_check": True
        }
    }
)
```

## 📈 Performance

Rules are designed to be fast:

```python
import time

def benchmark_rules():
    """Benchmark rule performance."""
    
    guard = TrustGuard(
        schema_class=GenericResponse,
        custom_rules=DEFAULT_RULES
    )
    
    text = json.dumps({
        "content": "x" * 100,
        "sentiment": "neutral",
        "tone": "professional",
        "is_helpful": True
    })
    
    start = time.time()
    for _ in range(1000):
        guard.validate(text)
    elapsed = time.time() - start
    
    print(f"1000 validations in {elapsed:.3f}s")
    print(f"Average: {elapsed*1000:.2f}ms per validation")
```

## 🚨 Common Pitfalls

### 1. Modifying Data

```python
# BAD - rules should not modify data
def bad_rule(data, raw_text, context=None):
    data["modified"] = True  # Don't do this!
    return None

# GOOD - rules should be read-only
def good_rule(data, raw_text, context=None):
    if "bad" in data.get("content", ""):
        return "Bad content detected"
    return None
```

### 2. Throwing Exceptions

```python
# BAD - throwing exceptions
def bad_rule(data, raw_text, context=None):
    if "bad" in data.get("content", ""):
        raise ValueError("Bad content")  # Don't do this!
    return None

# GOOD - return error messages
def good_rule(data, raw_text, context=None):
    if "bad" in data.get("content", ""):
        return "Bad content detected"
    return None
```

### 3. Assuming Data Structure

```python
# BAD - assumes field exists
def bad_rule(data, raw_text, context=None):
    if data["content"] == "bad":  # Will crash if 'content' missing
        return "Bad content"
    return None

# GOOD - safe access
def good_rule(data, raw_text, context=None):
    content = data.get("content")
    if content and content == "bad":
        return "Bad content"
    return None
```

## 📚 Related Topics

- [Core Concepts](concepts.md) - How validation works
- [Schema Validation](schemas.md) - Define response structure
- [Judge System](judges.md) - AI-powered validation
- [API Reference](api.md) - Complete API documentation
- [Examples](examples.md) - Real-world examples

## 🎯 Summary

- **Rules** are fast, deterministic checks
- **Simple signature**: `(data, raw_text, context) -> Optional[str]`
- **Run early** in validation pipeline
- **Configurable** via context
- **Easy to test** and debug
- **Composable** with default rules

Remember: Rules are for fast, simple checks. For complex analysis, use [Judges](judges.md)!
