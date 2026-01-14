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
    from .utils import ASTUtils, get_all_names, get_node_type, is_constant
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


# TODO [FEATURE] v1.5.1 - Import resolution for cross-file analysis
try:
    from .import_resolver import (
        CircularImport,
        ImportGraphResult,
        ImportInfo,
        ImportResolver,
        ImportType,
        SymbolDefinition,
    )
except ImportError:
    ImportResolver = None
    ImportInfo = None
    ImportType = None
    SymbolDefinition = None
    CircularImport = None
    ImportGraphResult = None

# TODO [FEATURE] v1.5.1 - Cross-file extraction
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

# TODO [DEPRECATION]: OSV Client moved to code_scalpel.security.dependencies
# For backward compatibility, import from new location
try:
    from code_scalpel.security.dependencies import osv_client
except ImportError:
    osv_client = None

# ============================================================================
# TIER 2: PRO (Commercial - Medium Priority)
# ============================================================================

# TODO [PRO] v3.0.0+ - Advanced analysis modules

# TODO [PRO][REFACTOR]: Extract type inference to dedicated module
# TODO [PRO]: Create type_inference.py with TypeInference, TypeInfo, FunctionTypeInfo
# TODO [PRO]: Support Python 3.9+ type hints (Generic, Union, Optional, Literal)
# TODO [PRO]: Infer return types from return statements
# TODO [PRO]: Infer variable types from assignments
# TODO [PRO]: Resolve forward references and string annotations
# TODO [PRO]: Add 25+ integration tests with real codebases
# from .type_inference import TypeInference, TypeInfo, FunctionTypeInfo
TypeInference = None  # TODO [PRO]: Implement module
TypeInfo = None  # TODO [PRO]: Implement dataclass
FunctionTypeInfo = None  # TODO [PRO]: Implement dataclass

# TODO [PRO][REFACTOR]: Extract control flow analysis to dedicated module
# TODO [PRO]: Create control_flow.py with ControlFlowBuilder, ControlFlowGraph, BasicBlock
# TODO [PRO]: Build CFG from AST
# TODO [PRO]: Detect basic blocks and dominators
# TODO [PRO]: Support branching analysis (if/while/for/try)
# TODO [PRO]: Identify unreachable code
# TODO [PRO]: Support async/await control flow
# TODO [PRO]: Add 30+ tests for CFG construction and analysis
# from .control_flow import ControlFlowBuilder, ControlFlowGraph, BasicBlock
ControlFlowBuilder = None  # TODO [PRO]: Implement module
ControlFlowGraph = None  # TODO [PRO]: Implement dataclass
BasicBlock = None  # TODO [PRO]: Implement dataclass

# TODO [PRO][REFACTOR]: Extract data flow analysis to dedicated module
# TODO [PRO]: Create data_flow.py with DataFlowAnalyzer, DataFlow, Definition, Usage
# TODO [PRO]: Track variable definitions and uses throughout program
# TODO [PRO]: Build def-use chains
# TODO [PRO]: Detect uninitialized variables
# TODO [PRO]: Support interprocedural data flow
# TODO [PRO]: Integration with symbolic execution engine
# TODO [PRO]: Add 35+ tests for def-use analysis
# from .data_flow import DataFlowAnalyzer, DataFlow, Definition, Usage
DataFlowAnalyzer = None  # TODO [PRO]: Implement module
DataFlow = None  # TODO [PRO]: Implement dataclass
Definition = None  # TODO [PRO]: Implement dataclass
Usage = None  # TODO [PRO]: Implement dataclass

# ============================================================================
# TIER 3: ENTERPRISE (Commercial - Lower Priority)
# ============================================================================

# TODO [ENTERPRISE] FEATURE: Code refactoring and smell detection
# TODO [ENTERPRISE]: Fix circular import in ast_refactoring module
# TODO [ENTERPRISE]: Implement God Class and God Function smell detection
# TODO [ENTERPRISE]: Identify duplicate code blocks
# TODO [ENTERPRISE]: Suggest design pattern implementations
# TODO [ENTERPRISE]: Generate refactoring impact analysis
# TODO [ENTERPRISE]: Support custom refactoring rule registration
# TODO [ENTERPRISE]: Add 40+ tests for smell detection accuracy
# TODO [FEATURE]: Refactoring pattern detection and code smell analysis
RefactoringAnalyzer = (
    None  # TODO [ENTERPRISE]: Implement module - fix circular import
)
RefactoringOpportunity = None  # TODO [ENTERPRISE]: Implement dataclass
CodeSmell = None  # TODO [ENTERPRISE]: Implement dataclass


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
