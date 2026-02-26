# Judge System

The judge system is the most powerful feature of trustguard. It allows you to use any AI model as a safety validator.

## 📋 Overview

Judges evaluate text for nuanced safety issues that rules might miss:

- Sarcasm and passive-aggression
- Subtle threats and manipulation
- Complex jailbreak attempts
- Context-aware policy violations
- Hidden PII and sensitive data

## 🏗️ Base Judge Interface

All judges inherit from `BaseJudge`:

```python
from trustguard.judges import BaseJudge

class MyJudge(BaseJudge):
    def judge(self, text: str) -> Dict[str, Any]:
        # Must return at minimum:
        return {
            "safe": True,  # or False
            "reason": "Explanation of verdict"
        }
        
        # Optional fields:
        # "risk_category": str
        # "confidence": float (0-1)
        # "severity": "low"/"medium"/"high"/"critical"
        # "metadata": dict
```

## 🤖 Built-in Judges

### 1. OpenAIJudge

Uses GPT-4 or GPT-3.5 for cloud-based validation.

```python
from trustguard.judges import OpenAIJudge

judge = OpenAIJudge(
    api_key="sk-...",  # or set OPENAI_API_KEY env var
    model="gpt-4o-mini",  # or gpt-4o, gpt-3.5-turbo
    weight=2.0,  # for ensemble voting
    config={
        "system_prompt": "You are a strict safety judge...",
        "safety_threshold": 0.8,
        "temperature": 0.0,
        "max_tokens": 500,
        "cache_size": 100
    }
)

result = judge.judge("Some text to evaluate")
```

### 2. OllamaJudge

Uses local models for privacy-focused validation.

```bash
# First, install and run Ollama
curl -fsSL https://ollama.ai/install.sh | sh
ollama pull phi3
ollama serve
```

```python
from trustguard.judges import OllamaJudge

judge = OllamaJudge(
    model="phi3",  # or llama3, mistral, etc.
    host="http://localhost:11434",
    weight=1.0,
    config={
        "temperature": 0.1,
        "max_tokens": 100,
        "prompt_template": "Custom prompt with {text}"
    }
)
```

### 3. AnthropicJudge

Uses Claude models for constitutional AI validation.

```python
from trustguard.judges import AnthropicJudge

judge = AnthropicJudge(
    api_key="sk-ant-...",
    model="claude-3-haiku-20240307",
    weight=1.0,
    config={
        "system_prompt": "You are a safety expert...",
        "max_tokens": 300
    }
)
```

### 4. CallableJudge (Universal Adapter)

Use ANY function or model as a judge.

```python
from trustguard.judges import CallableJudge

# Hugging Face example
from transformers import pipeline
classifier = pipeline("text-classification", 
                      model="unitary/toxic-bert")

def hf_judge(text):
    result = classifier(text[:512])[0]
    return {
        "safe": result["label"] == "non-toxic",
        "reason": f"Score: {result['score']:.3f}",
        "confidence": result["score"]
    }

judge = CallableJudge(
    hf_judge,
    name="HuggingFaceToxicBERT",
    weight=1.5
)

# Groq example
from groq import Groq
client = Groq(api_key="gsk_...")

def groq_judge(text):
    response = client.chat.completions.create(
        model="llama3-70b-8192",
        messages=[{"role": "user", "content": f"Check safety: {text}"}],
        response_format={"type": "json_object"}
    )
    return json.loads(response.choices[0].message.content)

judge = CallableJudge(groq_judge, name="GroqLlama3")
```

### 5. EnsembleJudge

Combine multiple judges for maximum accuracy.

```python
from trustguard.judges import EnsembleJudge

# Create individual judges
judge1 = OpenAIJudge(model="gpt-4o-mini", weight=2.0)
judge2 = OllamaJudge(model="phi3", weight=1.0)
judge3 = CallableJudge(my_local_judge, weight=1.5)

# Combine them
ensemble = EnsembleJudge(
    [judge1, judge2, judge3],
    strategy="weighted_vote",  # or majority_vote, strict, lenient
    config={"fail_on_error": False, "log_errors": True}
)

# Use in guard
from trustguard import TrustGuard
from trustguard.schemas import GenericResponse

guard = TrustGuard(
    schema_class=GenericResponse,
    judge=ensemble
)
```

## 🎯 Choosing the Right Judge

| Judge | Best For | Trade-offs |
|-------|----------|------------|
| **OpenAIJudge** | Production apps | Cost, internet required |
| **OllamaJudge** | Privacy, offline | Requires local GPU/RAM |
| **AnthropicJudge** | Safety-critical | Cost, slower |
| **CallableJudge** | Custom models | You implement logic |
| **EnsembleJudge** | Maximum accuracy | Multiple API calls |

## 🔧 Judge Configuration

### Common Config Options

| Option | Description | Default |
|--------|-------------|---------|
| `on_error` | What to do on error ("allow"/"block") | "allow" |
| `log_errors` | Log errors to console | True |
| `cache_size` | Number of results to cache | 100 |
| `timeout` | Timeout in seconds | 30 |

### Judge-Specific Options

**OpenAIJudge:**
- `system_prompt` - Custom system prompt
- `safety_threshold` - Confidence threshold (0-1)
- `temperature` - Model temperature (0-2)
- `max_tokens` - Max tokens in response

**OllamaJudge:**
- `prompt_template` - Custom prompt template
- `temperature` - Model temperature
- `top_p` - Nucleus sampling parameter

**AnthropicJudge:**
- `system_prompt` - Custom system prompt
- `max_tokens` - Max tokens in response

## 📊 Judge Output

All judges return a normalized dictionary:

```python
{
    "safe": True,  # boolean
    "reason": "Detailed explanation",
    "risk_category": "harassment",  # optional
    "confidence": 0.95,  # optional, 0-1
    "severity": "high",  # optional: low/medium/high/critical
    "metadata": {  # optional
        "model": "gpt-4o-mini",
        "latency_ms": 450
    }
}
```

## 🎯 Best Practices

### 1. Cascading Validation

Use cheap judges first, expensive ones only when needed:

```python
def cascading_validate(text):
    # Fast local judge
    local_result = ollama_judge.judge(text)
    if not local_result["safe"] and local_result["confidence"] > 0.9:
        return local_result
    
    # Expensive cloud judge for uncertain cases
    return openai_judge.judge(text)
```

### 2. Ensemble Voting

Combine multiple judges for higher accuracy:

```python
ensemble = EnsembleJudge([
    OpenAIJudge(model="gpt-4o-mini", weight=2.0),
    OllamaJudge(model="llama3", weight=1.0),
    CallableJudge(my_rule_judge, weight=1.0)
], strategy="weighted_vote")
```

### 3. Caching

Enable caching for repeated texts:

```python
judge = OpenAIJudge(
    config={"cache_size": 1000}  # Cache last 1000 results
)
```

### 4. Error Handling

Configure how judges handle errors:

```python
judge = OpenAIJudge(
    config={
        "on_error": "block",  # Block on errors
        "log_errors": True
    }
)

# Or in guard
guard = TrustGuard(
    schema_class=GenericResponse,
    judge=judge,
    config={"fail_on_judge_error": True}  # Raise on errors
)
```

## 📈 Performance Tips

1. **Use local judges** for high-volume, privacy-sensitive data
2. **Cache results** for repeated queries
3. **Batch validation** for multiple texts
4. **Set appropriate timeouts** to avoid hanging
5. **Use smaller models** (phi3, gpt-4o-mini) for speed
6. **Parallelize** independent judge calls

## 🚀 Advanced Examples

### Content Moderation System

```python
class ContentModerator:
    def __init__(self):
        self.judge = EnsembleJudge([
            OpenAIJudge(model="gpt-4o-mini", weight=2.0),
            CallableJudge(self.keyword_check, weight=1.0)
        ])
        self.guard = TrustGuard(
            schema_class=GenericResponse,
            judge=self.judge
        )
    
    def keyword_check(self, text):
        blocked = ["spam", "scam", "fraud"]
        if any(word in text.lower() for word in blocked):
            return {"safe": False, "reason": "Blocked keyword"}
        return {"safe": True}
    
    def moderate(self, text):
        result = self.guard.validate(text)
        return {
            "approved": result.is_approved,
            "reason": result.log,
            "data": result.data if result.is_approved else None
        }
```

### PII Redaction System

```python
def pii_judge(text):
    import re
    patterns = {
        'email': r'[\w\.-]+@[\w\.-]+\.\w+',
        'phone': r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',
        'ssn': r'\b\d{3}-\d{2}-\d{4}\b'
    }
    
    found = []
    for pii_type, pattern in patterns.items():
        if re.search(pattern, text):
            found.append(pii_type)
    
    if found:
        return {
            "safe": False,
            "reason": f"PII detected: {', '.join(found)}",
            "risk_category": "pii_leak"
        }
    return {"safe": True, "reason": "No PII found"}

judge = CallableJudge(pii_judge)
guard = TrustGuard(schema_class=GenericResponse, judge=judge)
```

## 🔄 Judge Lifecycle

1. **Initialization** - Judge is created with config
2. **Validation** - `judge()` method called for each text
3. **Caching** - Results optionally cached
4. **Cleanup** - Resources released when done

## 📊 Monitoring Judges

```python
# Track judge performance
stats = {
    "total_calls": 0,
    "avg_latency": 0,
    "error_rate": 0,
    "cache_hit_rate": 0
}

class MonitoredJudge(BaseJudge):
    def __init__(self, judge):
        self.judge = judge
        self.stats = {"calls": 0, "errors": 0, "total_latency": 0}
    
    def judge(self, text):
        import time
        start = time.time()
        try:
            result = self.judge.judge(text)
            self.stats["calls"] += 1
            self.stats["total_latency"] += time.time() - start
            return result
        except Exception as e:
            self.stats["errors"] += 1
            raise
```

## 🎨 Creating Custom Judges

### Step 1: Inherit from BaseJudge

```python
from trustguard.judges import BaseJudge

class MyCustomJudge(BaseJudge):
    def __init__(self, api_key=None, weight=1.0, config=None):
        super().__init__(config)
        self.api_key = api_key
        self.weight = weight
        # Initialize your client
```

### Step 2: Implement judge() method

```python
def judge(self, text: str) -> Dict[str, Any]:
    try:
        # Your validation logic
        result = self._call_api(text)
        return {
            "safe": result["safe"],
            "reason": result["reason"],
            "risk_category": result.get("category"),
            "confidence": result.get("confidence", 1.0),
            "severity": result.get("severity", "low"),
            "metadata": {"model": "my-model"}
        }
    except Exception as e:
        # Handle errors gracefully
        return {
            "safe": self.config.get("on_error", "allow") == "allow",
            "reason": f"Judge error: {e}",
            "risk_category": "system_error",
            "confidence": 0.0,
            "severity": "low"
        }
```

### Step 3: Add to judges module

```python
# In trustguard/judges/__init__.py
try:
    from .my_judge import MyCustomJudge
except ImportError:
    class MyCustomJudge:
        def __init__(self, *args, **kwargs):
            raise ImportError(
                "MyCustomJudge requires extra dependencies. "
                "Install with: pip install trustguard[my]"
            )
```

## 🚀 Next Steps

- [API Reference](api.md) - Complete judge API documentation
- [Examples](examples.md) - More real-world examples
- [Contributing](contributing.md) - Add your own judge
- [Quick Start](quickstart.md) - Get started quickly

## 📚 Related Topics

- [Rules System](rules.md) - Fast deterministic checks
- [Schema Validation](schemas.md) - Define response structures
- [Core Concepts](concepts.md) - How trustguard works

## 📈 What's Next?

- Learn about [Schemas](schemas.md) - Define your own response structures
- Explore the [Judge System](judges.md) - Use any model as a judge
- Check out [Examples](examples.md) - See real-world use cases
- Read the [API Reference](api.md) - Detailed documentation

## 🆘 Getting Help

- [GitHub Issues](https://github.com/Dr-Mo-Khalaf/trustguard/issues)
- [Discussions](https://github.com/Dr-Mo-Khalaf/trustguard/discussions)