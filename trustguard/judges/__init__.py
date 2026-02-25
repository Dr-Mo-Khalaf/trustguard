"""
Judges module for LLM-as-a-judge validation.
Provides pluggable safety judges for nuanced content evaluation.
"""

from trustguard.judges.base import BaseJudge
from trustguard.judges.custom import CallableJudge
from trustguard.judges.ensemble import EnsembleJudge

# Provider-specific judges (with helpful errors if missing)
try:
    from trustguard.judges.openai import OpenAIJudge
except ImportError:
    class OpenAIJudge:
        def __init__(self, *args, **kwargs):
            raise ImportError(
                "OpenAIJudge requires 'openai' package. "
                "Install with: pip install trustguard[openai]"
            )

try:
    from trustguard.judges.ollama import OllamaJudge
except ImportError:
    class OllamaJudge:
        def __init__(self, *args, **kwargs):
            raise ImportError(
                "OllamaJudge requires 'ollama' package. "
                "Install with: pip install trustguard[ai]"
            )

try:
    from trustguard.judges.anthropic import AnthropicJudge
except ImportError:
    class AnthropicJudge:
        def __init__(self, *args, **kwargs):
            raise ImportError(
                "AnthropicJudge requires 'anthropic' package. "
                "Install with: pip install trustguard[anthropic]"
            )

__all__ = [
    "BaseJudge",
    "CallableJudge",
    "OpenAIJudge",
    "OllamaJudge",
    "AnthropicJudge",
    "EnsembleJudge",
]
