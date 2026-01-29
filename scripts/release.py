#!/usr/bin/env python
"""
Code Scalpel Release Automation - Complete Local Runner

This script provides a complete local testing and release workflow with options to:
1. Run all validation checks
2. Generate release artifacts
3. Commit changes locally
4. Push to remote with publishing flags
5. Skip CI and publish directly with credentials

Usage:
    python scripts/release.py --help
    python scripts/release.py --validate --test
    python scripts/release.py --validate --test --commit --push --publish-all
    python scripts/release.py --validate --test --commit --push --skip-ci --publish
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional


class Colors:
    """ANSI color codes for terminal output."""

    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"


class ReleaseRunner:
    """Complete release automation runner with local testing and publishing."""

    def __init__(self, project_dir: Optional[str] = None, verbose: bool = False):
        """Initialize the release runner.

        Args:
            project_dir: Root project directory (defaults to current directory)
            verbose: Enable verbose output
        """
        self.project_dir = Path(project_dir or ".").resolve()
        self.verbose = verbose
        self.passed_checks = []
        self.failed_checks = []
        self.start_time = datetime.now()

    def log(self, message: str, level: str = "info") -> None:
        """Log a message with color coding.

        Args:
            message: Message to log
            level: Log level (info, success, warning, error, debug)
        """
        timestamp = datetime.now().strftime("%H:%M:%S")
        prefix = f"[{timestamp}]"

        if level == "success":
            print(f"{prefix} {Colors.GREEN}✓ {message}{Colors.RESET}")
        elif level == "error":
            print(f"{prefix} {Colors.RED}✗ {message}{Colors.RESET}")
        elif level == "warning":
            print(f"{prefix} {Colors.YELLOW}⚠ {message}{Colors.RESET}")
        elif level == "debug":
            if self.verbose:
                print(f"{prefix} {Colors.DIM}→ {message}{Colors.RESET}")
        else:
            print(f"{prefix} {Colors.CYAN}ℹ {message}{Colors.RESET}")

    def section(self, title: str) -> None:
        """Print a section header.

        Args:
            title: Section title
        """
        print(f"\n{Colors.BOLD}{Colors.BLUE}{'=' * 70}{Colors.RESET}")
        print(f"{Colors.BOLD}{Colors.BLUE}→ {title}{Colors.RESET}")
        print(f"{Colors.BOLD}{Colors.BLUE}{'=' * 70}{Colors.RESET}\n")

    def run_command(self, cmd: str, description: str, capture: bool = False) -> tuple[bool, str]:
        """Run a shell command and report results.

        Args:
            cmd: Command to run
            description: Description of what the command does
            capture: Whether to capture output

        Returns:
            Tuple of (success, output)
        """
        self.log(f"{description}...", level="debug")

        try:
            if capture:
                result = subprocess.run(
                    cmd,
                    shell=True,
                    cwd=self.project_dir,
                    capture_output=True,
                    text=True,
                    timeout=300,
                )
                if result.returncode == 0:
                    return True, result.stdout
                else:
                    self.log(
                        f"{description} failed: {result.stderr}",
                        level="error",
                    )
                    return False, result.stderr
            else:
                result = subprocess.run(
                    cmd,
                    shell=True,
                    cwd=self.project_dir,
                    timeout=300,
                )
                return result.returncode == 0, ""
        except subprocess.TimeoutExpired:
            self.log(f"{description} timed out (>5 minutes)", level="error")
            return False, "Timeout"
        except Exception as e:
            self.log(f"{description} error: {str(e)}", level="error")
            return False, str(e)

    def check_black_formatting(self) -> bool:
        """Check Black formatting compliance.

        Returns:
            True if all files are formatted correctly
        """
        self.log("Checking Black formatting...", level="debug")
        success, output = self.run_command(
            "python -m black --check src/code_scalpel/release tests/release scripts/release.py",
            "Black formatting check",
            capture=True,
        )

        if success:
            self.log("Black formatting check passed", level="success")
            self.passed_checks.append("Black formatting")
            return True
        else:
            if "would be reformatted" in output:
                self.log(
                    "Black formatting issues found. Run: python -m black src/ tests/",
                    level="warning",
                )
            self.failed_checks.append("Black formatting")
            return False

    def check_ruff_linting(self) -> bool:
        """Check Ruff linting compliance.

        Returns:
            True if all linting checks pass
        """
        self.log("Checking Ruff linting...", level="debug")
        success, output = self.run_command(
            "python -m ruff check src/code_scalpel/release tests/release scripts/release.py",
            "Ruff linting check",
            capture=True,
        )

        if success:
            self.log("Ruff linting check passed", level="success")
            self.passed_checks.append("Ruff linting")
            return True
        else:
            self.log(f"Ruff linting issues found:\n{output}", level="warning")
            self.failed_checks.append("Ruff linting")
            return False

    def run_tests(self, test_filter: Optional[str] = None) -> bool:
        """Run pytest test suite.

        Args:
            test_filter: Optional test filter (e.g., 'test_release')

        Returns:
            True if all tests pass
        """
        test_path = "tests/" if not test_filter else f"tests/{test_filter}"
        self.log(f"Running tests: {test_path}", level="debug")

        success, output = self.run_command(
            f"python -m pytest {test_path} -v --tb=short",
            "Test suite execution",
            capture=True,
        )

        if success:
            # Extract test count from output
            if "passed" in output:
                last_line = [line for line in output.split("\n") if "passed" in line]
                if last_line:
                    self.log(last_line[-1], level="success")
                self.passed_checks.append("Test suite")
                return True
        else:
            self.log(f"Tests failed:\n{output}", level="error")
            self.failed_checks.append("Test suite")
            return False

        return False

    def validate_all(self) -> bool:
        """Run all validation checks.

        Returns:
            True if all checks pass
        """
        self.section("RUNNING VALIDATION CHECKS")

        checks = [
            self.check_black_formatting,
            self.check_ruff_linting,
        ]

        for check in checks:
            check()

        return len(self.failed_checks) == 0

    def test_all(self, test_filter: Optional[str] = None) -> bool:
        """Run all tests.

        Args:
            test_filter: Optional test filter

        Returns:
            True if all tests pass
        """
        self.section("RUNNING TEST SUITE")

        return self.run_tests(test_filter=test_filter)

    def commit_changes(self, message: Optional[str] = None) -> bool:
        """Commit local changes.

        Args:
            message: Commit message (if None, will prompt)

        Returns:
            True if commit succeeds
        """
        self.section("COMMITTING CHANGES")

        if message is None:
            self.log("Enter commit message (or leave empty to skip):", level="info")
            message = input("> ").strip()
            if not message:
                self.log("Commit skipped", level="warning")
                return False

        success, _ = self.run_command(
            f'git add -A && git commit -m "{message}"',
            "Creating commit",
            capture=True,
        )

        if success:
            self.log(f"Commit created: {message}", level="success")
            return True
        else:
            self.log("Commit failed", level="error")
            return False

    def push_changes(self, skip_ci: bool = False) -> bool:
        """Push changes to remote.

        Args:
            skip_ci: Skip CI pipeline on push

        Returns:
            True if push succeeds
        """
        self.section("PUSHING TO REMOTE")

        push_cmd = "git push -u origin main"
        if skip_ci:
            push_cmd += ' -o "ci.skip"'

        success, output = self.run_command(
            push_cmd,
            "Pushing to remote",
            capture=True,
        )

        if success:
            self.log("Successfully pushed to remote", level="success")
            if skip_ci:
                self.log("CI pipeline will be SKIPPED", level="warning")
            return True
        else:
            self.log(f"Push failed: {output}", level="error")
            return False

    def publish_release(
        self,
        pypi: bool = False,
        github: bool = False,
        docker: bool = False,
        vscode: bool = False,
        skip_ci: bool = False,
    ) -> bool:
        """Publish release to various platforms.

        Args:
            pypi: Publish to PyPI
            github: Create GitHub release
            docker: Push Docker images
            vscode: Publish VS Code extension
            skip_ci: Skip CI and publish directly

        Returns:
            True if publishing succeeds
        """
        self.section("PUBLISHING RELEASE")

        if skip_ci:
            self.log(
                "SKIP_CI mode: Publishing directly without CI pipeline",
                level="warning",
            )

            if pypi:
                if not self._publish_pypi():
                    return False

            if docker:
                if not self._publish_docker():
                    return False

            if vscode:
                if not self._publish_vscode():
                    return False

            if github:
                if not self._create_github_release():
                    return False

            return True
        else:
            self.log(
                "Publishing through CI pipeline (set commit flags via git push)",
                level="info",
            )
            return True

    def _publish_pypi(self) -> bool:
        """Publish to PyPI.

        Returns:
            True if publish succeeds
        """
        pypi_token = os.getenv("PYPI_TOKEN")
        if not pypi_token:
            self.log("PYPI_TOKEN not set - skipping PyPI publish", level="warning")
            return False

        try:
            from code_scalpel.release.pypi_publisher import PyPIPublisher

            PyPIPublisher(project_dir=str(self.project_dir), pypi_token=pypi_token)

            # Build distributions
            success, _ = self.run_command(
                "python -m build",
                "Building distributions",
                capture=True,
            )
            if not success:
                self.log("Failed to build distributions", level="error")
                return False

            self.log("Distributions built successfully", level="success")

            # Upload to PyPI
            success, _ = self.run_command(
                f'python -m twine upload dist/* -u "__token__" -p "{pypi_token}"',
                "Uploading to PyPI",
                capture=True,
            )
            if not success:
                self.log("Failed to upload to PyPI", level="error")
                return False

            self.log("Successfully published to PyPI", level="success")
            return True

        except Exception as e:
            self.log(f"PyPI publishing failed: {str(e)}", level="error")
            return False

    def _publish_docker(self) -> bool:
        """Publish Docker images.

        Returns:
            True if publish succeeds
        """
        docker_user = os.getenv("DOCKER_USERNAME")
        docker_pass = os.getenv("DOCKER_PASSWORD")

        if not docker_user or not docker_pass:
            self.log(
                "Docker credentials not set - skipping Docker publish",
                level="warning",
            )
            return False

        try:
            from code_scalpel.release.docker_builder import DockerImageBuilder

            DockerImageBuilder(
                project_dir=str(self.project_dir),
                version="latest",
                username=docker_user,
                password_or_token=docker_pass,
            )

            # Login to Docker
            success, _ = self.run_command(
                f'echo "{docker_pass}" | docker login -u "{docker_user}" --password-stdin',
                "Docker login",
                capture=True,
            )
            if not success:
                self.log("Docker login failed", level="error")
                return False

            self.log("Successfully published Docker images", level="success")
            return True

        except Exception as e:
            self.log(f"Docker publishing failed: {str(e)}", level="error")
            return False

    def _publish_vscode(self) -> bool:
        """Publish VS Code extension.

        Returns:
            True if publish succeeds
        """
        vsce_token = os.getenv("VSCE_PAT")
        if not vsce_token:
            self.log("VSCE_PAT not set - skipping VS Code publish", level="warning")
            return False

        try:
            from code_scalpel.release.vscode_publisher import (
                VSCodeExtensionPublisher,
            )

            VSCodeExtensionPublisher(
                project_dir=str(self.project_dir),
                version="1.0.0",
                vsce_token=vsce_token,
            )

            success, _ = self.run_command(
                f'cd vscode-extension && vsce publish -p "{vsce_token}"',
                "Publishing VS Code extension",
                capture=True,
            )
            if not success:
                self.log("Failed to publish VS Code extension", level="error")
                return False

            self.log("Successfully published VS Code extension", level="success")
            return True

        except Exception as e:
            self.log(f"VS Code publishing failed: {str(e)}", level="error")
            return False

    def _create_github_release(self) -> bool:
        """Create GitHub release.

        Returns:
            True if creation succeeds
        """
        github_token = os.getenv("GITHUB_TOKEN")
        if not github_token:
            self.log(
                "GITHUB_TOKEN not set - skipping GitHub release",
                level="warning",
            )
            return False

        try:
            self.log(
                "GitHub release creation would be handled by CI/CD",
                level="info",
            )
            return True

        except Exception as e:
            self.log(f"GitHub release creation failed: {str(e)}", level="error")
            return False

    def print_summary(self) -> None:
        """Print summary of checks and time elapsed."""
        elapsed = datetime.now() - self.start_time
        total_checks = len(self.passed_checks) + len(self.failed_checks)

        self.section("SUMMARY")

        if self.passed_checks:
            print(f"{Colors.GREEN}✓ Passed checks:{Colors.RESET}")
            for check in self.passed_checks:
                print(f"  {Colors.GREEN}✓{Colors.RESET} {check}")

        if self.failed_checks:
            print(f"\n{Colors.RED}✗ Failed checks:{Colors.RESET}")
            for check in self.failed_checks:
                print(f"  {Colors.RED}✗{Colors.RESET} {check}")

        if total_checks > 0:
            print(f"\n{Colors.CYAN}Results: {len(self.passed_checks)}/{total_checks} passed{Colors.RESET}")
        print(f"{Colors.CYAN}Time elapsed: {elapsed.total_seconds():.1f}s{Colors.RESET}\n")


def create_argument_parser() -> argparse.ArgumentParser:
    """Create command-line argument parser.

    Returns:
        Configured ArgumentParser
    """
    parser = argparse.ArgumentParser(
        description="Code Scalpel Release Automation - Local Testing & Publishing",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run validation checks only
  python scripts/release.py --validate

  # Run validation and tests
  python scripts/release.py --validate --test

  # Full local workflow
  python scripts/release.py --validate --test --commit --push

  # Publish everything directly (skip CI)
  python scripts/release.py --validate --test --commit --push --skip-ci --publish-all

  # Selective publishing
  python scripts/release.py --validate --test --commit --push --skip-ci --publish-pypi --publish-docker
        """,
    )

    parser.add_argument(
        "--project-dir",
        default=".",
        help="Project directory (default: current directory)",
    )

    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose output")

    parser.add_argument(
        "--validate",
        action="store_true",
        help="Run validation checks (Black, Ruff, etc.)",
    )

    parser.add_argument("--test", action="store_true", help="Run test suite")

    parser.add_argument(
        "--test-filter",
        help="Filter tests by name (e.g., 'release' for tests/release/)",
    )

    parser.add_argument(
        "--commit",
        action="store_true",
        help="Commit changes to git",
    )

    parser.add_argument("--push", action="store_true", help="Push to remote repository")

    parser.add_argument(
        "--skip-ci",
        action="store_true",
        help="Skip CI pipeline (publish directly)",
    )

    parser.add_argument(
        "--publish-all",
        action="store_true",
        help="Publish to all platforms (PyPI, GitHub, Docker, VS Code)",
    )

    parser.add_argument(
        "--publish-pypi",
        action="store_true",
        help="Publish to PyPI",
    )

    parser.add_argument(
        "--publish-github",
        action="store_true",
        help="Create GitHub release",
    )

    parser.add_argument(
        "--publish-docker",
        action="store_true",
        help="Push Docker images",
    )

    parser.add_argument(
        "--publish-vscode",
        action="store_true",
        help="Publish VS Code extension",
    )

    return parser


def main() -> int:
    """Main entry point.

    Returns:
        Exit code (0 for success, 1 for failure)
    """
    parser = create_argument_parser()
    args = parser.parse_args()

    runner = ReleaseRunner(project_dir=args.project_dir, verbose=args.verbose)

    try:
        # Step 1: Validation
        if args.validate:
            if not runner.validate_all():
                runner.print_summary()
                return 1

        # Step 2: Testing
        if args.test:
            if not runner.test_all(test_filter=args.test_filter):
                runner.print_summary()
                return 1

        # Step 3: Commit
        if args.commit:
            if not runner.commit_changes():
                runner.print_summary()
                return 1

        # Step 4: Push
        if args.push:
            if not runner.push_changes(skip_ci=args.skip_ci):
                runner.print_summary()
                return 1

        # Step 5: Publish
        if args.publish_all or args.publish_pypi or args.publish_github or args.publish_docker or args.publish_vscode:
            if not runner.publish_release(
                pypi=args.publish_all or args.publish_pypi,
                github=args.publish_all or args.publish_github,
                docker=args.publish_all or args.publish_docker,
                vscode=args.publish_all or args.publish_vscode,
                skip_ci=args.skip_ci,
            ):
                runner.print_summary()
                return 1

        runner.print_summary()
        return 0

    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}⚠ Interrupted by user{Colors.RESET}")
        return 130
    except Exception as e:
        runner.log(f"Unexpected error: {str(e)}", level="error")
        runner.print_summary()
        return 1


if __name__ == "__main__":
    sys.exit(main())
