"""
Operator Enums for Unified IR.

These enums normalize operator representations across languages.
The STRUCTURE is normalized here, but SEMANTICS are handled by LanguageSemantics.
"""

# TODO [COMMUNITY] Add NULLISH_COALESCE operator (??) for JavaScript/TypeScript
# TODO [COMMUNITY] Add OPTIONAL_CHAIN operator (?.) for property access
# TODO [COMMUNITY] Add EXPONENT_ASSIGN operator (**=) for augmented assignment
# TODO [COMMUNITY] Add NULLISH_COALESCE_ASSIGN operator (??=)
# TODO [COMMUNITY] Add LOGICAL_AND_ASSIGN operator (&&=)
# TODO [COMMUNITY] Add LOGICAL_OR_ASSIGN operator (||=)
# TODO [COMMUNITY] Add SPREAD operator (...) for unpacking/spreading
# TODO [COMMUNITY] Add ARROW_FUNCTION operator (=>) for arrow functions
# TODO [COMMUNITY] Add PIPE operator (|) for functional composition
# TODO [COMMUNITY] Document operator precedence and associativity rules
# TODO [COMMUNITY] Add WALRUS_ASSIGN (:=) for assignment expressions
# TODO [COMMUNITY] Add STRING_CONCAT operator for explicit string concatenation
# TODO [COMMUNITY] Add REGEX_MATCH operator (=~, !~) for pattern matching
# TODO [COMMUNITY] Add SAFE_DEREFERENCE operator for null-safe access
# TODO [COMMUNITY] Add ELVIS operator (?:) for null coalescing alternatives
# TODO [COMMUNITY] Add RANGE_INCLUSIVE (..) and RANGE_EXCLUSIVE (...) operators
# TODO [COMMUNITY] Add SPACESHIP operator (<=>) for three-way comparison

# TODO [PRO] Add precedence_level to each operator enum (0-15 scale)
# TODO [PRO] Add associativity field (LEFT, RIGHT, NONE) to operators
# TODO [PRO] Add is_commutative flag for optimization
# TODO [PRO] Add language_availability tracking (Python vs JS only)
# TODO [PRO] Add operator aliases across languages mapping
# TODO [PRO] Add symbolic representation for formal verification
# TODO [PRO] Add operator family classification
# TODO [PRO] Add operator behavior matrix for cross-language analysis
# TODO [PRO] Add operator overload tracking
# TODO [PRO] Add operator_inverse mapping
# TODO [PRO] Add operator_identity element
# TODO [PRO] Add operator_short_circuit info
# TODO [PRO] Add operator_side_effects tracking
# TODO [PRO] Add operator_type_requirements
# TODO [PRO] Add operator_return_type specification
# TODO [PRO] Add operator_precedence_visualization() function
# TODO [PRO] Add operator_equivalence_across_languages() mapping
# TODO [PRO] Add operator_substitution_rules() for refactoring
# TODO [PRO] Add operator_simplification_rules() for optimization
# TODO [PRO] Add operator_validation_rules() for semantic checking
# TODO [PRO] Add operator_deprecation_tracking()
# TODO [PRO] Add operator_custom_implementations() for overloading
# TODO [PRO] Add operator_performance_hints() for optimization

# TODO [ENTERPRISE] Add distributed operator evaluation semantics
# TODO [ENTERPRISE] Add operator fusion optimization hints
# TODO [ENTERPRISE] Add hardware-accelerated operator support hints (SIMD)
# TODO [ENTERPRISE] Add operator profiling metadata
# TODO [ENTERPRISE] Add ML-based operator recommendation system
# TODO [ENTERPRISE] Add GPU-accelerated operator support detection
# TODO [ENTERPRISE] Add operator constraint propagation rules
# TODO [ENTERPRISE] Add multi-language operator equivalence mapping
# TODO [ENTERPRISE] Add custom operator registration system
# TODO [ENTERPRISE] Add operator versioning for semantic evolution
# TODO [ENTERPRISE] Add operator_async_equivalents
# TODO [ENTERPRISE] Add operator_lazy_evaluation hints
# TODO [ENTERPRISE] Add operator_memoization hints
# TODO [ENTERPRISE] Add operator_parallelization hints
# TODO [ENTERPRISE] Add operator_vectorization hints (SIMD)
# TODO [ENTERPRISE] Add operator_quantization hints (for ML)
# TODO [ENTERPRISE] Add operator_fusion_patterns() for compiler optimization
# TODO [ENTERPRISE] Add operator_strength_reduction() for perf improvement
# TODO [ENTERPRISE] Add operator_common_subexpression_elimination()
# TODO [ENTERPRISE] Add operator_dead_code_elimination_rules()
# TODO [ENTERPRISE] Add operator_loop_invariant_motion() hints
# TODO [ENTERPRISE] Add operator_branch_prediction hints
# TODO [ENTERPRISE] Add operator_cache_efficiency hints
# TODO [ENTERPRISE] Add operator_memory_bandwidth hints
# TODO [ENTERPRISE] Add operator_latency_characteristics() for real-time systems

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
