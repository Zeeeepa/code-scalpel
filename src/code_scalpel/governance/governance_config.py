"""
Governance Configuration System for Code Scalpel v3.0.0 "Autonomy"

[20251218_FEATURE] Config-driven autonomy with change budgeting, blast radius
control, and critical path protection.

This module provides:
- Change budgeting: Configurable limits on lines, files, complexity
- Blast radius control: Limit impact scope with call graph depth
- Critical paths: Stricter controls for security-sensitive directories
- Environment overrides: System-wide settings via env vars
- Integrity protection: SHA-256 hash validation and HMAC signatures

Configuration precedence:
1. Environment variables (SCALPEL_*)
2. .code-scalpel/config.json (with hash validation)
3. Default values

See docs/configuration/governance_config_schema.md for full specification.
"""

import hashlib

# TODO [CORE] Add GovernanceConfig.load() from file method
# TODO [CORE] Add GovernanceConfig.load_from_env() from environment
# TODO [CORE] Add GovernanceConfig.load_from_dict() from dictionary
# TODO [CORE] Add GovernanceConfig.validate() validation method
# TODO [CORE] Add GovernanceConfig.to_dict() serialization
# TODO [CORE] Add GovernanceConfig.to_json() JSON serialization
# TODO [CORE] Add GovernanceConfigLoader class
# TODO [CORE] Add validate_change_budgeting() validator
# TODO [CORE] Add validate_blast_radius() validator
# TODO [CORE] Add validate_autonomy_constraints() validator
# TODO [CORE] Add validate_audit_config() validator
# TODO [CORE] Add validate_critical_paths() path validator
# TODO [CORE] Add check_budget_exceeded() budget checker
# TODO [CORE] Add is_on_critical_path() critical path checker
# TODO [CORE] Add get_effective_limits(constraints) limit calculator
# TODO [CORE] Add merge_configs(base, override) merger
# TODO [CORE] Add config_to_yaml() YAML exporter
# TODO [CORE] Add config_from_yaml(yaml_str) YAML importer
# TODO [CORE] Add schema validation using JSON Schema
# TODO [CORE] Add config file hash verification
# TODO [CORE] Add HMAC signature validation
# TODO [CORE] Add config integrity check
# TODO [CORE] Add config compatibility checking
# TODO [CORE] Add explain_config_rules() documentation
# TODO [CORE] Add get_config_errors() error reporting
# TODO [PRO] Add config hot reload without restart
# TODO [PRO] Add config versioning and migrations
# TODO [PRO] Add config environment variable expansion
# TODO [PRO] Add config file encryption/decryption
# TODO [PRO] Add config diff and change tracking
# TODO [PRO] Add config inheritance/composition
# TODO [PRO] Add config profiles (dev, staging, prod)
# TODO [PRO] Add config secrets management
# TODO [PRO] Add config audit logging
# TODO [PRO] Add config access control (RBAC)
# TODO [PRO] Add config change notifications
# TODO [PRO] Add config performance profiling
# TODO [PRO] Add config optimization recommendations
# TODO [PRO] Add config debugging/tracing
# TODO [PRO] Add config dry-run mode for changes
# TODO [PRO] Add config rollback capabilities
# TODO [PRO] Add config backup and restore
# TODO [PRO] Add config documentation generation
# TODO [PRO] Add config example generation
# TODO [PRO] Add config conditional sections
# TODO [PRO] Add config macro expansion
# TODO [PRO] Add config template variables
# TODO [PRO] Add config JSON Schema validation
# TODO [PRO] Add config context-aware rules
# TODO [PRO] Add config policy inheritance chain
# TODO [ENTERPRISE] Add distributed config sync across agents
# TODO [ENTERPRISE] Add federated config management across orgs
# TODO [ENTERPRISE] Add multi-region config coordination
# TODO [ENTERPRISE] Add config replication and failover
# TODO [ENTERPRISE] Add config consensus and voting
# TODO [ENTERPRISE] Add config distributed locking
# TODO [ENTERPRISE] Add config event streaming
# TODO [ENTERPRISE] Add config change notifications
# TODO [ENTERPRISE] Add config cost tracking per org
# TODO [ENTERPRISE] Add config quota enforcement
# TODO [ENTERPRISE] Add config SLA monitoring
# TODO [ENTERPRISE] Add config audit trail logging
# TODO [ENTERPRISE] Add config compliance checking (SOC2/HIPAA/GDPR)
# TODO [ENTERPRISE] Add config encryption for sensitive data
# TODO [ENTERPRISE] Add config access control (RBAC)
# TODO [ENTERPRISE] Add config encryption key management
# TODO [ENTERPRISE] Add config multi-tenancy isolation
# TODO [ENTERPRISE] Add config disaster recovery
# TODO [ENTERPRISE] Add config failover mechanisms
# TODO [ENTERPRISE] Add config data retention policies
# TODO [ENTERPRISE] Add config billing integration
# TODO [ENTERPRISE] Add config executive reporting
# TODO [ENTERPRISE] Add config anomaly detection
# TODO [ENTERPRISE] Add config circuit breaker
# TODO [ENTERPRISE] Add config health monitoring
import hmac
import json
import logging
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

logger = logging.getLogger(__name__)


@dataclass
class ChangeBudgetingConfig:
    """
    Configuration for change budgeting limits.

    Controls how much code can be modified in a single autonomous operation.
    """

    enabled: bool = True
    max_lines_per_change: int = 500
    max_files_per_change: int = 10
    max_complexity_delta: int = 50
    require_justification: bool = True
    budget_refresh_interval_hours: int = 24


@dataclass
class BlastRadiusConfig:
    """
    Configuration for blast radius control.

    Limits the scope of changes by tracking affected functions, classes,
    and call graph depth. Provides special handling for critical paths.
    """

    enabled: bool = True
    max_affected_functions: int = 20
    max_affected_classes: int = 5
    max_call_graph_depth: int = 3
    warn_on_public_api_changes: bool = True
    block_on_critical_paths: bool = True
    critical_paths: List[str] = field(default_factory=list)
    critical_path_max_lines: int = 50
    critical_path_max_complexity_delta: int = 10

    def is_critical_path(self, file_path: str) -> bool:
        """
        Check if file matches any critical path pattern.

        Supports:
        - Exact paths: "src/security/auth.py"
        - Directory prefixes: "src/security/"
        - Glob patterns: "src/*/security/*.py"

        Args:
            file_path: Path to check

        Returns:
            True if path matches any critical path pattern
        """
        from fnmatch import fnmatch

        path_str = Path(file_path).as_posix()

        for pattern in self.critical_paths:
            # Direct match or prefix match
            if fnmatch(path_str, pattern) or path_str.startswith(pattern):
                return True

        return False


@dataclass
class AutonomyConstraintsConfig:
    """
    Configuration for autonomy constraints.

    Controls iteration limits and approval requirements for autonomous operations.
    """

    max_autonomous_iterations: int = 10
    require_approval_for_breaking_changes: bool = True
    require_approval_for_security_changes: bool = True
    sandbox_execution_required: bool = True


@dataclass
class AuditConfig:
    """
    Configuration for audit trail.

    Controls logging and retention of autonomous operations.
    """

    log_all_changes: bool = True
    log_rejected_changes: bool = True
    retention_days: int = 90


@dataclass
class GovernanceConfig:
    """
    Complete governance configuration.

    Aggregates all governance subsystems into a single config object.
    """

    change_budgeting: ChangeBudgetingConfig
    blast_radius: BlastRadiusConfig
    autonomy_constraints: AutonomyConstraintsConfig
    audit: AuditConfig


class GovernanceConfigLoader:
    """
    Load and validate governance configuration.

    Configuration precedence:
    1. Environment variables (SCALPEL_*)
    2. .code-scalpel/config.json (with hash validation)
    3. Default values

    Security features:
    - SHA-256 hash validation via SCALPEL_CONFIG_HASH
    - HMAC signature verification via SCALPEL_CONFIG_SECRET
    - Tamper detection with fail-closed behavior

    Example:
        >>> loader = GovernanceConfigLoader()
        >>> config = loader.load()
        >>> if config.blast_radius.is_critical_path("src/security/auth.py"):
        ...     print("Critical path - stricter limits apply")

    Environment variables:
        SCALPEL_CONFIG - Path to config.json override
        SCALPEL_CONFIG_HASH - Expected SHA-256 hash (format: sha256:...)
        SCALPEL_CONFIG_SECRET - HMAC secret key for signature verification
        SCALPEL_CONFIG_SIGNATURE - Expected HMAC signature
        SCALPEL_CHANGE_BUDGET_MAX_LINES - Override max lines per change
        SCALPEL_CHANGE_BUDGET_MAX_FILES - Override max files per change
        SCALPEL_CRITICAL_PATHS - Comma-separated list of critical paths
        SCALPEL_CRITICAL_PATH_MAX_LINES - Override critical path line limit
        SCALPEL_MAX_AUTONOMOUS_ITERATIONS - Override iteration limit
    """

    def __init__(self, config_path: Optional[Path] = None):
        """
        Initialize config loader.

        Args:
            config_path: Optional explicit path to config.json
                        Defaults to .code-scalpel/config.json in current directory
        """
        # [20251231_FEATURE] Track whether the caller provided an explicit path.
        # This matters for precedence: profile selection should not override an
        # explicit constructor path.
        self._explicit_config_path = config_path is not None
        self.config_path = config_path or Path.cwd() / ".code-scalpel" / "config.json"

    def _select_profile_config_path(self) -> Optional[Path]:
        """Select a profile config path if configured.

        Uses `SCALPEL_CONFIG_PROFILE` to load `.code-scalpel/config.<profile>.json`.

        [20251231_FEATURE] Governance config profile selection.
        """
        profile = (os.getenv("SCALPEL_CONFIG_PROFILE") or "").strip()
        if not profile:
            return None
        # Keep profile string safe and predictable.
        profile_norm = "".join(
            ch for ch in profile.lower() if ch.isalnum() or ch in {"-", "_"}
        )
        if not profile_norm:
            return None
        candidate = Path.cwd() / ".code-scalpel" / f"config.{profile_norm}.json"
        return candidate

    def load(self) -> GovernanceConfig:
        """
        Load configuration with integrity validation.

        Returns:
            GovernanceConfig object with all settings

        Raises:
            ValueError: If hash/signature validation fails
            FileNotFoundError: Only if config_path explicitly set and doesn't exist
        """
        # [20251231_FEATURE] Configuration precedence:
        # 1) SCALPEL_CONFIG (explicit path override)
        # 2) explicit constructor config_path
        # 3) SCALPEL_CONFIG_PROFILE -> .code-scalpel/config.<profile>.json
        # 4) default .code-scalpel/config.json

        config_path_env = os.getenv("SCALPEL_CONFIG")
        if config_path_env:
            self.config_path = Path(config_path_env)
        elif not self._explicit_config_path:
            candidate = self._select_profile_config_path()
            if candidate is not None and candidate.exists():
                self.config_path = candidate

        # Load configuration or use defaults
        if self.config_path.exists():
            logger.info(f"Loading governance config from {self.config_path}")
            config_data = self._load_and_validate()
        else:
            logger.warning(
                f"No governance configuration found at {self.config_path}, "
                "using defaults"
            )
            config_data = self._get_defaults()

        # Apply environment variable overrides
        config_data = self._apply_env_overrides(config_data)

        # Parse into typed dataclasses
        return self._parse_config(config_data)

    def _load_and_validate(self) -> dict:
        """
        Load and validate configuration file integrity.

        Returns:
            Parsed configuration dict

        Raises:
            ValueError: If hash or signature validation fails
        """
        with open(self.config_path, "rb") as f:
            content = f.read()

        # SHA-256 hash validation
        expected_hash = os.getenv("SCALPEL_CONFIG_HASH")
        if expected_hash:
            actual_hash = f"sha256:{hashlib.sha256(content).hexdigest()}"
            if actual_hash != expected_hash:
                raise ValueError(
                    f"Configuration hash mismatch. "
                    f"Expected {expected_hash}, got {actual_hash}. "
                    f"Configuration may have been tampered with. "
                    f"Regenerate hash: sha256sum {self.config_path}"
                )
            logger.debug("Configuration hash validation passed")

        # HMAC signature validation (enterprise feature)
        secret = os.getenv("SCALPEL_CONFIG_SECRET")
        expected_sig = os.getenv("SCALPEL_CONFIG_SIGNATURE")
        if secret and expected_sig:
            actual_sig = hmac.new(secret.encode(), content, hashlib.sha256).hexdigest()
            if actual_sig != expected_sig:
                raise ValueError(
                    "Configuration signature invalid. "
                    "Configuration may have been tampered with. "
                    "Regenerate signature with correct secret key."
                )
            logger.debug("Configuration HMAC signature validation passed")

        return json.loads(content)

    def _get_defaults(self) -> dict:
        """
        Return default configuration.

        Returns:
            Default configuration dict
        """
        return {
            "version": "3.0.0",
            "governance": {
                "change_budgeting": {
                    "enabled": True,
                    "max_lines_per_change": 500,
                    "max_files_per_change": 10,
                    "max_complexity_delta": 50,
                    "require_justification": True,
                    "budget_refresh_interval_hours": 24,
                },
                "blast_radius": {
                    "enabled": True,
                    "max_affected_functions": 20,
                    "max_affected_classes": 5,
                    "max_call_graph_depth": 3,
                    "warn_on_public_api_changes": True,
                    "block_on_critical_paths": True,
                    "critical_paths": [],
                    "critical_path_max_lines": 50,
                    "critical_path_max_complexity_delta": 10,
                },
                "autonomy_constraints": {
                    "max_autonomous_iterations": 10,
                    "require_approval_for_breaking_changes": True,
                    "require_approval_for_security_changes": True,
                    "sandbox_execution_required": True,
                },
                "audit": {
                    "log_all_changes": True,
                    "log_rejected_changes": True,
                    "retention_days": 90,
                },
            },
        }

    def _apply_env_overrides(self, config: dict) -> dict:
        """
        Apply environment variable overrides.

        Environment variables take precedence over file configuration.

        Args:
            config: Configuration dict to modify

        Returns:
            Modified configuration dict
        """
        gov = config.get("governance", {})

        # Change Budgeting overrides
        cb = gov.get("change_budgeting", {})
        max_lines_env = os.getenv("SCALPEL_CHANGE_BUDGET_MAX_LINES")
        if max_lines_env:
            cb["max_lines_per_change"] = int(max_lines_env)
        max_files_env = os.getenv("SCALPEL_CHANGE_BUDGET_MAX_FILES")
        if max_files_env:
            cb["max_files_per_change"] = int(max_files_env)
        max_complexity_env = os.getenv("SCALPEL_CHANGE_BUDGET_MAX_COMPLEXITY")
        if max_complexity_env:
            cb["max_complexity_delta"] = int(max_complexity_env)

        # Blast Radius & Critical Paths overrides
        br = gov.get("blast_radius", {})
        critical_paths_env = os.getenv("SCALPEL_CRITICAL_PATHS")
        if critical_paths_env:
            br["critical_paths"] = [p.strip() for p in critical_paths_env.split(",")]
        critical_path_max_lines_env = os.getenv("SCALPEL_CRITICAL_PATH_MAX_LINES")
        if critical_path_max_lines_env:
            br["critical_path_max_lines"] = int(critical_path_max_lines_env)
        max_call_graph_depth_env = os.getenv("SCALPEL_MAX_CALL_GRAPH_DEPTH")
        if max_call_graph_depth_env:
            br["max_call_graph_depth"] = int(max_call_graph_depth_env)

        # Autonomy Constraints overrides
        ac = gov.get("autonomy_constraints", {})
        max_iterations_env = os.getenv("SCALPEL_MAX_AUTONOMOUS_ITERATIONS")
        if max_iterations_env:
            ac["max_autonomous_iterations"] = int(max_iterations_env)

        # Audit overrides
        audit = gov.get("audit", {})
        retention_days_env = os.getenv("SCALPEL_AUDIT_RETENTION_DAYS")
        if retention_days_env:
            audit["retention_days"] = int(retention_days_env)

        return config

    def _parse_config(self, config_data: dict) -> GovernanceConfig:
        """
        Parse configuration dict into typed dataclasses.

        Args:
            config_data: Configuration dict

        Returns:
            GovernanceConfig object

        Raises:
            TypeError: If configuration values have wrong types
        """
        gov = config_data.get("governance", {})

        return GovernanceConfig(
            change_budgeting=ChangeBudgetingConfig(**gov.get("change_budgeting", {})),
            blast_radius=BlastRadiusConfig(**gov.get("blast_radius", {})),
            autonomy_constraints=AutonomyConstraintsConfig(
                **gov.get("autonomy_constraints", {})
            ),
            audit=AuditConfig(**gov.get("audit", {})),
        )
