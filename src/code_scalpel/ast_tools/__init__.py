# Core imports
from .analyzer import ASTAnalyzer, ClassMetrics, FunctionMetrics
from .builder import ASTBuilder

# These imports might fail due to incomplete implementations, handle gracefully
try:
    from .transformer import ASTTransformer
except ImportError:
    ASTTransformer = None

try:
    from .visualizer import ASTVisualizer
except ImportError:
    ASTVisualizer = None

try:
    from .validator import ASTValidator
except ImportError:
    ASTValidator = None

try:
    from .utils import ASTUtils, is_constant, get_node_type, get_all_names
except ImportError:
    ASTUtils = None
    is_constant = None
    get_node_type = None
    get_all_names = None


# Create convenience functions using the default ASTBuilder instance
_default_builder = ASTBuilder()


def build_ast(code: str, preprocess: bool = True, validate: bool = True):
    """Build an AST from Python code."""
    return _default_builder.build_ast(code, preprocess, validate)


def build_ast_from_file(filepath: str, preprocess: bool = True, validate: bool = True):
    """Build an AST from a Python source file."""
    return _default_builder.build_ast_from_file(filepath, preprocess, validate)


# Create convenience function for visualization
def visualize_ast(tree, output_file="ast_visualization", format="png", view=True):
    """Visualize an AST using graphviz."""
    if ASTVisualizer is not None:
        visualizer = ASTVisualizer()
        return visualizer.visualize(tree, output_file, format, view)
    raise ImportError("ASTVisualizer not available")


# [20251213_FEATURE] v1.5.1 - Import resolution for cross-file analysis
try:
    from .import_resolver import (
        ImportResolver,
        ImportInfo,
        ImportType,
        SymbolDefinition,
        CircularImport,
        ImportGraphResult,
    )
except ImportError:
    ImportResolver = None
    ImportInfo = None
    ImportType = None
    SymbolDefinition = None
    CircularImport = None
    ImportGraphResult = None

# [20251213_FEATURE] v1.5.1 - Cross-file extraction
try:
    from .cross_file_extractor import (
        CrossFileExtractor,
        ExtractedSymbol,
        ExtractionResult,
    )
except ImportError:
    CrossFileExtractor = None
    ExtractedSymbol = None
    ExtractionResult = None

# [20251225_DEPRECATE] OSV Client moved to code_scalpel.security.dependencies
# For backward compatibility, import from new location
try:
    from code_scalpel.security.dependencies import osv_client
except ImportError:
    osv_client = None

# ============================================================================
# TIER 2: PRO (Commercial - Medium Priority)
# ============================================================================

# [20251221_FEATURE] v3.0.0+ - Advanced analysis modules
# [20251224_TIER2_TODO] REFACTOR: Extract type inference to dedicated module
#   Purpose: Enable lazy loading and improve performance
#   Steps:
#     1. Create type_inference.py with TypeInference, TypeInfo, FunctionTypeInfo
#     2. Support Python 3.9+ type hints (Generic, Union, Optional, Literal)
#     3. Infer return types from return statements
#     4. Infer variable types from assignments
#     5. Resolve forward references and string annotations
#     6. Add 25+ integration tests with real codebases
# from .type_inference import TypeInference, TypeInfo, FunctionTypeInfo
TypeInference = None  # [20251224_TIER2_TODO] Implement module
TypeInfo = None  # [20251224_TIER2_TODO] Implement dataclass
FunctionTypeInfo = None  # [20251224_TIER2_TODO] Implement dataclass

# [20251224_TIER2_TODO] REFACTOR: Extract control flow analysis to dedicated module
#   Purpose: Enable program flow analysis for security and optimization
#   Steps:
#     1. Create control_flow.py with ControlFlowBuilder, ControlFlowGraph, BasicBlock
#     2. Build CFG from AST
#     3. Detect basic blocks and dominators
#     4. Support branching analysis (if/while/for/try)
#     5. Identify unreachable code
#     6. Support async/await control flow
#     7. Add 30+ tests for CFG construction and analysis
# from .control_flow import ControlFlowBuilder, ControlFlowGraph, BasicBlock
ControlFlowBuilder = None  # [20251224_TIER2_TODO] Implement module
ControlFlowGraph = None  # [20251224_TIER2_TODO] Implement dataclass
BasicBlock = None  # [20251224_TIER2_TODO] Implement dataclass

# [20251224_TIER2_TODO] REFACTOR: Extract data flow analysis to dedicated module
#   Purpose: Track variable definitions, uses, and data dependencies
#   Steps:
#     1. Create data_flow.py with DataFlowAnalyzer, DataFlow, Definition, Usage
#     2. Track variable definitions and uses throughout program
#     3. Build def-use chains
#     4. Detect uninitialized variables
#     5. Support interprocedural data flow
#     6. Integration with symbolic execution engine
#     7. Add 35+ tests for def-use analysis
# from .data_flow import DataFlowAnalyzer, DataFlow, Definition, Usage
DataFlowAnalyzer = None  # [20251224_TIER2_TODO] Implement module
DataFlow = None  # [20251224_TIER2_TODO] Implement dataclass
Definition = None  # [20251224_TIER2_TODO] Implement dataclass
Usage = None  # [20251224_TIER2_TODO] Implement dataclass

# ============================================================================
# TIER 3: ENTERPRISE (Commercial - Lower Priority)
# ============================================================================

# [20251224_TIER3_TODO] FEATURE: Code refactoring and smell detection
#   Purpose: Identify refactoring opportunities and code quality issues
#   Steps:
#     1. Fix circular import in ast_refactoring module
#     2. Implement God Class and God Function smell detection
#     3. Identify duplicate code blocks
#     4. Suggest design pattern implementations
#     5. Generate refactoring impact analysis
#     6. Support custom refactoring rule registration
#     7. Add 40+ tests for smell detection accuracy
# [20251221_FEATURE] Refactoring pattern detection and code smell analysis
RefactoringAnalyzer = (
    None  # [20251224_TIER3_TODO] Implement module - fix circular import
)
RefactoringOpportunity = None  # [20251224_TIER3_TODO] Implement dataclass
CodeSmell = None  # [20251224_TIER3_TODO] Implement dataclass


__all__ = [
    "ASTAnalyzer",
    "FunctionMetrics",
    "ClassMetrics",
    "ASTBuilder",
    "ASTTransformer",
    "ASTVisualizer",
    "ASTValidator",
    "ASTUtils",
    "is_constant",
    "get_node_type",
    "get_all_names",
    "build_ast",
    "build_ast_from_file",
    "visualize_ast",
    # v1.5.1 - Import resolution
    "ImportResolver",
    "ImportInfo",
    "ImportType",
    "SymbolDefinition",
    "CircularImport",
    "ImportGraphResult",
    # v1.5.1 - Cross-file extraction
    "CrossFileExtractor",
    "ExtractedSymbol",
    "ExtractionResult",
    # v1.5.3 - OSV Client
    "osv_client",
    # v3.0.0+ - Advanced analysis
    "TypeInference",
    "TypeInfo",
    "FunctionTypeInfo",
    "ControlFlowBuilder",
    "ControlFlowGraph",
    "BasicBlock",
    "DataFlowAnalyzer",
    "DataFlow",
    "Definition",
    "Usage",
    "RefactoringAnalyzer",
    "RefactoringOpportunity",
    "CodeSmell",
]
