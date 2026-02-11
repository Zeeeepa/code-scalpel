# Demo: "Supply Chain Guardian: Typosquat Detection"

**Persona**: Technical Leader
**Pillar**: Accurate AI
**Tier**: Enterprise (Custom pricing)
**Duration**: 8 minutes
**Fixture**: From Ninja Warrior "Typosquat Trap" obstacle

## Scenario

Dependencies include `pyaml` instead of `PyYAML` - a supply chain attack. Standard scanners miss it. Code Scalpel detects typosquatted/phantom packages.

## Tools Used

- `scan_dependencies` (Enterprise: typosquatting_detection=true)
- `analyze_code` (import analysis)

## Recording Script

### Step 1: The Silent Attack (0:00-1:00)

- Show `requirements.txt`:
  ```
  requests==2.31.0
  pyaml==23.5.9    # Typosquat!
  flask==3.0.0
  ```
- On-screen: "Can you spot the malicious package?"
- Voiceover: "pyaml vs PyYAML - one letter difference, huge impact"

### Step 2: Real-World Context (1:00-2:00)

- Explain typosquatting:
  - Attacker registers `pyaml` (looks like `PyYAML`)
  - Contains malware that steals secrets
  - Downloads: 50,000+ before detection
- On-screen: "Supply chain attacks are rising 700% YoY"

### Step 3: Standard Scanner Failure (2:00-3:00)

- Run `pip-audit`: No CVEs found ✓
- Run Snyk: Package exists, no known vulnerabilities ✓
- Problem: These tools check CVE databases
- Typosquats are NEW packages (no CVEs yet)

### Step 4: Code Scalpel Detection (3:00-5:00)

- Run `scan_dependencies --enable-typosquat-detection`
- Enterprise algorithm:
  1. Extract all imports from codebase
  2. Compare imports to actual package names
  3. Check for Levenshtein distance mismatches
  4. Verify against PyPI popularity data
- Finding: "pyaml imported but PyYAML installed - TYPOSQUAT DETECTED"

### Step 5: Visual Evidence (5:00-6:00)

- Show comparison table:
  | Import | Package | Similarity | Risk |
  |--------|---------|------------|------|
  | `import yaml` | `pyaml` | 90% match | HIGH ⚠ |
  | Expected | `PyYAML` | - | - |
- Highlight: Code expects PyYAML but got pyaml

### Step 6: Supply Chain Report (6:00-7:00)

- Full dependency risk report:
  - 15 direct dependencies analyzed
  - 247 transitive dependencies
  - 1 typosquat detected
  - 2 dependencies with known CVEs
  - 3 dependencies deprecated
- On-screen: "Comprehensive supply chain visibility"

### Step 7: Remediation (7:00-7:30)

- Fix: Replace `pyaml` with `PyYAML`
- Re-scan: All clear ✓
- Set policy: Block installs of suspicious packages

### Step 8: Enterprise Protection (7:30-8:00)

- Enterprise features:
  - Typosquatting detection
  - Private registry scanning
  - License compliance
  - Automated PR for fixes
- On-screen: "Protect your supply chain"

## Expected Outputs

- Dependency risk report (JSON + PDF)
- Typosquat alert with evidence
- Suggested remediation (PR-ready)

## Key Statistics

- Packages scanned: 262
- Typosquats found: 1
- False positives: 0
- CVEs found: 2
- Time: 12 seconds

## Detection Algorithm

### Phase 1: Import Extraction

```python
# Scan all Python files for imports
imports = {
    "yaml",      # from "import yaml"
    "requests",  # from "import requests"
    "flask",     # from "from flask import Flask"
}
```

### Phase 2: Package Mapping

```python
# Map imports to installed packages
installed_packages = {
    "pyaml": ["yaml"],        # pyaml provides "yaml" module
    "requests": ["requests"],
    "flask": ["flask"],
}
```

### Phase 3: Typosquat Detection

```python
# Check for mismatches
for import_name in imports:
    expected_packages = get_popular_packages(import_name)
    # expected: PyYAML (15M downloads/month)
    # actual: pyaml (50K downloads/month)

    if levenshtein_distance(installed, expected) <= 2:
        if popularity(installed) < 0.1 * popularity(expected):
            alert_typosquat(installed, expected)
```

### Phase 4: Verification

```python
# Verify with multiple sources
- PyPI metadata (author, upload date)
- GitHub repository (stars, activity)
- Download statistics
- Known typosquat database
```

## Real-World Typosquatting Examples

### Python Ecosystem

| Malicious | Legitimate | Downloads Before Detection |
|-----------|------------|----------------------------|
| `pyaml` | `PyYAML` | 50,000+ |
| `python3-dateutil` | `python-dateutil` | 20,000+ |
| `urllib4` | `urllib3` | 10,000+ |
| `reqeusts` | `requests` | 5,000+ |
| `beautifulsoup` | `beautifulsoup4` | 15,000+ |

### JavaScript/npm

| Malicious | Legitimate | Impact |
|-----------|------------|--------|
| `crossenv` | `cross-env` | Stole environment variables |
| `event-stream` | (legitimate) | Backdoor injected, stole Bitcoin |
| `eslint-scope` | (legitimate) | npm credentials stolen |

### Ruby Gems

| Malicious | Legitimate | Impact |
|-----------|------------|--------|
| `rest-client` | (typo in instructions) | Common mistake in tutorials |

## Supply Chain Risk Report

```json
{
  "scan_date": "2026-02-08T14:23:00Z",
  "repository": "api-service",
  "total_dependencies": 262,
  "direct_dependencies": 15,
  "transitive_dependencies": 247,

  "findings": {
    "typosquats": [
      {
        "installed": "pyaml",
        "expected": "PyYAML",
        "import_name": "yaml",
        "severity": "CRITICAL",
        "confidence": 0.95,
        "evidence": {
          "levenshtein_distance": 1,
          "popularity_ratio": 0.003,
          "upload_date": "2023-05-15",
          "author_mismatch": true
        },
        "recommendation": "Replace pyaml with PyYAML"
      }
    ],

    "cves": [
      {
        "package": "requests",
        "version": "2.28.0",
        "cve": "CVE-2023-XXXXX",
        "severity": "MEDIUM",
        "fixed_in": "2.31.0",
        "recommendation": "Upgrade to requests>=2.31.0"
      }
    ],

    "deprecated": [
      {
        "package": "flask-cors",
        "version": "3.0.0",
        "deprecated_since": "2025-01-01",
        "replacement": "flask>=3.0 (built-in CORS)"
      }
    ],

    "license_issues": [
      {
        "package": "pillow",
        "license": "HPND",
        "policy_violation": "GPL-incompatible",
        "severity": "LOW"
      }
    ]
  },

  "risk_score": {
    "overall": 7.2,
    "typosquat_risk": 9.5,
    "cve_risk": 6.0,
    "license_risk": 3.0,
    "freshness_risk": 5.0
  },

  "recommendations": [
    "URGENT: Remove typosquat package 'pyaml', install 'PyYAML'",
    "HIGH: Upgrade 2 packages with known CVEs",
    "MEDIUM: Replace 3 deprecated packages",
    "LOW: Review license compatibility"
  ]
}
```

## Key Talking Points

- "Standard scanners only check CVE databases - miss new attacks"
- "Typosquatting is rising 700% year-over-year"
- "Enterprise detects typosquats by comparing imports to installed packages"
- "Zero-day supply chain attack detection"
- "Private registry scanning for internal packages"
- "Automated fix PRs save hours of manual work"

## Enterprise Features

### 1. Typosquat Detection
- Import-to-package mapping
- Levenshtein distance analysis
- Popularity comparison
- Multi-source verification

### 2. Private Registry Support
- Scan internal PyPI/npm registries
- Custom package allowlists
- Organization-specific policies

### 3. License Compliance
- SPDX license database
- GPL compatibility checking
- Custom license policies
- Audit reports for legal teams

### 4. Automated Remediation
- Generate fix PRs automatically
- Include upgrade instructions
- Test compatibility before merging
- Rollback on failure

### 5. Continuous Monitoring
- Daily scans of dependencies
- Alert on new CVEs
- Monitor for typosquat uploads
- Track dependency freshness

## ROI Analysis

### Cost of Supply Chain Incident

Based on 2023 industry averages:
- Detection time: 3-6 months
- Investigation: 2 weeks (4 engineers)
- Remediation: 1-2 weeks
- Total cost: $150,000 - $500,000
- Reputational damage: Incalculable

### Prevention with Code Scalpel

- Daily scans: 12 seconds each
- Detection: Real-time (before deployment)
- Investigation: Automated report
- Remediation: PR generated automatically
- Total cost: $0 (included in Enterprise)

**Break-even**: Preventing 1 supply chain incident pays for 5-10 years of Enterprise licenses
