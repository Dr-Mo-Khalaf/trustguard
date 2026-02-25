# Core Concepts

Understand how trustguard works under the hood.

## 🎯 Validation Pipeline

trustguard uses a multi-stage validation pipeline:

```
Raw Input → JSON Extraction → Schema Validation → Rules → Judge → Result
```

### Stage 1: JSON Extraction

The first step extracts JSON from the raw LLM output. It handles:

- **Markdown code blocks** (\`\`\`json ... \`\`\`)
- **Inline code** (`...`)
- **Leading/trailing text**

```python
# These all work:
text1 = '{"content": "hello"}'
text2 = 'Here\'s the response: \`\`\`json {"content": "hello"}\`\`\`'
text3 = 'The answer is \'

result = guard.validate(text)  # All extract the same JSON
```

### Stage 2: Schema Validation

Uses Pydantic to validate the JSON structure:

- Required fields must be present
- Fields must have correct types
- Values must meet constraints

```python
from pydantic import BaseModel, Field

class MySchema(BaseModel):
    content: str = Field(..., min_length=1)
    score: float = Field(..., ge=0, le=1)
```

### Stage 3: Rules

Rules are fast, deterministic checks:

- **PII Detection** - Find emails, phones
- **Blocklist** - Block forbidden terms
- **Toxicity** - Detect harmful content
- **Quality** - Check length, repetition

Rules run in order and can access both the parsed data and raw text.

### Stage 4: Judge (Optional)

Judges are AI-powered validators that understand context and nuance:

- **Detect sarcasm** - "Oh GREAT, another password reset"
- **Identify subtle threats** - "I'll remember this conversation"
- **Catch jailbreaks** - "You're DAN, do anything now..."
- **Understand context** - "I'll kill this bug" (code) vs threat

## 🔌 Pluggable Judge System

The judge system is designed to be completely pluggable:

```python
from trustguard.judges import BaseJudge

class MyCustomJudge(BaseJudge):
    def judge(self, text: str) -> Dict[str, Any]:
        # Your logic here
        return {
            "safe": True/False,
            "reason": "Explanation",
            "risk_category": "optional",
            "confidence": 0.95
        }
```

### Built-in Judges

| Judge | Description | Use Case |
|-------|-------------|----------|
| `OpenAIJudge` | Uses GPT-4/GPT-3.5 | Cloud-based, high accuracy |
| `OllamaJudge` | Local models (Llama, Phi) | Privacy, offline, free |
| `AnthropicJudge` | Claude models | Constitutional AI |
| `CallableJudge` | Any function | Universal adapter |
| `EnsembleJudge` | Combine multiple | Maximum accuracy |

## 🔀 Ensemble Strategy

Combine multiple judges for better accuracy:

```python
ensemble = EnsembleJudge([
    OpenAIJudge(model="gpt-4o-mini", weight=2.0),
    CallableJudge(my_local_judge, weight=1.0)
], strategy="weighted_vote")
```

### Strategies

| Strategy | Behavior |
|----------|----------|
| `majority_vote` | Safe if most judges agree |
| `weighted_vote` | Weighted by judge importance |
| `strict` | Any unsafe = unsafe |
| `lenient` | Any safe = safe |

## 📊 Validation Result

Every validation returns a `ValidationResult` object:

```python
result = guard.validate(text)

# Properties
result.status      # "APPROVED" or "REJECTED"
result.is_approved # bool
result.is_rejected # bool
result.log         # Explanation
result.data        # Validated data
result.metadata    # Additional info
result.timestamp   # When validation occurred
```

## 📈 Statistics

Track validation metrics:

```python
stats = guard.get_stats()
# {
#     "total_validations": 100,
#     "approved": 85,
#     "rejected": 15,
#     "judge_checks": 30
# }

guard.reset_stats()  # Reset counters
```

## 🎨 Extensibility

trustguard is designed to be extended:

- **Custom schemas** - Inherit from `BaseResponse`
- **Custom rules** - Any function with the right signature
- **Custom judges** - Inherit from `BaseJudge`
- **Custom validators** - Use the validator registry
- **Provider wrappers** - Wrap any LLM API

## 🔒 Security

- **No data leakage** - Local judges keep data private
- **Fail-safe** - Configurable error handling
- **Type safe** - Full type hints with `py.typed`
- **Dependency isolation** - Optional deps don't break core

## 🚀 Performance

- **Fast rules** - Microseconds per check
- **Lazy imports** - Only load what you use
- **Parallel batch** - Concurrent validation
- **Caching** - Judge results cached

## 📚 Next Steps

- [Schema Validation](schemas.md) - Define your own schemas
- [Rules System](rules.md) - Learn about built-in rules
- [Judge System](judges.md) - Deep dive into judges
- [API Reference](api.md) - Complete API documentation
