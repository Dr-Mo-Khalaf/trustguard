"""
Toxixcity filtering rule.
"""
from typing import Optional, Dict, Any, Union, List, Tuple
import re

# Base toxic patterns
TOXIC_PATTERNS = [
    "hate", "stupid", "idiot", "dumb", "shit", "fuck", 
    "damn", "hell", "kill", "die", "threat", "attack"
]

def scan_toxicity(
    data: Union[Dict, List, str],
    parent_path: str = "",
    patterns: Optional[List[str]] = None
) -> List[Tuple[str, List[str], str]]:
    """
    Recursively scan nested dicts/lists/strings for toxic content.
    Returns list of tuples: (path, found_terms, value)
    """
    findings = []
    if not patterns:
        patterns = TOXIC_PATTERNS

    if isinstance(data, dict):
        for key, value in data.items():
            full_path = f"{parent_path}.{key}" if parent_path else key
            findings.extend(scan_toxicity(value, full_path, patterns))
    elif isinstance(data, list):
        for idx, item in enumerate(data):
            full_path = f"{parent_path}[{idx}]"
            findings.extend(scan_toxicity(item, full_path, patterns))
    elif isinstance(data, str):
        lower_text = data.lower()
        found_terms = [term for term in patterns if re.search(rf"\b{re.escape(term)}\b", lower_text)]
        if found_terms:
            findings.append((parent_path, found_terms, data))

    return findings

def validate_toxicity(
    data: Union[Dict[str, Any], List[Any], str, None] = None,
    raw_text: Optional[str] = None,
    context: Optional[Dict[str, Any]] = None,
    return_paths: bool = False
) -> Optional[Union[str, List[Tuple[str, List[str], str]]]]:
    """
    Universal toxicity validator.

    Parameters:
        data: dict, list, or JSON-like object
        raw_text: original raw text
        context: optional metadata (e.g., toxicity_sensitivity)
        return_paths: if True, return list of detected terms with paths

    Returns:
        - None if no toxic content
        - Summary string (default)
        - List of tuples (path, found_terms, value) if return_paths=True
    """
    # Normalize inputs
    if data is None:
        data = {}
    if isinstance(data, str) and raw_text is None:
        raw_text = data
        data = {}
    raw_text = raw_text or ""
    data = data or {}

    # Determine sensitivity
    sensitivity = context.get("toxicity_sensitivity", 5) if context else 5
    if sensitivity >= 8:
        patterns = TOXIC_PATTERNS + ["ugly", "angry"]
    elif sensitivity <= 3:
        patterns = ["kill", "threat", "attack", "fuck"]
    else:
        patterns = TOXIC_PATTERNS

    # Collect findings
    findings = []
    findings.extend(scan_toxicity(data, patterns=patterns))
    if raw_text:
        findings.extend(scan_toxicity(raw_text, "raw_text", patterns=patterns))

    if not findings:
        return None

    if return_paths:
        return findings

    # Default summary string
    summary_list = []
    for path, terms, _ in findings:
        terms_str = ", ".join(terms[:3])
        if len(terms) > 3:
            terms_str += f" and {len(terms) - 3} more"
        summary_list.append(f"{terms_str} in {path}")

    return "Toxic content detected: " + "; ".join(summary_list)