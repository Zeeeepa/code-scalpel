"""
[20251218_FEATURE] Autonomy Engine - Main orchestration for autonomous operations.

Coordinates all autonomy components with governance configuration:
- GovernanceConfigLoader for settings
- ChangeBudget for blast radius control
- BlastRadiusCalculator for critical path detection
- FixLoop for self-correction
- Audit system for operation logging

v3.0.0 "Autonomy" Release - Config-driven governance integration.
"""

# TODO [20251224] Phase 1 (COMMUNITY): Implement configuration validation on startup
# TODO [20251224] Phase 1 (COMMUNITY): Create component initialization and lifecycle
# TODO [20251224] Phase 1 (COMMUNITY): Add error propagation and handling
# TODO [20251224] Phase 1 (COMMUNITY): Implement change budget tracking
# TODO [20251224] Phase 1 (COMMUNITY): Create blast radius calculation
# TODO [20251224] Phase 1 (COMMUNITY): Add critical path identification
# TODO [20251224] Phase 1 (COMMUNITY): Implement operation sequencing
# TODO [20251224] Phase 1 (COMMUNITY): Create dependency resolution
# TODO [20251224] Phase 1 (COMMUNITY): Add operation queueing
# TODO [20251224] Phase 1 (COMMUNITY): Implement operation scheduling
# TODO [20251224] Phase 1 (COMMUNITY): Create logging for all operations
# TODO [20251224] Phase 1 (COMMUNITY): Add performance monitoring
# TODO [20251224] Phase 1 (COMMUNITY): Implement graceful degradation
# TODO [20251224] Phase 1 (COMMUNITY): Create fallback mechanisms
# TODO [20251224] Phase 1 (COMMUNITY): Add retry logic for transient failures
# TODO [20251224] Phase 1 (COMMUNITY): Implement timeout handling
# TODO [20251224] Phase 1 (COMMUNITY): Create operation cancellation
# TODO [20251224] Phase 1 (COMMUNITY): Add state persistence
# TODO [20251224] Phase 1 (COMMUNITY): Implement operation batching
# TODO [20251224] Phase 1 (COMMUNITY): Create resource pooling
# TODO [20251224] Phase 1 (COMMUNITY): Add operation prioritization
# TODO [20251224] Phase 1 (COMMUNITY): Implement throttling
# TODO [20251224] Phase 1 (COMMUNITY): Create operation affinity
# TODO [20251224] Phase 1 (COMMUNITY): Add health checks
# TODO [20251224] Phase 1 (COMMUNITY): Implement self-healing

# TODO [20251224] Phase 2 (PRO): Implement distributed orchestration
# TODO [20251224] Phase 2 (PRO): Create load balancing
# TODO [20251224] Phase 2 (PRO): Add parallel operation execution
# TODO [20251224] Phase 2 (PRO): Implement operation dependencies
# TODO [20251224] Phase 2 (PRO): Create DAG (directed acyclic graph) execution
# TODO [20251224] Phase 2 (PRO): Add dynamic reconfiguration
# TODO [20251224] Phase 2 (PRO): Implement adaptive scheduling
# TODO [20251224] Phase 2 (PRO): Create predictive resource allocation
# TODO [20251224] Phase 2 (PRO): Add cost optimization
# TODO [20251224] Phase 2 (PRO): Implement performance tuning
# TODO [20251224] Phase 2 (PRO): Create advanced monitoring and telemetry
# TODO [20251224] Phase 2 (PRO): Add metrics collection and export
# TODO [20251224] Phase 2 (PRO): Implement SLA tracking
# TODO [20251224] Phase 2 (PRO): Create performance profiling
# TODO [20251224] Phase 2 (PRO): Add bottleneck detection
# TODO [20251224] Phase 2 (PRO): Implement optimization suggestions
# TODO [20251224] Phase 2 (PRO): Create A/B testing framework
# TODO [20251224] Phase 2 (PRO): Add canary deployments
# TODO [20251224] Phase 2 (PRO): Implement blue-green deployments
# TODO [20251224] Phase 2 (PRO): Create advanced configuration management
# TODO [20251224] Phase 2 (PRO): Add dynamic policy updates
# TODO [20251224] Phase 2 (PRO): Implement feature flags
# TODO [20251224] Phase 2 (PRO): Create service mesh integration
# TODO [20251224] Phase 2 (PRO): Add advanced error recovery
# TODO [20251224] Phase 2 (PRO): Implement chaos engineering support

# TODO [20251224] Phase 3 (ENTERPRISE): Implement global orchestration
# TODO [20251224] Phase 3 (ENTERPRISE): Create multi-region support
# TODO [20251224] Phase 3 (ENTERPRISE): Add disaster recovery
# TODO [20251224] Phase 3 (ENTERPRISE): Implement high availability
# TODO [20251224] Phase 3 (ENTERPRISE): Create federated governance
# TODO [20251224] Phase 3 (ENTERPRISE): Add organization-level policies
# TODO [20251224] Phase 3 (ENTERPRISE): Implement compliance automation
# TODO [20251224] Phase 3 (ENTERPRISE): Create audit trail integration
# TODO [20251224] Phase 3 (ENTERPRISE): Add encryption for sensitive operations
# TODO [20251224] Phase 3 (ENTERPRISE): Implement role-based access control
# TODO [20251224] Phase 3 (ENTERPRISE): Create advanced logging with PII redaction
# TODO [20251224] Phase 3 (ENTERPRISE): Add compliance reporting
# TODO [20251224] Phase 3 (ENTERPRISE): Implement regulatory frameworks
# TODO [20251224] Phase 3 (ENTERPRISE): Create enterprise security
# TODO [20251224] Phase 3 (ENTERPRISE): Add advanced threat detection
# TODO [20251224] Phase 3 (ENTERPRISE): Implement anomaly detection
# TODO [20251224] Phase 3 (ENTERPRISE): Create executive dashboards
# TODO [20251224] Phase 3 (ENTERPRISE): Add cost tracking and billing
# TODO [20251224] Phase 3 (ENTERPRISE): Implement resource governance
# TODO [20251224] Phase 3 (ENTERPRISE): Create organizational hierarchy support
# TODO [20251224] Phase 3 (ENTERPRISE): Add cross-organization coordination
# TODO [20251224] Phase 3 (ENTERPRISE): Implement service level agreements
# TODO [20251224] Phase 3 (ENTERPRISE): Create incident management
# TODO [20251224] Phase 3 (ENTERPRISE): Add change advisory board (CAB) integration
# TODO [20251224] Phase 3 (ENTERPRISE): Implement advanced policy engine

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

from code_scalpel.autonomy.audit import AutonomyAuditTrail
from code_scalpel.autonomy.fix_loop import FixLoop, FixLoopResult
from code_scalpel.governance import GovernanceConfig, GovernanceConfigLoader
from code_scalpel.governance.change_budget import (
    BudgetDecision,
    ChangeBudget,
    FileChange,
    Operation,
)


@dataclass
class ChangeValidationResult:
    """
    Result of validating a proposed change.

    [20251218_FEATURE] Combines budget and critical path checks.
    """

    allowed: bool
    reason: str
    budget_decision: Optional[BudgetDecision] = None
    critical_path_violation: bool = False
    max_lines_allowed: int = 500
    max_files_allowed: int = 10


class BlastRadiusCalculator:
    """
    Calculate and enforce blast radius limits.

    [20251218_FEATURE] Integrates critical path detection with
    stricter limits for security-sensitive files.
    """

    def __init__(self, config: GovernanceConfig):
        """
        Initialize blast radius calculator with config.

        Args:
            config: Governance configuration with blast radius settings
        """
        self.config = config
        self.logger = logging.getLogger("scalpel.blast_radius")

    def check_critical_path_impact(
        self, files: List[str], lines_changed: Dict[str, int]
    ) -> tuple[bool, str, int]:
        """
        Check if change impacts critical paths and apply limits.

        Args:
            files: List of file paths affected
            lines_changed: Dict mapping file path to lines changed

        Returns:
            Tuple of (is_critical, reason, max_lines_allowed)
        """
        # Check if any file is in critical path
        critical_files = [
            f for f in files if self.config.blast_radius.is_critical_path(f)
        ]

        if not critical_files:
            # Standard limits apply
            return (
                False,
                "No critical paths affected",
                self.config.change_budgeting.max_lines_per_change,
            )

        # Critical path detected - apply stricter limits
        total_lines = sum(lines_changed.get(f, 0) for f in critical_files)
        max_lines = self.config.blast_radius.critical_path_max_lines

        if total_lines > max_lines:
            return (
                True,
                (
                    f"Critical path changes exceed limit. "
                    f"Files: {critical_files}. "
                    f"Attempted {total_lines} lines, maximum {max_lines} allowed."
                ),
                max_lines,
            )

        # Within critical path limits
        return (
            True,
            f"Critical path changes within limits ({total_lines}/{max_lines} lines)",
            max_lines,
        )


# TODO [20251221] Phase 1 Enhancement: Add agent composition and coordination
# TODO [20251221] Phase 1 Enhancement: Implement result caching across operations
# TODO [20251221] Phase 1 Enhancement: Add operation sequencing logic
# TODO [20251221] Phase 1 Enhancement: Support conditional branching
# TODO [20251221] Phase 1 Enhancement: Implement rollback mechanisms

# TODO [20251221] Phase 2 Feature: ML-based decision making
# TODO [20251221] Phase 2 Feature: Intelligent resource allocation
# TODO [20251221] Phase 2 Feature: Cross-agent communication
# TODO [20251221] Phase 2 Feature: Advanced policy evaluation
# TODO [20251221] Phase 2 Feature: Integration with external frameworks (AutoGen, CrewAI)
# TODO [20251221] Phase 2 Feature: Continuous monitoring and adjustment


class AutonomyEngine:
    """
    Main autonomy engine with governance controls.

    [20251218_FEATURE] Orchestrates autonomous operations with
    config-driven limits and critical path protection.

    Key Features:
    - Loads governance configuration from .code-scalpel/config.json
    - Enforces change budgeting with configurable limits
    - Detects and protects critical paths
    - Supervised fix loop with bounded iterations
    - Full audit trail of all operations

    Usage:
        engine = AutonomyEngine(project_root=Path("/path/to/project"))

        # Check if change is allowed
        result = engine.check_change_allowed(
            files=["src/security/auth.py"],
            lines_changed={"src/security/auth.py": 25}
        )

        if result.allowed:
            # Proceed with change
            ...
    """

    def __init__(
        self,
        project_root: Path,
        config_path: Optional[Path] = None,
        on_escalate: Optional[Callable] = None,
    ):
        """
        Initialize autonomy engine.

        Args:
            project_root: Root directory of the project
            config_path: Optional path to config file (default: .code-scalpel/config.json)
            on_escalate: Optional callback for fix loop escalation
        """
        self.project_root = project_root
        self.logger = logging.getLogger("scalpel.autonomy_engine")

        # [20251218_FEATURE] Load governance configuration
        if config_path is None:
            config_path = project_root / ".code-scalpel" / "config.json"

        config_loader = GovernanceConfigLoader(config_path)
        self.config = config_loader.load()

        self.logger.info(
            f"Loaded governance config: "
            f"max_lines={self.config.change_budgeting.max_lines_per_change}, "
            f"max_files={self.config.change_budgeting.max_files_per_change}, "
            f"max_iterations={self.config.autonomy_constraints.max_autonomous_iterations}, "
            f"critical_paths={len(self.config.blast_radius.critical_paths)}"
        )

        # [20251218_FEATURE] Initialize components with config values
        self.change_budget = ChangeBudget(
            {
                "max_files": self.config.change_budgeting.max_files_per_change,
                "max_lines_per_file": self.config.change_budgeting.max_lines_per_change,
                "max_total_lines": self.config.change_budgeting.max_lines_per_change
                * self.config.change_budgeting.max_files_per_change,
                "max_complexity_increase": self.config.change_budgeting.max_complexity_delta,
            }
        )

        self.blast_radius = BlastRadiusCalculator(self.config)

        self.fix_loop = FixLoop(
            max_attempts=self.config.autonomy_constraints.max_autonomous_iterations,
            max_duration_seconds=300,  # 5 minutes
            min_confidence_threshold=0.5,
            on_escalate=on_escalate,
        )

        # Initialize audit trail if enabled
        if self.config.audit.log_all_changes:
            audit_log_path = project_root / ".code-scalpel" / "autonomy_audit"
            audit_log_path.mkdir(parents=True, exist_ok=True)
            self.audit_trail = AutonomyAuditTrail(storage_path=audit_log_path)
        else:
            self.audit_trail = None

    def check_change_allowed(
        self, files: List[str], lines_changed: Dict[str, int]
    ) -> ChangeValidationResult:
        """
        Check if proposed change meets governance constraints.

        [20251218_FEATURE] Enforces both budget and critical path limits.

        Args:
            files: List of file paths to be changed
            lines_changed: Dict mapping file path to lines changed

        Returns:
            ChangeValidationResult with detailed decision
        """
        # [20251218_FEATURE] Check critical path impact first
        is_critical, crit_reason, max_lines = (
            self.blast_radius.check_critical_path_impact(files, lines_changed)
        )

        if is_critical and "exceed" in crit_reason:
            # Critical path violation - block immediately
            return ChangeValidationResult(
                allowed=False,
                reason=crit_reason,
                critical_path_violation=True,
                max_lines_allowed=max_lines,
            )

        # [20251218_FEATURE] Check change budgeting
        operation = Operation(
            changes=[
                FileChange(
                    file_path=f,
                    added_lines=[""] * lines_changed.get(f, 0),  # Placeholder
                    removed_lines=[],
                )
                for f in files
            ]
        )

        budget_decision = self.change_budget.validate_operation(operation)

        if not budget_decision.allowed:
            return ChangeValidationResult(
                allowed=False,
                reason=budget_decision.get_error_message(),
                budget_decision=budget_decision,
                max_lines_allowed=max_lines,
                max_files_allowed=self.config.change_budgeting.max_files_per_change,
            )

        # [20251218_FEATURE] Check approval requirements
        if is_critical and self.config.blast_radius.block_on_critical_paths:
            if self.config.autonomy_constraints.require_approval_for_security_changes:
                return ChangeValidationResult(
                    allowed=False,
                    reason=(
                        f"Critical path changes require human approval. "
                        f"Files: {files}"
                    ),
                    critical_path_violation=True,
                    max_lines_allowed=max_lines,
                )

        # Change allowed
        return ChangeValidationResult(
            allowed=True,
            reason=f"Change within limits. {crit_reason}",
            budget_decision=budget_decision,
            critical_path_violation=False,
            max_lines_allowed=max_lines,
            max_files_allowed=self.config.change_budgeting.max_files_per_change,
        )

    def run_fix_loop(
        self,
        initial_error: str,
        source_code: str,
        language: str,
        sandbox,
        error_engine,
        project_path: str,
    ) -> FixLoopResult:
        """
        Run supervised fix loop with config-driven iteration limits.

        [20251218_FEATURE] Delegates to FixLoop with configured max_attempts.

        Args:
            initial_error: Error message to fix
            source_code: Current source code
            language: Programming language
            sandbox: Sandbox executor
            error_engine: Error-to-diff engine
            project_path: Path to project

        Returns:
            FixLoopResult with success/failure and audit trail
        """
        result = self.fix_loop.run(
            initial_error=initial_error,
            source_code=source_code,
            language=language,
            sandbox=sandbox,
            error_engine=error_engine,
            project_path=project_path,
        )

        # Log to audit if enabled
        if self.audit_trail and self.config.audit.log_all_changes:

            self.audit_trail.record(
                event_type="fix_loop",
                operation="autonomous_fix_loop",
                input_data=initial_error,
                output_data=result.termination_reason,
                success=result.success,
                duration_ms=result.total_duration_ms,
                metadata={
                    "language": language,
                    "termination_reason": result.termination_reason,
                    "escalated": result.escalated_to_human,
                    "attempts": len(result.attempts),
                },
                parent_id=None,
            )

        return result

    def get_config_summary(self) -> Dict[str, Any]:
        """
        Get summary of active configuration.

        Returns:
            Dict with key config values for logging/debugging
        """
        return {
            "change_budgeting": {
                "max_lines": self.config.change_budgeting.max_lines_per_change,
                "max_files": self.config.change_budgeting.max_files_per_change,
                "max_complexity_delta": self.config.change_budgeting.max_complexity_delta,
            },
            "blast_radius": {
                "enabled": self.config.blast_radius.enabled,
                "critical_paths": self.config.blast_radius.critical_paths,
                "critical_path_max_lines": self.config.blast_radius.critical_path_max_lines,
                "block_on_critical_paths": self.config.blast_radius.block_on_critical_paths,
            },
            "autonomy_constraints": {
                "max_iterations": self.config.autonomy_constraints.max_autonomous_iterations,
                "require_approval_breaking": self.config.autonomy_constraints.require_approval_for_breaking_changes,
                "require_approval_security": self.config.autonomy_constraints.require_approval_for_security_changes,
                "sandbox_required": self.config.autonomy_constraints.sandbox_execution_required,
            },
            "audit": {
                "log_all_changes": self.config.audit.log_all_changes,
                "retention_days": self.config.audit.retention_days,
            },
        }
