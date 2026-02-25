#!/usr/bin/env python3
"""
Demo showing how to use ANY model with CallableJudge.
"""

import json
from trustguard import TrustGuard
from trustguard.schemas import GenericResponse
from trustguard.judges import CallableJudge


def demo_hugging_face():
    """Use Hugging Face transformers as a judge."""
    print("\n🤗 Hugging Face Judge Demo")
    print("-" * 40)
    
    try:
        from transformers import pipeline
        
        # Create a toxicity classifier
        classifier = pipeline(
            "text-classification",
            model="unitary/toxic-bert",
            device=-1  # CPU
        )
        
        def judge(text):
            # Extract content from JSON if needed
            try:
                data = json.loads(text)
                content = data.get("content", text)
            except:
                content = text
                
            result = classifier(content[:512])[0]  # Truncate long texts
            return {
                "safe": result["label"] == "non-toxic",
                "reason": f"Toxicity score: {result['score']:.3f}",
                "confidence": result["score"],
                "risk_category": "toxicity" if result["label"] != "non-toxic" else "none"
            }
        
        guard = TrustGuard(
            schema_class=GenericResponse,
            judge=CallableJudge(judge, name="HuggingFaceToxicBERT")
        )
        
        test_text = json.dumps({
            "content": "You are an idiot and I hate you!",
            "sentiment": "negative",
            "tone": "angry",
            "is_helpful": False
        })
        
        result = guard.validate(test_text)
        print(f"Result: {result.status}")
        print(f"Log: {result.log}")
        
    except ImportError:
        print("⚠️  transformers not installed. Run: pip install transformers")


def demo_simple_keyword():
    """Use a simple keyword-based judge."""
    print("\n🔧 Simple Keyword Judge Demo")
    print("-" * 40)
    
    # Simple rule-based judge
    def keyword_judge(text):
        bad_words = ["kill", "die", "hate", "stupid", "idiot"]
        
        # Extract content
        try:
            data = json.loads(text)
            content = data.get("content", "").lower()
        except:
            content = text.lower()
        
        found = [w for w in bad_words if w in content]
        if found:
            return {
                "safe": False,
                "reason": f"Found forbidden words: {', '.join(found)}",
                "risk_category": "profanity"
            }
        return {"safe": True, "reason": "No forbidden words"}
    
    guard = TrustGuard(
        schema_class=GenericResponse,
        judge=CallableJudge(keyword_judge, name="KeywordFilter")
    )
    
    # Test with safe text
    safe_text = json.dumps({
        "content": "I can help you with your problem.",
        "sentiment": "positive",
        "tone": "helpful",
        "is_helpful": True
    })
    
    print("\n📝 Testing safe text...")
    result = guard.validate(safe_text)
    print(f"Result: {result.status}")
    
    # Test with unsafe text
    unsafe_text = json.dumps({
        "content": "I hate this stupid service!",
        "sentiment": "negative",
        "tone": "angry",
        "is_helpful": False
    })
    
    print("\n📝 Testing unsafe text...")
    result = guard.validate(unsafe_text)
    print(f"Result: {result.status}")
    print(f"Log: {result.log}")


if __name__ == "__main__":
    demo_hugging_face()
    demo_simple_keyword()
