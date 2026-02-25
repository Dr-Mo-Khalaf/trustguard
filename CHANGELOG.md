# Changelog

All notable changes to trustguard will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - 2024-02-25

### Added
- 🎯 **Pluggable Judge System** - Use any AI model as a safety validator
- 🤖 **OpenAIJudge** - GPT-4/GPT-3.5 integration
- 🦙 **OllamaJudge** - Local model support (Llama, Phi, Mistral)
- 🎨 **AnthropicJudge** - Claude model integration
- 🔌 **CallableJudge** - Universal adapter for any function/model
- 🔀 **EnsembleJudge** - Combine multiple judges for maximum accuracy
- 📊 **Batch Validation** - Validate multiple responses at once
- 🔄 **Async Support** - Native async judge methods
- 📈 **Statistics Tracking** - Monitor validation metrics
- 🖥️ **Enhanced CLI** - Better command-line interface

### Changed
- ⚡ **Performance Improvements** - Faster JSON extraction
- 📝 **Better Error Messages** - More descriptive validation logs
- 🎨 **Code Organization** - Cleaner module structure
- 📚 **Documentation** - Comprehensive guides and examples

### Fixed
- 🐛 **JSON Extraction** - Better handling of markdown code blocks
- 🔧 **Schema Validation** - Stricter field validation
- 🚨 **Error Handling** - Graceful judge failures
- ⚙️ **Configuration** - More flexible config options

## [0.1.0] - 2024-01-15

### Added
- 🚀 **Initial Release** - Core validation engine
- 📋 **Schema Validation** - Pydantic-based JSON validation
- 🛡️ **Built-in Rules** - PII detection, blocklist, toxicity checks
- 🔧 **Custom Rules** - Easy to add your own validation logic
- 📦 **Generic Schema** - Ready-to-use response schema
- 🖥️ **Basic CLI** - Command-line interface for validation
- 📚 **Documentation** - Quick start guide and API reference

### Features
- **Fast** - Microsecond rule execution
- **Lightweight** - Minimal dependencies
- **Extensible** - Add custom rules easily
- **Type Safe** - Full type hints support
