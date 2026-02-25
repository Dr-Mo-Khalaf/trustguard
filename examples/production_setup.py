#!/usr/bin/env python3
"""
Production-ready setup with cascading validation for cost optimization.
"""

import json
import time
from typing import Dict, Any
from trustguard import TrustGuard
from trustguard.schemas import GenericResponse
from trustguard.judges import CallableJudge


class ProductionGuard:
    """
    Production-ready guard with cascading validation for cost optimization.
    
    Strategy:
    1. Fast rules (PII, blocklist) - always run
    2. Fast keyword judge - if available
    3. Slower ML judge - only if keyword judge is uncertain
    """
    
    def __init__(self):
        self.stats = {
            "total": 0,
            "rules_only": 0,
            "fast_judge": 0,
            "slow_judge": 0,
            "rejected": 0
        }
        
        # Create base guard without judge
        self.base_guard = TrustGuard(
            schema_class=GenericResponse
        )
        
        # Create fast keyword judge
        def keyword_judge(text):
            try:
                data = json.loads(text)
                content = data.get("content", "").lower()
            except:
                content = text.lower()
            
            # Very fast keyword check
            severe_words = ["kill", "die", "threat", "attack"]
            moderate_words = ["hate", "stupid", "idiot", "dumb"]
            
            for word in severe_words:
                if word in content:
                    return {
                        "safe": False,
                        "reason": f"Severe word detected: {word}",
                        "confidence": 1.0,
                        "risk_category": "severe"
                    }
            
            for word in moderate_words:
                if word in content:
                    return {
                        "safe": True,  # Uncertain, needs further checking
                        "reason": f"Moderate word detected: {word}",
                        "confidence": 0.5,
                        "risk_category": "moderate"
                    }
            
            return {"safe": True, "reason": "No issues found", "confidence": 0.9}
        
        self.fast_judge = CallableJudge(keyword_judge, name="FastKeyword")
        
        # Create slower ML-based judge (simulated)
        def ml_judge(text):
            # Simulate ML inference time
            time.sleep(0.1)
            
            try:
                data = json.loads(text)
                content = data.get("content", "").lower()
            except:
                content = text.lower()
            
            # More sophisticated analysis
            if "kill" in content and "bug" in content:
                return {"safe": True, "reason": "Context: bug fixing", "confidence": 0.95}
            if "hate" in content and "service" in content:
                return {"safe": True, "reason": "Service complaint", "confidence": 0.8}
            
            return {"safe": True, "reason": "ML judge approved", "confidence": 0.7}
        
        self.slow_judge = CallableJudge(ml_judge, name="MLJudge")
    
    def validate(self, text: str) -> Dict[str, Any]:
        """Validate with cascading judges."""
        self.stats["total"] += 1
        
        # Step 1: Fast rules only
        result = self.base_guard.validate(text)
        if result.is_rejected:
            self.stats["rejected"] += 1
            self.stats["rules_only"] += 1
            return result.to_dict()
        
        # Step 2: Fast keyword judge
        fast_result = self.fast_judge.judge(text)
        
        if not fast_result["safe"] and fast_result["confidence"] > 0.8:
            # High confidence rejection
            self.stats["rejected"] += 1
            self.stats["fast_judge"] += 1
            result.status = "REJECTED"
            result.log = f"Fast judge: {fast_result['reason']}"
            return result.to_dict()
        
        if fast_result["confidence"] < 0.7:
            # Uncertain, use slow judge
            self.stats["slow_judge"] += 1
            slow_result = self.slow_judge.judge(text)
            
            if not slow_result["safe"]:
                self.stats["rejected"] += 1
                result.status = "REJECTED"
                result.log = f"ML judge: {slow_result['reason']}"
        else:
            self.stats["fast_judge"] += 1
        
        return result.to_dict()
    
    def print_stats(self):
        """Print validation statistics."""
        print("\n📊 Production Guard Statistics")
        print("-" * 40)
        print(f"Total validations: {self.stats['total']}")
        if self.stats['total'] > 0:
            print(f"  Rules only: {self.stats['rules_only']} ({self.stats['rules_only']/self.stats['total']*100:.1f}%)")
            print(f"  Fast judge: {self.stats['fast_judge']} ({self.stats['fast_judge']/self.stats['total']*100:.1f}%)")
            print(f"  Slow judge: {self.stats['slow_judge']} ({self.stats['slow_judge']/self.stats['total']*100:.1f}%)")
            print(f"  Rejected: {self.stats['rejected']} ({self.stats['rejected']/self.stats['total']*100:.1f}%)")


def main():
    """Run production demo."""
    guard = ProductionGuard()
    
    # Simulate traffic
    test_cases = [
        '{"content":"Help me reset password","sentiment":"neutral","tone":"professional","is_helpful":true}',
        '{"content":"Your service sucks!","sentiment":"negative","tone":"angry","is_helpful":false}',
        '{"content":"Contact me at john@example.com","sentiment":"neutral","tone":"professional","is_helpful":true}',
        '{"content":"I will kill this bug in the code","sentiment":"frustrated","tone":"technical","is_helpful":true}',
        '{"content":"This is a normal request","sentiment":"neutral","tone":"professional","is_helpful":true}',
        '{"content":"I hate this stupid service!","sentiment":"negative","tone":"angry","is_helpful":false}',
    ] * 10  # 60 total
    
    print("🚀 Processing 60 validation requests with cascading judges...")
    start = time.time()
    
    for text in test_cases:
        guard.validate(text)
    
    elapsed = time.time() - start
    
    guard.print_stats()
    print(f"\n⏱️  Total time: {elapsed:.2f}s")
    print(f"⚡ Avg time: {elapsed/len(test_cases)*1000:.1f}ms per request")


if __name__ == "__main__":
    main()
