"""
Custom/Callable judge for using ANY model or logic.
"""

from typing import Callable, Dict, Any, Optional
from trustguard.judges.base import BaseJudge


class CallableJudge(BaseJudge):
    """
    Universal adapter that allows ANY function to be used as a judge.
    
    This is the key to the "use any model" requirement. Users can wrap:
    - Hugging Face pipelines
    - Groq API calls
    - Internal company models
    - Legacy safety systems
    - Custom business logic
    
    Example:
        ```python
        from trustguard import TrustGuard
        from trustguard.judges import CallableJudge
        
        def my_hf_judge(text):
            result = pipeline(text)[0]
            return {"safe": result["label"] != "TOXIC", "reason": result["score"]}
        
        guard = TrustGuard(schema, judge=CallableJudge(my_hf_judge))
        ```
    """
    
    def __init__(
        self,
        judge_function: Callable[[str], Dict[str, Any]],
        name: Optional[str] = None,
        weight: float = 1.0,
    ):
        """
        Initialize with any callable that takes text and returns a verdict.
        
        Args:
            judge_function: A function that takes a string and returns a dict
                with at least {"safe": bool, "reason": str}
            name: Optional name for the judge (defaults to function name)
            weight: Weight for ensemble voting
        """
        super().__init__()
        self.judge_function = judge_function
        self.name = name or getattr(judge_function, "__name__", "CustomJudge")
        self.weight = weight
    
    def judge(self, text: str) -> Dict[str, Any]:
        """
        Execute the custom judge function and normalize the result.
        
        Args:
            text: Text to evaluate
            
        Returns:
            Normalized verdict dictionary
        """
        try:
            result = self.judge_function(text)
            
            # Ensure result is a dict
            if not isinstance(result, dict):
                result = {"safe": bool(result), "reason": str(result)}
            
            # Normalize to BaseJudge interface
            return {
                "safe": bool(result.get("safe", True)),
                "reason": str(result.get("reason", "No reason provided")),
                "risk_category": result.get("risk_category", "custom"),
                "confidence": float(result.get("confidence", result.get("score", 1.0))),
                "severity": result.get("severity", "low"),
                "metadata": {
                    "judge_name": self.name,
                    **result.get("metadata", {})
                }
            }
            
        except Exception as e:
            error_msg = f"Custom judge '{self.name}' failed: {str(e)}"
            print(f"[trustguard] {error_msg}")
            
            return {
                "safe": True,
                "reason": error_msg,
                "risk_category": "system_error",
                "confidence": 0.0,
                "severity": "low",
                "metadata": {"error": str(e)}
            }
