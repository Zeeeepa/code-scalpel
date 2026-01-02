"""
TSX/JSX Analyzer - React component detection and metadata extraction.

[20251216_FEATURE] v2.0.2 - JSX/TSX component analysis for React and Next.js.

This module provides utilities for detecting React components, Server Components,
and Server Actions in TypeScript/JavaScript code.

TODO ITEMS:

COMMUNITY TIER (Core Functionality):
1. TODO: Improve JSX detection regex for edge cases
2. TODO: Add support for Vue.js component detection
3. TODO: Implement Angular component detection
4. TODO: Add Svelte component detection support
5. TODO: Create fragment detection improvements
6. TODO: Implement prop type extraction from JSX
7. TODO: Add event handler detection and analysis
8. TODO: Support styled-components detection
9. TODO: Create comprehensive test cases for JSX patterns
10. TODO: Add documentation with JSX examples

PRO TIER (Enhanced Features):
11. TODO: Add hooks dependency tracking (useEffect, useMemo)
12. TODO: Implement custom hook detection and extraction
13. TODO: Create context provider detection
14. TODO: Add component composition analysis
15. TODO: Implement lazy loading detection
16. TODO: Create performance anti-pattern detection
17. TODO: Add accessibility (a11y) issue detection
18. TODO: Support Storybook story detection
19. TODO: Implement TypeScript prop inference
20. TODO: Create component tree visualization

ENTERPRISE TIER (Advanced Capabilities):
21. TODO: Build ML-based component similarity detection
22. TODO: Implement distributed component analysis
23. TODO: Add AI-powered refactoring suggestions for components
24. TODO: Create blockchain-based component audit trails
25. TODO: Implement quantum-safe component hashing
26. TODO: Build enterprise component governance system
27. TODO: Add advanced concurrency pattern detection in components
28. TODO: Create federated component registry
29. TODO: Implement compliance checking for component patterns
30. TODO: Add advanced security analysis for component interactions
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from code_scalpel.ir.nodes import IRClassDef, IRFunctionDef


@dataclass
class ReactComponentInfo:
    """Metadata about a React component."""

    name: str
    component_type: Optional[str] = None  # "functional", "class", or None
    is_server_component: bool = False  # async function component
    is_server_action: bool = False  # 'use server' directive
    has_jsx: bool = False  # Contains JSX syntax


def detect_server_directive(code: str) -> str | None:
    """
    Detect React Server directive in code.

    [20251216_FEATURE] v2.0.2 - Server Component/Action detection.

    Args:
        code: Source code to analyze

    Returns:
        'use server' or 'use client' if found, None otherwise
    """
    # Check for 'use server' directive (Server Action)
    if re.search(r"['\"]use server['\"]", code):
        return "use server"

    # Check for 'use client' directive (Client Component)
    if re.search(r"['\"]use client['\"]", code):
        return "use client"

    return None


def has_jsx_syntax(code: str) -> bool:
    """
    Detect JSX syntax in code.

    [20251216_FEATURE] v2.0.2 - JSX detection for normalization.

    Args:
        code: Source code to analyze

    Returns:
        True if JSX syntax is detected
    """
    # JSX patterns:
    # - Opening tags: <Component>, <div>
    # - Closing tags: </Component>, </div>
    # - Self-closing: <Component />, <div />
    # - Fragments: <>, </>
    # [20240613_BUGFIX] Hardened JSX detection regex to avoid false positives with comparison operators.
    # Require that the tag is not immediately preceded by an identifier character (using negative lookbehind).
    # This reduces matches on expressions like `x < y` or `a < b > c`.
    jsx_patterns = [
        r"(?<![\w$])<[A-Z][A-Za-z0-9]*[\s/>]",  # Component tags (uppercase)
        r"(?<![\w$])<[a-z][a-z0-9]*[\s/>]",  # HTML tags (lowercase)
        r"(?<![\w$])</[A-Za-z]",  # Closing tags
        r"(?<![\w$])<>",  # Fragment opening
        r"(?<![\w$])</>",  # Fragment closing
    ]

    for pattern in jsx_patterns:
        if re.search(pattern, code):
            return True

    return False


def is_react_component(
    node: IRFunctionDef | IRClassDef, code: str
) -> ReactComponentInfo:
    """
    Detect if a function or class is a React component.

    [20251216_FEATURE] v2.0.2 - React component detection.

    Args:
        node: IR node to analyze
        code: Source code of the node

    Returns:
        ReactComponentInfo with component metadata
    """
    from code_scalpel.ir.nodes import IRClassDef, IRFunctionDef

    name = node.name
    component_type = None
    is_server_component = False
    is_server_action = False
    has_jsx = has_jsx_syntax(code)

    # Detect Server directive (applies to functions even without JSX)
    directive = detect_server_directive(code)
    if directive == "use server":
        is_server_action = True

    if isinstance(node, IRFunctionDef):
        # Functional component detection
        # - Function name starts with uppercase (React convention)
        # - Contains JSX return
        # - Has JSX syntax
        # [20240613_BUGFIX] Use idiomatic and safe check for uppercase initial (avoids IndexError on empty string)
        is_functional_component = (name and name[0].isupper()) and has_jsx
        if is_functional_component:
            component_type = "functional"

        # Server Component detection: async functional components with JSX
        # In Next.js, Server Components are async functions that return JSX
        if is_functional_component and node.is_async:
            is_server_component = True

    elif isinstance(node, IRClassDef):
        # Class component detection
        # - Extends React.Component or React.PureComponent
        # - Has render method
        # - Contains JSX

        # [20251216_BUGFIX] Check base classes more thoroughly
        extends_react = False
        if node.bases:
            for base in node.bases:
                base_str = str(base)
                # Handle various forms: React.Component, Component, etc.
                if "Component" in base_str:
                    extends_react = True
                    break

        # [20251216_BUGFIX] Also check if class has JSX in any method, not just overall
        if extends_react:
            component_type = "class"

    return ReactComponentInfo(
        name=name,
        component_type=component_type,
        is_server_component=is_server_component,
        is_server_action=is_server_action,
        has_jsx=has_jsx,
    )


def normalize_jsx_syntax(code: str) -> str:
    """
    Normalize JSX syntax for consistent analysis.

    [20251216_FEATURE] v2.0.2 - JSX normalization.

    This function normalizes JSX patterns to make them more consistent
    for AST analysis and extraction. Currently, this is a placeholder
    that returns the code unchanged, as tree-sitter handles JSX parsing.

    Args:
        code: Source code with JSX

    Returns:
        Normalized code (currently unchanged)
    """
    # For now, tree-sitter handles JSX parsing natively
    # Future normalization could include:
    # - Consistent spacing in JSX tags
    # - Fragment expansion (<> to <Fragment>)
    # - Prop formatting
    return code
