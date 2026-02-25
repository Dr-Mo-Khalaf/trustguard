Here's the complete corrected `index.md` file. Copy all of this and paste it into your Notepad file:

```markdown
# trustguard Documentation

<div align="center">

**Intelligent validation for LLM outputs with pluggable judge system**

[![PyPI version](https://badge.fury.io/py/trustguard.svg)](https://badge.fury.io/py/trustguard)
[![Python Versions](https://img.shields.io/pypi/pyversions/trustguard.svg)](https://pypi.org/project/trustguard/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

</div>

## 📚 Table of Contents

- [Quick Start Guide](quickstart.md)
- [Core Concepts](concepts.md)
- [Schema Validation](schemas.md)
- [Rules System](rules.md)
- [Judge System](judges.md)
- [API Reference](api.md)
- [Examples](examples.md)
- [Contributing](contributing.md)

## 🎯 What is trustguard?

trustguard is a lightweight, extensible Python library that validates LLM (Large Language Model) outputs. It combines fast rule-based validation with an intelligent pluggable judge system that can use any AI model for nuanced content evaluation.

### Key Features

| Feature | Description |
|---------|-------------|
| **🚀 Lightweight** | Pure Python, minimal dependencies |
| **📋 Schema Validation** | Enforce JSON structure with Pydantic |
| **🛡️ Built-in Rules** | PII detection, blocklist, toxicity checks |
| **🤖 Pluggable Judges** | Use ANY model as a safety judge |
| **🎯 Universal Adapter** | Wrap Hugging Face, Groq, internal APIs |
| **🔀 Ensemble Judges** | Combine multiple judges for accuracy |
| **📊 Batch Validation** | Validate multiple responses |
| **🔌 Provider Wrappers** | OpenAI/Anthropic integration |

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

## 📦 Installation

```bash
# Basic installation
pip install trustguard

# With judge support
pip install trustguard[openai]      # OpenAI GPT-4/GPT-3.5 judges
pip install trustguard[anthropic]   # Anthropic Claude judges
pip install trustguard[ai]          # Local Ollama judges
pip install trustguard[all]         # Everything
```

## 🚀 Quick Example

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

## 📖 Why trustguard?

### The Problem

LLMs can generate harmful, biased, or unsafe content. Traditional validation methods are either too simple (regex) or too complex (enterprise platforms).

### The Solution

trustguard provides a **middle path**:
- ✅ **Simple to use** - One-line initialization
- ✅ **Fast** - Microsecond rule checking
- ✅ **Smart** - Optional AI judges for nuance
- ✅ **Private** - Local judges keep data secure
- ✅ **Extensible** - Add your own rules and judges

## 🎯 Use Cases

| Use Case | Description |
|----------|-------------|
| **Chatbots** | Prevent toxic responses, detect PII |
| **Code Generation** | Block dangerous code patterns |
| **Content Moderation** | Filter harmful content |
| **Customer Support** | Ensure professional responses |
| **Education** | Keep AI tutors safe and appropriate |
| **Healthcare** | Validate medical information |

## 🔄 How It Works

1. **Input** - Raw LLM response (JSON string)
2. **Extract** - JSON parsing with markdown support
3. **Validate** - Schema validation with Pydantic
4. **Check** - Rule-based safety checks
5. **Judge** - Optional AI-powered evaluation
6. **Result** - Approved or rejected with explanation

## 🌟 Why Choose trustguard?

| Feature | trustguard | Custom Code | Enterprise Platforms |
|---------|------------|-------------|----------------------|
| **Setup Time** | 5 minutes | Days | Hours |
| **Cost** | Free | Developer time | $$$ |
| **Dependencies** | Minimal | Custom | Heavy |
| **AI Integration** | Plug-and-play | Custom coding | Limited |
| **Privacy** | Local judges | Custom | Usually cloud |
| **Extensibility** | Excellent | Good | Limited |

## 📈 Roadmap

- ✅ **v0.1.0** - Core validation, rules system
- ✅ **v0.2.0** - Pluggable judges, ensemble system
- 🔜 **v0.3.0** - Streaming support
- 🔜 **v0.4.0** - Web UI dashboard
- 🔜 **v0.5.0** - A/B testing framework
- 🔜 **v0.6.0** - Batch processing optimization

## 🤝 Contributing

We welcome contributions! See our [Contributing Guide](contributing.md) for:

- Adding new rules
- Creating custom judges
- Improving documentation
- Reporting bugs
- Suggesting features

## 📚 Next Steps

- [Quick Start Guide](quickstart.md) - Get up and running in 5 minutes
- [Core Concepts](concepts.md) - Understand how trustguard works
- [Judge System](judges.md) - Learn about pluggable judges
- [Examples](examples.md) - See real-world examples

## 📊 Project Stats

- **Stars**: ⭐ 0 (you can be the first!)
- **Contributors**: 👥 1
- **Version**: 📦 0.2.0
- **License**: 📄 MIT
- **Python**: 🐍 3.8+

## 🆘 Support

- [GitHub Issues](https://github.com/yourusername/trustguard/issues) - Bug reports, feature requests
- [Discussions](https://github.com/yourusername/trustguard/discussions) - Questions, ideas
- [Contributing Guide](contributing.md) - How to help

## 📄 License

MIT License - see [LICENSE](../LICENSE) file for details.

---

<div align="center">
Made with ❤️ for the AI community
</div>
```

*