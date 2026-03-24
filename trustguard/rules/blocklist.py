"""
Blocklist filtering rule.
"""

from typing import Optional, Dict, Any, Union, List, Tuple

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

def scan_blocklist(
    data: Union[Dict, List, str],
    parent_path: str = "",
    blocklist: Optional[List[str]] = None
) -> List[Tuple[str, List[str], str]]:
    """
    Recursively scan nested dicts/lists/strings for blocked terms.
    Returns list of tuples: (path, matched_terms, value)
    """
    findings = []
    blocklist = blocklist or DEFAULT_BLOCKED_TERMS

    if isinstance(data, dict):
        for key, value in data.items():
            full_path = f"{parent_path}.{key}" if parent_path else key
            findings.extend(scan_blocklist(value, full_path, blocklist))
    elif isinstance(data, list):
        for idx, item in enumerate(data):
            full_path = f"{parent_path}[{idx}]"
            findings.extend(scan_blocklist(item, full_path, blocklist))
    elif isinstance(data, str):
        lower_text = data.lower()
        matched_terms = [term for term in blocklist if term.lower() in lower_text]
        if matched_terms:
            findings.append((parent_path, matched_terms, data))

    return findings

def validate_blocklist(
    data: Union[Dict[str, Any], List[Any], str, None] = None,
    raw_text: Optional[str] = None,
    context: Optional[Dict[str, Any]] = None,
    return_paths: bool = False
) -> Optional[Union[str, List[Tuple[str, List[str], str]]]]:
    """
    Universal blocklist validator.

    Parameters:
        data: dict, list, or JSON-like object
        raw_text: original raw text
        context: optional metadata (e.g., custom blocklist)
        return_paths: if True, return list of detected terms with paths

    Returns:
        - None if no blocked terms
        - Summary string (default)
        - List of tuples (path, matched_terms, value) if return_paths=True
    """
    # Normalize inputs
    if data is None:
        data = {}
    if isinstance(data, str) and raw_text is None:
        raw_text = data
        data = {}
    raw_text = raw_text or ""
    data = data or {}

    # Use custom blocklist from context or default
    blocklist = context.get("blocklist") if context and "blocklist" in context else DEFAULT_BLOCKED_TERMS

    # Collect findings
    findings = []
    findings.extend(scan_blocklist(data, blocklist=blocklist))
    if raw_text:
        findings.extend(scan_blocklist(raw_text, "raw_text", blocklist=blocklist))

    if not findings:
        return None

    if return_paths:
        return findings

    # Default summary string
    summary_list = []
    for path, terms, _ in findings:
        summary_list.append(f"{', '.join(terms)} in {path}")

    return "Prohibited terms detected: " + "; ".join(summary_list)