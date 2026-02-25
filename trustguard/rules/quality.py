"""
Response quality validation rules.
"""

from typing import Optional, Dict, Any


def validate_quality(
    data: Dict[str, Any],
    raw_text: str,
    context: Optional[Dict[str, Any]] = None
) -> Optional[str]:
    """
    Check response quality (length, completeness, etc.).
    
    Args:
        data: Parsed JSON data
        raw_text: Original raw text
        context: Optional context dictionary
        
    Returns:
        Error message if quality issues found, None otherwise
    """
    # Check content length if present
    if "content" in data and isinstance(data["content"], str):
        content = data["content"]
        
        # Too short? (more lenient: 3 characters minimum)
        if len(content) < 3:
            return "Quality Issue: Response content too short (<3 characters)"
        
        # Too long?
        if len(content) > 10000:
            return "Quality Issue: Response content too long (>10000 characters)"
    
    # Check for repetitive content (only if text is long enough)
    words = raw_text.split()
    if len(words) > 50:  # Only check if there are enough words
        # Check for repeated words
        word_counts = {}
        for word in words:
            word_lower = word.lower()
            word_counts[word_lower] = word_counts.get(word_lower, 0) + 1
        
        max_repetition = max(word_counts.values())
        if max_repetition > len(words) * 0.5:  # 50% repetition (more lenient)
            return "Quality Issue: Excessive word repetition detected"
    
    return None
