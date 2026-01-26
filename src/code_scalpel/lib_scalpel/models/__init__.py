"""Data models for Oracle constraint specifications.

[20260126_FEATURE] Pydantic schemas for constraint specs and rules.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Literal
from pydantic import BaseModel, Field

# =============================================================================
# SYMBOL TABLE MODELS
# =============================================================================


class FunctionSignature(BaseModel):
    """Extracted function signature."""

    name: str
    signature: str
    params: List[Dict[str, str]] = Field(default_factory=list)
    returns: Optional[str] = None
    decorators: List[str] = Field(default_factory=list)
    line: int
    docstring: Optional[str] = None


class ClassSignature(BaseModel):
    """Extracted class signature."""

    name: str
    bases: List[str] = Field(default_factory=list)
    methods: List[FunctionSignature] = Field(default_factory=list)
    properties: List[str] = Field(default_factory=list)
    line: int
    docstring: Optional[str] = None


class ImportStatement(BaseModel):
    """Extracted import statement."""

    module: str
    symbols: List[str] = Field(default_factory=list)
    alias: Optional[str] = None
    line: int


class SymbolTable(BaseModel):
    """Extracted symbol table from a file."""

    file_path: str
    language: str  # "python", "typescript", "javascript", "java"
    functions: List[FunctionSignature] = Field(default_factory=list)
    classes: List[ClassSignature] = Field(default_factory=list)
    imports: List[ImportStatement] = Field(default_factory=list)
    top_level_variables: List[Dict[str, Any]] = Field(default_factory=list)


# =============================================================================
# GRAPH CONSTRAINT MODELS
# =============================================================================


class CallEdge(BaseModel):
    """An edge in the call/dependency graph."""

    caller: str
    callee: str
    line: Optional[int] = None
    inference_source: str = "static"


class GraphConstraints(BaseModel):
    """Graph-based constraints for a file."""

    file_path: str
    callers: List[str] = Field(default_factory=list)
    callees: List[str] = Field(default_factory=list)
    call_edges: List[CallEdge] = Field(default_factory=list)
    circular_dependencies: List[str] = Field(default_factory=list)
    depth: Optional[int] = None


class TopologyRule(BaseModel):
    """An architectural topology rule."""

    name: str
    description: str
    from_layer: str  # e.g., "src/views"
    to_layer: str  # e.g., "src/database"
    action: Literal["DENY", "WARN", "ALLOW"] = "DENY"
    severity: Literal["CRITICAL", "HIGH", "MEDIUM", "LOW"] = "HIGH"


class TopologyViolation(BaseModel):
    """A violation of an architectural rule."""

    rule: TopologyRule
    source_file: str
    target_file: str
    violation_type: str  # "import", "instantiate", "call"
    line: Optional[int] = None
    message: str


# =============================================================================
# CONSTRAINT SPEC MODELS
# =============================================================================


class CodeContext(BaseModel):
    """Relevant code context for the constraint spec."""

    file_path: str
    start_line: int
    end_line: int
    code: str
    language: str


class ConstraintSpec(BaseModel):
    """Complete constraint specification for code generation.

    This is what gets returned to the LLM for constrained code generation.
    """

    file_path: str
    instruction: str
    symbol_table: SymbolTable
    graph_constraints: GraphConstraints
    topology_rules: List[TopologyRule] = Field(default_factory=list)
    topology_violations: List[TopologyViolation] = Field(default_factory=list)
    code_context: Optional[CodeContext] = None
    implementation_notes: List[str] = Field(default_factory=list)
    tier: str = "community"  # "community", "pro", "enterprise"
    generated_at: str  # ISO 8601 timestamp
    spec_version: str = "1.0"

    class Config:
        """Pydantic config."""

        json_schema_extra = {
            "example": {
                "file_path": "src/auth.py",
                "instruction": "Add JWT validation",
                "symbol_table": {},
                "graph_constraints": {},
                "tier": "pro",
            }
        }


# =============================================================================
# MARKDOWN SPEC MODELS
# =============================================================================


@dataclass
class MarkdownSpec:
    """A constraint spec in Markdown format for LLM consumption."""

    file_path: str
    instruction: str
    markdown: str
    tier: str
    generated_at: str
    spec_version: str = "1.0"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "file_path": self.file_path,
            "instruction": self.instruction,
            "markdown": self.markdown,
            "tier": self.tier,
            "generated_at": self.generated_at,
            "spec_version": self.spec_version,
        }
