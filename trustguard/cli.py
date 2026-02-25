#!/usr/bin/env python3
"""
Command-line interface for trustguard.
"""

import argparse
import json
import sys
from pathlib import Path

from trustguard import TrustGuard, __version__
from trustguard.schemas import GenericResponse
from trustguard.rules import DEFAULT_RULES


def demo() -> int:
    """Run a demo of trustguard."""
    print("=" * 60)
    print("trustguard Demo - Intelligent LLM Validation")
    print("=" * 60)
    
    guard = TrustGuard(
        schema_class=GenericResponse,
        custom_rules=DEFAULT_RULES,
        config={"enable_judge": False}
    )
    
    test_cases = [
        {
            "name": "✅ Safe Response",
            "input": json.dumps({
                "content": "I'd be happy to help you reset your password.",
                "sentiment": "positive",
                "tone": "helpful",
                "is_helpful": True
            })
        },
        {
            "name": "⚠️  PII Leak",
            "input": json.dumps({
                "content": "Contact me at john.doe@example.com",
                "sentiment": "neutral",
                "tone": "professional",
                "is_helpful": True
            })
        },
        {
            "name": "🚫 Toxic Content",
            "input": json.dumps({
                "content": "You are so stupid!",
                "sentiment": "negative",
                "tone": "angry",
                "is_helpful": False
            })
        },
        {
            "name": "📦 Markdown JSON",
            "input": "Here's the response:\n```json\n{\n    \"content\": \"This is wrapped in markdown\",\n    \"sentiment\": \"neutral\",\n    \"tone\": \"professional\",\n    \"is_helpful\": true\n}\n```"
        }
    ]
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n📝 Test {i}: {test['name']}")
        print("-" * 40)
        print(f"Input: {test['input'][:80]}..." if len(test['input']) > 80 else f"Input: {test['input']}")
        
        result = guard.validate(test['input'])
        
        if result.is_approved:
            print(f"✅ Status: {result.status}")
            print(f"📋 Data: {json.dumps(result.data, indent=2)[:200]}...")
        else:
            print(f"❌ Status: {result.status}")
            print(f"📋 Log: {result.log}")
    
    print("\n" + "=" * 60)
    print("Demo complete! Run 'trustguard --help' for more options.")
    return 0


def validate_file(file_path: str, schema: str = "generic") -> int:
    """Validate JSON from a file."""
    path = Path(file_path)
    if not path.exists():
        print(f"❌ Error: File not found: {file_path}")
        return 1
    
    try:
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"❌ Error reading file: {e}")
        return 1
    
    if schema == "generic":
        schema_class = GenericResponse
    else:
        print(f"❌ Error: Unknown schema: {schema}")
        return 1
    
    guard = TrustGuard(schema_class=schema_class)
    result = guard.validate(content)
    
    print(json.dumps(result.to_dict(), indent=2))
    return 0 if result.is_approved else 1


def validate_string(json_str: str, schema: str = "generic") -> int:
    """Validate a JSON string."""
    if schema == "generic":
        schema_class = GenericResponse
    else:
        print(f"❌ Error: Unknown schema: {schema}")
        return 1
    
    guard = TrustGuard(schema_class=schema_class)
    result = guard.validate(json_str)
    
    print(json.dumps(result.to_dict(), indent=2))
    return 0 if result.is_approved else 1


def main() -> int:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="trustguard - Intelligent LLM Validation Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  trustguard                         Run interactive demo
  trustguard --validate '{"content":"test"}'  Validate JSON string
  trustguard --file response.json     Validate JSON from file
  trustguard --version                 Show version
  trustguard --help                    Show this help message
        """
    )
    
    parser.add_argument("--version", action="store_true", help="Show version and exit")
    parser.add_argument("--demo", action="store_true", help="Run interactive demo")
    parser.add_argument("--validate", type=str, metavar="JSON", help="Validate a JSON string")
    parser.add_argument("--file", type=str, metavar="PATH", help="Validate JSON from file")
    parser.add_argument("--schema", type=str, default="generic", choices=["generic"], help="Schema to use")
    
    args = parser.parse_args()
    
    # If no arguments, run the demo
    if len(sys.argv) == 1:
        return demo()
    
    if args.version:
        print(f"trustguard version {__version__}")
        return 0
    
    if args.demo:
        return demo()
    
    if args.validate:
        return validate_string(args.validate, args.schema)
    
    if args.file:
        return validate_file(args.file, args.schema)
    
    parser.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
