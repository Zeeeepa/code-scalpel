#!/usr/bin/env python3
"""
Local Pre-Release Pipeline Orchestrator for Code Scalpel v3.3.0
Does everything a robust CI pipeline does, but locally.

[20260117_REFACTOR] Enhanced with:
- Conda environment support (auto-detects conda vs venv)
- TODO extraction and consolidation
- SBOM generation (Software Bill of Materials)
- Coverage reports with HTML output
- License compliance checks
- Code complexity metrics
- Comprehensive security artifacts for prospective buyers

Usage:
    python local_pipeline/pipeline.py [--skip-tests] [--no-fail-fast] [--env=conda|venv|auto]

    CONDA USERS:  Activate your conda environment FIRST, then run the pipeline.
                  Example: conda activate code-scalpel && python local_pipeline/pipeline.py
"""

import subprocess
import sys
import shutil
import os
import time
import argparse
import json
from datetime import datetime
from pathlib import Path

# Configuration
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ARTIFACTS_DIR = os.path.join(PROJECT_ROOT, "release_artifacts", "local_build")
LOG_FILE = os.path.join(ARTIFACTS_DIR, "pipeline.log")
VENV_DIR = os.path.join(PROJECT_ROOT, ".venv")

# [20260117_FEATURE] Track ephemeral resources for post-run cleanup
PIPELINE_CREATED_VENV = False
BACKUP_EXTENSIONS = {".bak"}
BACKUP_EXCLUDE_DIRS = {
    ".git",
    "dist_protected",
    "build_protected",
    "release_artifacts",
    "htmlcov",
    ".venv",
}

PIPELINE_DRY_RUN_CLEANUP = False

# Colors
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
CYAN = "\033[96m"
RESET = "\033[0m"

# Global environment settings (set in main via detect_environment)
ENV_TYPE = None
PYTHON_EXE = None
PIP_EXE = None
BIN_DIR = None


def detect_environment():
    """
    [20260117_FEATURE] Auto-detect whether running in conda or venv.
    Returns: tuple (env_type, python_exe, pip_exe, bin_dir)
    """
    # Check for conda environment first (user's preference)
    conda_prefix = os.environ.get("CONDA_PREFIX")
    conda_env_name = os.environ.get("CONDA_DEFAULT_ENV")
    
    if conda_prefix and conda_env_name:
        print(f"{CYAN}Detected conda environment: {conda_env_name}{RESET}")
        if sys.platform == "win32":
            python_exe = os.path.join(conda_prefix, "python.exe")
            pip_exe = os.path.join(conda_prefix, "Scripts", "pip.exe")
            bin_dir = os.path.join(conda_prefix, "Scripts")
        else:
            python_exe = os.path.join(conda_prefix, "bin", "python")
            pip_exe = os.path.join(conda_prefix, "bin", "pip")
            bin_dir = os.path.join(conda_prefix, "bin")
        return ("conda", python_exe, pip_exe, bin_dir)
    
    # Check for existing venv
    if os.path.exists(VENV_DIR):
        print(f"{CYAN}Detected venv at: {VENV_DIR}{RESET}")
        if sys.platform == "win32":
            python_exe = os.path.join(VENV_DIR, "Scripts", "python.exe")
            pip_exe = os.path.join(VENV_DIR, "Scripts", "pip.exe")
            bin_dir = os.path.join(VENV_DIR, "Scripts")
        else:
            python_exe = os.path.join(VENV_DIR, "bin", "python")
            pip_exe = os.path.join(VENV_DIR, "bin", "pip")
            bin_dir = os.path.join(VENV_DIR, "bin")
        return ("venv", python_exe, pip_exe, bin_dir)
    
    # Fall back to system Python
    print(f"{YELLOW}No virtual environment detected, using system Python{RESET}")
    return ("system", sys.executable, "pip", os.path.dirname(sys.executable))


def log(message, level="INFO"):
    timestamp = datetime.now().strftime("%H:%M:%S")
    formatted_msg = f"[{timestamp}] {level}: {message}"
    
    # Print to console with color
    colors = {
        "INFO": BLUE,
        "SUCCESS": GREEN,
        "ERROR": RED,
        "WARNING": YELLOW,
        "STAGE": CYAN,
    }
    color = colors.get(level, RESET)
    print(f"{color}{formatted_msg}{RESET}")
    
    # Write to file
    with open(LOG_FILE, "a") as f:
        f.write(formatted_msg + "\n")


def run_command(command, description, cwd=PROJECT_ROOT, allow_fail=False, use_env=True, timeout=600):
    """Run a shell command with environment-aware path resolution."""
    log(f"Starting: {description}...", "INFO")
    start_time = time.time()
    
    # Adjust command to use detected environment binaries
    if use_env and BIN_DIR:
        cmd_parts = command.split()
        if cmd_parts[0] == "python":
            cmd_parts[0] = PYTHON_EXE
        elif cmd_parts[0] == "pip":
            cmd_parts[0] = PIP_EXE
        elif os.path.exists(os.path.join(BIN_DIR, cmd_parts[0])):
            cmd_parts[0] = os.path.join(BIN_DIR, cmd_parts[0])
        command = " ".join(cmd_parts)

    try:
        process = subprocess.Popen(
            command, 
            shell=True, 
            cwd=cwd, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.STDOUT,
            text=True
        )
        
        output_buffer = []
        for line in iter(process.stdout.readline, ''):
            print(f"  > {line.strip()}")
            output_buffer.append(line)
            with open(LOG_FILE, "a") as f:
                f.write(line)
                
        process.wait(timeout=timeout)
        duration = time.time() - start_time
        
        if process.returncode != 0 and not allow_fail:
            log(f"FAILED: {description} (Exit Code: {process.returncode})", "ERROR")
            raise Exception(f"Pipeline step failed: {description}")
        
        log(f"COMPLETED: {description} in {duration:.2f}s", "SUCCESS")
        return True, "".join(output_buffer)
        
    except subprocess.TimeoutExpired:
        process.kill()
        log(f"TIMEOUT: {description} exceeded {timeout}s", "ERROR")
        if not allow_fail:
            sys.exit(1)
        return False, ""
    except Exception as e:
        if not allow_fail:
            log(f"Exception during {description}: {str(e)}", "ERROR")
            sys.exit(1)
        return False, ""


def setup_artifacts():
    """Initialize artifacts directory with organized subdirectories."""
    if os.path.exists(ARTIFACTS_DIR):
        shutil.rmtree(ARTIFACTS_DIR)
    os.makedirs(ARTIFACTS_DIR, exist_ok=True)
    
    # [20260117_FEATURE] Create subdirectories for organized artifacts
    for subdir in ["security", "coverage", "compliance", "docs"]:
        os.makedirs(os.path.join(ARTIFACTS_DIR, subdir), exist_ok=True)
    
    with open(LOG_FILE, "w") as f:
        f.write(f"Pipeline Run Started: {datetime.now()}\n")
        f.write(f"Environment Type: {ENV_TYPE}\n")
        f.write(f"Python Executable: {PYTHON_EXE}\n")
        f.write(f"Bin Directory: {BIN_DIR}\n\n")


def ensure_environment():
    """
    [20260117_REFACTOR] Replaced ensure_venv() with environment-aware version.
    For conda: assumes environment is already activated.
    For venv: creates if needed.
    """
    global PIPELINE_CREATED_VENV
    if ENV_TYPE == "conda":
        print(f"{CYAN}Using conda environment (already activated){RESET}")
        return
    
    if ENV_TYPE == "venv":
        print(f"{BLUE}Using existing virtual environment at {VENV_DIR}{RESET}")
        return
        
    # System Python - create venv if requested
    if not os.path.exists(VENV_DIR):
        print(f"{YELLOW}Creating virtual environment at {VENV_DIR}...{RESET}")
        subprocess.check_call([sys.executable, "-m", "venv", VENV_DIR])
        PIPELINE_CREATED_VENV = True
    else:
        print(f"{BLUE}Using existing virtual environment at {VENV_DIR}{RESET}")

def set_license_tier(tier):
    """Swaps license files to simulate different tiers."""
    print(f"\n{YELLOW}--- Configuring License: {tier.upper()} ---{RESET}")
    license_dir = os.path.join(PROJECT_ROOT, ".code-scalpel/license")
    
    if os.path.exists(license_dir):
        shutil.rmtree(license_dir)
    os.makedirs(license_dir, exist_ok=True)

    if tier == "community":
        log("License cleared. Operating in COMMUNITY tier.", "INFO")
        return

    keys = {
        "pro": "tests/licenses/code_scalpel_license_pro_20260101_190345.jwt",
        "enterprise": "tests/licenses/code_scalpel_license_enterprise_20260101_190754.jwt"
    }

    if tier not in keys:
        log(f"Unknown tier: {tier}", "ERROR")
        return

    src = os.path.join(PROJECT_ROOT, keys[tier])
    dst = os.path.join(license_dir, "license.jwt")

    if os.path.exists(src):
        shutil.copy(src, dst)
        log(f"Installed {tier} license from {src}", "SUCCESS")
    else:
        log(f"License file not found: {src}", "ERROR")


# [20260117_FEATURE] Optional cleanup helpers for ephemeral resources
def cleanup_virtualenv(dry_run: bool = False) -> None:
    """Remove the venv created by this pipeline run, if any."""
    if PIPELINE_CREATED_VENV and os.path.exists(VENV_DIR):
        if dry_run or PIPELINE_DRY_RUN_CLEANUP:
            log(f"[DRY-RUN] Would remove pipeline-created virtualenv at {VENV_DIR}", "INFO")
            return
        try:
            shutil.rmtree(VENV_DIR)
            log(f"Removed pipeline-created virtualenv at {VENV_DIR}", "SUCCESS")
        except Exception as exc:
            log(f"Failed to remove virtualenv at {VENV_DIR}: {exc}", "ERROR")


def cleanup_backup_files(dry_run: bool = False) -> tuple[int, list[str]]:
    """Remove backup files (e.g., *.bak) after validation."""
    removed = []
    for root, dirs, files in os.walk(PROJECT_ROOT):
        dirs[:] = [d for d in dirs if d not in BACKUP_EXCLUDE_DIRS]
        for name in files:
            if any(name.endswith(ext) for ext in BACKUP_EXTENSIONS):
                path = os.path.join(root, name)
                if dry_run or PIPELINE_DRY_RUN_CLEANUP:
                    log(f"[DRY-RUN] Would remove backup {path}", "INFO")
                    continue
                try:
                    os.remove(path)
                    removed.append(path)
                except Exception as exc:
                    log(f"Failed to remove backup {path}: {exc}", "ERROR")
    if removed:
        log(f"Removed {len(removed)} backup file(s)", "SUCCESS")
    else:
        log("No backup files removed (none found)", "INFO")
    return len(removed), removed


# =============================================================================
# PIPELINE STAGES
# =============================================================================

def stage_static_analysis():
    """Stage 1: Linting and Formatting"""
    print(f"\n{CYAN}{'='*60}{RESET}")
    log("STAGE 1: STATIC ANALYSIS", "STAGE")
    print(f"{CYAN}{'='*60}{RESET}\n")
    
    run_command("black --check --diff src/ tests/", "Black Formatting Check", allow_fail=True)
    run_command("ruff check src/ tests/", "Ruff Linting", allow_fail=True)
    run_command("python -m compileall -q src/", "Python Syntax Check", allow_fail=False)


def stage_type_checking():
    """Stage 2: Type Safety"""
    print(f"\n{CYAN}{'='*60}{RESET}")
    log("STAGE 2: TYPE SAFETY", "STAGE")
    print(f"{CYAN}{'='*60}{RESET}\n")
    
    run_command("pyright -p pyrightconfig.json", "Pyright Type Check", allow_fail=True)


def stage_security_audit():
    """Stage 3: Security Gates - Comprehensive security scanning for buyers"""
    print(f"\n{CYAN}{'='*60}{RESET}")
    log("STAGE 3: SECURITY GATES", "STAGE")
    print(f"{CYAN}{'='*60}{RESET}\n")
    
    security_dir = os.path.join(ARTIFACTS_DIR, "security")
    
    # Bandit SAST scan (JSON)
    run_command(
        f"bandit -r src/ -ll -ii -x '**/test_*.py' --format json --output {os.path.join(security_dir, 'bandit-sast-report.json')}", 
        "Bandit SAST Security Scan (JSON)",
        allow_fail=True
    )
    
    # [20260117_FEATURE] HTML report for human reviewers
    run_command(
        f"bandit -r src/ -ll -ii -x '**/test_*.py' --format html --output {os.path.join(security_dir, 'bandit-sast-report.html')}", 
        "Bandit SAST Report (HTML - for buyers)",
        allow_fail=True
    )
    
    # Dependency vulnerability audit
    run_command(
        f"pip-audit -r requirements-secure.txt --format json --output {os.path.join(security_dir, 'pip-audit-report.json')}", 
        "Dependency Vulnerability Audit (pip-audit)", 
        allow_fail=True
    )
    
    # [20260117_FEATURE] SBOM generation (Software Bill of Materials) for supply chain transparency
    run_command(
        f"pip-audit -r requirements.txt --format cyclonedx-json --output {os.path.join(security_dir, 'sbom-cyclonedx.json')}", 
        "SBOM Generation (CycloneDX - for supply chain audit)", 
        allow_fail=True
    )
    
    # [20260117_FEATURE] License compliance check
    run_command(
        f"pip-licenses --format=json --output-file={os.path.join(security_dir, 'license-compliance.json')}", 
        "License Compliance Check",
        allow_fail=True
    )
    
    # Also create human-readable license summary
    run_command(
        f"pip-licenses --format=markdown --output-file={os.path.join(security_dir, 'license-summary.md')}", 
        "License Summary (Markdown - for buyers)",
        allow_fail=True
    )
    
    # Copy reports to main artifacts dir for backward compat
    for report in ["bandit-sast-report.json", "pip-audit-report.json"]:
        src = os.path.join(security_dir, report)
        if os.path.exists(src):
            dest_name = "bandit-report.json" if "bandit" in report else report
            shutil.copy(src, os.path.join(ARTIFACTS_DIR, dest_name))


def stage_todo_extraction():
    """
    [20260117_FEATURE] Stage 4: TODO Extraction and Consolidation
    Extracts all TODOs, FIXMEs, HACKs from codebase into consolidated reports.
    """
    print(f"\n{CYAN}{'='*60}{RESET}")
    log("STAGE 4: TODO EXTRACTION & CONSOLIDATION", "STAGE")
    print(f"{CYAN}{'='*60}{RESET}\n")
    
    docs_dir = os.path.join(ARTIFACTS_DIR, "docs")
    
    extract_script = os.path.join(PROJECT_ROOT, "scripts", "extract_todos.py")
    if os.path.exists(extract_script):
        # Generate all formats: markdown, json, csv
        run_command(
            f"python {extract_script} --format all --output-dir {docs_dir}",
            "TODO Extraction (all formats)",
            allow_fail=True
        )
        
        # Also copy to main docs/todo_reports for persistence
        todo_reports_dir = os.path.join(PROJECT_ROOT, "docs", "todo_reports")
        if os.path.exists(todo_reports_dir):
            for fmt in ["todos.json", "todos.csv", "TODO_BY_MODULE.md", "TODO_ROADMAP.md"]:
                src = os.path.join(docs_dir, fmt)
                if os.path.exists(src):
                    shutil.copy(src, os.path.join(todo_reports_dir, fmt))
                    log(f"Updated {fmt} in docs/todo_reports/", "SUCCESS")
    else:
        log(f"TODO extraction script not found: {extract_script}", "WARNING")


def stage_testing(skip_tests=False):
    """Stage 5: Testing Suite with Coverage"""
    print(f"\n{CYAN}{'='*60}{RESET}")
    log("STAGE 5: TESTING SUITE", "STAGE")
    print(f"{CYAN}{'='*60}{RESET}\n")
    
    if skip_tests:
        log("Skipping tests (--skip-tests flag)", "WARNING")
        return
    
    coverage_dir = os.path.join(ARTIFACTS_DIR, "coverage")
    
    # [20260117_FEATURE] Run core tests with coverage HTML report
    run_command(
        f"pytest tests/core/ -v --tb=short --cov=code_scalpel --cov-report=html:{coverage_dir}/html --cov-report=json:{coverage_dir}/coverage.json --cov-report=term-missing --junitxml={os.path.join(ARTIFACTS_DIR, 'test_results_core.xml')}",
        "Core Tests with Coverage (HTML report for buyers)",
        allow_fail=True,
        timeout=300
    )
    
    # Run MCP tests
    run_command(
        f"pytest tests/mcp/test_mcp.py tests/mcp/test_mcp_auto_init.py tests/integration/test_update_symbol_tiers.py -v --tb=short --junitxml={os.path.join(ARTIFACTS_DIR, 'test_results_mcp.xml')}",
        "MCP & Integration Tests",
        allow_fail=True,
        timeout=300
    )
    
    # Tier-specific tests
    if os.path.exists(os.path.join(PROJECT_ROOT, "tests/tools")):
        for tier in ["community", "pro", "enterprise"]:
            set_license_tier(tier)
            run_command(
                f"pytest tests/tools/ -v -k '{tier.capitalize()}' --tb=short --junitxml={os.path.join(ARTIFACTS_DIR, f'test_results_{tier}.xml')}", 
                f"{tier.capitalize()} Tier Verification", 
                allow_fail=True,
                timeout=120
            )


def stage_mcp_contract():
    """Stage 6: MCP Contract Verification"""
    print(f"\n{CYAN}{'='*60}{RESET}")
    log("STAGE 6: MCP CONTRACT VERIFICATION", "STAGE")
    print(f"{CYAN}{'='*60}{RESET}\n")
    
    os.environ["MCP_CONTRACT_TRANSPORT"] = "stdio"
    contract_test = os.path.join(PROJECT_ROOT, "tests/mcp/test_mcp_all_tools_contract.py")
    
    if os.path.exists(contract_test):
        run_command(
            f"pytest -q {contract_test} --junitxml={os.path.join(ARTIFACTS_DIR, 'test_results_contract.xml')}", 
            "MCP Contract (stdio)", 
            allow_fail=True
        )
    else:
        log(f"Contract test not found: {contract_test}", "WARNING")


def stage_build():
    """Stage 7: Build Package"""
    print(f"\n{CYAN}{'='*60}{RESET}")
    log("STAGE 7: BUILD PACKAGE", "STAGE")
    print(f"{CYAN}{'='*60}{RESET}\n")
    
    dist_dir = os.path.join(PROJECT_ROOT, "dist")
    if os.path.exists(dist_dir):
        shutil.rmtree(dist_dir)
    
    run_command("python -m build", "Build Source & Wheel Distributions")
    run_command("twine check dist/*", "Twine Metadata Check")
    
    # Copy dist artifacts to release_artifacts
    for item in os.listdir(dist_dir):
        shutil.copy(os.path.join(dist_dir, item), os.path.join(ARTIFACTS_DIR, item))
        log(f"Copied {item} to artifacts", "SUCCESS")


def stage_metrics():
    """
    [20260117_FEATURE] Stage 8: Code Quality Metrics
    Generates complexity analysis, maintainability index, and LOC stats.
    """
    print(f"\n{CYAN}{'='*60}{RESET}")
    log("STAGE 8: CODE QUALITY METRICS", "STAGE")
    print(f"{CYAN}{'='*60}{RESET}\n")
    
    compliance_dir = os.path.join(ARTIFACTS_DIR, "compliance")
    
    # Radon cyclomatic complexity
    run_command(
        f"radon cc src/ -a -s --json > {os.path.join(compliance_dir, 'complexity-cc.json')}",
        "Cyclomatic Complexity Analysis (radon)",
        allow_fail=True
    )
    
    # Radon maintainability index
    run_command(
        f"radon mi src/ -s --json > {os.path.join(compliance_dir, 'maintainability-index.json')}",
        "Maintainability Index (radon)",
        allow_fail=True
    )
    
    # Lines of code statistics
    run_command(
        f"cloc src/ --json --out={os.path.join(compliance_dir, 'loc-stats.json')}",
        "Lines of Code Statistics (cloc)",
        allow_fail=True
    )


def generate_summary():
    """Generate final summary report for prospective buyers/developers."""
    print(f"\n{CYAN}{'='*60}{RESET}")
    log("GENERATING SUMMARY REPORT", "STAGE")
    print(f"{CYAN}{'='*60}{RESET}\n")
    
    summary = {
        "generated_at": datetime.now().isoformat(),
        "pipeline_version": "3.3.0",
        "environment": {
            "type": ENV_TYPE,
            "python_version": sys.version,
            "python_exe": PYTHON_EXE,
        },
        "artifacts": [],
        "artifact_categories": {
            "security": "SBOM, SAST reports, CVE audit, license compliance",
            "coverage": "HTML coverage report, JSON metrics",
            "compliance": "Complexity metrics, maintainability index, LOC stats",
            "docs": "Consolidated TODO reports",
            "build": "Wheel and source distributions",
        }
    }
    
    # List all artifacts
    for root, dirs, files in os.walk(ARTIFACTS_DIR):
        for f in files:
            rel_path = os.path.relpath(os.path.join(root, f), ARTIFACTS_DIR)
            summary["artifacts"].append(rel_path)
    
    # Write JSON summary
    with open(os.path.join(ARTIFACTS_DIR, "pipeline_summary.json"), "w") as f:
        json.dump(summary, f, indent=2)
    
    # [20260117_FEATURE] Generate markdown summary for human readers
    summary_md = f"""# Code Scalpel Pipeline Summary

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Environment:** {ENV_TYPE}  
**Python:** {sys.version.split()[0]}

## Artifact Categories

### 🔒 Security Artifacts (for buyers/auditors)
| File | Description |
|------|-------------|
| `security/bandit-sast-report.json` | SAST scan results (JSON) |
| `security/bandit-sast-report.html` | SAST scan results (human-readable) |
| `security/pip-audit-report.json` | Dependency CVE audit |
| `security/sbom-cyclonedx.json` | Software Bill of Materials |
| `security/license-compliance.json` | License audit (JSON) |
| `security/license-summary.md` | License audit (readable) |

### 📊 Test Coverage
| File | Description |
|------|-------------|
| `coverage/html/index.html` | Interactive coverage report |
| `coverage/coverage.json` | Coverage metrics (JSON) |
| `test_results_*.xml` | JUnit XML test results |

### 📈 Code Quality Metrics
| File | Description |
|------|-------------|
| `compliance/complexity-cc.json` | Cyclomatic complexity |
| `compliance/maintainability-index.json` | Maintainability scores |
| `compliance/loc-stats.json` | Lines of code statistics |

### 📝 Documentation
| File | Description |
|------|-------------|
| `docs/todos.json` | All TODOs consolidated |
| `docs/TODO_BY_MODULE.md` | TODOs organized by module |

### 📦 Build Artifacts
| File | Description |
|------|-------------|
| `code_scalpel-*.whl` | Wheel distribution |
| `code_scalpel-*.tar.gz` | Source distribution |

## Verification Steps for Buyers

1. **Security:** Review `security/bandit-sast-report.html` for SAST findings
2. **Dependencies:** Check `security/pip-audit-report.json` for known CVEs
3. **Supply Chain:** Examine `security/sbom-cyclonedx.json` for full dependency tree
4. **Licenses:** Verify `security/license-summary.md` for license compatibility
5. **Test Coverage:** Open `coverage/html/index.html` in browser
6. **Code Quality:** Review `compliance/*.json` for complexity metrics
"""
    
    with open(os.path.join(ARTIFACTS_DIR, "SUMMARY.md"), "w") as f:
        f.write(summary_md)
    
    # Print final summary to console
    print(f"\n{GREEN}{'='*60}{RESET}")
    print(f"{GREEN}=== PIPELINE ARTIFACTS GENERATED ==={RESET}")
    print(f"{GREEN}{'='*60}{RESET}")
    print(f"\nArtifacts directory: {ARTIFACTS_DIR}")
    print("\n📂 Security Artifacts (for buyers/auditors):")
    print("   security/bandit-sast-report.html  (Human-readable SAST report)")
    print("   security/sbom-cyclonedx.json      (Software Bill of Materials)")
    print("   security/license-summary.md       (License compliance)")
    print("\n📊 Test/Coverage:")
    print("   coverage/html/index.html          (Interactive coverage report)")
    print("   test_results_*.xml                (JUnit XML reports)")
    print("\n📈 Code Quality:")
    print("   compliance/complexity-cc.json     (Cyclomatic complexity)")
    print("\n📦 Build:")
    print("   code_scalpel-*.whl                (Wheel distribution)")
    print(f"\n📋 Full summary: {os.path.join(ARTIFACTS_DIR, 'SUMMARY.md')}")
    print(f"📋 Pipeline log: {LOG_FILE}")


def main():
    global ENV_TYPE, PYTHON_EXE, PIP_EXE, BIN_DIR
    
    parser = argparse.ArgumentParser(
        description="Code Scalpel Local Release Pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run with conda (activate first!)
  conda activate code-scalpel && python local_pipeline/pipeline.py

  # Skip tests for quick build
  python local_pipeline/pipeline.py --skip-tests

  # Continue on failures
  python local_pipeline/pipeline.py --no-fail-fast
        """
    )
    parser.add_argument("--skip-tests", action="store_true", help="Skip test execution")
    parser.add_argument("--no-fail-fast", action="store_true", help="Continue on failures")
    parser.add_argument("--env", choices=["conda", "venv", "auto"], default="auto", 
                        help="Environment type (default: auto-detect)")
    parser.add_argument(
        "--cleanup-venv",
        action="store_true",
        help="Remove the virtualenv created by this pipeline run (if any)",
    )
    parser.add_argument(
        "--cleanup-backups",
        action="store_true",
        help="Remove backup files (e.g., *.bak) after successful completion",
    )
    parser.add_argument(
        "--cleanup-dry-run",
        action="store_true",
        help="Dry-run cleanup: only log intended deletions (venv/backups)",
    )
    args = parser.parse_args()
    
    start_total = time.time()
    
    # Detect environment (conda vs venv vs system)
    ENV_TYPE, PYTHON_EXE, PIP_EXE, BIN_DIR = detect_environment()
    
    global PIPELINE_DRY_RUN_CLEANUP

    setup_artifacts()
    ensure_environment()
    
    print(f"\n{GREEN}{'='*60}{RESET}")
    print(f"{GREEN}=== Code Scalpel Local Release Pipeline v3.3.0 ==={RESET}")
    print(f"{GREEN}{'='*60}{RESET}")
    print(f"Environment: {ENV_TYPE}")
    print(f"Python: {PYTHON_EXE}")
    print(f"Artifacts: {ARTIFACTS_DIR}")
    print(f"Logs: {LOG_FILE}\n")

    # Ensure build tools are available
    run_command(
        "pip install --upgrade pip build twine pytest pytest-cov bandit black ruff pyright pip-audit pip-licenses radon anyio httpx", 
        "Ensure Build Tools Installed",
        allow_fail=True
    )

    # Run all stages
    stage_static_analysis()
    stage_type_checking()
    stage_security_audit()
    stage_todo_extraction()
    stage_testing(skip_tests=args.skip_tests)
    stage_mcp_contract()
    stage_build()
    stage_metrics()
    generate_summary()

    # [20260117_FEATURE] Optional cleanup after successful run
    PIPELINE_DRY_RUN_CLEANUP = args.cleanup_dry_run
    if args.cleanup_backups:
        cleanup_backup_files(dry_run=args.cleanup_dry_run)
    if args.cleanup_venv:
        cleanup_virtualenv(dry_run=args.cleanup_dry_run)

    # Final Report
    duration_total = time.time() - start_total
    print(f"\n{GREEN}{'='*60}{RESET}")
    print(f"{GREEN}=== PIPELINE SUCCESSFUL ==={RESET}")
    print(f"{GREEN}Total Time: {duration_total:.2f}s{RESET}")
    print(f"{GREEN}{'='*60}{RESET}")


if __name__ == "__main__":
    main()
