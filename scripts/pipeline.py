#!/usr/bin/env python3
"""
Code Scalpel CI/CD Pipeline Script

This script performs comprehensive validation and artifact generation for Jenkins CI/CD.
It wraps the pre-commit verification process and adds additional checks and artifact generation.

Checks performed:
- Black formatting
- Ruff linting
- Pyright type checking
- Pytest with coverage
- pip-audit security scanning
- Package build validation
- MCP contract validation
- Artifact generation for Jenkins

Usage:
    python scripts/pipeline.py [--generate-artifacts] [--skip-tests] [--verbose]
"""

import argparse
import json
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Tuple

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


class PipelineRunner:
    def __init__(self, verbose: bool = False, generate_artifacts: bool = True):
        self.verbose = verbose
        self.generate_artifacts = generate_artifacts
        self.project_root = Path(__file__).parent.parent
        self.artifacts_dir = self.project_root / "artifacts"
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "checks": {},
            "artifacts": {},
            "summary": {},
        }

    def log(self, message: str, level: str = "INFO"):
        """Log a message with timestamp and level."""
        if self.verbose or level in ["ERROR", "WARNING"]:
            timestamp = datetime.now().strftime("%H:%M:%S")
            print(f"[{timestamp}] {level}: {message}")

    def run_command(
        self,
        cmd: List[str],
        cwd: Optional[Path] = None,
        capture_output: bool = True,
        check: bool = True,
    ) -> Tuple[int, str, str]:
        """Run a command and return exit code, stdout, stderr."""
        try:
            self.log(f"Running: {' '.join(cmd)}")
            result = subprocess.run(
                cmd,
                cwd=cwd or self.project_root,
                capture_output=capture_output,
                text=True,
                check=False,
            )
            return result.returncode, result.stdout, result.stderr
        except Exception as e:
            self.log(f"Command failed: {e}", "ERROR")
            return 1, "", str(e)

    def check_black_formatting(self) -> bool:
        """Check Black code formatting."""
        self.log("Checking Black formatting...")
        exit_code, stdout, stderr = self.run_command(
            ["black", "--check", "--diff", "."]
        )

        if exit_code == 0:
            self.log("✅ Black formatting check passed")
            self.results["checks"]["black"] = {
                "status": "passed",
                "output": "All files properly formatted",
            }
            return True
        else:
            self.log("❌ Black formatting check failed", "ERROR")
            self.results["checks"]["black"] = {
                "status": "failed",
                "output": stdout + stderr,
            }
            return False

    def check_ruff_linting(self) -> bool:
        """Check Ruff linting."""
        self.log("Checking Ruff linting...")
        exit_code, stdout, stderr = self.run_command(["ruff", "check", "."])

        if exit_code == 0:
            self.log("✅ Ruff linting check passed")
            self.results["checks"]["ruff"] = {
                "status": "passed",
                "output": "No linting issues found",
            }
            return True
        else:
            self.log("❌ Ruff linting check failed", "ERROR")
            self.results["checks"]["ruff"] = {
                "status": "failed",
                "output": stdout + stderr,
            }
            return False

    def check_pyright_types(self) -> bool:
        """Check Pyright type checking."""
        self.log("Checking Pyright type checking...")
        exit_code, stdout, stderr = self.run_command(["pyright"])

        if exit_code == 0:
            self.log("✅ Pyright type check passed")
            self.results["checks"]["pyright"] = {
                "status": "passed",
                "output": "No type errors found",
            }
            return True
        else:
            self.log("❌ Pyright type check failed", "ERROR")
            self.results["checks"]["pyright"] = {
                "status": "failed",
                "output": stdout + stderr,
            }
            return False

    def run_pytest_coverage(self) -> bool:
        """Run pytest with coverage."""
        self.log("Running pytest with coverage...")
        exit_code, stdout, stderr = self.run_command(
            [
                "pytest",
                "--cov=code_scalpel",
                "--cov-report=term-missing",
                "--cov-report=xml:artifacts/coverage.xml",
                "--junitxml=artifacts/junit.xml",
                "-v",
            ]
        )

        if exit_code == 0:
            self.log("✅ Pytest coverage check passed")
            # Extract coverage percentage from output
            coverage_percent = "Unknown"
            for line in stdout.split("\n"):
                if "TOTAL" in line and "%" in line:
                    parts = line.split()
                    for part in parts:
                        if "%" in part:
                            coverage_percent = part
                            break
                    break

            self.results["checks"]["pytest"] = {
                "status": "passed",
                "output": f"Tests passed with {coverage_percent} coverage",
                "coverage": coverage_percent,
            }
            return True
        else:
            self.log("❌ Pytest coverage check failed", "ERROR")
            self.results["checks"]["pytest"] = {
                "status": "failed",
                "output": stdout + stderr,
            }
            return False

    def check_security_audit(self) -> bool:
        """Run pip-audit security scanning."""
        self.log("Running pip-audit security scan...")

        # Run pip-audit, ignoring known unfixable CVEs
        # CVE-2026-0994 in protobuf 6.33.4 - no fix yet, ignore it
        exit_code, stdout, stderr = self.run_command(
            ["pip-audit", "--format", "json", "--ignore-vuln", "CVE-2026-0994"]
        )

        if exit_code == 0:
            self.log("✅ Security audit passed")
            self.results["checks"]["security"] = {
                "status": "passed",
                "output": "No security vulnerabilities found (excluding known unfixable CVEs)",
            }
            return True
        else:
            # pip-audit found vulnerabilities that need fixing
            self.log(
                "❌ Security audit failed - fixable vulnerabilities found", "ERROR"
            )

            # Run without JSON format to show human-readable output
            _, text_output, _ = self.run_command(
                ["pip-audit", "--ignore-vuln", "CVE-2026-0994"]
            )

            self.results["checks"]["security"] = {
                "status": "failed",
                "output": text_output,
            }
            return False

    def validate_package_build(self) -> bool:
        """Validate package can be built."""
        self.log("Validating package build...")
        build_dir = self.project_root / "build"
        dist_dir = self.project_root / "dist"

        # Clean previous builds
        if build_dir.exists():
            shutil.rmtree(build_dir)
        if dist_dir.exists():
            shutil.rmtree(dist_dir)

        exit_code, stdout, stderr = self.run_command(["python", "-m", "build"])

        if exit_code == 0:
            self.log("✅ Package build validation passed")
            self.results["checks"]["build"] = {
                "status": "passed",
                "output": "Package built successfully",
            }
            return True
        else:
            self.log("❌ Package build validation failed", "ERROR")
            self.results["checks"]["build"] = {
                "status": "failed",
                "output": stdout + stderr,
            }
            return False

    def validate_mcp_contracts(self) -> bool:
        """Validate MCP contracts by checking the contract module can be imported."""
        self.log("Validating MCP contracts...")
        try:
            # Import the contract module (singular, not plural)
            from code_scalpel.mcp.contract import (
                ToolResponseEnvelope,
                make_envelope,
                envelop_tool_function,
            )

            # Basic validation - check that key components exist and are callable
            validations = [
                ("ToolResponseEnvelope", ToolResponseEnvelope is not None),
                ("make_envelope", callable(make_envelope)),
                ("envelop_tool_function", callable(envelop_tool_function)),
            ]

            failed = [name for name, valid in validations if not valid]
            if not failed:
                self.log("✅ MCP contract validation passed")
                self.results["checks"]["mcp_contracts"] = {
                    "status": "passed",
                    "output": "All MCP contract components available",
                }
                return True
            else:
                self.log("❌ MCP contract validation failed", "ERROR")
                self.results["checks"]["mcp_contracts"] = {
                    "status": "failed",
                    "output": f"Missing components: {failed}",
                }
                return False
        except ImportError as e:
            self.log(f"❌ MCP contract module not found: {e}", "ERROR")
            self.results["checks"]["mcp_contracts"] = {
                "status": "failed",
                "output": f"Contract module import failed: {e}",
            }
            return False
        except Exception as e:
            self.log(f"❌ MCP contract validation error: {e}", "ERROR")
            self.results["checks"]["mcp_contracts"] = {
                "status": "error",
                "output": str(e),
            }
            return False

    def _generate_artifacts(self):
        """Generate artifacts for Jenkins."""
        if not self.generate_artifacts:
            return

        self.log("Generating artifacts...")
        self.artifacts_dir.mkdir(exist_ok=True)

        # Generate pipeline results JSON
        results_file = self.artifacts_dir / "pipeline_results.json"
        with open(results_file, "w") as f:
            json.dump(self.results, f, indent=2)

        # Generate summary report
        summary_file = self.artifacts_dir / "pipeline_summary.md"
        with open(summary_file, "w") as f:
            f.write("# Code Scalpel CI/CD Pipeline Results\n\n")
            f.write(f"**Timestamp:** {self.results['timestamp']}\n\n")

            f.write("## Check Results\n\n")
            all_passed = True
            for check_name, check_result in self.results["checks"].items():
                status = check_result["status"]
                status_emoji = (
                    "✅"
                    if status == "passed"
                    else ("⚠️" if status == "warning" else "❌")
                )
                f.write(f"- {status_emoji} **{check_name}**: {status}\n")
                if status == "failed":
                    all_passed = False

            f.write("\n## Overall Status\n\n")
            if all_passed:
                f.write("🎉 **ALL CHECKS PASSED**\n")
            else:
                f.write("⚠️ **SOME CHECKS FAILED**\n")

        self.log(f"Artifacts generated in {self.artifacts_dir}")

    def run_pipeline(self, skip_tests: bool = False, skip_build: bool = False) -> bool:
        """Run the complete pipeline."""
        self.log("🚀 Starting Code Scalpel CI/CD Pipeline")

        checks = [
            ("Black Formatting", self.check_black_formatting),
            ("Ruff Linting", self.check_ruff_linting),
            ("Pyright Types", self.check_pyright_types),
            ("MCP Contracts", self.validate_mcp_contracts),
        ]

        if not skip_build:
            checks.append(("Package Build", self.validate_package_build))

        checks.append(("Security Audit", self.check_security_audit))

        if not skip_tests:
            checks.append(("Pytest Coverage", self.run_pytest_coverage))

        all_passed = True
        for check_name, check_func in checks:
            self.log(f"Running {check_name}...")
            if not check_func():
                all_passed = False

        # Generate artifacts regardless of success/failure
        if self.generate_artifacts:
            self._generate_artifacts()

        if all_passed:
            self.log("🎉 Pipeline completed successfully!")
            return True
        else:
            self.log("❌ Pipeline failed - check artifacts for details", "ERROR")
            return False


def main():
    parser = argparse.ArgumentParser(description="Code Scalpel CI/CD Pipeline")
    parser.add_argument(
        "--generate-artifacts",
        action="store_true",
        default=True,
        help="Generate artifacts for Jenkins",
    )
    parser.add_argument(
        "--skip-tests", action="store_true", default=False, help="Skip running pytest"
    )
    parser.add_argument(
        "--skip-build",
        action="store_true",
        default=False,
        help="Skip package build validation",
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true", default=False, help="Verbose output"
    )

    args = parser.parse_args()

    pipeline = PipelineRunner(
        verbose=args.verbose, generate_artifacts=args.generate_artifacts
    )
    success = pipeline.run_pipeline(
        skip_tests=args.skip_tests, skip_build=args.skip_build
    )

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
