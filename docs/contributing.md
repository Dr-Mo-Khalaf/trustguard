# Contributing to trustguard

We love your input! We want to make contributing to trustguard as easy and transparent as possible.

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Development Process](#development-process)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Making Changes](#making-changes)
- [Adding New Rules](#adding-new-rules)
- [Adding New Judges](#adding-new-judges)
- [Testing Guidelines](#testing-guidelines)
- [Documentation](#documentation)
- [Pull Request Process](#pull-request-process)
- [Style Guidelines](#style-guidelines)
- [Release Process](#release-process)
- [Getting Help](#getting-help)

## 📜 Code of Conduct

### Our Pledge

In the interest of fostering an open and welcoming environment, we as contributors and maintainers pledge to making participation in our project and our community a harassment-free experience for everyone, regardless of age, body size, disability, ethnicity, gender identity and expression, level of experience, nationality, personal appearance, race, religion, or sexual identity and orientation.

### Our Standards

Examples of behavior that contributes to creating a positive environment include:

* Using welcoming and inclusive language
* Being respectful of differing viewpoints and experiences
* Gracefully accepting constructive criticism
* Focusing on what is best for the community
* Showing empathy towards other community members

Examples of unacceptable behavior include:

* The use of sexualized language or imagery and unwelcome sexual attention or advances
* Trolling, insulting/derogatory comments, and personal or political attacks
* Public or private harassment
* Publishing others' private information without explicit permission
* Other conduct which could reasonably be considered inappropriate in a professional setting

## 🔄 Development Process

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests (`pytest`)
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## 🚀 Getting Started

### Prerequisites

- Python 3.8 or higher
- Git
- Virtual environment (recommended)

### Quick Setup

```bash
# Fork and clone the repository
git clone https://github.com/yourusername/trustguard.git
cd trustguard

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -e ".[dev]"

# Verify installation
pytest
```

## 💻 Development Setup

### 1. Virtual Environment

We recommend using a virtual environment for development:

```bash
# Create virtual environment
python -m venv venv

# Activate it
# On Linux/Mac:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate

# Verify activation
which python  # Should point to your venv
```

### 2. Install Dependencies

```bash
# Install with all development dependencies
pip install -e ".[dev]"

# This installs:
# - pytest for testing
# - black for formatting
# - isort for import sorting
# - ruff for linting
# - mypy for type checking
# - Optional judge dependencies
```

### 3. Verify Setup

```bash
# Run tests
pytest

# Check code style
black --check trustguard tests

# Run linter
ruff check trustguard tests

# Type check
mypy trustguard
```

## 🛠️ Making Changes

### Branch Naming Convention

- `feature/` - New features (e.g., `feature/custom-judge`)
- `fix/` - Bug fixes (e.g., `fix/json-extraction`)
- `docs/` - Documentation (e.g., `docs/api-update`)
- `test/` - Testing improvements (e.g., `test/coverage`)
- `refactor/` - Code refactoring (e.g., `refactor/core-logic`)

### Code Structure

```
trustguard/
├── core.py              # Main TrustGuard class
├── exceptions.py        # Custom exceptions
├── cli.py               # Command line interface
├── schemas/             # Pydantic schemas
│   ├── base.py
│   └── generic.py
├── rules/               # Validation rules
│   ├── __init__.py
│   ├── pii.py
│   ├── blocklist.py
│   ├── toxicity.py
│   └── quality.py
├── judges/              # Judge system
│   ├── base.py
│   ├── custom.py
│   ├── openai.py
│   ├── ollama.py
│   ├── anthropic.py
│   └── ensemble.py
├── validators/          # Validator registry
│   ├── __init__.py
│   └── registry.py
└── wrappers/            # Provider wrappers
    ├── base.py
    └── openai.py
```

## 🎨 Adding New Rules

### Step 1: Create Rule File

Create a new file in `trustguard/rules/` (e.g., `my_rule.py`):

```python
"""
My custom validation rule.
"""

from typing import Optional, Dict, Any

def validate_my_rule(
    data: Dict[str, Any],
    raw_text: str,
    context: Optional[Dict[str, Any]] = None
) -> Optional[str]:
    """
    Check for something in the response.
    
    Args:
        data: Parsed JSON data
        raw_text: Original raw text
        context: Optional context dictionary
        
    Returns:
        Error message if check fails, None otherwise
    """
    # Your logic here
    if "bad" in raw_text.lower():
        return "Found bad content"
    
    # Check data fields
    if "sensitive_field" in data:
        value = data["sensitive_field"]
        if len(value) > 100:
            return "Sensitive field too long"
    
    return None
```

### Step 2: Add to __init__.py

Update `trustguard/rules/__init__.py`:

```python
from .my_rule import validate_my_rule

DEFAULT_RULES = [
    # ... existing rules ...
    validate_my_rule,
]

__all__.append("validate_my_rule")
```

### Step 3: Write Tests

Create tests in `tests/test_rules.py`:

```python
def test_my_rule():
    """Test my custom rule."""
    from trustguard.rules import validate_my_rule
    
    # Test with bad content
    result = validate_my_rule({}, "This has bad content")
    assert result is not None
    assert "bad" in result
    
    # Test with safe content
    result = validate_my_rule({}, "This is safe")
    assert result is None
    
    # Test with data
    data = {"sensitive_field": "x" * 200}
    result = validate_my_rule(data, "")
    assert result is not None
    assert "too long" in result
```

## 🤖 Adding New Judges

### Step 1: Create Judge File

Create a new file in `trustguard/judges/` (e.g., `my_judge.py`):

```python
"""
My custom judge implementation.
"""

from typing import Dict, Any, Optional
from trustguard.judges.base import BaseJudge

class MyJudge(BaseJudge):
    """
    Custom judge that does something amazing.
    
    Args:
        api_key: Optional API key
        weight: Weight for ensemble voting
        config: Additional configuration
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        weight: float = 1.0,
        config: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(config)
        self.api_key = api_key
        self.weight = weight
        
        # Initialize your client
        self.client = self._initialize_client()
        
        # Configuration
        self.timeout = self.config.get("timeout", 30)
        self.max_retries = self.config.get("max_retries", 3)
    
    def _initialize_client(self):
        """Initialize your API client."""
        # Your client initialization logic
        pass
    
    def judge(self, text: str) -> Dict[str, Any]:
        """
        Judge the text.
        
        Args:
            text: Text to evaluate
            
        Returns:
            Dictionary with safety verdict
        """
        try:
            # Your judgment logic
            result = self._call_api(text)
            
            # Normalize to BaseJudge interface
            return {
                "safe": result["safe"],
                "reason": result["reason"],
                "risk_category": result.get("category", "custom"),
                "confidence": result.get("confidence", 1.0),
                "severity": result.get("severity", "low"),
                "metadata": {
                    "judge_name": self.__class__.__name__,
                    "model": "my-model",
                    **result.get("metadata", {})
                }
            }
            
        except Exception as e:
            # Handle errors gracefully
            if self.config.get("fail_on_error", False):
                raise
            
            return {
                "safe": self.config.get("on_error", "allow") == "allow",
                "reason": f"Judge error: {str(e)}",
                "risk_category": "system_error",
                "confidence": 0.0,
                "severity": "low",
                "metadata": {"error": str(e)}
            }
    
    def _call_api(self, text: str) -> Dict[str, Any]:
        """Call your API."""
        # Your API call logic
        pass
```

### Step 2: Add to __init__.py

Update `trustguard/judges/__init__.py`:

```python
# Add safe import with helpful error message
try:
    from .my_judge import MyJudge
except ImportError:
    class MyJudge:
        def __init__(self, *args, **kwargs):
            raise ImportError(
                "MyJudge requires extra dependencies. "
                "Install with: pip install trustguard[my]"
            )

__all__.append("MyJudge")
```

### Step 3: Update pyproject.toml

Add optional dependencies if needed:

```toml
[project.optional-dependencies]
my = ["my-package>=1.0.0"]  # Add your dependencies
all = ["trustguard[ai,openai,anthropic,my]"]  # Update all
```

### Step 4: Write Tests

Create tests in `tests/test_judges.py`:

```python
def test_my_judge():
    """Test my custom judge."""
    from trustguard.judges import MyJudge
    
    # Test with mock
    judge = MyJudge(api_key="test")
    
    # Test safe text
    result = judge.judge("safe text")
    assert result["safe"] is True
    
    # Test unsafe text
    result = judge.judge("bad text")
    assert result["safe"] is False
    
    # Test error handling
    result = judge.judge("error")
    assert "error" in result["reason"].lower()
```

## 🧪 Testing Guidelines

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=trustguard --cov-report=html

# Run specific test file
pytest tests/test_core.py

# Run specific test
pytest tests/test_core.py::test_schema_validation -v

# Run tests matching pattern
pytest -k "judge"
```

### Writing Tests

```python
import pytest
import json
from trustguard import TrustGuard
from trustguard.schemas import GenericResponse

def test_my_feature():
    """Test my new feature."""
    # Arrange
    guard = TrustGuard(schema_class=GenericResponse)
    test_input = json.dumps({
        "content": "test",
        "sentiment": "neutral",
        "tone": "professional",
        "is_helpful": True
    })
    
    # Act
    result = guard.validate(test_input)
    
    # Assert
    assert result.is_approved
    assert result.data["content"] == "test"

@pytest.mark.parametrize("input_text,expected", [
    ('{"content":"good"}', "REJECTED"),  # Missing fields
    ('{"content":"test","sentiment":"neutral","tone":"professional","is_helpful":true}', "APPROVED"),
])
def test_parametrized(input_text, expected):
    """Test with multiple inputs."""
    guard = TrustGuard(schema_class=GenericResponse)
    result = guard.validate(input_text)
    assert result.status == expected
```

### Test Coverage

Aim for at least 80% coverage. Run coverage report:

```bash
pytest --cov=trustguard --cov-report=term-missing
```

## 📚 Documentation

### Docstring Format

Use Google-style docstrings:

```python
def my_function(param1: str, param2: int = 0) -> bool:
    """
    Short description of function.
    
    Longer description if needed.
    
    Args:
        param1: Description of param1
        param2: Description of param2, defaults to 0
        
    Returns:
        Description of return value
        
    Raises:
        ValueError: Description of when this error occurs
        
    Example:
        >>> my_function("test", 5)
        True
    """
    pass
```

### Updating Documentation

1. Update relevant `.md` files in `docs/`
2. Add examples to `examples/` directory
3. Update docstrings in code
4. Run `mkdocs serve` to preview

### Building Documentation

```bash
# Install mkdocs
pip install mkdocs mkdocs-material

# Serve locally
mkdocs serve

# Build static site
mkdocs build
```

## 🔀 Pull Request Process

### Before Submitting

1. **Run all tests**: `pytest`
2. **Check code style**: `black . && isort .`
3. **Run linter**: `ruff check . --fix`
4. **Type check**: `mypy trustguard`
5. **Update documentation** if needed
6. **Add tests** for new features

### PR Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Added tests
- [ ] All tests pass
- [ ] Manual testing done

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No new warnings
- [ ] Tests added/updated
- [ ] All tests pass
```

### Review Process

1. At least one maintainer must approve
2. All CI checks must pass
3. No merge conflicts
4. Documentation updated if needed

## 📏 Style Guidelines

### Python Style

- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/)
- Use [Black](https://black.readthedocs.io/) for formatting
- Use [isort](https://pycqa.github.io/isort/) for imports
- Maximum line length: 100 characters
- Use type hints for all functions

### Import Order

```python
# Standard library
import json
import re
from datetime import datetime
from typing import Dict, List, Optional

# Third party
from pydantic import BaseModel, Field

# Local
from trustguard.core import TrustGuard
from trustguard.exceptions import ValidationError
```

### Naming Conventions

- Classes: `CamelCase`
- Functions/methods: `snake_case`
- Variables: `snake_case`
- Constants: `UPPER_CASE`
- Private attributes: `_leading_underscore`

## 📦 Release Process

### Version Numbers

We follow [Semantic Versioning](https://semver.org/):

- **MAJOR**: Incompatible API changes
- **MINOR**: New functionality (backward compatible)
- **PATCH**: Bug fixes (backward compatible)

### Creating a Release

1. Update version in `trustguard/__init__.py`
2. Update `CHANGELOG.md`
3. Create release commit: `git commit -m "Release v0.2.0"`
4. Create tag: `git tag v0.2.0`
5. Push: `git push && git push --tags`
6. GitHub Actions will publish to PyPI

### Changelog Format

```markdown
## [0.2.0] - 2024-01-01
### Added
- New feature X
- Support for Y

### Changed
- Improved performance of Z
- Updated dependency requirements

### Fixed
- Bug in JSON extraction
- Issue with judge error handling
```

## 🆘 Getting Help

### Where to Ask

- **Issues**: Bug reports, feature requests
- **Discussions**: Questions, ideas, help
- **Pull Requests**: Code contributions

### Before Asking

1. Check existing issues/discussions
2. Read relevant documentation
3. Try to isolate the problem
4. Include minimal example if possible

### Good Bug Reports Include

- Summary of the issue
- Steps to reproduce
- Expected vs actual behavior
- Code samples
- Environment details
- Screenshots if applicable

## 🙏 Thank You!

Your contributions help make trustguard better for everyone. We appreciate your time and effort!

<div align="center">
Made with ❤️ by the trustguard community
</div>
