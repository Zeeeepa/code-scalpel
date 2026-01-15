"""
Language Semantics - Behavioral Dispatch for Cross-Language Analysis.

This module separates STRUCTURE (IR nodes) from BEHAVIOR (language semantics).
"""

# TODO [COMMUNITY/1] Add bitwise_and(), bitwise_or(), bitwise_xor() operations
# TODO [COMMUNITY/2] Add bitwise_not(), left_shift(), right_shift() operations
# TODO [COMMUNITY/3] Add TypeScriptSemantics class for type-specific behavior
# TODO [COMMUNITY/4] Add JavaSemantics class for Java-specific behavior
# TODO [COMMUNITY/5] Add property_access() for object property retrieval
# TODO [COMMUNITY/6] Add array_index_access() for array element retrieval
# TODO [COMMUNITY/7] Add object_keys() helper to list object properties
# TODO [COMMUNITY/8] Add array_length() helper for sequence length
# TODO [COMMUNITY/9] Add is_truthy() helper for truthiness evaluation
# TODO [COMMUNITY/10] Document semantic method calling convention
# TODO [COMMUNITY/11] Add string_concatenation() with type coercion rules
# TODO [COMMUNITY/12] Add numeric_coercion() for implicit type conversion
# TODO [COMMUNITY/13] Add boolean_coercion() for truthiness rules
# TODO [COMMUNITY/14] Add unary_negation() with language-specific behavior
# TODO [COMMUNITY/15] Add unary_logical_not() with language-specific truthiness
# TODO [COMMUNITY/16] Add unary_bitwise_not() for bitwise inversion
# TODO [COMMUNITY/17] Add modulo_operation() with language-specific sign handling
# TODO [COMMUNITY/18] Add integer_division() with floor vs truncation rules
# TODO [COMMUNITY/19] Add exponentiation() with language-specific behavior
# TODO [COMMUNITY/20] Add matrix_multiply() for Python @ operator
# TODO [COMMUNITY/21] Add string_index_access() for character retrieval
# TODO [COMMUNITY/22] Add slice_operation() for array/string slicing
# TODO [COMMUNITY/23] Add range_creation() for range objects
# TODO [COMMUNITY/24] Add set_operations() (union, intersection, difference)
# TODO [COMMUNITY/25] Add dict_merge_operations() for combining objects
# TODO [PRO/26] Add nullish_coalesce() for ?? operator semantics
# TODO [PRO/27] Add optional_chain() for optional chaining (?.) semantics
# TODO [PRO/28] Add Promise semantics for JavaScript async operations
# TODO [PRO/29] Add async_await() handling for async/await patterns
# TODO [PRO/30] Add prototype_chain() for JavaScript object inheritance
# TODO [PRO/31] Add type_coercion() for implicit type conversions
# TODO [PRO/32] Add loose_equality() for == vs === distinction
# TODO [PRO/33] Add deep_equal() for recursive equality checking
# TODO [PRO/34] Add nan_handling() for IEEE 754 special cases
# TODO [PRO/35] Add error_propagation() for exception semantics
# TODO [PRO/36] Add try_catch_semantics() for exception handling
# TODO [PRO/37] Add finally_block_semantics() guaranteed execution
# TODO [PRO/38] Add throw_statement_semantics() exception throwing
# TODO [PRO/39] Add custom_error_types() for user-defined exceptions
# TODO [PRO/40] Add error_stack_trace_tracking() for debugging
# TODO [PRO/41] Add error_message_interpolation() for error formatting
# TODO [PRO/42] Add walrus_assignment_semantics() for := operator
# TODO [PRO/43] Add scope_isolation_rules() for variable scoping
# TODO [PRO/44] Add closure_capture_rules() for capturing outer scope
# TODO [PRO/45] Add this_binding_rules() for context binding
# TODO [PRO/46] Add super_method_calling() for inheritance
# TODO [PRO/47] Add method_resolution_order() for MRO
# TODO [PRO/48] Add static_vs_instance_methods() distinction
# TODO [PRO/49] Add property_getter_setter_semantics()
# TODO [PRO/50] Add lazy_evaluation_semantics() for deferred execution
# TODO [ENTERPRISE/51] Add distributed semantic evaluation across network
# TODO [ENTERPRISE/52] Add constraint propagation through operations
# TODO [ENTERPRISE/53] Add ML-based semantic inference
# TODO [ENTERPRISE/54] Add polyglot operation composition
# TODO [ENTERPRISE/55] Add semantic caching and memoization
# TODO [ENTERPRISE/56] Add symbolic execution integration
# TODO [ENTERPRISE/57] Add type narrowing guidance for conditionals
# TODO [ENTERPRISE/58] Add generic type parameter handling
# TODO [ENTERPRISE/59] Add variance tracking for type systems
# TODO [ENTERPRISE/60] Add semantic versioning for language evolution
# TODO [ENTERPRISE/61] Add async_stream_semantics() for reactive programming
# TODO [ENTERPRISE/62] Add concurrent_operation_semantics() for parallelism
# TODO [ENTERPRISE/63] Add transaction_semantics() for ACID properties
# TODO [ENTERPRISE/64] Add lock_semantics() for concurrency control
# TODO [ENTERPRISE/65] Add race_condition_detection() for thread safety
# TODO [ENTERPRISE/66] Add deadlock_detection() for synchronization issues
# TODO [ENTERPRISE/67] Add memory_safety_semantics() for pointer operations
# TODO [ENTERPRISE/68] Add bounds_checking() for array access safety
# TODO [ENTERPRISE/69] Add null_pointer_checking() for null safety
# TODO [ENTERPRISE/70] Add overflow_checking() for numeric safety
# TODO [ENTERPRISE/71] Add unicode_semantics() for string handling
# TODO [ENTERPRISE/72] Add regex_matching_semantics() for pattern matching
# TODO [ENTERPRISE/73] Add json_parsing_semantics() for JSON operations
# TODO [ENTERPRISE/74] Add xml_semantics() for XML operations
# TODO [ENTERPRISE/75] Add serialization_deserialization_semantics() for data interchange

from abc import ABC, abstractmethod
from typing import Any

from z3 import And, ArithRef, BoolRef, Concat, ExprRef, Not, Or, SeqRef


class LanguageSemantics(ABC):
    """
    Abstract base class for language-specific operation semantics.

    Subclasses implement the BEHAVIOR of operators for their language.
    The interpreter calls these methods when evaluating IR nodes.

    All methods accept Z3 symbolic values and return Z3 symbolic values.
    This allows symbolic execution across languages.

    [20251220_TODO] Add semantic operation categories:
        - Bitwise operations (and, or, xor, not, shift)
        - Object/array operations (access, set, keys, length)
        - String operations (concat, slice, index, match)
        - Type checking and guards
        - Error handling and exception semantics

    [20251220_TODO] Add constraint tracking:\n        - Track value ranges and type constraints
        - Propagate type information through operations
        - Enable type narrowing in conditionals
        - Support optional chaining constraints
    """

    # [20250105_REFACTOR] Abstract stubs are excluded from coverage; implementations live in concrete semantics classes.

    @property
    @abstractmethod
    def name(self) -> str:
        """Return the language name."""
        pass  # pragma: no cover

    # =========================================================================
    # Binary Arithmetic Operations
    # =========================================================================

    @abstractmethod
    def binary_add(self, left: Any, right: Any) -> Any:
        """
        Implement the + operator.

        Semantic differences:
            Python: str + int -> TypeError
            JavaScript: str + int -> string concatenation
        """
        pass  # pragma: no cover

    @abstractmethod
    def binary_sub(self, left: Any, right: Any) -> Any:
        """Implement the - operator."""
        pass  # pragma: no cover

    @abstractmethod
    def binary_mul(self, left: Any, right: Any) -> Any:
        """
        Implement the * operator.

        Semantic differences:
            Python: "ab" * 3 -> "ababab"
            JavaScript: "ab" * 3 -> NaN
        """
        pass  # pragma: no cover

    @abstractmethod
    def binary_div(self, left: Any, right: Any) -> Any:
        """
        Implement the / operator.

        Semantic differences:
            Python 3: 5 / 2 -> 2.5 (true division)
            JavaScript: 5 / 2 -> 2.5
        """
        pass  # pragma: no cover

    @abstractmethod
    def binary_floor_div(self, left: Any, right: Any) -> Any:
        """
        Implement floor division.

        Python: 5 // 2 -> 2
        JavaScript: Math.floor(5 / 2) -> 2 (no // operator)
        """
        pass  # pragma: no cover

    @abstractmethod
    def binary_mod(self, left: Any, right: Any) -> Any:
        """
        Implement the % operator.

        Semantic differences:
            Python: -7 % 3 -> 2 (result has sign of divisor)
            JavaScript: -7 % 3 -> -1 (result has sign of dividend)
        """
        pass  # pragma: no cover

    @abstractmethod
    def binary_pow(self, left: Any, right: Any) -> Any:
        """Implement the ** operator."""
        pass  # pragma: no cover

    # =========================================================================
    # Comparison Operations
    # =========================================================================

    @abstractmethod
    def compare_eq(self, left: Any, right: Any) -> Any:
        """
        Implement == comparison.

        Semantic differences:
            Python: 1 == "1" -> False
            JavaScript: 1 == "1" -> True (type coercion)
        """
        pass  # pragma: no cover

    @abstractmethod
    def compare_strict_eq(self, left: Any, right: Any) -> Any:
        """
        Implement === comparison (JS only).

        JavaScript: 1 === "1" -> False (no type coercion)
        Python: N/A (always strict)
        """
        pass  # pragma: no cover

    @abstractmethod
    def compare_lt(self, left: Any, right: Any) -> Any:
        """Implement < comparison."""
        pass  # pragma: no cover

    @abstractmethod
    def compare_le(self, left: Any, right: Any) -> Any:
        """Implement <= comparison."""
        pass  # pragma: no cover

    @abstractmethod
    def compare_gt(self, left: Any, right: Any) -> Any:
        """Implement > comparison."""
        pass  # pragma: no cover

    @abstractmethod
    def compare_ge(self, left: Any, right: Any) -> Any:
        """Implement >= comparison."""
        pass  # pragma: no cover

    # =========================================================================
    # Boolean Operations
    # =========================================================================

    @abstractmethod
    def bool_and(self, left: Any, right: Any) -> Any:
        """
        Implement logical AND.

        Both Python and JS short-circuit, but return values differ:
            Python: 0 and "hello" -> 0 (returns first falsy)
            JavaScript: 0 && "hello" -> 0 (same behavior)
        """
        pass  # pragma: no cover

    @abstractmethod
    def bool_or(self, left: Any, right: Any) -> Any:
        """
        Implement logical OR.

        Both Python and JS short-circuit:
            Python: 0 or "hello" -> "hello"
            JavaScript: 0 || "hello" -> "hello"
        """
        pass  # pragma: no cover

    @abstractmethod
    def bool_not(self, operand: Any) -> Any:
        """
        Implement logical NOT.

        Truthiness rules differ:
            Python: not [] -> True (empty list is falsy)
            JavaScript: ![] -> False (empty array is truthy!)
        """
        pass  # pragma: no cover

    # =========================================================================
    # Type Coercion
    # =========================================================================

    @abstractmethod
    def to_boolean(self, value: Any) -> Any:
        """
        Convert value to boolean.

        Truthiness differs significantly:
            Python falsy: None, False, 0, "", [], {}, set()
            JavaScript falsy: null, undefined, false, 0, "", NaN
            JavaScript truthy: [], {} (empty array/object are truthy!)
        """
        pass  # pragma: no cover

    @abstractmethod
    def to_string(self, value: Any) -> Any:
        """Convert value to string."""
        pass  # pragma: no cover

    @abstractmethod
    def to_number(self, value: Any) -> Any:
        """
        Convert value to number.

        JavaScript: Number("42") -> 42, Number("hello") -> NaN
        Python: int("42") -> 42, int("hello") -> ValueError
        """
        pass  # pragma: no cover


class PythonSemantics(LanguageSemantics):
    """
    Python language semantics.

    Key characteristics:
        - Strong typing (no implicit coercion in +)
        - Truthy: non-empty sequences, non-zero numbers
        - Modulo has sign of divisor
    """

    @property
    def name(self) -> str:
        return "python"

    # =========================================================================
    # Binary Arithmetic - Python is strongly typed
    # =========================================================================

    def binary_add(self, left: Any, right: Any) -> Any:
        """
        Python +: No implicit type coercion.

        str + str -> str (concatenation)
        int + int -> int
        str + int -> TypeError
        """
        # For symbolic execution, we check types
        if isinstance(left, SeqRef) and isinstance(right, SeqRef):
            # String concatenation
            return Concat(left, right)
        elif isinstance(left, ArithRef) and isinstance(right, ArithRef):
            # Numeric addition
            return left + right
        elif isinstance(left, SeqRef) or isinstance(right, SeqRef):
            # Mixed string and non-string: Python raises TypeError
            raise TypeError(
                f'can only concatenate str (not "{type(right).__name__}") to str'
            )
        else:
            # Concrete values - use Python's native behavior
            return left + right

    def binary_sub(self, left: Any, right: Any) -> Any:
        """Python -: Numeric subtraction only."""
        if isinstance(left, (ArithRef, int, float)) and isinstance(
            right, (ArithRef, int, float)
        ):
            return left - right
        raise TypeError("unsupported operand type(s) for -")

    def binary_mul(self, left: Any, right: Any) -> Any:
        """
        Python *: Numeric multiplication OR string repetition.

        "ab" * 3 -> "ababab"
        3 * "ab" -> "ababab"
        """
        # String repetition is complex in Z3, skip for now
        if isinstance(left, ArithRef) and isinstance(right, ArithRef):
            return left * right
        return left * right

    def binary_div(self, left: Any, right: Any) -> Any:
        """Python /: True division (always returns float in Python 3)."""
        if isinstance(left, ArithRef) and isinstance(right, ArithRef):
            # Z3 integer division - note: this is floor division
            # For true division we'd need Real sort
            return left / right
        return left / right

    def binary_floor_div(self, left: Any, right: Any) -> Any:
        """Python //: Floor division."""
        if isinstance(left, ArithRef) and isinstance(right, ArithRef):
            return left / right  # Z3 Int division is floor division
        return left // right

    def binary_mod(self, left: Any, right: Any) -> Any:
        """
        Python %: Modulo with sign of divisor.

        -7 % 3 -> 2 (not -1)
        """
        if isinstance(left, ArithRef) and isinstance(right, ArithRef):
            return left % right
        return left % right

    def binary_pow(self, left: Any, right: Any) -> Any:
        """Python **: Exponentiation."""
        # Z3 doesn't have native power, would need unrolling or approximation
        if isinstance(left, (int, float)) and isinstance(right, (int, float)):
            return left**right
        raise NotImplementedError("Symbolic exponentiation not supported")

    # =========================================================================
    # Comparison - Python is always strict
    # =========================================================================

    def compare_eq(self, left: Any, right: Any) -> Any:
        """Python ==: Strict equality (no type coercion)."""
        if isinstance(left, ExprRef) or isinstance(right, ExprRef):
            return left == right
        return left == right

    def compare_strict_eq(self, left: Any, right: Any) -> Any:
        """Python doesn't have ===, delegate to ==."""
        return self.compare_eq(left, right)

    def compare_lt(self, left: Any, right: Any) -> Any:
        """Python <: Less than."""
        return left < right

    def compare_le(self, left: Any, right: Any) -> Any:
        """Python <=: Less than or equal."""
        return left <= right

    def compare_gt(self, left: Any, right: Any) -> Any:
        """Python >: Greater than."""
        return left > right

    def compare_ge(self, left: Any, right: Any) -> Any:
        """Python >=: Greater than or equal."""
        return left >= right

    # =========================================================================
    # Boolean Operations
    # =========================================================================

    def bool_and(self, left: Any, right: Any) -> Any:
        """Python and: Short-circuit, returns operand value."""
        if isinstance(left, BoolRef) and isinstance(right, BoolRef):
            return And(left, right)
        # Concrete: return first falsy or last truthy
        # [20251220_BUGFIX] Cannot check BoolRef with if statement - separate symbolic/concrete paths
        left_is_falsy = not left if not isinstance(left, (BoolRef, ExprRef)) else False
        if left_is_falsy:
            return left
        return right

    def bool_or(self, left: Any, right: Any) -> Any:
        """Python or: Short-circuit, returns operand value."""
        if isinstance(left, BoolRef) and isinstance(right, BoolRef):
            return Or(left, right)
        # Concrete: return first truthy or last falsy
        # [20251220_BUGFIX] Cannot check BoolRef with if statement - separate symbolic/concrete paths
        left_is_truthy = left if not isinstance(left, (BoolRef, ExprRef)) else None
        if left_is_truthy:
            return left
        return right

    def bool_not(self, operand: Any) -> Any:
        """Python not: Logical negation."""
        if isinstance(operand, BoolRef):
            return Not(operand)
        return not operand

    # =========================================================================
    # Type Coercion
    # =========================================================================

    def to_boolean(self, value: Any) -> Any:
        """
        Python truthiness:
            Falsy: None, False, 0, 0.0, "", [], {}, set()
            Everything else is truthy.
        """
        if isinstance(value, BoolRef):
            return value
        return bool(value)

    def to_string(self, value: Any) -> Any:
        """Python str(): Convert to string."""
        if isinstance(value, SeqRef):
            return value
        return str(value)

    def to_number(self, value: Any) -> Any:
        """
        Python int()/float(): Strict conversion.

        Raises ValueError on invalid input.
        """
        if isinstance(value, ArithRef):
            return value
        if isinstance(value, str):
            return int(value)  # May raise ValueError
        return int(value)


class JavaScriptSemantics(LanguageSemantics):
    """
    JavaScript language semantics.

    Key characteristics:
        - Weak typing (implicit coercion everywhere)
        - Truthy: everything except null, undefined, false, 0, "", NaN
        - Empty array [] is TRUTHY (unlike Python!)
        - Modulo has sign of dividend
    """

    @property
    def name(self) -> str:
        return "javascript"

    # =========================================================================
    # Binary Arithmetic - JavaScript coerces types
    # =========================================================================

    def binary_add(self, left: Any, right: Any) -> Any:
        """
        JavaScript +: String wins!

        "5" + 3 -> "53"
        5 + "3" -> "53"
        5 + 3 -> 8
        """
        # Check if either operand is a string
        left_is_string = isinstance(left, (str, SeqRef))
        right_is_string = isinstance(right, (str, SeqRef))

        if left_is_string or right_is_string:
            # String concatenation with coercion
            if isinstance(left, SeqRef) and isinstance(right, SeqRef):
                return Concat(left, right)
            # Concrete: coerce to string and concatenate
            return str(left) + str(right)
        else:
            # Numeric addition
            if isinstance(left, ArithRef) and isinstance(right, ArithRef):
                return left + right
            return left + right

    def binary_sub(self, left: Any, right: Any) -> Any:
        """
        JavaScript -: Coerce to numbers.

        "5" - 3 -> 2
        "hello" - 3 -> NaN
        """
        if isinstance(left, ArithRef) and isinstance(right, ArithRef):
            return left - right
        # Coerce strings to numbers
        try:
            left_num = float(left) if isinstance(left, str) else left
            right_num = float(right) if isinstance(right, str) else right
            return left_num - right_num
        except (ValueError, TypeError):
            return float("nan")

    def binary_mul(self, left: Any, right: Any) -> Any:
        """
        JavaScript *: Coerce to numbers.

        "5" * 3 -> 15 (NOT "555" like you might expect!)
        "ab" * 3 -> NaN
        """
        if isinstance(left, ArithRef) and isinstance(right, ArithRef):
            return left * right
        try:
            left_num = float(left) if isinstance(left, str) else left
            right_num = float(right) if isinstance(right, str) else right
            return left_num * right_num
        except (ValueError, TypeError):
            return float("nan")

    def binary_div(self, left: Any, right: Any) -> Any:
        """JavaScript /: Coerce to numbers."""
        if isinstance(left, ArithRef) and isinstance(right, ArithRef):
            return left / right
        try:
            left_num = float(left) if isinstance(left, str) else left
            right_num = float(right) if isinstance(right, str) else right
            # [20251220_BUGFIX] Cannot use ArithRef in if conditional - check for concrete types
            right_is_zero = (
                right_num == 0 if isinstance(right_num, (int, float)) else False
            )
            if right_is_zero:
                left_is_positive = (
                    left_num >= 0 if isinstance(left_num, (int, float)) else True
                )
                return float("inf") if left_is_positive else float("-inf")
            return left_num / right_num
        except (ValueError, TypeError):
            return float("nan")

    def binary_floor_div(self, left: Any, right: Any) -> Any:
        """JavaScript doesn't have //, use Math.floor(a/b)."""
        result = self.binary_div(left, right)
        if isinstance(result, float) and not (result != result):  # not NaN
            return int(result)
        return result

    def binary_mod(self, left: Any, right: Any) -> Any:
        """
        JavaScript %: Modulo with sign of DIVIDEND (opposite of Python!).

        -7 % 3 -> -1 (not 2)
        """
        if isinstance(left, ArithRef) and isinstance(right, ArithRef):
            # Z3 modulo - need to adjust for JS semantics
            return left % right
        try:
            left_num = float(left) if isinstance(left, str) else left
            right_num = float(right) if isinstance(right, str) else right
            # Python's % has sign of divisor, JS has sign of dividend
            # JS: a % b = a - (b * trunc(a/b))
            import math

            # [20251220_BUGFIX] math.trunc() needs concrete float, not ArithRef
            if isinstance(left_num, (int, float)) and isinstance(
                right_num, (int, float)
            ):
                return left_num - right_num * math.trunc(left_num / right_num)
            # For symbolic values, fall back to modulo operator
            return left_num % right_num
        except (ValueError, TypeError, ZeroDivisionError):
            return float("nan")

    def binary_pow(self, left: Any, right: Any) -> Any:
        """JavaScript **: Exponentiation (ES2016+)."""
        try:
            left_num = float(left) if isinstance(left, str) else left
            right_num = float(right) if isinstance(right, str) else right
            return left_num**right_num
        except (ValueError, TypeError):
            return float("nan")

    # =========================================================================
    # Comparison
    # =========================================================================

    def compare_eq(self, left: Any, right: Any) -> Any:
        """
        JavaScript ==: Loose equality with type coercion.

        1 == "1" -> true
        null == undefined -> true
        0 == false -> true
        """
        if isinstance(left, ExprRef) or isinstance(right, ExprRef):
            return left == right
        # Coercion rules are complex, simplified version:
        if type(left) is type(right):
            return left == right
        # String to number coercion
        try:
            if isinstance(left, str):
                return float(left) == right
            if isinstance(right, str):
                return left == float(right)
        except ValueError:
            pass
        return left == right

    def compare_strict_eq(self, left: Any, right: Any) -> Any:
        """
        JavaScript ===: Strict equality (no type coercion).

        1 === "1" -> false
        1 === 1 -> true
        """
        if isinstance(left, ExprRef) or isinstance(right, ExprRef):
            # In symbolic mode, types should match
            return left == right
        # No coercion: types must match
        if type(left) is not type(right):
            return False
        return left == right

    def compare_lt(self, left: Any, right: Any) -> Any:
        """JavaScript <: With coercion."""
        return left < right

    def compare_le(self, left: Any, right: Any) -> Any:
        """JavaScript <=: With coercion."""
        return left <= right

    def compare_gt(self, left: Any, right: Any) -> Any:
        """JavaScript >: With coercion."""
        return left > right

    def compare_ge(self, left: Any, right: Any) -> Any:
        """JavaScript >=: With coercion."""
        return left >= right

    # =========================================================================
    # Boolean Operations
    # =========================================================================

    def bool_and(self, left: Any, right: Any) -> Any:
        """JavaScript &&: Short-circuit, returns operand value."""
        if isinstance(left, BoolRef) and isinstance(right, BoolRef):
            return And(left, right)
        if not self._is_truthy(left):
            return left
        return right

    def bool_or(self, left: Any, right: Any) -> Any:
        """JavaScript ||: Short-circuit, returns operand value."""
        if isinstance(left, BoolRef) and isinstance(right, BoolRef):
            return Or(left, right)
        if self._is_truthy(left):
            return left
        return right

    def bool_not(self, operand: Any) -> Any:
        """JavaScript !: Logical negation."""
        if isinstance(operand, BoolRef):
            return Not(operand)
        return not self._is_truthy(operand)

    def _is_truthy(self, value: Any) -> bool:
        """
        JavaScript truthiness rules.

        Falsy: null, undefined, false, 0, "", NaN
        Truthy: EVERYTHING ELSE including [] and {}!
        """
        if value is None:  # null/undefined
            return False
        if value is False:
            return False
        if value == 0:
            return False
        if value == "":
            return False
        if isinstance(value, float) and value != value:  # NaN check
            return False
        return True

    # =========================================================================
    # Type Coercion
    # =========================================================================

    def to_boolean(self, value: Any) -> Any:
        """Convert to boolean using JS truthiness rules."""
        if isinstance(value, BoolRef):
            return value
        return self._is_truthy(value)

    def to_string(self, value: Any) -> Any:
        """JavaScript String(): Convert to string."""
        if isinstance(value, SeqRef):
            return value
        if value is None:
            return "null"
        if value is True:
            return "true"
        if value is False:
            return "false"
        return str(value)

    def to_number(self, value: Any) -> Any:
        """
        JavaScript Number(): Convert to number.

        Returns NaN for invalid input (not exception).
        """
        if isinstance(value, ArithRef):
            return value
        if value is None:
            return 0  # Number(null) -> 0
        if value is True:
            return 1
        if value is False:
            return 0
        if isinstance(value, str):
            try:
                return float(value) if "." in value else int(value)
            except ValueError:
                return float("nan")
        return float(value)
