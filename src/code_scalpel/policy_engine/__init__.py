"""
Policy Engine - Enterprise Governance for AI Agents.

[20251216_FEATURE] v2.5.0 Guardian - Policy-as-Code enforcement using OPA/Rego

This module provides declarative policy enforcement using Open Policy Agent's
Rego language for enterprise governance. It enables organizations to define
rules that agents must follow when modifying code.

Key Features:
- Declarative policy definitions in YAML
- Rego-based policy evaluation via OPA CLI
- Semantic code analysis (SQL injection, etc.)
- Fail CLOSED security model
- Human override with audit trail

Example:
    from code_scalpel.policy_engine import PolicyEngine, Operation
    
    engine = PolicyEngine(".scalpel/policy.yaml")
    operation = Operation(
        type="code_edit",
        code="cursor.execute('SELECT * FROM users WHERE id=' + user_id)",
        language="python",
        file_path="app.py"
    )
    
    decision = engine.evaluate(operation)
    if not decision.allowed:
        print(f"Policy violation: {decision.reason}")
"""

from .policy_engine import (
    PolicyEngine,
    Policy,
    PolicyDecision,
    PolicyViolation,
    Operation,
    OverrideDecision,
    PolicyError,
)

from .semantic_analyzer import SemanticAnalyzer

__all__ = [
    "PolicyEngine",
    "Policy",
    "PolicyDecision",
    "PolicyViolation",
    "Operation",
    "OverrideDecision",
    "PolicyError",
    "SemanticAnalyzer",
]
