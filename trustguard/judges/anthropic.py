"""
Anthropic Claude-based safety judge.
"""

import json
import re
from typing import Dict, Any, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from anthropic import Anthropic

from trustguard.judges.base import BaseJudge


class AnthropicJudge(BaseJudge):
    """
    Uses Anthropic Claude models for safety judgment.
    
    Claude excels at:
    - Nuanced safety evaluation
    - Constitutional AI principles
    - Detecting subtle manipulation
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "claude-3-haiku-20240307",
        weight: float = 1.0,
        config: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize Anthropic judge.
        
        Args:
            api_key: Anthropic API key
            model: Claude model to use
            weight: Weight for ensemble voting
            config: Additional configuration
        """
        super().__init__(config)
        self.model = model
        self.weight = weight
        
        try:
            from anthropic import Anthropic
            self.client = Anthropic(api_key=api_key)
        except ImportError:
            raise ImportError(
                "AnthropicJudge requires 'anthropic' package. "
                "Install with: pip install trustguard[anthropic]"
            )
        
        self.system_prompt = self.config.get(
            "system_prompt",
            "You are an AI safety expert. Analyze the user input for risks."
        )
    
    def judge(self, text: str) -> Dict[str, Any]:
        """
        Judge the text using Claude.
        
        Args:
            text: Text to evaluate
            
        Returns:
            Dict with safety verdict
        """
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=self.config.get("max_tokens", 300),
                temperature=self.config.get("temperature", 0.0),
                system=self.system_prompt,
                messages=[
                    {
                        "role": "user",
                        "content": f"""Analyze this text for safety risks.
Return a JSON with: safe (boolean), reason (string), risk_level (low/medium/high).

Text: {text}"""
                    }
                ]
            )
            
            # Parse response
            content = response.content[0].text
            
            # Extract JSON if present
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group())
            else:
                # Fallback parsing
                safe = "safe" in content.lower() and "unsafe" not in content.lower()
                result = {"safe": safe, "reason": content}
            
            return {
                "safe": result.get("safe", True),
                "reason": result.get("reason", "No reason provided"),
                "risk_category": result.get("risk_category", "unknown"),
                "confidence": result.get("confidence", 0.9),
                "severity": result.get("risk_level", "low"),
                "metadata": {"model": self.model}
            }
            
        except Exception as e:
            return {
                "safe": self.config.get("on_error", "allow") == "allow",
                "reason": f"Claude error: {str(e)}",
                "risk_category": "system_error",
                "confidence": 0.0,
                "severity": "low"
            }
