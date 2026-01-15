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
- Tamper-resistant policy enforcement
- HMAC-signed audit logging
- TOTP-based human override system
- Policy file integrity verification

Example:
    from code_scalpel.policy_engine import PolicyEngine, Operation

    engine = PolicyEngine(".code-scalpel/policy.yaml")
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

# TODO [COMMUNITY]: Implement basic YAML policy file loading and parsing
# TODO [COMMUNITY]: Create OPA/Rego policy evaluation engine
# TODO [COMMUNITY]: Implement Operation and PolicyDecision data models
# TODO [COMMUNITY]: Add policy validation on load (syntax, required fields)
# TODO [COMMUNITY]: Implement fail-closed security model for policy errors
# TODO [COMMUNITY]: Create basic audit logging framework
# TODO [COMMUNITY]: Add semantic analysis for SQL injection detection
# TODO [COMMUNITY]: Implement TOTP-based override verification
# TODO [COMMUNITY]: Create comprehensive error handling and exceptions
# TODO [COMMUNITY]: Document policy syntax and examples with tutorials
# TODO [PRO]: Add policy hot-reload without restart capability
# TODO [PRO]: Implement JSONSchema-based alternative policy format
# TODO [PRO]: Add policy versioning and evolution tracking
# TODO [PRO]: Create policy inheritance system (parent/child policies)
# TODO [PRO]: Implement custom severity levels for organizations
# TODO [PRO]: Add policy tagging and categorization system
# TODO [PRO]: Create policy conflict detection and resolution
# TODO [PRO]: Implement rate limiting for policy violations
# TODO [PRO]: Add audit log rotation with retention policies
# TODO [PRO]: Create policy testing framework for validation
# TODO [ENTERPRISE]: Build ML-based semantic code understanding using AST embeddings
# TODO [ENTERPRISE]: Implement distributed policy evaluation across regions
# TODO [ENTERPRISE]: Add X.509 certificate chain support for policy signing
# TODO [ENTERPRISE]: Create blockchain-style audit log linking (hash chains)
# TODO [ENTERPRISE]: Implement policy encryption at rest with key rotation
# TODO [ENTERPRISE]: Build federated policy governance across organizations
# TODO [ENTERPRISE]: Add quantum-safe cryptographic signatures
# TODO [ENTERPRISE]: Implement zero-knowledge proof policy verification
# TODO [ENTERPRISE]: Create AI-powered policy generation from compliance specs
# TODO [ENTERPRISE]: Build advanced threat modeling integration with policies

from __future__ import annotations

from typing import TYPE_CHECKING

# NOTE: This package contains both:
# - YAML/OPA policy engine components (require optional deps like PyYAML)
# - Cryptographic integrity verification (pure stdlib)
#
# Importing the cryptographic verifier must NOT require PyYAML, because the MCP
# server can be run in a minimal environment where only the integrity tool is
# needed.

if TYPE_CHECKING:
    from .audit_log import AuditLog
    from .exceptions import (
        InvalidOverrideCodeError,
        OverrideTimeoutError,
        PolicyEngineError,
        PolicyModificationError,
        TamperDetectedError,
    )
    from .models import HumanResponse
    from .policy_engine import (
        Operation,
        OverrideDecision,
        Policy,
        PolicyDecision,
        PolicyEngine,
        PolicyError,
        PolicyViolation,
    )
    from .semantic_analyzer import SemanticAnalyzer
    from .tamper_resistance import TamperResistance

# [20250108_FEATURE] Cryptographic Policy Verification (v2.5.0 Guardian)
from .crypto_verify import (
    CryptographicPolicyVerifier,
    PolicyManifest,
    SecurityError,
    VerificationResult,
    verify_policy_integrity_crypto,
)

# TODO [COMMUNITY]: Export minimal API for Community tier (policy verification only)
# TODO [PRO]: Add support for policy versioning and rollback
# TODO [ENTERPRISE]: Multi-tenant policy namespacing and inheritance hierarchies
# TODO [PRO/ENTERPRISE]: Add policy schema validation and auto-documentation
# TODO [ENTERPRISE]: Support for policy audit trails with blockchain-style linking


def __getattr__(name: str):
    """Lazy-load YAML/OPA-dependent policy engine symbols.

    This keeps cryptographic verification usable even when optional policy
    engine dependencies (like PyYAML) are not installed.
    """

    if name in {
        "PolicyEngine",
        "Policy",
        "PolicyDecision",
        "PolicyViolation",
        "Operation",
        "OverrideDecision",
        "PolicyError",
    }:
        from . import policy_engine as _policy_engine

        return getattr(_policy_engine, name)

    if name == "SemanticAnalyzer":
        from .semantic_analyzer import SemanticAnalyzer

        return SemanticAnalyzer

    if name in {
        "TamperResistance",
        "AuditLog",
        "PolicyEngineError",
        "TamperDetectedError",
        "PolicyModificationError",
        "OverrideTimeoutError",
        "InvalidOverrideCodeError",
        "HumanResponse",
    }:
        from .audit_log import AuditLog
        from .exceptions import (
            InvalidOverrideCodeError,
            OverrideTimeoutError,
            PolicyEngineError,
            PolicyModificationError,
            TamperDetectedError,
        )
        from .models import HumanResponse
        from .tamper_resistance import TamperResistance

        mapping = {
            "TamperResistance": TamperResistance,
            "AuditLog": AuditLog,
            "PolicyEngineError": PolicyEngineError,
            "TamperDetectedError": TamperDetectedError,
            "PolicyModificationError": PolicyModificationError,
            "OverrideTimeoutError": OverrideTimeoutError,
            "InvalidOverrideCodeError": InvalidOverrideCodeError,
            "HumanResponse": HumanResponse,
        }
        return mapping[name]

    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = [
    # Policy Engine core
    "PolicyEngine",
    "Policy",
    "PolicyDecision",
    "PolicyViolation",
    "Operation",
    "OverrideDecision",
    "PolicyError",
    "SemanticAnalyzer",
    # Tamper Resistance
    "TamperResistance",
    "AuditLog",
    # Cryptographic Verification (v2.5.0)
    "CryptographicPolicyVerifier",
    "PolicyManifest",
    "VerificationResult",
    "SecurityError",
    "verify_policy_integrity_crypto",
    # Exceptions
    "PolicyEngineError",
    "TamperDetectedError",
    "PolicyModificationError",
    "OverrideTimeoutError",
    "InvalidOverrideCodeError",
    # Models
    "HumanResponse",
]
