"""
PII (Personally Identifiable Information) detection rule.
"""

import re
from typing import Optional, Dict, Any


def validate_pii(
    data: Dict[str, Any],
    raw_text: str,
    context: Optional[Dict[str, Any]] = None
) -> Optional[str]:
    """
    Check for PII (emails, phones) in the response.
    
    Args:
        data: Parsed JSON data
        raw_text: Original raw text
        context: Optional context dictionary
        
    Returns:
        Error message if PII found, None otherwise
    """
    # Email pattern
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    
    # Phone pattern (simplified)
    phone_pattern = r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
    
    # Check in data values
    for key, value in data.items():
        if isinstance(value, str):
            # Skip if field is explicitly marked as allowed
            if context and context.get("allow_pii_fields") and key in context["allow_pii_fields"]:
                continue
            
            if re.search(email_pattern, value):
                return f"PII Detected: Email address found in field '{key}'"
            
            if re.search(phone_pattern, value):
                return f"PII Detected: Phone number found in field '{key}'"
    
    # Check in raw text as fallback
    if re.search(email_pattern, raw_text):
        return "PII Detected: Email address found in response"
    
    if re.search(phone_pattern, raw_text):
        return "PII Detected: Phone number found in response"
    
    return None
