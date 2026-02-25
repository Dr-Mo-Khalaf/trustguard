"""
OpenAI-based safety judge with advanced nuance detection.
"""

import json
from typing import Dict, Any, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from openai import OpenAI

from trustguard.judges.base import BaseJudge


class OpenAIJudge(BaseJudge):
    """
    Uses OpenAI models (GPT-4, GPT-3.5, etc.) to judge response safety.
    
    This judge can detect:
    - Subtle toxicity and harassment
    - Sarcasm and passive-aggressive content
    - Complex jailbreak attempts
    - Context-aware policy violations
    - Hidden PII and sensitive data
    
    Example:
        ```python
        judge = OpenAIJudge(
            api_key="sk-...",
            model="gpt-4o-mini",
            weight=2.0,  # For ensemble voting
            config={
                "system_prompt": "You are a strict compliance officer...",
                "safety_threshold": 0.8
            }
        )
        ```
    """
    
    SAFETY_CATEGORIES = [
        "hate_speech", "harassment", "sexual_content", "violent_content",
        "self_harm", "pii_leak", "jailbreak_attempt", "misinformation",
        "professional_boundary", "none"
    ]
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "gpt-4o-mini",
        weight: float = 1.0,
        config: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize OpenAI judge.
        
        Args:
            api_key: OpenAI API key (falls back to OPENAI_API_KEY env var)
            model: Model to use (gpt-4o, gpt-4o-mini, gpt-3.5-turbo, etc.)
            weight: Weight for ensemble voting
            config: Additional configuration
        """
        super().__init__(config)
        self.model = model
        self.weight = weight
        
        # Lazy import to handle optional dependency
        try:
            from openai import OpenAI
            self.client = OpenAI(api_key=api_key)
        except ImportError:
            raise ImportError(
                "OpenAIJudge requires 'openai' package. "
                "Install with: pip install trustguard[openai]"
            )
        
        # Customizable system prompt
        self.system_prompt = self.config.get(
            "system_prompt",
            self._default_system_prompt()
        )
        
        self.safety_threshold = self.config.get("safety_threshold", 0.7)
        self._cache = {}
        self.cache_size = self.config.get("cache_size", 100)
    
    def _default_system_prompt(self) -> str:
        categories = ", ".join(self.SAFETY_CATEGORIES[:-1])
        return f"""You are an expert AI Safety Auditor. Analyze text for safety risks.

Categories: {categories}

Respond ONLY with JSON:
{{
    "safe": boolean,
    "reason": string,
    "risk_category": string,
    "confidence": float (0-1),
    "severity": "low"|"medium"|"high"|"critical"
}}"""
    
    def judge(self, text: str) -> Dict[str, Any]:
        """Judge the text using OpenAI."""
        cache_key = hash(text)
        if cache_key in self._cache:
            return self._cache[cache_key].copy()
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": text}
                ],
                response_format={"type": "json_object"},
                temperature=self.config.get("temperature", 0.0),
                max_tokens=self.config.get("max_tokens", 500)
            )
            
            content = response.choices[0].message.content
            result = json.loads(content)
            
            verdict = self._normalize_verdict(result)
            
            if len(self._cache) < self.cache_size:
                self._cache[cache_key] = verdict.copy()
            
            return verdict
            
        except Exception as e:
            fail_action = self.config.get("on_error", "allow")
            error_response = {
                "safe": fail_action == "allow",
                "reason": f"OpenAI error: {str(e)}",
                "risk_category": "system_error",
                "confidence": 0.0,
                "severity": "low",
                "metadata": {"error": str(e)}
            }
            if self.config.get("log_errors", True):
                print(f"[OpenAIJudge] Error: {e}")
            return error_response
    
    def _normalize_verdict(self, raw: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize and validate the judge's response."""
        verdict = {
            "safe": bool(raw.get("safe", True)),
            "reason": str(raw.get("reason", "No reason provided")),
            "risk_category": raw.get("risk_category", "none"),
            "confidence": float(raw.get("confidence", raw.get("score", 1.0))),
            "severity": raw.get("severity", "low"),
            "metadata": raw.get("metadata", {})
        }
        
        if verdict["risk_category"] not in self.SAFETY_CATEGORIES:
            verdict["risk_category"] = "none"
        
        if verdict["confidence"] < self.safety_threshold:
            verdict["safe"] = True
        
        return verdict
    
    def clear_cache(self):
        """Clear the judgment cache."""
        self._cache.clear()
