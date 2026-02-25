"""
trustguard - Intelligent validation for LLM outputs.
Lightweight, schema-first safety checks with pluggable judge system for AI applications.
"""

__version__ = "0.2.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

from trustguard.core import TrustGuard
from trustguard import rules
from trustguard import schemas
from trustguard import exceptions
from trustguard import validators
from trustguard import wrappers
from trustguard import judges

__all__ = [
    "TrustGuard",
    "rules",
    "schemas",
    "exceptions",
    "validators",
    "wrappers",
    "judges",
]
