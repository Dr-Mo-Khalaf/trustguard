"""
Ollama-based safety judge for local, private validation.
"""

import json
from typing import Dict, Any, Optional

from trustguard.judges.base import BaseJudge


class OllamaJudge(BaseJudge):
    """
    Uses local Ollama models (Llama 3, Phi-3, etc.) for privacy-focused validation.
    
    Benefits:
    - 100% private, no data leaves your infrastructure
    - Free to use
    - Works offline
    - No API costs
    """
    
    def __init__(
        self,
        model: str = "phi3",
        host: str = "http://localhost:11434",
        weight: float = 1.0,
        config: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize Ollama judge.
        
        Args:
            model: Ollama model name (phi3, llama3, mistral, etc.)
            host: Ollama server host
            weight: Weight for ensemble voting
            config: Additional configuration
        """
        super().__init__(config)
        self.model = model
        self.host = host
        self.weight = weight
        
        # Lazy import to handle optional dependency
        try:
            import ollama
            self.client = ollama.Client(host=host)
            # Test connection
            self.client.list()
        except ImportError:
            raise ImportError(
                "OllamaJudge requires 'ollama' package. "
                "Install with: pip install trustguard[ai]"
            )
        except Exception as e:
            raise ConnectionError(
                f"Cannot connect to Ollama at {host}. "
                f"Make sure Ollama is running. Error: {e}"
            )
        
        # Customizable prompt
        self.prompt_template = self.config.get(
            "prompt_template",
            """You are a safety judge for AI content.
Classify the following text as either 'SAFE' or 'UNSAFE'.

SAFE: Professional, helpful, non-toxic, appropriate.
UNSAFE: Contains profanity, hate speech, threats, sexual content, or harmful instructions.

Text: "{text}"

Respond with exactly:
SAFE
or
UNSAFE: [brief reason]"""
        )
    
    def judge(self, text: str) -> Dict[str, Any]:
        """
        Judge the text using local Ollama.
        
        Args:
            text: Text to evaluate
            
        Returns:
            Dict with safety verdict
        """
        try:
            prompt = self.prompt_template.format(text=text)
            
            response = self.client.generate(
                model=self.model,
                prompt=prompt,
                options={
                    "num_predict": self.config.get("max_tokens", 100),
                    "temperature": self.config.get("temperature", 0.1),
                    "top_p": self.config.get("top_p", 0.9),
                }
            )
            
            result = response['response'].strip()
            
            # Parse response
            if result.upper().startswith("UNSAFE"):
                reason = result.split(":", 1)[-1].strip() if ":" in result else "Content flagged as unsafe"
                return {
                    "safe": False,
                    "reason": reason,
                    "risk_category": "unsafe_content",
                    "confidence": 0.9,
                    "severity": "medium",
                    "metadata": {"model": self.model}
                }
            
            return {
                "safe": True,
                "reason": "Content appears safe",
                "risk_category": "none",
                "confidence": 0.8,
                "severity": "low",
                "metadata": {"model": self.model}
            }
            
        except Exception as e:
            fail_action = self.config.get("on_error", "allow")
            return {
                "safe": fail_action == "allow",
                "reason": f"Ollama error: {str(e)}",
                "risk_category": "system_error",
                "confidence": 0.0,
                "severity": "low",
                "metadata": {"error": str(e)}
            }
