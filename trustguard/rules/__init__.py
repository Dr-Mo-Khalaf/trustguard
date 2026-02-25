"""
Built-in validation rules for trustguard.
"""

from trustguard.rules.pii import validate_pii
from trustguard.rules.blocklist import validate_blocklist
from trustguard.rules.toxicity import validate_toxicity
from trustguard.rules.quality import validate_quality

# Default rules included in the package
DEFAULT_RULES = [
    validate_pii,
    validate_blocklist,
    validate_toxicity,
    validate_quality,
]

__all__ = [
    "DEFAULT_RULES",
    "validate_pii",
    "validate_blocklist",
    "validate_toxicity",
    "validate_quality",
]
