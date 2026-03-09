"""
Toxicity detection rule.


March-2026 update :Toxicity detection rule with word boundaries to avoid false positives.
"""

from typing import Optional, Dict, Any, List
import re

# Common toxic patterns
TOXIC_PATTERNS = [
    "hate",
    "stupid",
    "idiot",
    "dumb",
    "shit",
    "fuck",
    "damn",
    "hell",
    "kill",
    "die",
    "threat",
    "attack",
]

def validate_toxicity(
    data: Dict[str, Any],
    raw_text: str,
    context: Optional[Dict[str, Any]] = None
) -> Optional[str]:
    """
    Check for toxic or harmful content using word boundaries.
    
    Args:
        data: Parsed JSON data
        raw_text: Original raw text
        context: Optional context dictionary
        
    Returns:
        Error message if toxic content found, None otherwise
    """
    # Get sensitivity from context (1-10, higher = more sensitive)
    sensitivity = context.get("toxicity_sensitivity", 5) if context else 5
    
    # Adjust patterns based on sensitivity
    if sensitivity >= 8:
        # Very sensitive - include milder terms
        patterns = TOXIC_PATTERNS + ["ugly", "angry"]
    elif sensitivity <= 3:
        # Less sensitive - only severe terms
        patterns = ["kill", "threat", "attack", "fuck"]
    else:
        patterns = TOXIC_PATTERNS
    
    lower_text = raw_text.lower()
    found_terms = []
    
    # Use word boundaries to avoid false matches like "hell" in "hello"
    for pattern in patterns:
        if re.search(rf"\b{re.escape(pattern)}\b", lower_text):
            found_terms.append(pattern)
    
    if found_terms:
        terms_str = ", ".join(found_terms[:3])
        if len(found_terms) > 3:
            terms_str += f" and {len(found_terms) - 3} more"
        return f"Toxic content detected: {terms_str}"
    
    return None