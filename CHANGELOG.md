# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [3.3.0] - 2026-01-12
### Added
- **New Tool: `verify_policy_integrity`**
  - Cryptographic verification of policy files to prevent tampering.
  - Fail-closed security model (Deny All on manifest mismatch).
  - Supports git-based, env-based, and file-based manifest loading.
- **New Tool: `code_policy_check`**
  - Automated code compliance and style checking.
  - Community: Style guides (PEP8, ESLint).
  - Enterprise: Compliance frameworks (PCI-DSS, HIPAA).
- **New Tool: `rename_symbol`**
  - Safe, atomic symbol renaming for Python (v1.0).
  - Updates definition and all references consistently.
  - Includes syntax validation and backup creation.

### Changed
- **System-Wide: Tier Transparency**
  - All tools now include `_meta` fields in output to indicate active tier, limits applied, and upgrade prompts.
- **`analyze_code`**
  - v1.0 Stable release.
  - Auto-detection of language from code content.
  - Standardized complexity scoring across languages.
- **`crawl_project`**
  - Removed `limits.toml` restrictions for smoother large-project analysis.
  - Added new project metric visualizations.
- **`security_scan`**
  - Expanded taint analysis rulesets.
  - Added "CWE" mapping for all findings.
- **`generate_unit_tests`**
  - Added `data_driven` parameter for parametrized test generation (Pro).
  - Enterprise tier: Bug reproduction from crash logs.

### Fixed
- **`extract_code`**
  - Resolved Python-only dependency limitation for import extraction.
  - Improved handling of nested classes.
- **`get_cross_file_dependencies`**
  - Fixed re-export chain resolution for cleaner graphs.

### Security
- **`type_evaporation_scan`**
  - Added detection for "Implicit Any" in API responses.
  - Correlates TypeScript frontend `fetch` with Python backend routes.
- **`unified_sink_detect`**
  - Standardized confidence thresholds across all languages.
  - Added coverage for 15+ new sink types.
