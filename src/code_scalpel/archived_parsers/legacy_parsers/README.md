# Parsers Module

**Purpose:** Minimal parser factory and base classes

## Overview

This is a lightweight module providing parser abstractions. **Note:** Most actual parsing logic is in `polyglot/` and `code_parser/` modules.

## Key Components

### base_parser.py (1,218 LOC)
Abstract base class for all parsers:
```python
class BaseParser(ABC):
    @abstractmethod
    def parse(self, code: str) -> AST:
        """Parse code into AST."""
        pass
```

### factory.py (1,554 LOC)
Parser factory for creating language-specific parsers:
```python
class ParserFactory:
    @staticmethod
    def get_parser(language: str) -> BaseParser:
        """Get parser for language."""
        if language == "python":
            return PythonParser()
        elif language == "java":
            return JavaParser()
        # ...
```

### python_parser.py (1,882 LOC)
Minimal Python parser implementation:
- Wraps Python's built-in `ast` module
- Provides consistent interface with other parsers

## Usage

```python
from code_scalpel.parsers import ParserFactory

# Get parser for language
parser = ParserFactory.get_parser("python")
ast = parser.parse("def foo(): return 1")

# Or use directly
from code_scalpel.parsers import PythonParser
parser = PythonParser()
ast = parser.parse(code)
```

## Relationship to Other Modules

- **polyglot/**: Modern multi-language parsing with tree-sitter
- **code_parser/**: Legacy language-specific parsers
- **parsers/**: Lightweight factory and base classes

**Recommendation:** Use `polyglot/` for new code. This module exists for backward compatibility.

## v3.0.5 Status

- Base classes: Stable
- Factory: Stable
- Python parser: Stable
- Other languages: See `polyglot/` and `code_parser/`
