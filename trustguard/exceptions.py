"""
Custom exceptions for trustguard.
"""

class TrustGuardError(Exception):
    """Base exception for all trustguard errors."""
    pass


class ConfigurationError(TrustGuardError):
    """Raised when there's a configuration issue."""
    pass


class ValidationError(TrustGuardError):
    """Raised when validation fails."""
    pass


class SchemaError(ValidationError):
    """Raised when schema validation fails."""
    pass


class RuleError(ValidationError):
    """Raised when a custom rule fails."""
    pass


class JudgeError(TrustGuardError):
    """Raised when a judge fails."""
    pass


class WrapperError(TrustGuardError):
    """Raised when LLM provider wrapper fails."""
    pass


class RegistryError(TrustGuardError):
    """Raised when validator registry operations fail."""
    pass
