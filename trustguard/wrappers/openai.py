"""
OpenAI client wrapper with proper proxy pattern and safe optional dependency handling.
"""

from typing import Optional, Dict, Any, TYPE_CHECKING
import datetime

# Use TYPE_CHECKING to import OpenAI types only for static analysis
if TYPE_CHECKING:
    from openai import OpenAI
    from openai.types.chat import ChatCompletion

from trustguard.wrappers.base import BaseWrapper
from trustguard.core import TrustGuard
from trustguard.exceptions import WrapperError


class _CompletionsProxy:
    """Proxy for openai.resources.chat.completions.Completions"""
    
    def __init__(
        self,
        completions_obj: Any,
        validator: TrustGuard,
        default_context: Dict[str, Any],
        auto_validate: bool,
        raise_on_reject: bool,
    ):
        self._completions = completions_obj
        self._validator = validator
        self._default_context = default_context
        self._auto_validate = auto_validate
        self._raise_on_reject = raise_on_reject

    def create(self, **kwargs) -> "ChatCompletion":
        """
        Create a chat completion and validate the response.
        """
        response = self._completions.create(**kwargs)
        
        if not self._auto_validate:
            return response
        
        content = response.choices[0].message.content
        
        if content:
            context = self._default_context.copy()
            context.update({
                "model": kwargs.get("model"),
                "temperature": kwargs.get("temperature"),
                "max_tokens": kwargs.get("max_tokens"),
                "validation_timestamp": datetime.datetime.now().isoformat(),
            })
            context.update(kwargs.get("validation_context", {}))
            
            result = self._validator.validate(content, context=context)
            response._validation_result = result
            
            if self._raise_on_reject and result.is_rejected:
                raise WrapperError(f"Response rejected: {result.log}")
        
        return response


class _ChatProxy:
    """Proxy for openai.resources.chat.Chat"""
    
    def __init__(
        self,
        chat_obj: Any,
        validator: TrustGuard,
        default_context: Dict[str, Any],
        auto_validate: bool,
        raise_on_reject: bool,
    ):
        self.completions = _CompletionsProxy(
            chat_obj.completions,
            validator,
            default_context,
            auto_validate,
            raise_on_reject,
        )


class OpenAIClient(BaseWrapper):
    """
    Wrapper for OpenAI client with automatic validation.
    """
    
    def __init__(
        self,
        client: "OpenAI",
        validator: TrustGuard,
        auto_validate: bool = True,
        raise_on_reject: bool = False,
        default_context: Optional[Dict[str, Any]] = None,
    ):
        self._client = client
        self.validator = validator
        self.auto_validate = auto_validate
        self.raise_on_reject = raise_on_reject
        self.default_context = default_context or {}
        self._init_proxies()
    
    def _init_proxies(self):
        """Initialize proxy objects for all OpenAI resources."""
        self.chat = _ChatProxy(
            self._client.chat,
            self.validator,
            self.default_context,
            self.auto_validate,
            self.raise_on_reject,
        )
    
    def __getattr__(self, name: str) -> Any:
        """Delegate any other attributes to the underlying client."""
        return getattr(self._client, name)
    
    def validate_response(self, content: str, context: Optional[Dict[str, Any]] = None) -> Any:
        """Manually validate a response string."""
        ctx = self.default_context.copy()
        if context:
            ctx.update(context)
        return self.validator.validate(content, context=ctx)
