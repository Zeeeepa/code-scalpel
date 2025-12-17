"""
[20251217_FEATURE] Autonomy module - v3.0.0 autonomous code repair features.

This module provides supervised autonomous code repair capabilities with
safety guarantees:

1. Error-to-Diff Engine: Converts error messages to actionable fix hints
   with confidence scoring and human review flagging.

2. Fix Loop Termination: Prevents infinite retry loops with hard limits,
   timeouts, and repeated error detection.

3. Mutation Test Gate: Prevents "hollow fixes" where tests pass because
   functionality was deleted, not because the bug was fixed.

Features:
- Multi-language error parsing (Python, TypeScript, Java)
- Confidence-scored fix generation
- Bounded fix attempts with timeout
- Repeated error detection
- Human escalation on failure
- Full audit trail
- Hollow fix detection via mutation testing
- Mutation score calculation

Usage:
    from code_scalpel.autonomy import (
        ErrorToDiffEngine,
        FixLoop,
        MutationTestGate,
    )
    
    # Parse error and generate fix hints
    engine = ErrorToDiffEngine(project_root="/path/to/project")
    analysis = engine.analyze_error(error_output, "python", source_code)
    
    # Create fix loop for automated repair
    fix_loop = FixLoop(max_attempts=5, max_duration_seconds=300)
    
    # Run fix loop
    result = fix_loop.run(
        initial_error="NameError: name 'x' is not defined",
        source_code=buggy_code,
        language="python",
        sandbox=sandbox_executor,
        error_engine=error_to_diff_engine,
        project_path="/path/to/project"
    )
    
    # Validate fix with mutation testing
    mutation_gate = MutationTestGate(sandbox=sandbox_executor)
    gate_result = mutation_gate.validate_fix(
        original_code=buggy_code,
        fixed_code=fixed_code,
        test_files=["tests/test_feature.py"],
        language="python"
    )
    
    if gate_result.hollow_fix_detected:
        print("ALERT: Hollow fix detected!")

References:
- DEVELOPMENT_ROADMAP.md: v3.0.0 Autonomy specifications
- docs/: Architecture and design documentation
"""

# [20251217_FEATURE] Error-to-Diff Engine (merged from main)
from code_scalpel.autonomy.error_to_diff import (
    ErrorType,
    FixHint as ErrorToFixHint,
    ErrorAnalysis as ErrorToAnalysis,
    ErrorToDiffEngine,
    ParsedError,
)

# [20251217_FEATURE] Fix Loop Termination
from code_scalpel.autonomy.fix_loop import (
    FixLoop,
    FixLoopResult,
    FixAttempt,
)

# [20251217_FEATURE] Mutation Test Gate
from code_scalpel.autonomy.mutation_gate import (
    MutationTestGate,
    MutationGateResult,
    MutationResult,
    Mutation,
    MutationType,
)

# [20251217_FEATURE] Stubs for external implementations
from code_scalpel.autonomy.stubs import (
    ErrorAnalysis,
    FixHint,
    FileChange,
    ExecutionTestResult,
    SandboxResult,
    SandboxExecutor,
    ErrorToDiffEngine as StubErrorToDiffEngine,
)

__all__ = [
    # Error-to-Diff Engine
    "ErrorType",
    "ErrorToDiffEngine",
    "ParsedError",
    "ErrorToFixHint",
    "ErrorToAnalysis",
    # Fix Loop
    "FixLoop",
    "FixLoopResult",
    "FixAttempt",
    # Mutation Gate
    "MutationTestGate",
    "MutationGateResult",
    "MutationResult",
    "Mutation",
    "MutationType",
    # Stubs (for external implementations)
    "ErrorAnalysis",
    "FixHint",
    "FileChange",
    "ExecutionTestResult",
    "SandboxResult",
    "SandboxExecutor",
    "StubErrorToDiffEngine",
]

# [20251217_FEATURE] Version indicator for autonomy module
__version__ = "3.0.0"
