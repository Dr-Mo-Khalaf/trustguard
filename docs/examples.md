

# Examples Gallery

Real-world examples of using trustguard in various scenarios.

## 📋 Basic Examples

### 1. Customer Support Chatbot

```python
from trustguard import TrustGuard
from trustguard.schemas import GenericResponse
from trustguard.judges import OpenAIJudge

# Define customer support schema (extending GenericResponse)
class SupportResponse(GenericResponse):
    ticket_id: str = None
    escalation_needed: bool = False

# Create judge for sentiment analysis
judge = OpenAIJudge(
    model="gpt-4o-mini",
    config={
        "system_prompt": "You are a customer support quality analyst. "
                        "Flag responses that are rude, unhelpful, or escalate unnecessarily."
    }
)

# Initialize guard
guard = TrustGuard(
    schema_class=SupportResponse,
    judge=judge
)

# Validate support responses
response = '''
{
    "content": "I've helped the user reset their password. They were very grateful.",
    "sentiment": "positive",
    "tone": "helpful",
    "is_helpful": true,
    "ticket_id": "TKT-123",
    "escalation_needed": false
}
'''

result = guard.validate(response)
if result.is_approved:
    print("✅ Support response approved")
    print(f"Ticket: {result.data['ticket_id']}")
else:
    print(f"❌ Response blocked: {result.log}")
```

### 2. Code Generation Assistant

```python
from trustguard import TrustGuard
from trustguard.schemas import BaseResponse
from trustguard.judges import CallableJudge
import ast
import json

class CodeResponse(BaseResponse):
    code: str
    language: str
    explanation: str
    has_errors: bool = False

def security_check(text):
    """Check for dangerous code patterns."""
    data = json.loads(text)
    code = data.get("code", "")
    
    dangerous_patterns = [
        "eval(", "exec(", "__import__", "subprocess",
        "os.system", "shutil.rmtree", "rm -rf",
        "sudo ", "chmod 777", "chown"
    ]
    
    for pattern in dangerous_patterns:
        if pattern in code:
            return {
                "safe": False,
                "reason": f"Dangerous pattern detected: {pattern}",
                "risk_category": "security"
            }
    
    # Try to parse Python code for syntax errors
    if data.get("language") == "python":
        try:
            ast.parse(code)
        except SyntaxError as e:
            return {
                "safe": False,
                "reason": f"Syntax error: {e}",
                "risk_category": "quality"
            }
    
    return {"safe": True, "reason": "Code looks safe"}

# Create guard
guard = TrustGuard(
    schema_class=CodeResponse,
    judge=CallableJudge(security_check, name="CodeSecurity")
)

# Validate generated code
code_response = '''
{
    "code": "def hello():\\n    print('Hello, World!')",
    "language": "python",
    "explanation": "Simple hello world function",
    "has_errors": false
}
'''

result = guard.validate(code_response)
print(f"Code validation: {result.status}")
if result.is_approved:
    print("✅ Code is safe to use")
```

### 3. Medical Information Validator

```python
from trustguard import TrustGuard
from trustguard.schemas import BaseResponse
from trustguard.judges import EnsembleJudge, OpenAIJudge, CallableJudge
from typing import List

class MedicalResponse(BaseResponse):
    diagnosis: str
    confidence: float
    recommendations: List[str]
    disclaimer: str
    requires_doctor: bool

def medical_terminology_check(data, raw_text, context=None):
    """Check for proper medical terminology."""
    text = raw_text.lower()
    red_flags = ["cure", "miracle", "guaranteed", "secret", "ancient remedy"]
    
    for flag in red_flags:
        if flag in text:
            return f"Unprofessional term detected: {flag}"
    return None

def disclaimer_check(data, raw_text, context=None):
    """Ensure proper medical disclaimer is present."""
    if "consult" not in data.get("disclaimer", "").lower():
        return "Missing required medical disclaimer"
    if "doctor" not in data.get("disclaimer", "").lower():
        return "Disclaimer must mention consulting a doctor"
    return None

# Create ensemble of judges
judges = [
    OpenAIJudge(
        model="gpt-4o-mini",
        weight=2.0,
        config={
            "system_prompt": "You are a medical ethics reviewer. "
                            "Flag any response that could be harmful or lacks proper disclaimers."
        }
    ),
    CallableJudge(medical_terminology_check, weight=1.0),
]

guard = TrustGuard(
    schema_class=MedicalResponse,
    custom_rules=[disclaimer_check],
    judge=EnsembleJudge(judges, strategy="strict")
)

# Validate medical response
medical_response = '''
{
    "diagnosis": "Common cold symptoms",
    "confidence": 0.7,
    "recommendations": ["Rest", "Hydrate", "Consult doctor if symptoms persist"],
    "disclaimer": "This is for informational purposes only. Consult a healthcare provider.",
    "requires_doctor": true
}
'''

result = guard.validate(medical_response)
print(f"Medical validation: {result.status}")
if not result.is_approved:
    print(f"Issues: {result.log}")
```

## 🔧 Advanced Examples

### 4. Multi-Language Content Moderation

```python
from trustguard import TrustGuard
from trustguard.schemas import GenericResponse
from trustguard.judges import EnsembleJudge, CallableJudge
from langdetect import detect
import json

class MultiLangResponse(GenericResponse):
    language: str
    translation: str = None

def language_detector(text):
    """Detect and validate language."""
    try:
        data = json.loads(text)
        content = data.get("content", "")
        detected = detect(content)
        
        if detected != data.get("language", ""):
            return {
                "safe": False,
                "reason": f"Language mismatch: detected {detected}, expected {data.get('language')}",
                "risk_category": "language_mismatch"
            }
    except:
        pass
    return {"safe": True, "reason": "Language check passed"}

def toxicity_check(text):
    """Multi-language toxicity check using external API."""
    # Using a mock implementation - replace with actual API
    data = json.loads(text)
    content = data.get("content", "")
    
    # Simple keyword check for demo
    toxic_words = ["hate", "kill", "stupid", "idiot"]
    found = [word for word in toxic_words if word in content.lower()]
    
    if found:
        return {
            "safe": False,
            "reason": f"Toxic content detected: {', '.join(found)}",
            "confidence": 0.9,
            "risk_category": "toxicity"
        }
    return {"safe": True, "reason": "Content appears safe"}

# Create guard with ensemble
guard = TrustGuard(
    schema_class=MultiLangResponse,
    judge=EnsembleJudge([
        CallableJudge(language_detector, weight=1.0, name="LanguageDetector"),
        CallableJudge(toxicity_check, weight=2.0, name="ToxicityChecker")
    ], strategy="weighted_vote")
)

# Test multilingual content
test_input = '''
{
    "content": "Je déteste ce service!",
    "sentiment": "negative",
    "tone": "angry",
    "is_helpful": false,
    "language": "fr"
}
'''

result = guard.validate(test_input)
print(f"Multi-language check: {result.status}")
print(f"Reason: {result.log}")
```

### 5. Financial Compliance Checker

```python
from trustguard import TrustGuard
from trustguard.schemas import BaseResponse
from trustguard.judges import OpenAIJudge, CallableJudge
import re
import json

class FinancialResponse(BaseResponse):
    advice: str
    risk_level: str  # "low", "medium", "high"
    disclaimer: str
    regulated: bool
    ticker_symbols: List[str] = []

def compliance_rules(data, raw_text, context=None):
    """Check financial compliance rules."""
    text = raw_text.lower()
    
    # Check for required disclaimers
    required_disclaimers = [
        "past performance does not guarantee future results",
        "not financial advice",
        "consult a financial advisor",
        "invest at your own risk"
    ]
    
    missing = []
    for disclaimer in required_disclaimers:
        if disclaimer not in text:
            missing.append(disclaimer)
    
    if missing:
        return f"Missing required disclaimers: {', '.join(missing[:2])}..."
    
    # Check for regulated terms
    regulated_terms = [
        "guaranteed return", "risk-free", "certain profit",
        "beat the market", "secret strategy", "insider tip"
    ]
    
    for term in regulated_terms:
        if term in text:
            return f"Prohibited regulated term: {term}"
    
    return None

# Create compliance judge
compliance_judge = OpenAIJudge(
    model="gpt-4o-mini",
    config={
        "system_prompt": "You are a financial compliance officer at the SEC. "
                        "Flag any advice that violates regulations or could mislead investors."
    }
)

guard = TrustGuard(
    schema_class=FinancialResponse,
    custom_rules=[compliance_rules],
    judge=compliance_judge
)

# Validate financial advice
financial_response = '''
{
    "advice": "Consider diversifying your portfolio with index funds like VOO and QQQ.",
    "risk_level": "low",
    "disclaimer": "Past performance does not guarantee future results. This is not financial advice. Consult a financial advisor. Invest at your own risk.",
    "regulated": false,
    "ticker_symbols": ["VOO", "QQQ"]
}
'''

result = guard.validate(financial_response)
print(f"Financial compliance: {result.status}")
if result.is_approved:
    print("✅ Response complies with regulations")
```

### 6. Real-Time Streaming Validation

```python
import asyncio
from trustguard import TrustGuard
from trustguard.schemas import GenericResponse
from trustguard.judges import OllamaJudge

class StreamingValidator:
    def __init__(self):
        self.guard = TrustGuard(
            schema_class=GenericResponse,
            judge=OllamaJudge(model="phi3")
        )
        self.buffer = ""
        self.results = []
    
    async def validate_stream(self, stream):
        """Validate a streaming response in real-time."""
        async for chunk in stream:
            self.buffer += chunk
            
            # Try to extract complete JSON objects
            if self.buffer.count('{') == self.buffer.count('}'):
                # Complete JSON object
                result = await self.guard.judge.async_judge(self.buffer)
                self.results.append(result)
                
                if not result["safe"]:
                    print(f"⚠️ Safety issue detected: {result['reason']}")
                    # Take action (stop stream, flag content, etc.)
                    await stream.close()
                    break
                
                self.buffer = ""
        
        return self.results

# Usage
async def main():
    validator = StreamingValidator()
    
    # Simulate streaming response
    async def mock_stream():
        chunks = [
            '{"content": "First part of response",',
            '"sentiment": "positive",',
            '"tone": "helpful",',
            '"is_helpful": true}'
        ]
        for chunk in chunks:
            yield chunk
            await asyncio.sleep(0.1)
    
    results = await validator.validate_stream(mock_stream())
    print(f"Validated {len(results)} chunks")

# Run
# asyncio.run(main())
```

## 🚀 Production Examples

### 7. High-Volume API Endpoint

```python
from fastapi import FastAPI, HTTPException
from trustguard import TrustGuard
from trustguard.schemas import GenericResponse
from trustguard.judges import EnsembleJudge, OpenAIJudge, OllamaJudge
import aioredis
import json
import time

app = FastAPI()

# Initialize cache (mock for demo - use real Redis in production)
class MockRedis:
    def __init__(self):
        self.cache = {}
    
    async def get(self, key):
        return self.cache.get(key)
    
    async def setex(self, key, ttl, value):
        self.cache[key] = value

redis = MockRedis()

# Create judge with caching
class CachedJudge:
    def __init__(self, judge, redis_client, ttl=3600):
        self.judge = judge
        self.redis = redis_client
        self.ttl = ttl
    
    async def judge(self, text):
        # Check cache
        cache_key = f"judge:{hash(text)}"
        cached = await self.redis.get(cache_key)
        if cached:
            return json.loads(cached)
        
        # Run judge
        start = time.time()
        result = await self.judge.async_judge(text)
        latency = time.time() - start
        
        # Add metadata
        result["metadata"] = result.get("metadata", {})
        result["metadata"]["cache_hit"] = False
        result["metadata"]["latency_ms"] = round(latency * 1000, 2)
        
        # Cache result
        await self.redis.setex(
            cache_key,
            self.ttl,
            json.dumps(result)
        )
        
        return result

# Initialize production guard
guard = TrustGuard(
    schema_class=GenericResponse,
    judge=CachedJudge(
        EnsembleJudge([
            OllamaJudge(model="phi3", weight=1.0),  # Fast local
            OpenAIJudge(model="gpt-4o-mini", weight=2.0)  # Accurate cloud
        ], strategy="weighted_vote"),
        redis
    ),
    config={"fail_on_judge_error": False}  # Don't block on errors
)

@app.post("/validate")
async def validate_response(response: dict):
    """Validate an LLM response."""
    try:
        result = guard.validate(json.dumps(response))
        
        return {
            "status": result.status,
            "log": result.log,
            "data": result.data if result.is_approved else None,
            "timestamp": result.timestamp
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/stats")
async def get_stats():
    """Get validation statistics."""
    return guard.get_stats()

# To run: uvicorn main:app --reload
```

### 8. A/B Testing Framework

```python
from trustguard import TrustGuard
from trustguard.schemas import GenericResponse
from trustguard.judges import OpenAIJudge, OllamaJudge, EnsembleJudge
import random
import json
from datetime import datetime

class ABTestGuard:
    """A/B test different judge configurations."""
    
    def __init__(self):
        self.configs = {
            "A": {  # Fast, cheap
                "name": "Fast Local",
                "judge": OllamaJudge(model="phi3"),
                "rules": True,
                "cost_per_request": 0.001,
                "enabled": True
            },
            "B": {  # Accurate, expensive
                "name": "Cloud GPT",
                "judge": OpenAIJudge(model="gpt-4o-mini"),
                "rules": True,
                "cost_per_request": 0.01,
                "enabled": True
            },
            "C": {  # Ensemble
                "name": "Hybrid Ensemble",
                "judge": EnsembleJudge([
                    OllamaJudge(model="phi3", weight=1.0),
                    OpenAIJudge(model="gpt-4o-mini", weight=2.0)
                ]),
                "rules": True,
                "cost_per_request": 0.011,
                "enabled": True
            }
        }
        
        self.results = {config_id: {
            "total": 0,
            "approved": 0,
            "rejected": 0,
            "cost": 0,
            "total_latency": 0,
            "errors": 0
        } for config_id in self.configs}
    
    def validate(self, text, config_name=None):
        """Validate using specified or random config."""
        if config_name is None:
            # A/B test - randomly assign from enabled configs
            enabled = [k for k, v in self.configs.items() if v["enabled"]]
            config_name = random.choice(enabled)
        
        config = self.configs[config_name]
        
        # Create guard with this config
        guard = TrustGuard(
            schema_class=GenericResponse,
            judge=config["judge"]
        )
        
        # Validate with timing
        start = datetime.now()
        try:
            result = guard.validate(text)
            latency = (datetime.now() - start).total_seconds()
            
            # Track results
            self.results[config_name]["total"] += 1
            if result.is_approved:
                self.results[config_name]["approved"] += 1
            else:
                self.results[config_name]["rejected"] += 1
            
            self.results[config_name]["cost"] += config["cost_per_request"]
            self.results[config_name]["total_latency"] += latency
            
            return result, config_name
            
        except Exception as e:
            self.results[config_name]["errors"] += 1
            raise e
    
    def get_report(self):
        """Get A/B test results."""
        report = {}
        for config_id, stats in self.results.items():
            if stats["total"] > 0:
                report[config_id] = {
                    "name": self.configs[config_id]["name"],
                    "total": stats["total"],
                    "approval_rate": stats["approved"] / stats["total"],
                    "rejection_rate": stats["rejected"] / stats["total"],
                    "avg_cost": stats["cost"] / stats["total"],
                    "avg_latency_ms": (stats["total_latency"] / stats["total"]) * 1000,
                    "error_rate": stats["errors"] / stats["total"] if stats["total"] > 0 else 0
                }
        return report

# Usage
tester = ABTestGuard()

# Simulate traffic
test_texts = [
    '{"content":"Help me reset my password","sentiment":"neutral","tone":"professional","is_helpful":true}',
    '{"content":"Your service sucks!","sentiment":"negative","tone":"angry","is_helpful":false}',
    '{"content":"Contact me at john@example.com","sentiment":"neutral","tone":"professional","is_helpful":true}',
]

for _ in range(100):
    text = random.choice(test_texts)
    result, config = tester.validate(text)

# Get results
print(json.dumps(tester.get_report(), indent=2))
```

## 📊 Example Outputs

### Safe Response
```json
{
    "status": "APPROVED",
    "log": "All checks passed.",
    "data": {
        "content": "I can help you with that.",
        "sentiment": "positive",
        "tone": "helpful",
        "is_helpful": true
    },
    "timestamp": "2024-01-01T00:00:00.000000+00:00"
}
```

### PII Detection
```json
{
    "status": "REJECTED",
    "log": "PII Detected: Email address found in field 'content'",
    "data": {
        "content": "Contact me at john@example.com",
        "sentiment": "neutral",
        "tone": "professional",
        "is_helpful": true
    },
    "timestamp": "2024-01-01T00:00:00.000000+00:00"
}
```

### Judge Detection
```json
{
    "status": "REJECTED",
    "log": "Judge [harassment] (medium): Text contains insulting language",
    "data": {
        "content": "You are so stupid!",
        "sentiment": "negative",
        "tone": "angry",
        "is_helpful": false
    },
    "timestamp": "2024-01-01T00:00:00.000000+00:00"
}
```

### Batch Validation Report
```text
Total: 100 | Passed: 85 | Failed: 15
Top failures:
  - PII Detected: 8
  - Toxicity: 4
  - Schema Error: 2
  - Judge [harassment]: 1
```

## 🎯 Next Steps

- Try the [Quick Start Guide](quickstart.md) to get started
- Learn about [Custom Judges](judges.md)
- Read the [API Reference](api.md)
- [Contribute](contributing.md) your own examples

## 📚 Related Topics

- [Core Concepts](concepts.md) - How trustguard works
- [Judge System](judges.md) - Deep dive into judges
- [Rules System](rules.md) - Built-in validation rules
- [Schema Validation](schemas.md) - Define your own schemas
