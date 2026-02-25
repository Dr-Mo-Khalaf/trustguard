"""
Ensemble judge that combines multiple judges for maximum accuracy.
"""

from typing import List, Dict, Any, Optional, Union
from trustguard.judges.base import BaseJudge
from trustguard.judges.custom import CallableJudge


class EnsembleJudge(BaseJudge):
    """
    Combines multiple judges using voting or weighted scoring.
    
    This provides:
    - Higher accuracy through consensus
    - Reduced false positives/negatives
    - Graceful degradation if one judge fails
    - Support for mixing provider judges with custom callables
    
    Example:
        ```python
        from trustguard.judges import EnsembleJudge, OpenAIJudge, CallableJudge
        
        judges = [
            OpenAIJudge(model="gpt-4o-mini", weight=2.0),
            CallableJudge(my_hf_pipeline, weight=1.5),
            CallableJudge(my_rule_based_checker, weight=1.0)
        ]
        
        ensemble = EnsembleJudge(judges, strategy="weighted_vote")
        ```
    """
    
    STRATEGIES = ["majority_vote", "weighted_vote", "strict", "lenient"]
    
    def __init__(
        self,
        judges: List[Union[BaseJudge, CallableJudge, callable]],
        strategy: str = "weighted_vote",
        config: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize ensemble judge.
        
        Args:
            judges: List of judges (can be BaseJudge instances, callables, or CallableJudge)
            strategy: Combination strategy
            config: Additional configuration
        """
        # Handle None config
        config = config or {}
        super().__init__(config)
        
        # Normalize judges (convert callables to CallableJudge)
        self.judges = []
        self.weights = []
        
        for judge in judges:
            if isinstance(judge, BaseJudge):
                self.judges.append(judge)
                self.weights.append(getattr(judge, "weight", 1.0))
            elif callable(judge):
                # Auto-wrap callables
                wrapped = CallableJudge(judge)
                self.judges.append(wrapped)
                self.weights.append(1.0)
            else:
                raise TypeError(f"Expected BaseJudge or callable, got {type(judge)}")
        
        self.strategy = strategy if strategy in self.STRATEGIES else "weighted_vote"
        self.fail_on_error = config.get("fail_on_error", False)
    
    def judge(self, text: str) -> Dict[str, Any]:
        """
        Combine judgments from all judges.
        
        Args:
            text: Text to evaluate
            
        Returns:
            Combined verdict
        """
        results = []
        
        for judge in self.judges:
            try:
                result = judge.judge(text)
                results.append(result)
            except Exception as e:
                if self.fail_on_error:
                    raise
                if self.config.get("log_errors", True):
                    print(f"[EnsembleJudge] Judge {judge.name} failed: {e}")
                continue
        
        if not results:
            return self._error_response("All judges failed")
        
        # Apply strategy
        if self.strategy == "majority_vote":
            return self._majority_vote(results)
        elif self.strategy == "weighted_vote":
            return self._weighted_vote(results)
        elif self.strategy == "strict":
            return self._strict(results)
        elif self.strategy == "lenient":
            return self._lenient(results)
        else:
            return self._weighted_vote(results)
    
    def _majority_vote(self, results: List[Dict]) -> Dict[str, Any]:
        """Simple majority vote."""
        safe_count = sum(1 for r in results if r["safe"])
        unsafe_count = len(results) - safe_count
        safe = safe_count > unsafe_count
        
        reasons = [r["reason"] for r in results if r["safe"] != safe]
        
        return {
            "safe": safe,
            "reason": f"Majority verdict: {safe_count}/{len(results)} judges agree" + 
                     (f" | Dissenting: {'; '.join(reasons)}" if reasons else ""),
            "risk_category": self._get_common_category(results),
            "confidence": max(safe_count, unsafe_count) / len(results),
            "severity": self._get_max_severity(results),
            "metadata": {
                "strategy": "majority_vote",
                "votes": {"safe": safe_count, "unsafe": unsafe_count}
            }
        }
    
    def _weighted_vote(self, results: List[Dict]) -> Dict[str, Any]:
        """Weighted vote using judge weights."""
        safe_weight = 0.0
        unsafe_weight = 0.0
        reasons = []
        
        for i, result in enumerate(results):
            weight = self.weights[i] if i < len(self.weights) else 1.0
            if result["safe"]:
                safe_weight += weight
            else:
                unsafe_weight += weight
                reasons.append(f"{result['risk_category']}: {result['reason']}")
        
        safe = safe_weight >= unsafe_weight
        total = safe_weight + unsafe_weight
        
        return {
            "safe": safe,
            "reason": f"Weighted verdict: {safe_weight:.1f} vs {unsafe_weight:.1f}" +
                     (f" | Issues: {'; '.join(reasons)}" if reasons else ""),
            "risk_category": self._get_common_category(results),
            "confidence": max(safe_weight, unsafe_weight) / total if total > 0 else 1.0,
            "severity": self._get_max_severity(results),
            "metadata": {
                "strategy": "weighted_vote",
                "weights": {"safe": safe_weight, "unsafe": unsafe_weight}
            }
        }
    
    def _strict(self, results: List[Dict]) -> Dict[str, Any]:
        """Any unsafe = unsafe (conservative approach)."""
        unsafe = [r for r in results if not r["safe"]]
        
        if unsafe:
            reasons = [f"{r['risk_category']}: {r['reason']}" for r in unsafe]
            return {
                "safe": False,
                "reason": f"Strict: {len(unsafe)} judge(s) flagged issues | {'; '.join(reasons)}",
                "risk_category": unsafe[0].get("risk_category", "unknown"),
                "confidence": 1.0,
                "severity": self._get_max_severity(unsafe),
                "metadata": {"strategy": "strict", "flagged": len(unsafe)}
            }
        
        return {
            "safe": True,
            "reason": "All judges passed",
            "risk_category": "none",
            "confidence": 1.0,
            "severity": "low",
            "metadata": {"strategy": "strict"}
        }
    
    def _lenient(self, results: List[Dict]) -> Dict[str, Any]:
        """Any safe = safe (liberal approach)."""
        safe = [r for r in results if r["safe"]]
        
        if safe:
            return {
                "safe": True,
                "reason": f"Lenient: {len(safe)} judge(s) approved",
                "risk_category": "none",
                "confidence": 1.0,
                "severity": "low",
                "metadata": {"strategy": "lenient", "approved": len(safe)}
            }
        
        reasons = [f"{r['risk_category']}: {r['reason']}" for r in results]
        return {
            "safe": False,
            "reason": f"All judges flagged issues | {'; '.join(reasons)}",
            "risk_category": results[0].get("risk_category", "unknown"),
            "confidence": 1.0,
            "severity": self._get_max_severity(results),
            "metadata": {"strategy": "lenient"}
        }
    
    def _get_common_category(self, results: List[Dict]) -> str:
        """Get the most common risk category."""
        from collections import Counter
        categories = [r.get("risk_category", "unknown") for r in results]
        if not categories:
            return "unknown"
        return Counter(categories).most_common(1)[0][0]
    
    def _get_max_severity(self, results: List[Dict]) -> str:
        """Get the highest severity level."""
        severity_order = {"low": 0, "medium": 1, "high": 2, "critical": 3}
        severities = [r.get("severity", "low") for r in results]
        if not severities:
            return "low"
        return max(severities, key=lambda s: severity_order.get(s, 0))
    
    def _error_response(self, message: str) -> Dict[str, Any]:
        """Generate error response."""
        return {
            "safe": self.config.get("on_error", "allow") == "allow",
            "reason": f"Ensemble error: {message}",
            "risk_category": "system_error",
            "confidence": 0.0,
            "severity": "low",
            "metadata": {"error": message}
        }
