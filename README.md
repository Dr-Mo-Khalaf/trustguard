# 🔒 trustguard

<div align="center">

**Bidirectional validation for LLM applications - secure both input and output with pluggable AI judges**

[![PyPI version](https://img.shields.io/pypi/v/trustguard)](https://pypi.org/project/trustguard/)
[![Python Versions](https://img.shields.io/pypi/pyversions/trustguard.svg?cacheSeconds=1)](https://pypi.org/project/trustguard/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Documentation](https://img.shields.io/badge/docs-github.io-blue)](https://github.com/Dr-Mo-Khalaf/trustguard/blob/main/docs/index.md)
<!-- [![GitHub Stars](https://img.shields.io/github/stars/Dr-Mo-Khalaf/trustguard?style=social)](https://github.com/Dr-Mo-Khalaf/trustguard) -->
![Downloads](https://pepy.tech/badge/trustguard)

</div>

**Lightweight, schema-first safety checks for AI applications**

[Key Features](#key-features) •
[Quick Start](#quick-start) •
[Documentation](#documentation) •
[Installation](#installation) •
[Examples](#examples) •
[Contributing](#contributing)

</div>

---

## 📋 Overview

trustguard is a lightweight, extensible Python framework that provides comprehensive validation for Large Language Model (LLM) applications. It operates at both ends of the LLM pipeline:

- **Input Validation**: Blocks harmful prompts, jailbreak attempts, and toxic user content before they reach your LLM
- **Output Validation**: Filters unsafe responses, PII leakage, and policy violations before they reach your users

The framework combines two complementary approaches:
- **Fast rule-based validation** (microseconds) for deterministic checks like PII detection, blocklist filtering, and toxicity detection
- **Pluggable judge system** that can use any AI model (OpenAI GPT-4, Anthropic Claude, local Ollama, or custom models) for nuanced, context-aware evaluation

With its modular architecture, trustguard is easy to extend with custom rules, judges, and schemas - making it suitable for everything from simple chatbots to complex enterprise AI applications.

---

## ✨ Key Features

| Feature | Description |
|---------|-------------|
| **🚀 Lightweight** | Pure Python, minimal dependencies, no external services required |
| **📋 Schema Validation** | Enforce JSON structure with Pydantic V2 |
| **🛡️ Built-in Rules** | PII detection, blocklist filtering, toxicity checks, quality validation |
| **🤖 Pluggable Judges** | Use ANY AI model as a safety validator |
| **🎯 Universal Adapter** | Wrap Hugging Face, Groq, internal APIs with `CallableJudge` |
| **🔀 Ensemble Judges** | Combine multiple judges with voting strategies for maximum accuracy |
| **🔌 Provider Wrappers** | One-line integration with OpenAI, Anthropic, and local Ollama |
| **📊 Batch Validation** | Validate multiple responses with detailed reporting |
| **📈 Statistics** | Built-in metrics tracking for monitoring and optimization |
| **🖥️ CLI** | Command-line interface for quick testing and integration |

---

## 🏗️ Architecture

```
Raw Input → JSON Extraction → Schema Validation → Rules → Judge → Result
```

```
trustguard/
├── core/          # Core validation engine
├── rules/         # Built-in validation rules
│   ├── pii.py     # Email/phone detection
│   ├── blocklist.py # Forbidden terms
│   ├── toxicity.py # Harmful content
│   └── quality.py # Length/repetition checks
├── schemas/       # Pydantic schemas
├── judges/        # Pluggable judge system
│   ├── base.py    # Abstract base class
│   ├── openai.py  # GPT-4/GPT-3.5 judges
│   ├── ollama.py  # Local model judges
│   ├── anthropic.py # Claude judges
│   ├── custom.py  # Universal adapter
│   └── ensemble.py # Combine multiple judges
└── wrappers/      # LLM provider wrappers
```

---

## 📦 Installation

### Basic Installation

```bash
pip install trustguard
```

### With Judge Support

```bash
# OpenAI judges (GPT-4, GPT-3.5)
pip install trustguard[openai]

# Anthropic Claude judges
pip install trustguard[anthropic]

# Local Ollama judges
pip install trustguard[ai]

# Everything
pip install trustguard[all]
```

### Development Installation

```bash
git clone https://github.com/Dr-Mo-Khalaf/trustguard.git
cd trustguard
pip install -e ".[dev]"
```

### Production with uv (Recommended)

```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create virtual environment
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install trustguard
uv pip install trustguard
```

---

## 🚀 Quick Start

### 1. Basic Validation

```python
from trustguard import TrustGuard
from trustguard.schemas import GenericResponse

# Initialize with a schema
guard = TrustGuard(schema_class=GenericResponse)

# Validate an LLM response
result = guard.validate('''
{
    "content": "I can help you reset your password",
    "sentiment": "positive",
    "tone": "helpful",
    "is_helpful": true
}
''')

if result.is_approved:
    print(f"✅ Safe: {result.data}")
else:
    print(f"🛑 Blocked: {result.log}")
```

### 2. Add Custom Rules

```python
def check_profanity(data, raw_text, context=None):
    profanity_list = ["badword1", "badword2"]
    content = data.get("content", "").lower()
    
    for word in profanity_list:
        if word in content:
            return f"Profanity detected: {word}"
    return None

guard = TrustGuard(
    schema_class=GenericResponse,
    custom_rules=[check_profanity]
)
```

### 3. Use an AI Judge

```python
from trustguard.judges import OpenAIJudge

# Create a GPT-4 judge
judge = OpenAIJudge(
    model="gpt-4o-mini",
    config={"system_prompt": "You are a strict safety judge."}
)

guard = TrustGuard(
    schema_class=GenericResponse,
    judge=judge
)

# Catches nuanced issues
result = guard.validate('{"content": "Sure, I can help... you idiot."}')
print(result.log)  # "Judge [harassment]: Text contains insult"
```

---

## 🤖 Judge System

### Available Judges

| Judge | Description | Best For |
|-------|-------------|----------|
| `OpenAIJudge` | GPT-4/GPT-3.5 | Production apps, high accuracy |
| `OllamaJudge` | Local models (Llama, Phi) | Privacy, offline, free |
| `AnthropicJudge` | Claude models | Constitutional AI |
| `CallableJudge` | Any function | Universal adapter |
| `EnsembleJudge` | Combine multiple | Maximum accuracy |

### Ensemble Example

```python
from trustguard.judges import EnsembleJudge, OpenAIJudge, CallableJudge

ensemble = EnsembleJudge([
    OpenAIJudge(model="gpt-4o-mini", weight=2.0),
    CallableJudge(my_local_judge, weight=1.0),
    CallableJudge(my_rule_judge, weight=1.0)
], strategy="weighted_vote")  # or majority_vote, strict, lenient

guard = TrustGuard(schema_class=GenericResponse, judge=ensemble)
```

### Custom Judge

```python
from trustguard.judges import BaseJudge

class MyJudge(BaseJudge):
    def judge(self, text: str) -> Dict[str, Any]:
        # Your logic here
        return {
            "safe": True,
            "reason": "Explanation",
            "confidence": 0.95
        }
```

## 🔥 **Real-World Example: Safe Chatbot with GLM-5**

This complete example shows how to build a production-ready chatbot with built-in safety validation:

### ✨ Features Demonstrated
- ✅ **GLM-5 integration** via HuggingFace Inference API
- ✅ **Custom safety judge** using the same model
- ✅ **Conversation history** management
- ✅ **JSON response** formatting
- ✅ **Follow-up shortcuts** for natural conversation

### 🚀 Quick Start

```bash
# Create project
uv init my-chatbot && cd my-chatbot
uv add trustguard huggingface_hub python-dotenv

# Add your HuggingFace token
echo "HF_TOKEN=hf_your_token_here" > .env

# Create and run the chatbot
uv run python chatbot.py
```

### 📝 Complete Code (`chatbot.py`)

```python
import os, json
from dotenv import load_dotenv
from huggingface_hub import InferenceClient
from trustguard import TrustGuard
from trustguard.schemas import GenericResponse
from trustguard.judges import BaseJudge

load_dotenv()

# ── GLM-5 Client ────────────────────────────────────────────────────
client = InferenceClient(
    model="zai-org/GLM-5",
    token=os.getenv("HF_TOKEN"),
)

def llm(messages, max_tokens=500):
    response = client.chat_completion(messages=messages, max_tokens=max_tokens)
    return response.choices[0].message.content


# ── Safety Judge (also GLM-5) ───────────────────────────────────────
class SafetyJudge(BaseJudge):
    def judge(self, text):
        raw = llm([
            {"role": "system", "content": (
                "You are a safety judge. Mark unsafe ONLY if it contains: "
                "hate speech, violence, self-harm, explicit sexual content, or exploits.\n"
                "Coding help, math, and general knowledge are always SAFE.\n"
                'Reply ONLY with JSON: {"safe": bool, "reason": "...", "confidence": 0.0-1.0}'
            )},
            {"role": "user", "content": f"Evaluate:\n\n{text}"},
        ], max_tokens=100)

        try:
            s, e = raw.find("{"), raw.rfind("}") + 1
            return json.loads(raw[s:e])
        except Exception:
            return {"safe": True, "reason": "Could not parse", "confidence": 0.5}


# ── TrustGuard Setup ─────────────────────────────────────────────────
guard = TrustGuard(schema_class=GenericResponse, judge=SafetyJudge())

SYSTEM = 'Reply in JSON: {"content": "...", "sentiment": "positive|neutral|negative", "tone": "helpful", "is_helpful": true}'

# ── Chat Loop ────────────────────────────────────────────────────────
print("🤖 Safe Chatbot (GLM-5 + TrustGuard) | type 'quit' to exit\n")

history = []
last_reply = None
follow_ups = {"yes", "more", "ok", "continue", "go on"}

while True:
    user = input("You: ").strip()
    if user.lower() in ("quit", "exit", ""): break

    # Follow-up shortcut
    if user.lower() in follow_ups and last_reply:
        user = f"Tell me more about: {last_reply}"

    # Get response from GLM-5
    history.append({"role": "user", "content": user})
    raw = llm([{"role": "system", "content": SYSTEM}] + history)

    # Extract JSON
    try:
        s, e = raw.find("{"), raw.rfind("}") + 1
        json_str = raw[s:e]
        json.loads(json_str)
    except Exception:
        json_str = json.dumps({"content": raw.strip(), "sentiment": "neutral", 
                               "tone": "helpful", "is_helpful": True})

    # Validate with TrustGuard
    result = guard.validate(json_str)

    if result.is_approved:
        last_reply = result.data["content"]
        history.append({"role": "assistant", "content": last_reply})
        print(f"Bot: {last_reply}\n")
    else:
        history.pop()  # Remove unsafe turn
        print(f"Bot: 🛑 Blocked — {result.log}\n")
```

### 💡 How It Works

1. **User input** → Added to conversation history
2. **GLM-5** → Generates JSON response
3. **Safety judge** → Validates response (same model)
4. **TrustGuard** → Blocks unsafe responses automatically


---

## 📊 Batch Validation

```python
# Validate multiple responses at once
responses = [response1, response2, response3]
report = guard.validate_batch(responses, parallel=True, max_workers=4)

print(report.summary())
# Total: 3 | Passed: 2 | Failed: 1
# Top failures:
#   - PII Detected: 1

# Convert to pandas DataFrame
df = report.to_dataframe()

# Convert to polars DataFrame
pl_df = report.to_polars()
```

---

## 📈 Statistics

```python
# Track validation metrics
stats = guard.get_stats()
# {
#     "total_validations": 100,
#     "approved": 85,
#     "rejected": 15,
#     "judge_checks": 30
# }

guard.reset_stats()  # Reset counters
```

---

## 🖥️ CLI Usage

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

---

## 📚 Documentation

Comprehensive documentation is available at [docs](https://https://github.com/Dr-Mo-Khalaf/trustguard/trustguard/docs/index.md)

| Guide | Description |
|-------|-------------|
| [Quick Start](https://https://github.com/Dr-Mo-Khalaf/trustguard/trustguard/docsdocs/quickstart.md) | Get up and running in 5 minutes |
| [Core Concepts](https://https://github.com/Dr-Mo-Khalaf/trustguard/trustguard/docsdocs/concepts.md) | Understand how trustguard works |
| [Schema Validation](https://https://github.com/Dr-Mo-Khalaf/trustguard/trustguard/docsdocs/schemas.md) | Define your own response structures |
| [Rules System](https://https://github.com/Dr-Mo-Khalaf/trustguard/trustguard/docsdocs/rules.md) | Built-in validation rules |
| [Judge System](https://https://github.com/Dr-Mo-Khalaf/trustguard/trustguard/docsdocs/judges.md) | Deep dive into AI judges |
| [API Reference](https://https://github.com/Dr-Mo-Khalaf/trustguard/trustguard/docsdocs/api.md) | Complete API documentation |
| [Examples](https://https://github.com/Dr-Mo-Khalaf/trustguard/trustguard/docsdocs/examples.md) | Real-world use cases |
| [Contributing](https://https://github.com/Dr-Mo-Khalaf/trustguard/trustguard/docsdocs/contributing.md) | How to contribute |

---

## 🎯 Use Cases

| Use Case | Example |
|----------|---------|
| **Chatbots** | Prevent toxic responses, detect PII |
| **Code Generation** | Block dangerous code patterns |
| **Content Moderation** | Filter harmful content |
| **Customer Support** | Ensure professional responses |
| **Education** | Keep AI tutors safe and appropriate |
| **Healthcare** | Validate medical information |

---

## 🔧 Configuration

### Guard Configuration

```python
config = {
    "fail_on_judge_error": False,  # Don't crash on judge errors
    "on_error": "allow"             # Allow on errors
}

guard = TrustGuard(
    schema_class=GenericResponse,
    config=config,
    judge=my_judge
)
```

### Judge Configuration

```python
judge = OpenAIJudge(
    config={
        "cache_size": 1000,     # Cache last 1000 results
        "timeout": 30,           # Timeout in seconds
        "on_error": "allow",     # What to do on error
        "log_errors": True       # Log errors to console
    }
)
```

---

## 🚀 Performance

| Operation | Speed |
|-----------|-------|
| Rules | Microseconds |
| Local Judge (Ollama) | 50-100ms |
| Cloud Judge (GPT-4o-mini) | 200-500ms |
| Batch Validation | Parallel by default |

### Optimization Tips

1. **Use local judges** for high-volume, privacy-sensitive data
2. **Cache results** for repeated queries
3. **Batch validation** for multiple texts
4. **Set appropriate timeouts** to avoid hanging
5. **Use smaller models** (phi3, gpt-4o-mini) for speed

---

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=trustguard --cov-report=html

# Run specific test
pytest tests/test_core.py::test_schema_validation -v
```

---

## 🤝 Contributing

We welcome contributions! Here's how you can help:

- 🐛 **Report bugs** - Open an issue
- 💡 **Suggest features** - Start a discussion
- 📝 **Improve documentation** - Submit a PR
- 🔧 **Add new rules or judges** - Follow our [contributing guide](https://https://github.com/Dr-Mo-Khalaf/trustguard/trustguard/docs/contributing.md)
- 🌟 **Star the project** - Show your support

See [CONTRIBUTING.md](https://https://github.com/Dr-Mo-Khalaf/trustguard/trustguard/docs/contributing.md) for detailed guidelines.

---

## 📄 License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

---

## 👥 Authors

- **Dr-Mo-Khalaf** - [@github](https://github.com/Dr-Mo-Khalaf)

---

## 🙏 Acknowledgments

- [Pydantic](https://docs.pydantic.dev/) - Schema validation
- [Ollama](https://ollama.ai/) - Local model support
- [OpenAI](https://openai.com/) - GPT integration
- [Anthropic](https://www.anthropic.com/) - Claude integration


---

## 📊 Project Stats

| Metric | Value |
|--------|-------|
| **PyPI Downloads** | [![Downloads](https://pepy.tech/badge/trustguard)](https://pepy.tech/project/trustguard) |
| **GitHub Stars** | [![GitHub stars](https://img.shields.io/github/stars/Dr-Mo-Khalaf/trustguard)](https://github.com/Dr-Mo-Khalaf/trustguard) |
| **Python Versions** | 3.8+ |
| **License** | Apache License 2.0 |
| **Last Release** | v0.2.3 |

---

## 📬 Support
- [Documentation](https://github.com/Dr-Mo-Khalaf/trustguard/blob/main/docs/index.md) - Guides and API reference
- [GitHub Issues](https://github.com/Dr-Mo-Khalaf/trustguard/issues) - Bug reports, feature requests
- [Discussions](https://github.com/Dr-Mo-Khalaf/trustguard/discussions) - Questions, ideas


---

<div align="center">

Copyright 2026 Khalaf

Licensed under the Apache License, Version 2.0

If you find this project useful, please give it a ⭐ on [GitHub](https://github.com/Dr-Mo-Khalaf/trustguard)!

</div>
```
