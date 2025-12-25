"""
Policy Engine Exceptions.

# [20251216_FEATURE] v2.5.0 Guardian - Tamper resistance exceptions

TODO ITEMS:

COMMUNITY TIER (Core Functionality):
1. TODO: PolicyEngineError - Base exception class
2. TODO: TamperDetectedError - Tamper detection
3. TODO: PolicyModificationError - Modification prevention
4. TODO: OverrideTimeoutError - Override timeout
5. TODO: InvalidOverrideCodeError - Invalid override codes
6. TODO: PolicyParseError - Policy syntax errors
7. TODO: OPAError - OPA CLI integration errors
8. TODO: PolicyEvaluationError - Policy evaluation failures
9. TODO: AuditLogError - Audit logging failures
10. TODO: FilePermissionError - File permission issues

PRO TIER (Enhanced Features):
11. TODO: AuditLogTamperError - Append-only log integrity failures
12. TODO: RateLimitError - Too many overrides requested
13. TODO: PolicyExpiredError - Time-bound policies expired
14. TODO: PolicyInheritanceError - Scope/role-based policy conflicts
15. TODO: ConflictingPoliciesError - Multiple conflicting policies
16. TODO: MissingPolicyError - Required policy not found
17. TODO: KeyRotationError - Key rotation failures
18. TODO: ComplianceError - Compliance check failures
19. TODO: ManifestError - Policy manifest errors
20. TODO: IntegrityError - Cryptographic integrity failures

ENTERPRISE TIER (Advanced Capabilities):
21. TODO: DelegationError - Invalid override delegation
22. TODO: FederatedPolicyError - Cross-organization policy errors
23. TODO: DistributedVerificationError - Distributed verification failures
24. TODO: BlockchainError - Blockchain-based verification failures
25. TODO: QuantumSafeError - Quantum-safe cryptography errors
26. TODO: ZeroKnowledgeError - Zero-knowledge proof failures
27. TODO: HSMError - Hardware security module errors
28. TODO: DecentralizedIdentityError - DID verification failures
29. TODO: AnomalyDetectionError - ML-based anomaly detection errors
30. TODO: FederatedIdentityError - Federated identity verification errors
"""


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
