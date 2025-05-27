# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Build and Test Commands
- Installation: `uv sync` (uses UV package manager)
- Build package: `python -m build`
- Install dev mode: `pip install -e .`
- Run all tests: `pytest`
- Run specific test file: `pytest test/test_identity.py`
- Run single test: `pytest test/test_identity.py::test_function_name`
- Manual testing: `python test/test.py`

## Code Style Guidelines
- Indentation: 4 spaces
- Imports: stdlib first, third-party next, grouped by category
- Type hints: Required for parameters and return values
- Naming: PascalCase for classes, snake_case for functions/variables
- Docstrings: Use double quotes, include for all classes and functions
- Error handling: Use specific exceptions with descriptive messages
- String quotes: Double for docstrings, single for regular strings
- Class structure: Match Azure resource organization hierarchy
- OOP: Prefer composition and proper inheritance
- Documentation: Keep docstrings updated alongside code changes