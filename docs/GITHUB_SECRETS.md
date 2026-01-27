# GitHub Secrets Configuration for Code Scalpel CI/CD

This document describes how to configure GitHub Secrets for Code Scalpel's CI/CD pipeline, specifically for tier-based feature testing and license validation.

## Overview

Code Scalpel uses a tiered licensing model (Community, Pro, Enterprise) to control access to different MCP tools. During CI/CD testing, GitHub Secrets are used to inject valid test licenses into the build environment, allowing comprehensive testing of tier-based functionality.

## Required Secrets

The following GitHub Secrets must be configured in your repository:

### Test License Secrets

These secrets contain valid JWT licenses for testing tier-based functionality:

#### `TEST_PRO_LICENSE_JWT`
- **Type**: JWT License Token
- **Tier**: Pro
- **Purpose**: Enable Pro-tier tools during CI testing
- **Used in**: `tests/tools/tiers/`, `tests/capabilities/`
- **Content**: Valid Pro tier JWT license signed with production public key

#### `TEST_ENTERPRISE_LICENSE_JWT`
- **Type**: JWT License Token
- **Tier**: Enterprise
- **Purpose**: Enable Enterprise-tier tools during CI testing
- **Used in**: `tests/tools/tiers/`, `tests/capabilities/`
- **Content**: Valid Enterprise tier JWT license signed with production public key

#### `TEST_PRO_LICENSE_BROKEN_JWT`
- **Type**: JWT License Token (Invalid)
- **Tier**: Pro
- **Purpose**: Test license validation error handling
- **Used in**: Tests validating license rejection
- **Content**: JWT with missing required claims (e.g., `sub` claim)

#### `TEST_ENTERPRISE_LICENSE_BROKEN_JWT`
- **Type**: JWT License Token (Invalid)
- **Tier**: Enterprise
- **Purpose**: Test license validation error handling
- **Used in**: Tests validating license rejection
- **Content**: JWT with missing required claims (e.g., `sub` claim)

### Optional Secrets

#### `CODECOV_TOKEN`
- **Type**: Codecov API Token
- **Purpose**: Upload coverage reports to Codecov
- **Used in**: Coverage upload step (line 188 in `.github/workflows/ci.yml`)
- **Optional**: Can be left empty; coverage upload will be skipped

## How Licenses Are Used in CI/CD

### 1. License Injection (CI Workflow)

In `.github/workflows/ci.yml`, the test job injects licenses before running tests:

```yaml
- name: Setup test licenses for tier testing
  run: |
    mkdir -p tests/licenses
    echo "${{ secrets.TEST_PRO_LICENSE_JWT }}" > tests/licenses/code_scalpel_license_pro_20260101_190345.jwt
    echo "${{ secrets.TEST_ENTERPRISE_LICENSE_JWT }}" > tests/licenses/code_scalpel_license_enterprise_20260101_190754.jwt
    echo "${{ secrets.TEST_PRO_LICENSE_BROKEN_JWT }}" > tests/licenses/code_scalpel_license_pro_test_broken.jwt
    echo "${{ secrets.TEST_ENTERPRISE_LICENSE_BROKEN_JWT }}" > tests/licenses/code_scalpel_license_enterprise_test_broken.jwt
```

### 2. License File Paths

Test licenses are written to:
```
tests/licenses/
├── code_scalpel_license_pro_20260101_190345.jwt
├── code_scalpel_license_enterprise_20260101_190754.jwt
├── code_scalpel_license_pro_test_broken.jwt
└── code_scalpel_license_enterprise_test_broken.jwt
```

These paths are automatically discovered by pytest fixtures in:
- `tests/capabilities/conftest.py` (`pro_license_path` and `enterprise_license_path` fixtures)
- `tests/tools/get_graph_neighborhood/licensing/conftest.py`

### 3. Test Discovery and Usage

Tests that need licenses automatically use the injected files:

```python
# In test_ci_license_injection.py
def test_pro_tier_shows_pro_tools(self, clear_all_caches, pro_license_path):
    os.environ["CODE_SCALPEL_LICENSE_PATH"] = str(pro_license_path)
    # ... test code
```

## Setting Up GitHub Secrets

### Step 1: Obtain Test Licenses

Contact your Code Scalpel team or licensing administrator to obtain valid test licenses:

1. **Pro Tier License**: JWT signed with production key, tier claim set to "pro"
2. **Enterprise Tier License**: JWT signed with production key, tier claim set to "enterprise"
3. **Broken Licenses** (for validation testing): JWTs with missing required claims

### Step 2: Add Secrets to Repository

#### Using GitHub Web UI:

1. Navigate to your repository
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Create each secret:
   - Name: `TEST_PRO_LICENSE_JWT`
   - Value: (paste entire JWT token)
5. Repeat for other secrets

#### Using GitHub CLI:

```bash
# Set Pro license
gh secret set TEST_PRO_LICENSE_JWT < pro_license.jwt

# Set Enterprise license
gh secret set TEST_ENTERPRISE_LICENSE_JWT < enterprise_license.jwt

# Set broken Pro license
gh secret set TEST_PRO_LICENSE_BROKEN_JWT < pro_license_broken.jwt

# Set broken Enterprise license
gh secret set TEST_ENTERPRISE_LICENSE_BROKEN_JWT < enterprise_license_broken.jwt
```

### Step 3: Verify Secrets Are Configured

Check that secrets are available in your workflow:

```bash
# List configured secrets
gh secret list
```

Expected output:
```
TEST_PRO_LICENSE_JWT               Updated: 2026-01-27
TEST_ENTERPRISE_LICENSE_JWT        Updated: 2026-01-27
TEST_PRO_LICENSE_BROKEN_JWT        Updated: 2026-01-27
TEST_ENTERPRISE_LICENSE_BROKEN_JWT Updated: 2026-01-27
```

## License JWT Structure

All test licenses should follow this structure:

```json
{
  "tier": "pro",                    // or "enterprise"
  "sub": "test-customer-001",       // subject (customer ID)
  "iss": "code-scalpel",           // issuer
  "aud": "code-scalpel-users",     // audience
  "exp": 1798823075,               // expiration (unix timestamp)
  "iat": 1767287075,               // issued at
  "jti": "unique-token-id",        // JWT ID
  "nbf": 1767287075,               // not before
  "org": "Test Organization",       // organization name
  "seats": 1                        // number of seats
}
```

### Key Requirements:

- **Signature**: Must be signed with RS256 algorithm using production private key
- **Expiration**: Should be far in future (2027+) to avoid test failures
- **Claims**: Must include all required claims listed above
- **Tier**: Must match the secret name (pro or enterprise)

## Broken License Requirements

For validation testing, broken licenses must:

1. Have valid RS256 signature
2. Have valid expiration (future date)
3. **Missing one or more required claims** (typically `sub`)

Example broken license (missing `sub`):
```json
{
  "tier": "pro",
  "iss": "code-scalpel",
  "aud": "code-scalpel-users",
  "exp": 1798823075,
  "iat": 1767287075,
  // "sub" is intentionally missing
  "jti": "unique-token-id",
  "nbf": 1767287075,
  "org": "Test Organization",
  "seats": 1
}
```

## Testing with Local Development

For local development without GitHub Secrets:

### Option 1: Set Environment Variable

```bash
export CODE_SCALPEL_LICENSE_PATH=/path/to/your/test/license.jwt
pytest tests/capabilities/
```

### Option 2: Place License in Expected Location

```bash
cp your_test_license.jwt tests/licenses/code_scalpel_license_pro_20260101_190345.jwt
pytest tests/capabilities/
```

Pytest fixtures will automatically discover the license.

### Option 3: Mock Tier for Testing

If no valid license is available:

```python
# In your test
from unittest.mock import patch

with patch('code_scalpel.mcp.server._get_current_tier', return_value='pro'):
    # Your test code here
    pass
```

## CI/CD Workflow Integration

The `.github/workflows/ci.yml` workflow includes these tier-related steps:

1. **Smoke Test** (5 min): Basic import validation
2. **License Setup** (2 min): Inject licenses from secrets
3. **Test Suite** (15 min): Run all tests with real licenses
   - Multi-version Python (3.10, 3.11, 3.12, 3.13)
   - Full coverage calculation
   - Real JWT validation against production keys
4. **Upload Coverage** (5 min): Report to Codecov

## Troubleshooting

### Licenses Not Injected

**Symptom**: Tests fail with "No license found" errors

**Solution**:
1. Verify secrets are configured: `gh secret list`
2. Check `.github/workflows/ci.yml` for license setup step
3. Ensure secret names match exactly (case-sensitive)

### License Validation Fails

**Symptom**: JWT signature validation fails in tests

**Solution**:
1. Verify license is signed with production public key: `vault-prod-2026-01.pem`
2. Check license expiration is in future: `jti_decode --no-verify <token>`
3. Verify all required claims are present
4. Check license tier matches secret name

### Tier Detection Returns Community

**Symptom**: Tests detect "community" tier even with Pro license

**Solution**:
1. Clear license cache before test:
   ```python
   from code_scalpel.licensing import jwt_validator
   jwt_validator._LICENSE_VALIDATION_CACHE = None
   ```
2. Verify `CODE_SCALPEL_LICENSE_PATH` env var is set
3. Check that license file exists and is readable

### Tests Use Wrong License Path

**Symptom**: Tests can't find injected licenses

**Solution**:
1. Check test fixtures in `conftest.py` match actual filenames
2. Verify CI workflow writes to correct path (`tests/licenses/`)
3. Ensure `.gitignore` doesn't exclude the directory

## Updating Licenses

When test licenses expire or need renewal:

1. Obtain new licenses from licensing team
2. Update GitHub Secrets:
   ```bash
   gh secret set TEST_PRO_LICENSE_JWT < new_pro_license.jwt
   gh secret set TEST_ENTERPRISE_LICENSE_JWT < new_enterprise_license.jwt
   ```
3. Verify in next workflow run that licenses are injected correctly

## Security Considerations

⚠️ **Important**: 

- Never commit license files to git (`.gitignore` blocks `*.jwt`)
- GitHub Secrets are encrypted and only available during workflow execution
- Test licenses should have limited seats and clearly marked as test licenses
- Production licenses should never be stored in GitHub Secrets
- Licenses are only injected into CI/CD builds, never persisted

## Related Documentation

- **License Validation**: `tests/licenses/README.md`
- **Tier System**: `src/code_scalpel/licensing/`
- **Capabilities Resolver**: `src/code_scalpel/capabilities/`
- **CI/CD Workflow**: `.github/workflows/ci.yml`
- **Test Fixtures**: `tests/capabilities/conftest.py`

## Questions or Issues?

If you encounter issues with GitHub Secrets configuration:

1. Check this document for setup instructions
2. Review `tests/licenses/README.md` for license details
3. Examine `.github/workflows/ci.yml` for workflow integration
4. Open an issue at https://github.com/anomalyco/opencode
