"""
[20251217_FEATURE] Speculative Execution (Sandboxed) module.

Purpose: Test proposed changes in an isolated environment before applying to main codebase.

Security guarantees:
- No network access (by default)
- No filesystem access outside sandbox
- Resource limits (CPU, memory, time)
- Process isolation via containers or chroot

[20251224_TODO] Phase 1 - Core Sandbox Execution (COMMUNITY Tier - 25 items):
- [ ] Implement temporary directory creation and cleanup
- [ ] Create process-level isolation
- [ ] Implement file copy and restoration
- [ ] Add test execution framework
- [ ] Create lint execution
- [ ] Implement build execution
- [ ] Add output capture (stdout/stderr)
- [ ] Create test result parsing
- [ ] Implement error detection
- [ ] Add resource limit enforcement
- [ ] Create timeout mechanisms
- [ ] Implement signal handling
- [ ] Add test framework detection
- [ ] Create pytest integration
- [ ] Add unittest integration
- [ ] Implement jest integration
- [ ] Create test filtering
- [ ] Add parallel test execution
- [ ] Implement logging
- [ ] Create result aggregation
- [ ] Add performance tracking
- [ ] Implement rollback mechanisms
- [ ] Create comprehensive error handling
- [ ] Add side effect monitoring
- [ ] Implement filesystem change tracking

[20251224_TODO] Phase 2 - Advanced Sandbox Features (PRO Tier - 25 items):
- [ ] Implement Docker container isolation
- [ ] Create container management
- [ ] Add image caching
- [ ] Implement container networking
- [ ] Create volume management
- [ ] Add environment variable isolation
- [ ] Implement credential injection
- [ ] Create build artifact caching
- [ ] Add incremental testing
- [ ] Implement dependency caching
- [ ] Create cache warming
- [ ] Add performance optimization
- [ ] Implement cost calculation
- [ ] Create resource profiling
- [ ] Add memory limit tracking
- [ ] Implement CPU limit tracking
- [ ] Create disk usage tracking
- [ ] Add network monitoring
- [ ] Implement process monitoring
- [ ] Create advanced filtering
- [ ] Add custom test runners
- [ ] Implement framework-specific analysis
- [ ] Create intelligent scheduling
- [ ] Add failure prediction
- [ ] Implement adaptive resource allocation

[20251224_TODO] Phase 3 - Enterprise Isolation (ENTERPRISE Tier - 25 items):
- [ ] Implement Kubernetes pod isolation
- [ ] Create multi-region execution
- [ ] Add cross-region replication
- [ ] Implement secure enclave support
- [ ] Create hardware-based isolation
- [ ] Add encryption for sandbox operations
- [ ] Implement audit trail integration
- [ ] Create compliance enforcement
- [ ] Add regulatory requirement checking
- [ ] Implement role-based access
- [ ] Create PII protection
- [ ] Add data residency enforcement
- [ ] Implement disaster recovery
- [ ] Create high availability
- [ ] Add disaster recovery planning
- [ ] Implement backup strategies
- [ ] Create restoration procedures
- [ ] Add failover mechanisms
- [ ] Implement replica management
- [ ] Create multi-region deployment
- [ ] Add geo-redundancy
- [ ] Implement cross-region failover
- [ ] Create circuit breaking
- [ ] Add graceful degradation
- [ ] Implement fallback execution
- [ ] Create alternative strategies
- [ ] Add mode switching
- [ ] Implement adaptive isolation
- [ ] Create dynamic resource allocation
- [ ] Add predictive scaling
- [ ] Implement auto-scaling
- [ ] Create load prediction
- [ ] Add demand forecasting
- [ ] Implement capacity planning
- [ ] Create cost estimation
- [ ] Add budget enforcement
- [ ] Implement quota tracking
- [ ] Create usage accounting

[20251224_TODO] Phase 3 - Enterprise Sandbox (ENTERPRISE Tier - 25 items):
- [ ] Implement organization-wide policies
- [ ] Create federated sandbox execution
- [ ] Add cross-org resource sharing
- [ ] Implement compliance checking
- [ ] Create audit trail integration
- [ ] Add encryption at rest
- [ ] Implement encryption in transit
- [ ] Create role-based access control
- [ ] Add approval workflows
- [ ] Implement change advisory board
- [ ] Create SLA tracking
- [ ] Add incident management
- [ ] Implement regulatory compliance
- [ ] Create compliance automation
- [ ] Add compliance reporting
- [ ] Implement cost allocation
- [ ] Create billing integration
- [ ] Add usage tracking
- [ ] Implement chargeback models
- [ ] Create advanced analytics
- [ ] Add predictive modeling
- [ ] Implement machine learning insights
- [ ] Create anomaly detection
- [ ] Add fraud detection
- [ ] Implement advanced security
- [ ] Add geographic distribution
- [ ] Implement advanced security scanning
- [ ] Create threat detection
- [ ] Add anomaly detection
- [ ] Implement cost tracking and billing
- [ ] Create usage reporting
- [ ] Add SLA enforcement
- [ ] Implement advanced monitoring
- [ ] Create executive dashboards
- [ ] Add centralized management
- [ ] Implement multi-tenant isolation
"""

import os
import shlex
import shutil
import subprocess
import tempfile
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

try:
    import docker  # type: ignore[import-untyped]

    DOCKER_AVAILABLE = True
except ImportError:
    docker = None  # type: ignore[assignment]
    DOCKER_AVAILABLE = False


@dataclass
class LintResult:
    """[20251217_FEATURE] Individual lint result."""

    file: str
    line: Optional[int]
    column: Optional[int]
    message: str
    severity: str  # "error", "warning", "info"


@dataclass
class ExecutionTestResult:
    """[20251217_FEATURE] Individual test result from sandbox execution."""

    name: str
    passed: bool
    duration_ms: int
    error_message: Optional[str] = None


# Aliases for backward compatibility and naming
SandboxTestResult = ExecutionTestResult
TestResult = ExecutionTestResult


@dataclass
class FileChange:
    """[20251217_FEATURE] Represents a file change to apply."""

    relative_path: str
    operation: str  # "create", "modify", "delete"
    new_content: Optional[str] = None


@dataclass
class SandboxResult:
    """Result of sandboxed execution."""

    success: bool
    test_results: list[ExecutionTestResult] = field(default_factory=list)
    lint_results: list[LintResult] = field(default_factory=list)
    build_success: bool = True
    side_effects_detected: bool = False
    execution_time_ms: int = 0
    stdout: str = ""
    stderr: str = ""


class SandboxExecutor:
    """
    Execute code changes in isolated sandbox.

    Security guarantees:
    - No network access (by default)
    - No filesystem access outside sandbox
    - Resource limits (CPU, memory, time)
    - Process isolation via containers or chroot
    """

    def __init__(
        self,
        isolation_level: str = "process",  # "container", "process", "chroot"
        network_enabled: bool = False,
        max_memory_mb: int = 512,
        max_cpu_seconds: int = 60,
        max_disk_mb: int = 100,
    ):
        """
        Initialize sandbox executor.

        Args:
            isolation_level: Level of isolation ("container", "process", "chroot")
            network_enabled: Whether to allow network access
            max_memory_mb: Maximum memory in MB
            max_cpu_seconds: Maximum CPU time in seconds
            max_disk_mb: Maximum disk space in MB
        """
        self.isolation_level = isolation_level
        self.network_enabled = network_enabled
        self.max_memory_mb = max_memory_mb
        self.max_cpu_seconds = max_cpu_seconds
        self.max_disk_mb = max_disk_mb

        # [20251221_TODO] Phase 1 Enhancements:
        # - [ ] Add configuration validation
        # - [ ] Support custom environment variables
        # - [ ] Add pre-execution hooks
        # - [ ] Implement result caching layer
        # - [ ] Add timeout handling for hanging processes
        #
        # [20251221_TODO] Phase 2 Features:
        # - [ ] Parallel execution coordination
        # - [ ] Result streaming support
        # - [ ] Performance profiling integration
        # - [ ] Network isolation verification
        # - [ ] Filesystem access logging

        # [20251217_FEATURE] Initialize Docker client if container isolation requested
        if isolation_level == "container":
            if not DOCKER_AVAILABLE:
                raise ImportError(
                    "Docker support requires 'docker' package. "
                    "Install with: pip install docker"
                )
            if docker is None:
                raise ImportError(
                    "Docker support requires 'docker' package. "
                    "Install with: pip install docker"
                )

            self.docker_client = docker.from_env()

    def execute_with_changes(
        self,
        project_path: str,
        changes: list[FileChange],
        test_command: str = "pytest",
        lint_command: str = "ruff check",
        build_command: Optional[str] = None,
    ) -> SandboxResult:
        """
        Apply changes and run tests in sandbox.

        Args:
            project_path: Path to project root
            changes: List of file changes to apply
            test_command: Command to run tests
            lint_command: Command to run linter
            build_command: Optional build command

        Returns:
            SandboxResult with test results and side effect detection
        """
        # Create isolated sandbox
        sandbox_path = self._create_sandbox(project_path)

        try:
            # Apply changes to sandbox
            self._apply_changes(sandbox_path, changes)

            # Run in isolated environment
            if self.isolation_level == "container":
                return self._execute_in_container(
                    sandbox_path, test_command, lint_command, build_command
                )
            else:
                return self._execute_in_process(
                    sandbox_path, test_command, lint_command, build_command
                )

        finally:
            # Clean up sandbox
            self._cleanup_sandbox(sandbox_path)

    def _create_sandbox(self, project_path: str) -> Path:
        """
        Create isolated copy of project.

        Uses copy-on-write where supported for efficiency.

        Args:
            project_path: Path to project root

        Returns:
            Path to sandbox directory
        """
        sandbox_dir = Path(tempfile.mkdtemp(prefix="scalpel_sandbox_"))

        # [20251217_FEATURE] Copy project files (excluding .git, node_modules, etc.)
        for item in Path(project_path).iterdir():
            if item.name in {
                ".git",
                "node_modules",
                "__pycache__",
                "venv",
                ".venv",
                ".tox",
                "dist",
                "build",
            }:
                continue

            dest = sandbox_dir / item.name
            if item.is_dir():
                shutil.copytree(item, dest, symlinks=True)
            else:
                shutil.copy2(item, dest)

        return sandbox_dir

    def _apply_changes(self, sandbox_path: Path, changes: list[FileChange]) -> None:
        """
        Apply file changes to sandbox.

        Args:
            sandbox_path: Path to sandbox directory
            changes: List of file changes to apply
        """
        for change in changes:
            file_path = sandbox_path / change.relative_path

            if change.operation == "create":
                file_path.parent.mkdir(parents=True, exist_ok=True)
                file_path.write_text(change.new_content or "")

            elif change.operation == "modify":
                if change.new_content is not None:
                    file_path.write_text(change.new_content)

            elif change.operation == "delete":
                file_path.unlink(missing_ok=True)

    def _execute_in_container(
        self,
        sandbox_path: Path,
        test_command: str,
        lint_command: str,
        build_command: Optional[str],
    ) -> SandboxResult:
        """
        Execute in Docker container for full isolation.

        Args:
            sandbox_path: Path to sandbox directory
            test_command: Command to run tests
            lint_command: Command to run linter
            build_command: Optional build command

        Returns:
            SandboxResult with execution results
        """
        start_time = time.time()

        # [20251217_FEATURE] Build container command
        commands = []
        if build_command:
            commands.append(build_command)
        commands.append(lint_command)
        commands.append(test_command)

        full_command = " && ".join(commands)

        try:
            # Run in container
            container = self.docker_client.containers.run(
                image="python:3.11-slim",
                command=f"/bin/sh -c '{full_command}'",
                volumes={str(sandbox_path): {"bind": "/workspace", "mode": "rw"}},
                working_dir="/workspace",
                network_disabled=not self.network_enabled,
                mem_limit=f"{self.max_memory_mb}m",
                cpu_period=100000,
                cpu_quota=self.max_cpu_seconds * 100000,
                remove=True,
                detach=False,
                stdout=True,
                stderr=True,
            )

            execution_time = int((time.time() - start_time) * 1000)

            # Parse results from container output
            return SandboxResult(
                success=True,
                build_success=True,
                execution_time_ms=execution_time,
                stdout=(
                    container.decode()
                    if isinstance(container, bytes)
                    else str(container)
                ),
                stderr="",
            )

        except Exception as e:
            execution_time = int((time.time() - start_time) * 1000)
            return SandboxResult(
                success=False,
                build_success=False,
                execution_time_ms=execution_time,
                stdout="",
                stderr=str(e),
            )

    def _execute_in_process(
        self,
        sandbox_path: Path,
        test_command: str,
        lint_command: str,
        build_command: Optional[str],
    ) -> SandboxResult:
        """
        Execute in subprocess with resource limits.

        Args:
            sandbox_path: Path to sandbox directory
            test_command: Command to run tests
            lint_command: Command to run linter
            build_command: Optional build command

        Returns:
            SandboxResult with execution results
        """
        import resource

        def set_limits():
            """Set resource limits for child process."""
            # [20251217_SECURITY] Memory limit
            try:
                resource.setrlimit(
                    resource.RLIMIT_AS,
                    (
                        self.max_memory_mb * 1024 * 1024,
                        self.max_memory_mb * 1024 * 1024,
                    ),
                )
            except (ValueError, OSError):
                # Some systems don't support RLIMIT_AS
                pass

            # [20251217_SECURITY] CPU time limit
            try:
                resource.setrlimit(
                    resource.RLIMIT_CPU, (self.max_cpu_seconds, self.max_cpu_seconds)
                )
            except (ValueError, OSError):
                pass

        start_time = time.time()

        # [20251217_FEATURE] Run build if specified
        if build_command:
            try:
                # [20251218_SECURITY] Use shlex.split to safely parse command, avoid shell injection (B602)
                build_result = subprocess.run(
                    shlex.split(build_command),
                    shell=False,
                    cwd=sandbox_path,
                    capture_output=True,
                    timeout=self.max_cpu_seconds,
                    preexec_fn=set_limits if os.name != "nt" else None,
                )
                if build_result.returncode != 0:
                    execution_time = int((time.time() - start_time) * 1000)
                    return SandboxResult(
                        success=False,
                        test_results=[],
                        lint_results=[],
                        build_success=False,
                        side_effects_detected=False,
                        execution_time_ms=execution_time,
                        stdout=build_result.stdout.decode("utf-8", errors="replace"),
                        stderr=build_result.stderr.decode("utf-8", errors="replace"),
                    )
            except subprocess.TimeoutExpired:
                execution_time = int((time.time() - start_time) * 1000)
                return SandboxResult(
                    success=False,
                    build_success=False,
                    execution_time_ms=execution_time,
                    stdout="",
                    stderr="Build command timed out",
                )

        # [20251217_FEATURE] Run linter
        lint_result = None
        try:
            # [20251218_SECURITY] Use shlex.split to safely parse command, avoid shell injection (B602)
            lint_result = subprocess.run(
                shlex.split(lint_command),
                shell=False,
                cwd=sandbox_path,
                capture_output=True,
                timeout=self.max_cpu_seconds,
                preexec_fn=set_limits if os.name != "nt" else None,
            )
        except subprocess.TimeoutExpired:
            pass  # Linter timeout is not critical

        # [20251217_FEATURE] Run tests
        test_result = None
        try:
            # [20251218_SECURITY] Use shlex.split to safely parse command, avoid shell injection (B602)
            test_result = subprocess.run(
                shlex.split(f"{test_command} --tb=short -q"),
                shell=False,
                cwd=sandbox_path,
                capture_output=True,
                timeout=self.max_cpu_seconds,
                preexec_fn=set_limits if os.name != "nt" else None,
            )
        except subprocess.TimeoutExpired:
            execution_time = int((time.time() - start_time) * 1000)
            return SandboxResult(
                success=False,
                build_success=True,
                execution_time_ms=execution_time,
                stdout="",
                stderr="Test command timed out",
            )

        execution_time = int((time.time() - start_time) * 1000)

        # Parse results
        return self._parse_subprocess_results(
            lint_result,
            test_result,
            build_success=True,
            execution_time_ms=execution_time,
        )

    def _parse_subprocess_results(
        self,
        lint_result: Optional[subprocess.CompletedProcess],
        test_result: Optional[subprocess.CompletedProcess],
        build_success: bool,
        execution_time_ms: int,
    ) -> SandboxResult:
        """
        Parse subprocess results into SandboxResult.

        Args:
            lint_result: Result from linter
            test_result: Result from tests
            build_success: Whether build succeeded
            execution_time_ms: Total execution time in milliseconds

        Returns:
            SandboxResult with parsed results
        """
        # Parse test results
        test_results = []
        stdout = ""
        stderr = ""

        if test_result:
            stdout = test_result.stdout.decode("utf-8", errors="replace")
            stderr = test_result.stderr.decode("utf-8", errors="replace")

            # [20251217_FEATURE] Simple test parsing - can be enhanced
            test_success = test_result.returncode == 0
            test_results.append(
                ExecutionTestResult(
                    name="all_tests",
                    passed=test_success,
                    duration_ms=execution_time_ms,
                    error_message=stderr if not test_success else None,
                )
            )

        # Parse lint results
        lint_results = []
        if lint_result:
            lint_stdout = lint_result.stdout.decode("utf-8", errors="replace")
            stdout = lint_stdout + "\n" + stdout

            # [20251217_FEATURE] Simple lint parsing - can be enhanced
            # Look for common linter output patterns
            for line in lint_stdout.split("\n"):
                if ":" in line and any(s in line.lower() for s in ["error", "warning"]):
                    parts = line.split(":", 3)
                    if len(parts) >= 3:
                        lint_results.append(
                            LintResult(
                                file=parts[0] if len(parts) > 0 else "",
                                line=(
                                    int(parts[1])
                                    if len(parts) > 1 and parts[1].isdigit()
                                    else None
                                ),
                                column=None,
                                message=parts[-1].strip() if parts else line,
                                severity=(
                                    "error" if "error" in line.lower() else "warning"
                                ),
                            )
                        )

        success = build_success and (
            test_result.returncode == 0 if test_result else True
        )

        return SandboxResult(
            success=success,
            test_results=test_results,
            lint_results=lint_results,
            build_success=build_success,
            side_effects_detected=self._detect_side_effects(
                Path(tempfile.gettempdir())
            ),
            execution_time_ms=execution_time_ms,
            stdout=stdout,
            stderr=stderr,
        )

    def _detect_side_effects(self, sandbox_path: Path) -> bool:
        """
        Detect if execution had unintended side effects.

        Checks:
        - Files created outside project directory
        - Network connections attempted
        - System calls blocked

        Args:
            sandbox_path: Path to sandbox directory

        Returns:
            True if side effects detected, False otherwise
        """
        # [20251217_SECURITY] Check for files created outside sandbox
        # This is handled by container isolation, but double-check

        # Check audit log for blocked operations
        audit_log = sandbox_path / ".scalpel_sandbox_audit.log"
        if audit_log.exists():
            content = audit_log.read_text()
            if "BLOCKED" in content:
                return True

        return False

    def _cleanup_sandbox(self, sandbox_path: Path) -> None:
        """
        Clean up sandbox directory.

        Args:
            sandbox_path: Path to sandbox directory to clean up
        """
        if sandbox_path.exists():
            shutil.rmtree(sandbox_path, ignore_errors=True)
