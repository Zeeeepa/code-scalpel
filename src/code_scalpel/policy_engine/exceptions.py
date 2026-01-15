"""
Policy Engine Exceptions.

# [20251216_FEATURE] v2.5.0 Guardian - Tamper resistance exceptions
"""

# TODO [COMMUNITY]: PolicyEngineError - Base exception class
# TODO [COMMUNITY]: TamperDetectedError - Tamper detection
# TODO [COMMUNITY]: PolicyModificationError - Modification prevention
# TODO [COMMUNITY]: OverrideTimeoutError - Override timeout
# TODO [COMMUNITY]: InvalidOverrideCodeError - Invalid override codes
# TODO [COMMUNITY]: PolicyParseError - Policy syntax errors
# TODO [COMMUNITY]: OPAError - OPA CLI integration errors
# TODO [COMMUNITY]: PolicyEvaluationError - Policy evaluation failures
# TODO [COMMUNITY]: AuditLogError - Audit logging failures
# TODO [COMMUNITY]: FilePermissionError - File permission issues
# TODO [PRO]: AuditLogTamperError - Append-only log integrity failures
# TODO [PRO]: RateLimitError - Too many overrides requested
# TODO [PRO]: PolicyExpiredError - Time-bound policies expired
# TODO [PRO]: PolicyInheritanceError - Scope/role-based policy conflicts
# TODO [PRO]: ConflictingPoliciesError - Multiple conflicting policies
# TODO [PRO]: MissingPolicyError - Required policy not found
# TODO [PRO]: KeyRotationError - Key rotation failures
# TODO [PRO]: ComplianceError - Compliance check failures
# TODO [PRO]: ManifestError - Policy manifest errors
# TODO [PRO]: IntegrityError - Cryptographic integrity failures
# TODO [ENTERPRISE]: DelegationError - Invalid override delegation
# TODO [ENTERPRISE]: FederatedPolicyError - Cross-organization policy errors
# TODO [ENTERPRISE]: DistributedVerificationError - Distributed verification failures
# TODO [ENTERPRISE]: BlockchainError - Blockchain-based verification failures
# TODO [ENTERPRISE]: QuantumSafeError - Quantum-safe cryptography errors
# TODO [ENTERPRISE]: ZeroKnowledgeError - Zero-knowledge proof failures
# TODO [ENTERPRISE]: HSMError - Hardware security module errors
# TODO [ENTERPRISE]: DecentralizedIdentityError - DID verification failures
# TODO [ENTERPRISE]: AnomalyDetectionError - ML-based anomaly detection errors
# TODO [ENTERPRISE]: FederatedIdentityError - Federated identity verification errors



class PolicyEngineError(Exception):
    """Base exception for policy engine errors."""

    pass


class TamperDetectedError(PolicyEngineError):
    """Raised when policy file tampering is detected."""

    pass


class PolicyModificationError(PolicyEngineError):
    """Raised when agent attempts to modify protected policy files."""

    pass


class OverrideTimeoutError(PolicyEngineError):
    """Raised when human override request times out."""

    pass


class InvalidOverrideCodeError(PolicyEngineError):
    """Raised when invalid override code is provided."""

    pass


# TODO [PRO]: Add AuditLogTamperError for append-only log integrity failures
# TODO [ENTERPRISE]: Add PolicyInheritanceError for scope/role-based policy conflicts
# TODO [ENTERPRISE]: Add RateLimitError for when too many overrides requested
# TODO [ENTERPRISE]: Add PolicyExpiredError for time-bound policies
# TODO [ENTERPRISE]: Add DelegationError for invalid override delegation
