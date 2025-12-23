# v3.1.1 Hotfix Release Summary

**Release Date**: December 22, 2025  
**Release Type**: CRITICAL HOTFIX  
**PyPI**: https://pypi.org/project/code-scalpel/3.1.1/  
**GitHub**: https://github.com/tescolopio/code-scalpel/releases/tag/v3.1.1

## Critical Issue Fixed

**Problem**: The `code-scalpel init` command was creating only 7 minimal configuration files, while the v3.1.0 project actually uses a much richer governance structure with ~23 files including complete policy templates.

**Impact**: New users running `code-scalpel init` after installing v3.1.0 from PyPI would get an incomplete, outdated configuration that didn't match the advertised v3.1.0 features.

**Severity**: HIGH - Major usability issue affecting all new users

## What Was Fixed

### Templates Added (9 new constants in `templates.py`)

1. **DEV_GOVERNANCE_YAML_TEMPLATE** - Development meta-policies for AI agents
2. **PROJECT_STRUCTURE_YAML_TEMPLATE** - File organization rules
3. **POLICIES_README_TEMPLATE** - Main policies documentation
4. **ARCHITECTURE_README_TEMPLATE** - Architecture policy documentation
5. **DEVOPS_README_TEMPLATE** - DevOps policy documentation
6. **DEVSECOPS_README_TEMPLATE** - DevSecOps policy documentation
7. **PROJECT_README_TEMPLATE** - Project structure policy documentation
8. **LAYERED_ARCHITECTURE_REGO_TEMPLATE** - Layered architecture enforcement policy
9. **DOCKER_SECURITY_REGO_TEMPLATE** - Docker security best practices policy
10. **SECRET_DETECTION_REGO_TEMPLATE** - Hardcoded secret detection policy
11. **PROJECT_STRUCTURE_REGO_TEMPLATE** - Project structure enforcement policy

### New Directory Structure Created by `init`

```
.code-scalpel/
├── README.md
├── policy.yaml
├── budget.yaml
├── config.json
├── .gitignore
├── audit.log
├── dev-governance.yaml          # NEW - Development governance
├── project-structure.yaml       # NEW - Project structure config
└── policies/                    # NEW - Policy templates
    ├── README.md
    ├── architecture/
    │   ├── README.md
    │   └── layered_architecture.rego
    ├── devops/
    │   ├── README.md
    │   └── docker_security.rego
    ├── devsecops/
    │   ├── README.md
    │   └── secret_detection.rego
    └── project/
        ├── README.md
        └── structure.rego
```

**Total Files**: 23 (was 7 before)

## Files Modified

1. **src/code_scalpel/config/templates.py** (+449 lines)
   - Added 11 new template constants
   - All templates are production-ready with documentation

2. **src/code_scalpel/config/init_config.py** (+67 lines)
   - Updated `init_config_dir()` to create complete structure
   - Creates policies/ directory with 4 subdirectories
   - Each subdirectory gets README + sample .rego policy

3. **pyproject.toml** (version bump)
   - Version: 3.1.0 → 3.1.1

4. **CHANGELOG.md** (release notes)
   - Added v3.1.1 section with detailed fix description

## Validation

- ✅ Python syntax check passed
- ✅ No import errors
- ✅ Twine check PASSED for both wheel and source distribution
- ✅ Successfully uploaded to PyPI
- ✅ Git tagged and pushed to GitHub

## Git Commits

1. **ad7ce73** - [HOTFIX] v3.1.0 - Complete init templates with full governance structure
2. **0f9004f** - [RELEASE] v3.1.1 - Init Template Hotfix

## Release Artifacts

- **Wheel**: `code_scalpel-3.1.1-py3-none-any.whl` (1.2 MB)
- **Source**: `code_scalpel-3.1.1.tar.gz` (1.0 MB)
- **Tag**: v3.1.1

## Installation

Users can now upgrade to get the fixed init command:

```bash
pip install --upgrade code-scalpel
code-scalpel init  # Now creates complete 23-file structure
```

## Verification

To verify the fix works:

```bash
# Create a test directory
mkdir test-project && cd test-project

# Initialize Code Scalpel
code-scalpel init

# Check what was created
ls -la .code-scalpel/
ls -la .code-scalpel/policies/
ls -la .code-scalpel/policies/architecture/
ls -la .code-scalpel/policies/devops/
ls -la .code-scalpel/policies/devsecops/
ls -la .code-scalpel/policies/project/
```

Expected output: 23 files across 5 directories

## Next Steps

1. ✅ Release published to PyPI
2. ✅ Git tag pushed to GitHub
3. Optional: Create GitHub Release page with release notes
4. Optional: Announce hotfix to users

## Notes

This was identified immediately after v3.1.0 release during post-release testing. The quick turnaround (same day) ensures minimal user impact from the incomplete init templates.

---

*Hotfix completed: December 22, 2025*
