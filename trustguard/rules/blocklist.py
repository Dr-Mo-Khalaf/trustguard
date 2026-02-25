"""
Blocklist filtering rule.
"""

from typing import Optional, Dict, Any, List


# Default blocked terms
DEFAULT_BLOCKED_TERMS = [
    "secret_code",
    "admin_override",
    "backdoor",
    "hack",
    "exploit",
    "vulnerability",
    "password",
    "credit card",
    "ssn",
    "social security",
]


def validate_blocklist(
    data: Dict[str, Any],
    raw_text: str,
    context: Optional[Dict[str, Any]] = None
) -> Optional[str]:
    """
    Check for forbidden terms in the response.
    
    Args:
        data: Parsed JSON data
        raw_text: Original raw text
        context: Optional context dictionary with custom blocklist
        
    Returns:
        Error message if blocked term found, None otherwise
    """
    # Get blocklist from context or use default
    blocklist = context.get("blocklist", DEFAULT_BLOCKED_TERMS) if context else DEFAULT_BLOCKED_TERMS
    
    # Convert to lowercase for case-insensitive matching
    lower_text = raw_text.lower()
    
    for term in blocklist:
        if term.lower() in lower_text:
            return f"Prohibited Term: '{term}' found in response"
    
    return None
