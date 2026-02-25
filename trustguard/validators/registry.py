"""
Validator registry system for trustguard.
"""

import json
from typing import Dict, Any, Callable, Optional, List
from functools import wraps
from datetime import datetime
from pathlib import Path

from trustguard.exceptions import RegistryError


class ValidatorRegistry:
    """
    Registry for managing and discovering validators.
    """
    
    def __init__(self, registry_file: Optional[str] = None):
        self._validators: Dict[str, Dict[str, Any]] = {}
        self.registry_file = registry_file
        
        # Load from file if exists
        if registry_file and Path(registry_file).exists():
            self.load(registry_file)
    
    def register(
        self,
        name: str,
        priority: int = 0,
        description: str = "",
        tags: Optional[List[str]] = None,
    ) -> Callable:
        """
        Decorator to register a validator.
        
        Args:
            name: Validator name
            priority: Priority (higher runs first)
            description: Validator description
            tags: List of tags for categorization
        """
        def decorator(func: Callable) -> Callable:
            self._validators[name] = {
                "function": func,
                "priority": priority,
                "description": description or func.__doc__ or "",
                "tags": tags or [],
                "registered_at": datetime.utcnow().isoformat(),
                "name": name,
            }
            
            @wraps(func)
            def wrapper(*args, **kwargs):
                return func(*args, **kwargs)
            
            return wrapper
        return decorator
    
    def get(self, name: str) -> Optional[Callable]:
        """Get validator by name."""
        if name in self._validators:
            return self._validators[name]["function"]
        return None
    
    def list(self, tag: Optional[str] = None) -> List[Dict[str, Any]]:
        """List all registered validators."""
        validators = list(self._validators.values())
        
        if tag:
            validators = [v for v in validators if tag in v["tags"]]
        
        # Sort by priority (higher first)
        return sorted(validators, key=lambda x: -x["priority"])
    
    def run(self, name: str, *args, **kwargs) -> Any:
        """Run a validator by name."""
        validator = self.get(name)
        if not validator:
            raise RegistryError(f"Validator '{name}' not found")
        return validator(*args, **kwargs)
    
    def save(self, filepath: str):
        """Save registry to file."""
        data = {
            name: {k: v for k, v in info.items() if k != "function"}
            for name, info in self._validators.items()
        }
        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)
    
    def load(self, filepath: str):
        """Load registry from file."""
        with open(filepath) as f:
            data = json.load(f)
        
        # Note: This only loads metadata, not functions
        for name, info in data.items():
            if name not in self._validators:
                self._validators[name] = {
                    "function": None,  # Function needs to be registered separately
                    **info
                }


# Global registry instance
registry = ValidatorRegistry()


def rule(
    name: Optional[str] = None,
    priority: int = 0,
    description: str = "",
    tags: Optional[List[str]] = None,
) -> Callable:
    """
    Decorator to register a validation rule.
    
    Example:
        @rule(name="no_profanity", priority=1, tags=["safety"])
        def check_profanity(data, raw_text):
            if "badword" in raw_text:
                return "Profanity detected"
            return None
    """
    def decorator(func: Callable) -> Callable:
        rule_name = name or func.__name__
        registry.register(
            name=rule_name,
            priority=priority,
            description=description,
            tags=tags,
        )(func)
        return func
    return decorator
