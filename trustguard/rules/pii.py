"""
PII (Personally Identifiable Information) detection rule.
"""
import re
from typing import Optional, Dict, Any, Union

# Base PII patterns
PII_PATTERNS = {
    "email": r"\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b",
    "phone": r"\b(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b",
    "ssn": r"\b\d{3}-\d{2}-\d{4}\b",
    "credit_card": r"\b(?:\d[ -]*?){13,16}\b",
    "ip_address": r"\b(?:\d{1,3}\.){3}\d{1,3}\b",
    "api_key": r"\b[A-Za-z0-9]{32,}\b"
}

# Pattern to detect obfuscated emails
OBFUSCATED_EMAIL_PATTERN = re.compile(
    r"\b[a-zA-Z0-9._%+-]+\s*(?:\[at\]|\(at\)|@|\s+at\s+)\s*"
    r"[a-zA-Z0-9.-]+\s*(?:\[dot\]|\(dot\)|\.|\s+dot\s+)\s*[a-zA-Z]{2,}\b"
)

def normalize_text(text: str) -> str:
    """
    Normalize obfuscated emails safely without affecting normal text.
    """
    text = re.sub(r"\[at\]|\(at\)|\bat\b", "@", text, flags=re.IGNORECASE)
    text = re.sub(r"\[dot\]|\(dot\)|\bdot\b", ".", text, flags=re.IGNORECASE)
    return text

def check_text(text: str, location="response") -> Optional[str]:
    """
    Check a single string for PII.
    """
    normalized = normalize_text(text)

    # Check obfuscated email
    if re.search(OBFUSCATED_EMAIL_PATTERN, normalized):
        return f"PII Detected: email (obfuscated) found in {location}"

    # Check standard PII patterns
    for pii_type, pattern in PII_PATTERNS.items():
        if re.search(pattern, normalized):
            return f"PII Detected: {pii_type} found in {location}"

    return None

def scan_data(data: Union[Dict, list, str], parent_path="") -> Optional[str]:
    """
    Recursively scan nested dicts and lists for PII.
    """
    if isinstance(data, dict):
        for key, value in data.items():
            full_path = f"{parent_path}.{key}" if parent_path else key
            result = scan_data(value, full_path)
            if result:
                return result
    elif isinstance(data, list):
        for idx, item in enumerate(data):
            full_path = f"{parent_path}[{idx}]"
            result = scan_data(item, full_path)
            if result:
                return result
    elif isinstance(data, str):
        return check_text(data, f"field '{parent_path}'")
    return None

def validate_pii(
    data: Union[Dict[str, Any], None] = None,
    raw_text: Union[str, None] = None,
    context: Optional[Dict[str, Any]] = None
) -> Optional[str]:
    """
    Universal PII validator.
    
    Accepts:
      - Just a raw string
      - Dict (parsed JSON)
      - Both
      - Optional context
    """
    # If only one argument passed and it's a string, treat it as raw_text
    if data is not None and isinstance(data, str) and raw_text is None:
        raw_text = data
        data = {}

    data = data or {}
    raw_text = raw_text or ""

    # 1️⃣ Scan structured data
    result = scan_data(data)
    if result:
        return result

    # 2️⃣ Scan raw text
    result = check_text(raw_text, location="raw_text")
    if result:
        return result

    return None


