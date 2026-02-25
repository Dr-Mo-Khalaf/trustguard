#!/usr/bin/env python3
"""
Demo showing ensemble of judges for maximum accuracy.
"""

import json
from trustguard import TrustGuard
from trustguard.schemas import GenericResponse
from trustguard.judges import EnsembleJudge, CallableJudge


def simple_rule_judge(text):
    """Simple rule-based judge for demonstration."""
    try:
        data = json.loads(text)
        content = data.get("content", "").lower()
    except:
        content = text.lower()
    
    if "kill" in content and "bug" not in content:
        return {"safe": False, "reason": "Violent content detected", "risk_category": "violence"}
    if "hate" in content:
        return {"safe": False, "reason": "Hate speech detected", "risk_category": "hate_speech"}
    return {"safe": True, "reason": "Passed rule check"}


def sentiment_judge(text):
    """Judge based on sentiment."""
    try:
        data = json.loads(text)
        sentiment = data.get("sentiment", "neutral")
        if sentiment == "negative":
            return {"safe": False, "reason": "Negative sentiment detected", "risk_category": "negative_sentiment"}
        return {"safe": True, "reason": "Positive/neutral sentiment"}
    except:
        return {"safe": True, "reason": "Could not parse sentiment"}


def length_judge(text):
    """Judge based on content length."""
    try:
        data = json.loads(text)
        content = data.get("content", "")
        if len(content) > 200:
            return {"safe": False, "reason": "Response too long", "risk_category": "length"}
        if len(content) < 10:
            return {"safe": False, "reason": "Response too short", "risk_category": "length"}
        return {"safe": True, "reason": "Appropriate length"}
    except:
        return {"safe": True, "reason": "Could not check length"}


def main():
    print("=" * 60)
    print("Ensemble Judge Demo - Maximum Accuracy")
    print("=" * 60)
    
    # Create multiple judges with different weights
    judges = [
        CallableJudge(simple_rule_judge, name="RuleJudge", weight=2.0),
        CallableJudge(sentiment_judge, name="SentimentJudge", weight=1.5),
        CallableJudge(length_judge, name="LengthJudge", weight=1.0),
    ]
    
    # Test different ensemble strategies
    strategies = ["weighted_vote", "majority_vote", "strict", "lenient"]
    
    # Test cases
    test_cases = [
        {
            "name": "Safe technical content",
            "text": json.dumps({
                "content": "To fix the bug, we need to update the database schema.",
                "sentiment": "neutral",
                "tone": "technical",
                "is_helpful": True
            })
        },
        {
            "name": "Ambiguous threat",
            "text": json.dumps({
                "content": "I will kill this process if it doesn't respond.",
                "sentiment": "frustrated",
                "tone": "technical",
                "is_helpful": True
            })
        },
        {
            "name": "Negative but safe",
            "text": json.dumps({
                "content": "I'm not happy with the service today.",
                "sentiment": "negative",
                "tone": "frustrated",
                "is_helpful": False
            })
        }
    ]
    
    for strategy in strategies:
        print(f"\n📊 Strategy: {strategy}")
        print("-" * 40)
        
        # Create ensemble with this strategy
        ensemble = EnsembleJudge(judges, strategy=strategy)
        guard = TrustGuard(schema_class=GenericResponse, judge=ensemble)
        
        for test in test_cases:
            result = guard.validate(test['text'])
            status = "✅" if result.is_approved else "❌"
            print(f"{status} {test['name'][:30]:<30} | {result.log[:50]}...")


if __name__ == "__main__":
    main()
