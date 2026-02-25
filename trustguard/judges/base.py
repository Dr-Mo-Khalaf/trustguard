"""
Base judge interface for LLM-as-a-judge validation.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional


class BaseJudge(ABC):
    """
    Abstract base class for safety judges.
    
    All judges must implement the judge() method. This provides a consistent
    interface for plugging different AI models into the validation pipeline.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the judge with optional configuration.
        
        Args:
            config: Judge-specific configuration (thresholds, prompts, etc.)
        """
        self.config = config or {}
        self.name = self.__class__.__name__
    
    @abstractmethod
    def judge(self, text: str) -> Dict[str, Any]:
        """
        Evaluate the safety of a text.
        
        Args:
            text: The text to evaluate
            
        Returns:
            Dictionary with at minimum:
            - "safe": bool (True if safe, False if unsafe)
            - "reason": str (Explanation of the verdict)
            
            Optional fields:
            - "risk_category": str (Type of risk detected)
            - "confidence": float (0-1 confidence score)
            - "severity": str ("low", "medium", "high", "critical")
            - "metadata": dict (Additional data)
        """
        pass
    
    async def async_judge(self, text: str) -> Dict[str, Any]:
        """
        Async version of judge. Override for native async support.
        
        Default implementation runs the sync version in a thread pool.
        
        Args:
            text: The text to evaluate
            
        Returns:
            Same as judge()
        """
        import asyncio
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.judge, text)
    
    def __repr__(self) -> str:
        return f"{self.name}(config={self.config})"
