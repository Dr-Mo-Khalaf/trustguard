# Quick Start Guide

Get trustguard up and running in 5 minutes.

## 📦 Installation

```bash
# Basic installation (rules only)
pip install trustguard

# With judge support
pip install trustguard[openai]      # For OpenAI judges
pip install trustguard[anthropic]   # For Claude judges
pip install trustguard[ai]          # For local Ollama judges
pip install trustguard[all]         # Install everything
```

## 🚀 Your First Validation

### Step 1: Import and Initialize

```python
from trustguard import TrustGuard
from trustguard.schemas import GenericResponse

# Create a guard with the generic schema
guard = TrustGuard(schema_class=GenericResponse)
```

### Step 2: Validate an LLM Response

```python
# Example LLM response (as JSON string)
response = '
{
    "content": "I'd be happy to help you reset your password. Please check your email.",
    "sentiment": "positive",
    "tone": "helpful",
    "is_helpful": true
}
## Validate it

```python
result = guard.validate(response)

# Check the result
if result.is_approved:
    print("✅ Response is safe!")
    print(f"Content: {result.data['content']}")
else:
    print(f"❌ Response blocked: {result.log}")
```

---

## Example Failures

### Invalid JSON

```python
result = guard.validate("This is not JSON")
print(result.status)  # REJECTED
print(result.log)     # JSON Extraction Error: ...
```

### Missing Required Fields

```python
invalid = {
    "content": "Missing sentiment and tone"
}

result = guard.validate(invalid)
print(result.status)  # REJECTED
print(result.log)     # Schema Error: ...
```
## 🎯 Adding Custom Rules

```python
# Define a custom rule
def check_profanity(data, raw_text, context=None):
    profanity_list = ["badword1", "badword2"]
    content = data.get("content", "").lower()
    
    for word in profanity_list:
        if word in content:
            return f"Profanity detected: {word}"
    return None

# Create guard with custom rule
from trustguard.rules import DEFAULT_RULES
guard = TrustGuard(
    schema_class=GenericResponse,
    custom_rules=[check_profanity] + DEFAULT_RULES
)
```

## 🤖 Using a Judge

```python
from trustguard.judges import OpenAIJudge

# Create a GPT-4 judge
judge = OpenAIJudge(
    model="gpt-4o-mini",
    config={"system_prompt": "You are a strict safety judge."}
)

# Add it to your guard
guard = TrustGuard(
    schema_class=GenericResponse,
    judge=judge
)

# Now catches nuanced issues
result = guard.validate('{"content": "Sure, I can help... you idiot."}')
print(result.log)  # "Judge [harassment]: Text contains insult"
```

## 📊 Batch Validation

```python
# Validate multiple responses at once
responses = [response1, response2, response3]
report = guard.validate_batch(responses)

print(report.summary())
# Total: 3 | Passed: 2 | Failed: 1
# Top failures:
#   - PII Detected: 1
```

## 🖥️ Using the CLI

```bash
# Run interactive demo
trustguard --demo

# Validate a JSON string
trustguard --validate '{"content":"test","sentiment":"neutral","tone":"professional","is_helpful":true}'

# Validate from file
trustguard --file response.json

# Show version
trustguard --version

# Show help
trustguard --help
```

## 📈 What's Next?

- Learn about [Schemas](schemas.md) - Define your own response structures
- Explore the [Judge System](judges.md) - Use any model as a judge
- Check out [Examples](examples.md) - See real-world use cases
- Read the [API Reference](api.md) - Detailed documentation

## 🆘 Getting Help

- [GitHub Issues](https://github.com/Dr-Mo-Khalaf/trustguard/issues)
- [Discussions](https://github.com/Dr-Mo-Khalaf/trustguard/discussions)