"""
Response quality validation rules.
"""

from typing import Optional, Dict, Any, Union, List, Tuple

def scan_quality(
    data: Union[Dict, List, str],
    parent_path: str = ""
) -> List[Tuple[str, str, str]]:
    """
    Recursively scan nested dicts/lists/strings for quality issues.
    Returns list of tuples (path, issue_type, value)
    """
    findings = []

    if isinstance(data, dict):
        for key, value in data.items():
            full_path = f"{parent_path}.{key}" if parent_path else key
            findings.extend(scan_quality(value, full_path))
    elif isinstance(data, list):
        for idx, item in enumerate(data):
            full_path = f"{parent_path}[{idx}]"
            findings.extend(scan_quality(item, full_path))
    elif isinstance(data, str):
        # Too short
        if len(data) < 3:
            findings.append((parent_path, "too_short", data))
        # Too long
        elif len(data) > 10000:
            findings.append((parent_path, "too_long", data))
        # Repetition check (only if long enough)
        words = data.split()
        if len(words) > 50:
            word_counts = {}
            for word in words:
                w = word.lower()
                word_counts[w] = word_counts.get(w, 0) + 1
            max_repeat = max(word_counts.values())
            if max_repeat > len(words) * 0.5:
                findings.append((parent_path, "excessive_repetition", data))

    return findings

def validate_quality(
    data: Union[Dict[str, Any], List[Any], str, None] = None,
    raw_text: Optional[str] = None,
    context: Optional[Dict[str, Any]] = None,
    return_paths: bool = False
) -> Optional[Union[str, List[Tuple[str, str, str]]]]:
    """
    Universal response quality validator.
    
    Checks content length, completeness, and repetition.
    
    Parameters:
        data: dict, list, or JSON-like object
        raw_text: original raw text
        context: optional metadata
        return_paths: if True, return list of issues with paths
        
    Returns:
        - None if no issues
        - String summary (default)
        - List of tuples (path, issue_type, value) if return_paths=True
    """
    # Normalize inputs
    if data is None:
        data = {}
    if isinstance(data, str) and raw_text is None:
        raw_text = data
        data = {}  # Treat the string as raw_text
    raw_text = raw_text or ""

    # Collect findings
    findings = []
    findings.extend(scan_quality(data))
    if raw_text:
        findings.extend(scan_quality(raw_text, "raw_text"))

    if not findings:
        return None

    if return_paths:
        return findings

    # Default summary string
    messages = [f"{issue} in {path}" for path, issue, _ in findings]
    return "Quality Issues Detected: " + "; ".join(messages)