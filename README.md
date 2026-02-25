# trustguard 🔒

<div align="center">

**Intelligent validation for LLM outputs with pluggable judge system. Lightweight, schema-first safety checks for AI applications.**

[![PyPI version](https://badge.fury.io/py/trustguard.svg)](https://badge.fury.io/py/trustguard)
[![Python Versions](https://img.shields.io/pypi/pyversions/trustguard.svg)](https://pypi.org/project/trustguard/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

</div>

## ✨ Features

- **🚀 Lightweight & Fast** - Pure Python, minimal dependencies
- **📋 Schema Validation** - Enforce JSON structure with Pydantic
- **🛡️ Built-in Rules** - PII detection, blocklist, toxicity checks
- **🤖 Pluggable Judge System** - Use ANY model as a safety judge
- **🎯 Universal Adapter** - Wrap Hugging Face, Groq, internal APIs
- **🔀 Ensemble Judges** - Combine multiple judges for maximum accuracy
- **🔌 Provider Wrappers** - One-line integration with OpenAI/Anthropic
- **📊 Batch Validation** - Validate multiple responses with reporting
- **🎨 Extensible** - Easy to add custom rules and judges

## 📦 Installation

```bash
# Basic installation
pip install trustguard

# With judge support
pip install trustguard[openai]      # OpenAI GPT-4/GPT-3.5 judges
pip install trustguard[anthropic]   # Anthropic Claude judges
pip install trustguard[ai]          # Local Ollama judges
pip install trustguard[all]          # Everything
```

## 🚀 Quick Start

### Basic Validation

```python
from trustguard import TrustGuard
from trustguard.schemas import GenericResponse

# Initialize with a schema
guard = TrustGuard(schema_class=GenericResponse)

result = guard.validate('''
Here's the response:
```json
{
    "content": "I can help you reset your password",
    "sentiment": "positive",
    "tone": "helpful",
    "is_helpful": true
}
```
''')

if result.is_approved:
    print(f"✅ Safe: {result.data}")
else:
    print(f"🛑 Blocked: {result.log}")
```

### Using a Judge (GPT-4 for Nuance Detection)

```python
from trustguard import TrustGuard
from trustguard.schemas import GenericResponse
from trustguard.judges import OpenAIJudge

# Create a GPT-4 judge
judge = OpenAIJudge(
    model="gpt-4o-mini",
    config={"system_prompt": "You are a strict safety judge."}
)

# Add it to your guard
guard = TrustGuard(
    schema_class=GenericResponse,
    judge=judge  # <-- Now catches sarcasm and subtle threats!
)

# This would pass basic rules but get caught by the judge
result = guard.validate('{"content": "Sure, I can help... you idiot."}')
print(result.log)  # "Judge [harassment]: Text contains insult"
```

### Using ANY Model with CallableJudge

```python
from trustguard import TrustGuard
from trustguard.judges import CallableJudge

# Hugging Face example
from transformers import pipeline
classifier = pipeline("text-classification", model="unitary/toxic-bert")

def hf_judge(text):
    result = classifier(text[:512])[0]
    return {
        "safe": result["label"] == "non-toxic",
        "reason": f"Score: {result['score']:.3f}"
    }

guard = TrustGuard(
    schema_class=GenericResponse,
    judge=CallableJudge(hf_judge, name="HuggingFaceToxicBERT")
)
```

### Ensemble of Judges

```python
from trustguard.judges import EnsembleJudge, OpenAIJudge, CallableJudge

# Combine multiple judges with weighted voting
ensemble = EnsembleJudge([
    OpenAIJudge(model="gpt-4o-mini", weight=2.0),
    CallableJudge(my_local_judge, weight=1.0),
    CallableJudge(my_rule_judge, weight=1.0)
], strategy="weighted_vote")

guard = TrustGuard(schema_class=GenericResponse, judge=ensemble)
```

## 🏗️ Architecture

```
trustguard/
├── core/          # Core validation engine
├── rules/         # Built-in validation rules
├── schemas/       # Pydantic schemas
├── validators/    # Validator registry
├── wrappers/      # LLM provider wrappers
└── judges/        # Pluggable judge system
    ├── base.py           # Abstract base class
    ├── custom.py         # Universal adapter (ANY model)
    ├── openai.py         # GPT-4/GPT-3.5 judges
    ├── ollama.py         # Local model judges
    ├── anthropic.py      # Claude judges
    └── ensemble.py       # Combine multiple judges
```

## 📈 Roadmap

- [x] Core validation engine
- [x] PII detection & blocklist
- [x] OpenAI wrapper
- [x] Pluggable judge system
- [x] Universal CallableJudge (any model)
- [x] Ensemble judges
- [ ] Streaming support (v0.3.0)
- [ ] Web UI dashboard (v0.4.0)
- [ ] A/B testing framework (v0.5.0)

## 📄 License

MIT License - see [LICENSE](LICENSE) file.

---

<div align="center">
Made with ❤️ for the AI community
</div>
