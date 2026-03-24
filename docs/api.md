# API Reference

Complete API documentation for trustguard.

## 📦 Core Classes

### `TrustGuard`

The main validation class.

```python
from trustguard import TrustGuard

guard = TrustGuard(
    schema_class=GenericResponse,      # Required: Pydantic model
    custom_rules=None,                  # Optional: List of rule functions
    config=None,                        # Optional: Configuration dict
    validator_registry=None,            # Optional: Custom registry
    judge=None                          # Optional: Judge instance
)
```

#### Parameters

| Parameter | Type | Description | Required |
|-----------|------|-------------|----------|
| `schema_class` | `Type[BaseModel]` | Pydantic model defining expected JSON structure | Yes |
| `custom_rules` | `List[Callable]` | Custom validation functions | No |
| `config` | `Dict[str, Any]` | Configuration options | No |
| `validator_registry` | `ValidatorRegistry` | Custom validator registry | No |
| `judge` | `BaseJudge` | AI judge for nuanced validation | No |

#### Methods

| Method | Description | Returns |
|--------|-------------|---------|
| `validate(text, context=None, skip_judge=False)` | Validate a single input | `ValidationResult` |
| `validate_batch(inputs, contexts=None, parallel=False, max_workers=4)` | Validate multiple inputs | `BatchValidationReport` |
| `get_stats()` | Get validation statistics | `Dict[str, int]` |
| `reset_stats()` | Reset statistics | `None` |

### `ValidationResult`

Result of a validation operation.

```python
result = guard.validate(text)

# Properties
result.status        # "APPROVED" or "REJECTED"
result.is_approved   # bool
result.is_rejected   # bool
result.log          # str - Explanation
result.data         # dict - Validated data
result.metadata     # dict - Additional info
result.timestamp    # str - ISO timestamp

# Methods
result.to_dict()    # Convert to dictionary
```

#### Example
```python
{
    "status": "APPROVED",
    "log": "All checks passed.",
    "data": {
        "content": "Safe response",
        "sentiment": "positive"
    },
    "metadata": {
        "phase": "complete",
        "checks_passed": true
    },
    "timestamp": "2024-01-01T00:00:00.000000+00:00"
}
```

### `BatchValidationReport`

Result of batch validation.

```python
report = guard.validate_batch(inputs)

# Properties
report.total        # Total inputs
report.passed       # Number passed
report.failed       # Number failed
report.results      # List of ValidationResult

# Methods
report.summary()                    # Text summary
report.to_dataframe()               # pandas DataFrame
report.to_polars()                  # polars DataFrame
```

#### Example
```python
print(report.summary())
# Total: 100 | Passed: 85 | Failed: 15
# Top failures:
#   - PII Detected: 8
#   - Schema Error: 5
#   - Judge [harassment]: 2
```

## 📐 Schemas

### `BaseResponse`

Base class for all schemas.

```python
from pydantic import ConfigDict
from trustguard.schemas import BaseResponse

class MySchema(BaseResponse):
    field1: str
    field2: int
    
    model_config = ConfigDict(
        extra="forbid",              # Don't allow extra fields
        validate_assignment=True,     # Validate on attribute assignment
        str_strip_whitespace=True     # Strip whitespace from strings
    )
```

### `GenericResponse`

Ready-to-use generic schema.

```python
from trustguard.schemas import GenericResponse

class MyResponse(GenericResponse):
    # Add custom fields
    custom_field: str
    timestamp: datetime
    
# Or use directly
schema = GenericResponse

# Fields
# - content: str (required)
# - sentiment: "positive"|"neutral"|"negative" (required)
# - tone: str (required)
# - is_helpful: bool (required)
# - confidence: Optional[float] (optional)
```

## 🛡️ Rules

### Built-in Rules

```python
from trustguard.rules import (
    validate_pii,           # Email/phone detection
    validate_blocklist,      # Forbidden terms
    validate_toxicity,       # Toxic content
    validate_quality,        # Length/repetition
    DEFAULT_RULES           # All default rules
)
```

### Rule Function Signature

```python
from typing import Optional, Dict, Any

def my_rule(
    data: Dict[str, Any],    # Parsed JSON data
    raw_text: str,            # Original text
    context: Optional[Dict] = None  # Context dict
) -> Optional[str]:           # Return error message or None
    """
    Custom validation rule.
    
    Args:
        data: Parsed JSON data from the LLM response
        raw_text: Original raw text (before JSON parsing)
        context: Optional context dictionary with additional data
        
    Returns:
        Error message if validation fails, None if passes
    """
    if "bad" in raw_text:
        return "Found bad content"
    return None
```

### Adding Rules to Guard

```python
from trustguard.rules import DEFAULT_RULES

guard = TrustGuard(
    schema_class=GenericResponse,
    custom_rules=[my_rule] + DEFAULT_RULES  # Add custom rule to defaults
)
```

## ⚖️ Judges

### `BaseJudge`

Abstract base class for all judges.

```python
from trustguard.judges import BaseJudge
from typing import Dict, Any

class MyJudge(BaseJudge):
    def judge(self, text: str) -> Dict[str, Any]:
        """
        Evaluate text safety.
        
        Args:
            text: Text to evaluate
            
        Returns:
            Dictionary with at minimum:
            - "safe": bool
            - "reason": str
        """
        return {
            "safe": True/False,
            "reason": "Explanation",
            "risk_category": "optional",     # e.g., "harassment", "pii"
            "confidence": 0.95,               # 0-1 score
            "severity": "low/medium/high/critical",
            "metadata": {                      # Additional data
                "model": "my-model",
                "latency_ms": 150
            }
        }
    
    async def async_judge(self, text: str) -> Dict[str, Any]:
        """Optional async implementation."""
        return await self.judge(text)
```

### `CallableJudge`

Universal adapter for any function.

```python
from trustguard.judges import CallableJudge

def my_judge_func(text: str) -> Dict[str, Any]:
    return {
        "safe": True,
        "reason": "OK",
        "confidence": 1.0
    }

judge = CallableJudge(
    my_judge_func,
    name="MyJudge",     # Optional custom name
    weight=1.0          # For ensemble voting
)
```

### `OpenAIJudge`

```python
from trustguard.judges import OpenAIJudge

judge = OpenAIJudge(
    api_key="sk-...",           # Optional, uses OPENAI_API_KEY env var
    model="gpt-4o-mini",         # Model name: gpt-4o, gpt-4o-mini, gpt-3.5-turbo
    weight=1.0,                  # Ensemble weight
    config={
        "system_prompt": str,    # Custom system prompt
        "safety_threshold": 0.7, # Confidence threshold (0-1)
        "temperature": 0.0,      # Model temperature (0-2)
        "max_tokens": 500,       # Max response tokens
        "cache_size": 100,       # Result cache size
        "on_error": "allow",     # "allow" or "block"
        "log_errors": True       # Log errors to console
    }
)
```

### `OllamaJudge`

```python
from trustguard.judges import OllamaJudge

judge = OllamaJudge(
    model="phi3",                # Model: phi3, llama3, mistral, etc.
    host="http://localhost:11434", # Ollama server host
    weight=1.0,
    config={
        "prompt_template": "Custom prompt with {text}",
        "temperature": 0.1,
        "max_tokens": 100,
        "top_p": 0.9,
        "on_error": "allow"
    }
)
```

### `AnthropicJudge`

```python
from trustguard.judges import AnthropicJudge

judge = AnthropicJudge(
    api_key="sk-ant-...",
    model="claude-3-haiku-20240307",  # claude-3-haiku, claude-3-sonnet, etc.
    weight=1.0,
    config={
        "system_prompt": "You are a safety expert...",
        "max_tokens": 300,
        "temperature": 0.0,
        "on_error": "allow"
    }
)
```

### `EnsembleJudge`

```python
from trustguard.judges import EnsembleJudge

judge = EnsembleJudge(
    judges=[judge1, judge2, judge3],  # List of judges
    strategy="weighted_vote",          # Strategy name
    config={
        "fail_on_error": False,
        "log_errors": True,
        "on_error": "allow"
    }
)
```

#### Ensemble Strategies

| Strategy | Description | Use Case |
|----------|-------------|----------|
| `majority_vote` | Safe if most judges agree | General purpose |
| `weighted_vote` | Weighted by judge importance | When some judges are more reliable |
| `strict` | Any unsafe = unsafe | Safety-critical applications |
| `lenient` | Any safe = safe | When you want to minimize false positives |

## 🔌 Wrappers

### `BaseWrapper`

Base class for LLM provider wrappers.

```python
from trustguard.wrappers import BaseWrapper

class MyWrapper(BaseWrapper):
    def __init__(self, client, validator, **kwargs):
        super().__init__(client, validator, **kwargs)
        # Custom initialization
    
    def _validate_response(self, response, context=None):
        """Custom response validation."""
        result = self.validator.validate(response, context)
        return result.to_dict()
```

### `OpenAIClient`

Wraps OpenAI client with automatic validation.

```python
from trustguard.wrappers import OpenAIClient
from openai import OpenAI

# Create OpenAI client
client = OpenAI(api_key="sk-...")

# Create validator
validator = TrustGuard(schema_class=GenericResponse)

# Wrap client
wrapped = OpenAIClient(
    client,
    validator,
    auto_validate=True,        # Automatically validate responses
    raise_on_reject=False,      # Raise exception on rejection
    default_context={           # Default context for validation
        "source": "chat-api"
    }
)

# Use exactly like OpenAI client
response = wrapped.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[{"role": "user", "content": "Hello"}],
    response_format={"type": "json_object"},
    validation_context={        # Per-call context
        "user_id": "123"
    }
)

# Check validation result
if hasattr(response, '_validation_result'):
    result = response._validation_result
    if result.is_approved:
        data = result.data
        print(f"✅ Validated: {data['content']}")
```

## 📊 Validators Registry

### `ValidatorRegistry`

Manage and discover validators.

```python
from trustguard.validators import registry, rule

@rule(name="my_rule", priority=1, tags=["safety", "custom"])
def my_rule(data, raw_text, context=None):
    """My custom validation rule."""
    # Rule logic
    pass

# List all validators
all_validators = registry.list()

# List by tag
safety_rules = registry.list(tag="safety")

# Get specific validator
validator = registry.get("my_rule")

# Run validator
result = registry.run("my_rule", data, raw_text)

# Save registry to file
registry.save("validators.json")

# Load registry from file
registry.load("validators.json")
```

### Registry Methods

| Method | Description |
|--------|-------------|
| `register(name, priority, description, tags)` | Register a validator |
| `get(name)` | Get validator by name |
| `list(tag=None)` | List all validators (optionally filtered by tag) |
| `run(name, *args, **kwargs)` | Run a validator by name |
| `save(filepath)` | Save registry metadata to file |
| `load(filepath)` | Load registry metadata from file |

## 🚨 Exceptions

```python
from trustguard.exceptions import (
    TrustGuardError,      # Base exception for all errors
    ConfigurationError,    # Configuration issues
    ValidationError,       # Validation failures
    SchemaError,          # Schema validation errors
    RuleError,            # Rule execution errors
    JudgeError,           # Judge failures
    WrapperError,         # Wrapper issues
    RegistryError         # Registry operations
)

try:
    result = guard.validate(text)
except SchemaError as e:
    print(f"Schema validation failed: {e}")
except JudgeError as e:
    print(f"Judge failed: {e}")
except TrustGuardError as e:
    print(f"Other error: {e}")
```

## 🖥️ CLI

### Commands

```bash
# Show version
trustguard --version

# Run interactive demo
trustguard --demo

# Validate JSON string
trustguard --validate '{"content":"test","sentiment":"neutral","tone":"professional","is_helpful":true}'

# Validate from file
trustguard --file response.json

# Show help
trustguard --help
```

### Options

| Option | Description | Default |
|--------|-------------|---------|
| `--version` | Show version | - |
| `--demo` | Run interactive demo | - |
| `--validate JSON` | Validate JSON string | - |
| `--file PATH` | Validate JSON from file | - |
| `--schema` | Schema to use | "generic" |

## ⚙️ Configuration

### Guard Configuration

```python
config = {
    "enable_judge": True,           # Enable judge (default: True if judge provided)
    "fail_on_judge_error": False,    # Raise exception on judge errors
    "on_error": "allow",              # "allow" or "block" on errors
    "log_errors": True                # Log errors to console
}

guard = TrustGuard(
    schema_class=GenericResponse,
    config=config,
    judge=my_judge
)
```

### Judge Configuration

See individual judge classes for specific options.

Common options across all judges:

```python
judge_config = {
    "on_error": "allow",        # What to do on error ("allow" or "block")
    "log_errors": True,         # Log errors to console
    "cache_size": 100,          # Number of results to cache
    "timeout": 30               # Timeout in seconds
}
```

## 📈 Statistics

```python
# Get current statistics
stats = guard.get_stats()
# {
#     "total_validations": 100,
#     "approved": 85,
#     "rejected": 15,
#     "judge_checks": 30
# }

# Reset statistics
guard.reset_stats()

# Track custom metrics
stats = guard.get_stats()
approval_rate = stats["approved"] / stats["total_validations"]
rejection_rate = stats["rejected"] / stats["total_validations"]
```

## 🔧 Development

### Install Development Dependencies

```bash
pip install -e ".[dev]"
```

### Run Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=trustguard --cov-report=html

# Run specific test
pytest tests/test_core.py::test_schema_validation -v
```

### Code Quality

```bash
# Format code
black trustguard tests

# Sort imports
isort trustguard tests

# Lint
ruff check trustguard tests --fix

# Type check
mypy trustguard
```

### Build Package

```bash
# Clean previous builds
rm -rf dist build *.egg-info

# Build
python -m build

# Check package
twine check dist/*
```

## 📚 Type Hints

trustguard provides full type hints with `py.typed` marker.

```python
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from trustguard.judges import BaseJudge
    from trustguard.types import JudgeResult, ValidationResult

def process_result(result: ValidationResult) -> None:
    if result.is_approved:
        data: dict = result.data
        print(data["content"])
```

## 🎯 Best Practices

### 1. Error Handling

```python
guard = TrustGuard(
    schema_class=GenericResponse,
    config={
        "fail_on_judge_error": False,  # Don't crash on judge errors
        "on_error": "allow"             # Allow on errors
    },
    judge=my_judge
)

try:
    result = guard.validate(text)
    if result.is_rejected:
        # Log rejection
        logger.warning(f"Rejected: {result.log}")
except Exception as e:
    # Log unexpected errors
    logger.error(f"Validation failed: {e}")
```

### 2. Performance Optimization

```python
# Enable caching
judge = OpenAIJudge(config={"cache_size": 1000})

# Use parallel batch validation
report = guard.validate_batch(texts, parallel=True, max_workers=4)

# Monitor performance
stats = guard.get_stats()
avg_judge_time = stats["judge_checks"] / stats["total_validations"]
```

### 3. Testing

```python
def test_custom_rule():
    def always_fail(data, raw_text, context=None):
        return "Failed"
    
    guard = TrustGuard(
        schema_class=GenericResponse,
        custom_rules=[always_fail]
    )
    
    result = guard.validate('{"content":"test"}')
    assert result.is_rejected
    assert result.log == "Failed"
```

## 📋 API Version History

### v0.2.7 (Current)
- Added pluggable judge system
- Added EnsembleJudge
- Added CallableJudge for universal adapter
- Added OpenAI, Ollama, Anthropic judges
- Added batch validation

### v0.1.0
- Initial release
- Core validation engine
- PII detection
- Blocklist filtering
- Schema validation with Pydantic

## 🚀 Quick Reference

```python
# Minimal setup
from trustguard import TrustGuard
from trustguard.schemas import GenericResponse

guard = TrustGuard(schema_class=GenericResponse)
result = guard.validate(response)

# With custom rules
def my_rule(data, raw_text, context):
    if "bad" in raw_text:
        return "Bad content"
    return None

guard = TrustGuard(
    schema_class=GenericResponse,
    custom_rules=[my_rule]
)

# With judge
from trustguard.judges import OpenAIJudge

judge = OpenAIJudge(model="gpt-4o-mini")
guard = TrustGuard(
    schema_class=GenericResponse,
    judge=judge
)

# Batch validation
report = guard.validate_batch(responses)
print(report.summary())

# Get stats
stats = guard.get_stats()
print(f"Approval rate: {stats['approved']/stats['total_validations']:.2%}")
```

## 📚 Related Documentation

- [Quick Start Guide](quickstart.md) - Get started in 5 minutes
- [Core Concepts](concepts.md) - How trustguard works
- [Judge System](judges.md) - Deep dive into judges
- [Examples](examples.md) - Real-world examples
- [Contributing](contributing.md) - How to contribute


