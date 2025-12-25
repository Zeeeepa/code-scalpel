"""
Operator Enums for Unified IR.

These enums normalize operator representations across languages.
The STRUCTURE is normalized here, but SEMANTICS are handled by LanguageSemantics.

TODO ITEMS: operators.py
======================================================================
COMMUNITY TIER - Core Operator Definitions
======================================================================
1. Add NULLISH_COALESCE operator (??) for JavaScript/TypeScript
2. Add OPTIONAL_CHAIN operator (?.) for property access
3. Add EXPONENT_ASSIGN operator (**=) for augmented assignment
4. Add NULLISH_COALESCE_ASSIGN operator (??=) operator
5. Add LOGICAL_AND_ASSIGN operator (&&=) operator
6. Add LOGICAL_OR_ASSIGN operator (||=) operator
7. Add SPREAD operator (...) for unpacking/spreading
8. Add ARROW_FUNCTION operator (=>) for arrow functions
9. Add PIPE operator (|) for functional composition (future)
10. Document operator precedence and associativity rules
11. Add WALRUS_ASSIGN (:=) for assignment expressions
12. Add POWER_OPERATOR (**) for exponentiation
13. Add STRING_CONCAT operator for explicit string concatenation
14. Add REGEX_MATCH operator (=~, !~) for pattern matching
15. Add SAFE_DEREFERENCE operator for null-safe access
16. Add ELVIS operator (?:) for null coalescing alternatives
17. Add RANGE_INCLUSIVE (..) and RANGE_EXCLUSIVE (...) operators
18. Add SPACESHIP operator (<=>) for three-way comparison
19. Add MODULO_ASSIGN (%=) augmented assignment
20. Add BITWISE_AND_ASSIGN (&=) augmented assignment
21. Add BITWISE_OR_ASSIGN (|=) augmented assignment
22. Add BITWISE_XOR_ASSIGN (^=) augmented assignment
23. Add LEFT_SHIFT_ASSIGN (<<=) augmented assignment
24. Add RIGHT_SHIFT_ASSIGN (>>=) augmented assignment
25. Add EXPONENTIATION (**) operator with proper precedence

PRO TIER - Operator Metadata and Analysis
======================================================================
26. Add precedence_level to each operator enum (0-15 scale)
27. Add associativity field (LEFT, RIGHT, NONE) to operators
28. Add is_commutative flag for optimization
29. Add language_availability tracking (Python vs JS only)
30. Add operator aliases across languages mapping
31. Add symbolic representation for formal verification
32. Add operator family classification (arithmetic, comparison, logical)
33. Add bitwise operator complete set (AND, OR, XOR, NOT, SHIFT)
34. Add operator behavior matrix for cross-language analysis
35. Add operator overload tracking for custom implementations
36. Add operator_inverse mapping (e.g., + -> -)
37. Add operator_identity element (e.g., 0 for +, 1 for *)
38. Add operator_short_circuit info (&&, || behavior)
39. Add operator_side_effects tracking (mutation, IO)
40. Add operator_type_requirements (operand types)
41. Add operator_return_type specification
42. Add operator_associativity_chains (left-associative chains)
43. Add operator_precedence_visualization() function
44. Add operator_equivalence_across_languages() mapping
45. Add operator_substitution_rules() for refactoring
46. Add operator_simplification_rules() for optimization
47. Add operator_validation_rules() for semantic checking
48. Add operator_deprecation_tracking() for language evolution
49. Add operator_custom_implementations() for overloading
50. Add operator_performance_hints() for optimization

ENTERPRISE TIER - Advanced Operator Features
======================================================================
51. Add distributed operator evaluation semantics
52. Add operator fusion optimization hints
53. Add hardware-accelerated operator support hints (SIMD)
54. Add operator profiling metadata (hot paths)
55. Add ML-based operator recommendation system
56. Add GPU-accelerated operator support detection
57. Add operator constraint propagation rules
58. Add multi-language operator equivalence mapping
59. Add custom operator registration system
60. Add operator versioning for semantic evolution
61. Add operator_async_equivalents (async versions of sync ops)
62. Add operator_lazy_evaluation hints
63. Add operator_memoization hints
64. Add operator_parallelization hints
65. Add operator_vectorization hints (SIMD)
66. Add operator_quantization hints (for ML)
67. Add operator_fusion_patterns() for compiler optimization
68. Add operator_strength_reduction() for perf improvement
69. Add operator_common_subexpression_elimination()
70. Add operator_dead_code_elimination_rules()
71. Add operator_loop_invariant_motion() hints
72. Add operator_branch_prediction hints
73. Add operator_cache_efficiency hints
74. Add operator_memory_bandwidth hints
75. Add operator_latency_characteristics() for real-time systems

Example:
    Python `ast.Add` -> BinaryOperator.ADD
    JS `+` token -> BinaryOperator.ADD

But the BEHAVIOR of ADD differs:
    Python: "5" + 3 -> TypeError
    JS: "5" + 3 -> "53"

This difference is handled in semantics.py, not here.

[20251220_TODO] Add missing operators:
    - Nullish coalescing: ?? (JavaScript)
    - Optional chaining: ?. (JavaScript/TypeScript)
    - Template literal: ` (backtick) for dynamic strings
    - Logical XOR operator (for completeness)
    - Pipe operator | for functional composition (future)

[20251220_TODO] Add operator metadata:
    - Precedence level for each operator
    - Associativity (left/right/none)
    - Is_commutative flag for optimization
    - Language-specific availability
"""

from enum import Enum


class BinaryOperator(Enum):
    """
    Binary operators normalized across languages.

    Maps:
        Python ast.Add, ast.Sub, etc.
        JavaScript +, -, *, /, etc. tokens
    """

    # Arithmetic
    ADD = "+"
    SUB = "-"
    MUL = "*"
    DIV = "/"
    FLOOR_DIV = "//"  # Python: //, JS: Math.floor(a/b) - semantic difference!
    MOD = "%"
    POW = "**"  # Python: **, JS: **

    # Bitwise
    BIT_AND = "&"
    BIT_OR = "|"
    BIT_XOR = "^"
    LSHIFT = "<<"
    RSHIFT = ">>"

    # Matrix multiplication (Python-only, PEP 465)
    MATMUL = "@"


class CompareOperator(Enum):
    """
    Comparison operators normalized across languages.

    Note: JavaScript has both == (loose) and === (strict).
    Python only has ==. The semantic difference is preserved via source_language.
    """

    # Universal
    EQ = "=="
    NE = "!="
    LT = "<"
    LE = "<="
    GT = ">"
    GE = ">="

    # Python-specific
    IS = "is"
    IS_NOT = "is not"
    IN = "in"
    NOT_IN = "not in"

    # JavaScript-specific (strict equality)
    STRICT_EQ = "==="
    STRICT_NE = "!=="


class UnaryOperator(Enum):
    """
    Unary operators normalized across languages.

    Note: Python `not` vs JS `!` have same semantics but different truthiness rules.
    """

    NEG = "-"  # Negation: -x
    POS = "+"  # Unary plus: +x (rarely used, but valid)
    NOT = "not"  # Logical not: Python `not`, JS `!`
    INVERT = "~"  # Bitwise invert: ~x


class BoolOperator(Enum):
    """
    Boolean/logical operators normalized across languages.

    Note: Python `and`/`or` return operand values (short-circuit with value).
    JS `&&`/`||` also short-circuit but coerce to boolean in some contexts.
    """

    AND = "and"  # Python: and, JS: &&
    OR = "or"  # Python: or, JS: ||


class AugAssignOperator(Enum):
    """
    Augmented assignment operators (+=, -=, etc.).

    These map 1:1 to BinaryOperator but are used in different context.
    """

    ADD = "+="
    SUB = "-="
    MUL = "*="
    DIV = "/="
    FLOOR_DIV = "//="
    MOD = "%="
    POW = "**="
    BIT_AND = "&="
    BIT_OR = "|="
    BIT_XOR = "^="
    LSHIFT = "<<="
    RSHIFT = ">>="
    MATMUL = "@="
