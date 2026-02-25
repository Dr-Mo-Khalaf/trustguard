"""
Base wrapper class for LLM providers.
"""

from typing import Any, Dict, Optional
from pydantic import BaseModel

from trustguard.core import TrustGuard
from trustguard.exceptions import WrapperError


class BaseWrapper:
    """
    Base class for LLM provider wrappers.
    """
    
    def __init__(
        self,
        client: Any,
        validator: TrustGuard,
        auto_validate: bool = True,
        raise_on_reject: bool = False,
    ):
        """
        Initialize wrapper.
        
        Args:
            client: Underlying LLM client
            validator: TrustGuard validator instance
            auto_validate: Automatically validate responses
            raise_on_reject: Raise exception on rejection
        """
        self._client = client
        self.validator = validator
        self.auto_validate = auto_validate
        self.raise_on_reject = raise_on_reject
    
    def _validate_response(
        self,
        response: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Validate a response."""
        if not self.auto_validate:
            return {"status": "SKIPPED", "data": response}
        
        result = self.validator.validate(response, context=context)
        
        if result.is_rejected and self.raise_on_reject:
            raise WrapperError(f"Response rejected: {result.log}")
        
        return result.to_dict()
    
    def __getattr__(self, name: str) -> Any:
        """Delegate to underlying client."""
        return getattr(self._client, name)
