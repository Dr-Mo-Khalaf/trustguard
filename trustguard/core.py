"""
Core validation engine for trustguard.
"""

import json
import re
import random
from datetime import datetime, timezone
from typing import List, Callable, Dict, Any, Optional, Type
from pydantic import BaseModel, ValidationError

from trustguard.validators.registry import ValidatorRegistry
from trustguard.exceptions import ValidationError as TrustValidationError


class ValidationResult:
    """Result of a validation operation."""
    
    def __init__(
        self,
        status: str,
        log: str = "",
        data: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        self.status = status  # "APPROVED" or "REJECTED"
        self.log = log
        self.data = data or {}
        self.metadata = metadata or {}
        self.timestamp = datetime.now(timezone.utc).isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "status": self.status,
            "log": self.log,
            "data": self.data,
            "metadata": self.metadata,
            "timestamp": self.timestamp,
        }
    
    @property
    def is_approved(self) -> bool:
        return self.status == "APPROVED"
    
    @property
    def is_rejected(self) -> bool:
        return self.status == "REJECTED"
    
    def __repr__(self) -> str:
        return f"ValidationResult(status={self.status}, log={self.log!r})"


class BatchValidationReport:
    """Report for batch validation operations."""
    
    def __init__(self, results: List[ValidationResult]):
        self.results = results
        self.total = len(results)
        self.passed = sum(1 for r in results if r.is_approved)
        self.failed = self.total - self.passed
        
        self.failure_counts = {}
        for r in results:
            if r.is_rejected and r.log:
                reason = r.log.split(":")[0] if ":" in r.log else r.log
                self.failure_counts[reason] = self.failure_counts.get(reason, 0) + 1
    
    def summary(self) -> str:
        lines = [
            f"Total: {self.total} | Passed: {self.passed} | Failed: {self.failed}",
        ]
        if self.failure_counts:
            lines.append("Top failures:")
            for reason, count in sorted(
                self.failure_counts.items(), key=lambda x: x[1], reverse=True
            )[:5]:
                lines.append(f"  - {reason}: {count}")
        return "\n".join(lines)
    
    def to_dataframe(self):
        try:
            import pandas as pd
            return pd.DataFrame([r.to_dict() for r in self.results])
        except ImportError:
            raise ImportError("pandas is required for dataframe conversion")
    
    def to_polars(self):
        try:
            import polars as pl
            return pl.DataFrame([r.to_dict() for r in self.results])
        except ImportError:
            raise ImportError("polars is required for dataframe conversion")


class TrustGuard:
    """
    Main validation engine for trustguard.
    
    Args:
        schema_class: A Pydantic BaseModel class defining the expected output structure
        custom_rules: List of validation functions taking (data, raw_text) -> error_msg or None
        config: Configuration dictionary
        validator_registry: Custom validator registry instance
        judge: Optional judge for AI-powered validation
    """
    
    def __init__(
        self,
        schema_class: Type[BaseModel],
        custom_rules: Optional[List[Callable]] = None,
        config: Optional[Dict[str, Any]] = None,
        validator_registry: Optional[ValidatorRegistry] = None,
        judge: Optional['BaseJudge'] = None,
    ):
        self.schema_class = schema_class
        self.custom_rules = custom_rules or []
        self.config = config or {}
        self.validator_registry = validator_registry or ValidatorRegistry()
        self.judge = judge
        
        # Load default rules if no custom rules provided
        # if not custom_rules: # bug solved report1
        if custom_rules is None:
            try:
                from trustguard.rules import DEFAULT_RULES
                self.custom_rules = DEFAULT_RULES.copy()
            except (ImportError, AttributeError):
                pass
        
        # Statistics
        self.stats = {
            "total_validations": 0,
            "approved": 0,
            "rejected": 0,
            "judge_checks": 0,
        }
    
    def validate(
        self,
        raw_input: str,
        context: Optional[Dict[str, Any]] = None,
        skip_judge: bool = False,
    ) -> ValidationResult:
        """
        Validate a single LLM output.
        
        Args:
            raw_input: Raw string output from an LLM
            context: Optional context dictionary (for rules that need external data)
            skip_judge: Skip judge checks even if configured
            
        Returns:
            ValidationResult object
        """
        self.stats["total_validations"] += 1
        context = context or {}
        
        # Step 1: Extract JSON
        try:
            json_str = self._extract_json(raw_input)
            data = json.loads(json_str)
        except Exception as e:
            self.stats["rejected"] += 1
            return ValidationResult(
                status="REJECTED",
                log=f"JSON Extraction Error: {str(e)}",
                metadata={"error_type": "json_extraction", "phase": "parsing"}
            )
        
        # Step 2: Schema Validation
        try:
            validated_obj = self.schema_class.model_validate(data)
            result_dict = validated_obj.model_dump()
        except ValidationError as e:
            self.stats["rejected"] += 1
            return ValidationResult(
                status="REJECTED",
                log=f"Schema Error: {str(e)}",
                data=data,
                metadata={"error_type": "schema", "phase": "validation"}
            )
        
        # Step 3: Run Custom Rules
        for rule in self.custom_rules:
            try:
                rule_name = getattr(rule, "__name__", "unknown")
                error = rule(result_dict, raw_input, context=context)
                
                if error:
                    self.stats["rejected"] += 1
                    return ValidationResult(
                        status="REJECTED",
                        log=error,
                        data=result_dict,
                        metadata={
                            "error_type": "rule",
                            "rule": rule_name,
                            "phase": "rules"
                        }
                    )
            except Exception as e:
                rule_name = getattr(rule, "__name__", "unknown")
                print(f"[trustguard] Rule {rule_name} failed: {e}")
        
        # Step 4: Judge Check (if configured)
        if not skip_judge and self.judge:
            self.stats["judge_checks"] += 1
            try:
                verdict = self.judge.judge(raw_input)
                
                if not verdict.get("safe", True):
                    self.stats["rejected"] += 1
                    risk_cat = verdict.get("risk_category", "Unknown")
                    reason = verdict.get("reason", "No reason provided")
                    severity = verdict.get("severity", "low")
                    
                    return ValidationResult(
                        status="REJECTED",
                        log=f"Judge [{risk_cat}] ({severity}): {reason}",
                        data=result_dict,
                        metadata={
                            "error_type": "judge",
                            "judge_name": getattr(self.judge, "name", "Unknown"),
                            "judge_verdict": verdict,
                            "phase": "judge"
                        }
                    )
            except Exception as e:
                if self.config.get("fail_on_judge_error", False):
                    raise
                print(f"[trustguard] Judge {getattr(self.judge, 'name', 'Unknown')} failed: {e}")
        
        self.stats["approved"] += 1
        return ValidationResult(
            status="APPROVED",
            data=result_dict,
            log="All checks passed.",
            metadata={"phase": "complete", "checks_passed": True}
        )
    
    def validate_batch(
        self,
        inputs: List[str],
        contexts: Optional[List[Dict[str, Any]]] = None,
        parallel: bool = False,
        max_workers: int = 4,
        **kwargs
    ) -> BatchValidationReport:
        """Validate multiple LLM outputs."""
        if contexts is None:
            contexts = [{}] * len(inputs)
        
        if len(inputs) != len(contexts):
            raise ValueError("inputs and contexts must have same length")
        
        if parallel:
            import concurrent.futures
            results = []
            with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
                futures = [
                    executor.submit(self.validate, inp, ctx, **kwargs)
                    for inp, ctx in zip(inputs, contexts)
                ]
                for future in concurrent.futures.as_completed(futures):
                    results.append(future.result())
        else:
            results = [
                self.validate(inp, ctx, **kwargs)
                for inp, ctx in zip(inputs, contexts)
            ]
        
        return BatchValidationReport(results)
    
    def _extract_json(self, text: str) -> str:
        """Extract JSON object from text, handling Markdown code blocks."""
        # Remove Markdown code blocks
        code_block_pattern = r'```(?:json)?\s*(.*?)\s*```'
        match = re.search(code_block_pattern, text, re.DOTALL | re.IGNORECASE)
        if match:
            text = match.group(1)
        
        # Remove inline code blocks
        inline_code_pattern = r'`(.*?)`'
        text = re.sub(inline_code_pattern, r'\1', text)
        
        # Try to find JSON between braces
        start = text.find('{')
        end = text.rfind('}')
        if start != -1 and end != -1 and start < end:
            return text[start:end+1]
        
        # Try to find JSON between brackets
        start = text.find('[')
        end = text.rfind(']')
        if start != -1 and end != -1 and start < end:
            return text[start:end+1]
        
        raise ValueError("No valid JSON object found in response.")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get validation statistics."""
        return self.stats.copy()
    
    def reset_stats(self):
        """Reset validation statistics."""
        self.stats = {
            "total_validations": 0,
            "approved": 0,
            "rejected": 0,
            "judge_checks": 0,
        }
    
    def __repr__(self) -> str:
        return f"TrustGuard(schema={self.schema_class.__name__}, rules={len(self.custom_rules)}, judge={self.judge is not None})"


# For type hints
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from trustguard.judges.base import BaseJudge
