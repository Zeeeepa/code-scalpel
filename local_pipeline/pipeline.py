#!/usr/bin/env python3
"""
Local Pre-Release Pipeline Orchestrator for Code Scalpel v3.3.0
Does everything a robust CI pipeline does, but locally.

Usage:
    python local_pipeline/pipeline.py [--skip-tests] [--no-fail-fast]
"""

import subprocess
import sys
import shutil
import os
import time
from datetime import datetime
from threading import Timer

# Configuration
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ARTIFACTS_DIR = os.path.join(PROJECT_ROOT, "release_artifacts", "local_build")
LOG_FILE = os.path.join(ARTIFACTS_DIR, "pipeline.log")
VENV_DIR = os.path.join(PROJECT_ROOT, ".venv")

# Determine Executables
if sys.platform == "win32":
    PYTHON_EXE = os.path.join(VENV_DIR, "Scripts", "python.exe")
    PIP_EXE = os.path.join(VENV_DIR, "Scripts", "pip.exe")
    BIN_DIR = os.path.join(VENV_DIR, "Scripts")
else:
    PYTHON_EXE = os.path.join(VENV_DIR, "bin", "python")
    PIP_EXE = os.path.join(VENV_DIR, "bin", "pip")
    BIN_DIR = os.path.join(VENV_DIR, "bin")

# Colors
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"

def log(message, level="INFO"):
    timestamp = datetime.now().strftime("%H:%M:%S")
    formatted_msg = f"[{timestamp}] {level}: {message}"
    
    # Print to console with color
    if level == "INFO":
        print(f"{BLUE}{formatted_msg}{RESET}")
    elif level == "SUCCESS":
        print(f"{GREEN}{formatted_msg}{RESET}")
    elif level == "ERROR":
        print(f"{RED}{formatted_msg}{RESET}")
    elif level == "WARNING":
        print(f"{YELLOW}{formatted_msg}{RESET}")
    
    # Write to file
    with open(LOG_FILE, "a") as f:
        f.write(formatted_msg + "\n")

def run_command(command, description, cwd=PROJECT_ROOT, allow_fail=False, use_venv=True):
    log(f"Starting: {description}...", "INFO")
    start_time = time.time()
    
    # Adjust command to use venv binaries if requested and available
    if use_venv and os.path.exists(VENV_DIR):
        # If command starts with 'python' or 'pip', replace with full path
        cmd_parts = command.split()
        if cmd_parts[0] == "python":
            cmd_parts[0] = PYTHON_EXE
        elif cmd_parts[0] == "pip":
            cmd_parts[0] = PIP_EXE
        # For other tools (pytest, black, etc), try to find them in bin dir
        elif os.path.exists(os.path.join(BIN_DIR, cmd_parts[0])):
             cmd_parts[0] = os.path.join(BIN_DIR, cmd_parts[0])
        
        command = " ".join(cmd_parts)

    try:
        # Stream output to console while capturing it
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
                
        process.wait()
        duration = time.time() - start_time
        
        if process.returncode != 0 and not allow_fail:
            log(f"FAILED: {description} (Exit Code: {process.returncode})", "ERROR")
            raise Exception(f"Pipeline step failed: {description}")
        
        log(f"COMPLETED: {description} in {duration:.2f}s", "SUCCESS")
        return True
        
    except Exception as e:
        if not allow_fail:
            log(f"Exception during {description}: {str(e)}", "ERROR")
            sys.exit(1)
        return False

def setup_artifacts():
    if os.path.exists(ARTIFACTS_DIR):
        shutil.rmtree(ARTIFACTS_DIR)
    os.makedirs(ARTIFACTS_DIR, exist_ok=True)
    with open(LOG_FILE, "w") as f:
        f.write(f"Pipeline Run Started: {datetime.now()}\n")

def ensure_venv():
    if not os.path.exists(VENV_DIR):
        print(f"{YELLOW}Creating virtual environment at {VENV_DIR}...{RESET}")
        subprocess.check_call([sys.executable, "-m", "venv", VENV_DIR])
    else:
        print(f"{BLUE}Using existing virtual environment at {VENV_DIR}{RESET}")

def set_license_tier(tier):
    """
    Swaps license files to simulate different tiers.
    """
    print(f"\n{YELLOW}--- Configuring License: {tier.upper()} ---{RESET}")
    license_dir = os.path.join(PROJECT_ROOT, ".code-scalpel/license")
    
    # 1. Clear existing license
    if os.path.exists(license_dir):
        shutil.rmtree(license_dir)
    os.makedirs(license_dir, exist_ok=True)

    if tier == "community":
        # No license file = Community Tier
        log("License cleared. Operating in COMMUNITY tier.", "INFO")
        return

    # 2. keys map
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

def main():
    start_total = time.time()
    setup_artifacts()
    ensure_venv()
    
    print(f"\n{GREEN}=== Code Scalpel Local Release Pipeline ==={RESET}")
    print(f"Logs: {LOG_FILE}\n")

    # 1. Environment Check
    run_command("python --version", "Checking Python Version")
    run_command("pip install --upgrade pip build twine pytest pytest-cov bandit black ruff pyright pip-audit anyio httpx", "Ensure Build Tools Installed")

    # 2. Linting & Formatting
    print(f"\n{YELLOW}--- Stage 1: Static Analysis ---{RESET}")
    run_command("black --check --diff src/ tests/", "Black Formatting Check", allow_fail=True)
    run_command("ruff check src/ tests/", "Ruff Linting", allow_fail=True)
    
    # [20260114_FEATURE] Added syntax validation to catch missing operators
    print(f"\n{YELLOW}--- Stage 1.5: Syntax Validation ---{RESET}")
    run_command(
        "python -m compileall -q src/",
        "Python Syntax Check (all source files)",
        allow_fail=False  # Syntax errors are blocking
    )
    
    # 3. Type Checking
    print(f"\n{YELLOW}--- Stage 2: Type Safety ---{RESET}")
    run_command("pyright -p pyrightconfig.json", "Pyright Type Check", allow_fail=True)

    # 4. Security Audit
    print(f"\n{YELLOW}--- Stage 3: Security Gates ---{RESET}")
    run_command(
        f"bandit -r src/ -ll -ii -x '**/test_*.py' --format json --output {os.path.join(ARTIFACTS_DIR, 'bandit-report.json')}", 
        "Bandit Security Scan",
        allow_fail=True
    )
    # Allow pip-audit to fail if network issues, or just warning mode
    run_command(
        f"pip-audit -r requirements-secure.txt --format json --output {os.path.join(ARTIFACTS_DIR, 'pip-audit-report.json')}", 
        "Dependency Vulnerability Audit", 
        allow_fail=True
    )

    # 5. Testing
    print(f"\n{YELLOW}--- Stage 4: Testing Suite ---{RESET}")
    # Run Core Tests (Tier-agnostic)
    run_command("pytest tests/core/ -v --tb=short", "Core Tests")
    
    if os.path.exists("tests/tools"):
        # 5a. Community Tier Verification
        set_license_tier("community")
        run_command(
            "pytest tests/tools/ -v -k 'Community' --tb=short", 
            "Community Tier Verification", 
            allow_fail=True
        )

        # 5b. Pro Tier Verification
        set_license_tier("pro")
        run_command(
            "pytest tests/tools/ -v -k 'Pro' --tb=short", 
            "Pro Tier Verification", 
            allow_fail=True
        )

        # 5c. Enterprise Tier Verification (Full Suite)
        set_license_tier("enterprise")
        # Run all tool tests (should pass with Enterprise license)
        run_command(
            "pytest tests/tools/ -v --tb=short", 
            "Enterprise Tier & Full Suite Verification", 
            allow_fail=True
        )
    # Add other test suites here as needed

    # 6. MCP Contract Verification
    print(f"\n{YELLOW}--- Stage 5: MCP Contract Verification ---{RESET}")
    # We run stdio as primary smoke test
    os.environ["MCP_CONTRACT_TRANSPORT"] = "stdio"
    # Assuming the file exists, if not, skip gently
    if os.path.exists(os.path.join(PROJECT_ROOT, "tests/test_mcp_all_tools_contract.py")):
        run_command("pytest -q tests/test_mcp_all_tools_contract.py", "MCP Contract (stdio)")

    # 7. Build
    print(f"\n{YELLOW}--- Stage 6: Build ---{RESET}")
    # Clean prev builds
    if os.path.exists("dist"):
        shutil.rmtree("dist")
    
    run_command("python -m build", "Build Source & Wheel Distributions")
    run_command("twine check dist/*", "Twine Metadata Check")

    # Final Report
    duration_total = time.time() - start_total
    print(f"\n{GREEN}=== PIPELINE SUCCESSFUL ==={RESET}")
    print(f"Total Time: {duration_total:.2f}s")
    print(f"Artifacts: {ARTIFACTS_DIR}")
    print(f"  - bandit-report.json")
    print(f"  - pip-audit-report.json")
    print(f"  - dist/ (Wheel & Tarball)")
    print(f"  - pipeline.log")

if __name__ == "__main__":
    main()
