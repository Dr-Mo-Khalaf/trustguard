"""
LLM provider wrappers for trustguard.
"""

from trustguard.wrappers.base import BaseWrapper

# Only import OpenAI wrapper if openai is installed
try:
    from trustguard.wrappers.openai import OpenAIClient
except ImportError:
    # Define a placeholder that raises a helpful error
    class OpenAIClient:
        def __init__(self, *args, **kwargs):
            raise ImportError(
                "OpenAI support requires extra dependencies. "
                "Install with: pip install trustguard[openai]"
            )

__all__ = ["BaseWrapper", "OpenAIClient"]
