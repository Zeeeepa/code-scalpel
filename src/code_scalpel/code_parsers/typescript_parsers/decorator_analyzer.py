"""
TypeScript Decorator Analyzer.

[20251216_FEATURE] Extract and analyze TypeScript decorators for security analysis.

This module provides tools to extract decorator information from TypeScript code
and identify security-sensitive decorators (e.g., HTTP endpoints, database operations).

TODO ITEMS:

COMMUNITY TIER (Core Functionality):
1. TODO: Improve decorator extraction accuracy for complex patterns
2. TODO: Add support for chained decorators
3. TODO: Implement decorator argument parsing
4. TODO: Create parameter decorator detection
5. TODO: Add accessor decorator support
6. TODO: Implement error handling for malformed decorators
7. TODO: Create comprehensive decorator pattern library
8. TODO: Add caching for decorator analysis results
9. TODO: Document decorator security patterns
10. TODO: Create test suite for all decorator types

PRO TIER (Enhanced Features):
11. TODO: Add NestJS-specific decorator support
12. TODO: Implement TypeORM decorator analysis
13. TODO: Add Angular decorator pattern detection
14. TODO: Create custom decorator plugin system
15. TODO: Implement decorator metadata extraction
16. TODO: Add reflection support for runtime decorators
17. TODO: Create decorator composition analysis
18. TODO: Implement mixin decorator detection
19. TODO: Add performance decorator detection
20. TODO: Create security decorator validation

ENTERPRISE TIER (Advanced Capabilities):
21. TODO: Build ML-based decorator security risk detection
22. TODO: Implement distributed decorator analysis
23. TODO: Add AI-powered decorator refactoring suggestions
24. TODO: Create blockchain-based decorator audit trails
25. TODO: Implement quantum-safe decorator hashing
26. TODO: Build enterprise decorator governance system
27. TODO: Add compliance checking for decorator patterns
28. TODO: Implement federated decorator registry
29. TODO: Create advanced security threat modeling for decorators
30. TODO: Add quantum-safe reflection support
"""

from __future__ import annotations

import re
from typing import Any

from .parser import Decorator, TSNode


# [20251216_FEATURE] Security-sensitive decorator patterns
SECURITY_SINK_DECORATORS = {
    # HTTP endpoint decorators (NestJS, Angular, etc.)
    "@Post",
    "@Put",
    "@Delete",
    "@Patch",
    "@Get",
    # Database operation decorators
    "@Query",
    "@Mutation",
    "@Resolver",
    # Transaction decorators
    "@Transactional",
    "@Transaction",
    # Authentication/Authorization
    "@Public",
    "@AllowAnonymous",
    # File upload
    "@UseInterceptors",
    "@FileInterceptor",
    "@FilesInterceptor",
}


class DecoratorAnalyzer:
    """
    [20251216_FEATURE] Analyzer for TypeScript decorators.

    Extracts decorator information and identifies security-sensitive patterns.

    Example:
        >>> analyzer = DecoratorAnalyzer()
        >>> code = '''
        ... @Controller('users')
        ... export class UserController {
        ...   @Post()
        ...   @UseGuards(AuthGuard)
        ...   async createUser(@Body() data: CreateUserDto) {}
        ... }
        ... '''
        >>> result = analyzer.extract_decorators_from_code(code)
        >>> print(len(result['classes']))
        1
        >>> print(result['classes'][0]['decorators'][0].name)
        Controller
    """

    def __init__(self):
        """Initialize the decorator analyzer."""
        # Regex pattern to match decorators
        # Matches: @DecoratorName or @DecoratorName(args)
        self.decorator_pattern = re.compile(r"@(\w+(?:\.\w+)*)\s*(?:\(([^)]*)\))?")

    def extract_decorators(self, node: TSNode) -> list[Decorator]:
        """
        Extract decorators from a TSNode.

        Args:
            node: TypeScript AST node

        Returns:
            List of Decorator objects

        [20251216_FEATURE] Extract decorator names, arguments, and metadata
        """
        return node.decorators if hasattr(node, "decorators") else []

    def extract_decorators_from_code(self, code: str) -> dict[str, Any]:
        """
        Extract decorators from TypeScript source code using regex.

        This is a fallback method when full AST parsing is not available.

        Args:
            code: TypeScript source code

        Returns:
            Dictionary with extracted decorators organized by target type

        [20251216_FEATURE] Regex-based decorator extraction for fallback parsing
        """
        # First pass: extract parameter decorators from the entire code
        # This handles multi-line signatures better
        param_decorators = re.findall(r"@(\w+)\s*\(([^)]*)\)\s+(\w+)\s*:", code)
        result: dict[str, Any] = {
            "classes": [],
            "methods": [],
            "parameters": [],
        }

        for param_match in param_decorators:
            decorator_name = param_match[0]
            args_str = param_match[1]
            param_name = param_match[2]

            arguments = []
            if args_str:
                arguments = [arg.strip() for arg in args_str.split(",")]

            # Find line number
            param_pattern = (
                f"@{decorator_name}\\s*\\({re.escape(args_str)}\\)\\s+{param_name}\\s*:"
            )
            for line_num, line in enumerate(code.split("\n"), 1):
                if re.search(param_pattern, line):
                    result["parameters"].append(
                        {
                            "parameter_name": param_name,
                            "decorator": Decorator(
                                name=decorator_name,
                                arguments=arguments,
                                is_factory=True,
                                line=line_num,
                                metadata={"raw_args": args_str},
                            ),
                            "line": line_num,
                        }
                    )
                    break

        # Second pass: extract class and method decorators
        lines = code.split("\n")
        current_decorators: list[Decorator] = []

        for line_num, line in enumerate(lines, 1):
            stripped = line.strip()

            # Check for decorator
            decorator_match = self.decorator_pattern.match(stripped)
            if decorator_match:
                name = decorator_match.group(1)
                args_str = decorator_match.group(2)
                arguments = []

                if args_str:
                    # Parse arguments (simple approach - split by comma)
                    arguments = [arg.strip() for arg in args_str.split(",")]

                decorator = Decorator(
                    name=name,
                    arguments=arguments,
                    is_factory=args_str is not None,
                    line=line_num,
                    metadata={"raw_args": args_str},
                )
                current_decorators.append(decorator)
                continue

            # Check for class declaration
            if stripped.startswith("class ") or " class " in stripped:
                class_match = re.search(r"class\s+(\w+)", stripped)
                if class_match and current_decorators:
                    result["classes"].append(
                        {
                            "name": class_match.group(1),
                            "decorators": current_decorators.copy(),
                            "line": line_num,
                        }
                    )
                    current_decorators = []
                continue

            # Check for method declaration
            method_match = re.match(
                r"(?:async\s+)?(\w+)\s*\([^)]*\)\s*(?::\s*[^{]+)?", stripped
            )
            if method_match and current_decorators:
                result["methods"].append(
                    {
                        "name": method_match.group(1),
                        "decorators": current_decorators.copy(),
                        "line": line_num,
                    }
                )
                current_decorators = []
                continue

            # Reset decorators if we hit a non-decorator line
            # (unless it's a blank line or comment)
            if (
                stripped
                and not stripped.startswith("@")
                and not stripped.startswith("//")
            ):
                if not any(
                    keyword in stripped
                    for keyword in ["class", "function", "async", "constructor"]
                ):
                    # Keep decorators for next declaration
                    pass

        return result

    def is_security_sink(self, decorators: list[Decorator]) -> bool:
        """
        Check if decorators indicate security-sensitive operations.

        Args:
            decorators: List of decorators to check

        Returns:
            True if any decorator is security-sensitive

        [20251216_FEATURE] Identify security-sensitive decorators
        """
        for decorator in decorators:
            # Check exact matches
            decorator_name = f"@{decorator.name}"
            if decorator_name in SECURITY_SINK_DECORATORS:
                return True

            # Check partial matches (e.g., @Post, @PostMapping)
            for sink in SECURITY_SINK_DECORATORS:
                if decorator_name.startswith(sink):
                    return True

        return False

    def get_security_metadata(self, decorators: list[Decorator]) -> dict[str, Any]:
        """
        Extract security-relevant metadata from decorators.

        Args:
            decorators: List of decorators

        Returns:
            Dictionary with security metadata

        [20251216_FEATURE] Extract security metadata from decorators
        """
        metadata: dict[str, Any] = {
            "is_endpoint": False,
            "http_methods": [],
            "requires_auth": False,
            "routes": [],
        }

        for decorator in decorators:
            name = decorator.name

            # HTTP method decorators
            if name in ["Get", "Post", "Put", "Delete", "Patch"]:
                metadata["is_endpoint"] = True
                metadata["http_methods"].append(name.upper())

                # Extract route from arguments
                if decorator.arguments:
                    route = decorator.arguments[0].strip("'\"")
                    metadata["routes"].append(route)

            # Controller decorator
            if name == "Controller":
                metadata["is_endpoint"] = True
                if decorator.arguments:
                    base_route = decorator.arguments[0].strip("'\"")
                    metadata["routes"].append(base_route)

            # Authentication decorators
            if name in ["UseGuards", "Authorize", "Authenticated"]:
                metadata["requires_auth"] = True

            # Public/anonymous access
            if name in ["Public", "AllowAnonymous", "SkipAuth"]:
                metadata["requires_auth"] = False

        return metadata


# [20251216_FEATURE] Convenience function for quick decorator extraction
def extract_decorators_from_code(code: str) -> dict[str, Any]:
    """
    Extract decorators from TypeScript code.

    Args:
        code: TypeScript source code

    Returns:
        Dictionary with extracted decorators

    Example:
        >>> result = extract_decorators_from_code('''
        ... @Controller('users')
        ... class UserController {}
        ... ''')
        >>> print(result['classes'][0]['name'])
        UserController
    """
    analyzer = DecoratorAnalyzer()
    return analyzer.extract_decorators_from_code(code)
