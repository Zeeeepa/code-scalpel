# Test License Files

This directory contains JWT license files for testing tier-based functionality in Code Scalpel.

## Files

### Valid Test Licenses (Expected Status)
- `code_scalpel_license_pro_20260101_170435.jwt` - Pro tier license
- `code_scalpel_license_enterprise_20260101_170506.jwt` - Enterprise tier license

**Status**: Currently have **invalid signatures** because they were signed with a different private key than the production public key (`vault-prod-2026-01.pem`).

**Required Claims**: All test licenses include:
- `tier`: "pro" or "enterprise"
- `sub`: customer ID (e.g., "test-pro-001")
- `iss`: "code-scalpel" (issuer)
- `aud`: "code-scalpel-users" (audience)
- `exp`: expiration timestamp
- `iat`: issued at timestamp
- `jti`: unique token ID
- `nbf`: not before timestamp
- `org`: organization name
- `seats`: number of seats

### Broken Test Licenses (Intentionally Invalid)
- `code_scalpel_license_pro_test_broken.jwt` - Missing `sub` claim
- `code_scalpel_license_enterprise_test_broken.jwt` - Missing `sub` claim

**Purpose**: Verify that the validator rejects licenses with missing required claims.

## Public Key Authentication

License validation uses a two-stage authentication flow:

1. **Offline Validation** (Always)
   - Uses RSA public key: `src/code_scalpel/licensing/public_key/vault-prod-2026-01.pem`
   - Verifies JWT signature cryptographically
   - No network required

2. **Online Validation** (Every 24 hours)
   - Connects to remote verifier: `CODE_SCALPEL_LICENSE_VERIFIER_URL`
   - Checks revocation status
   - Validates entitlements
   - 24-hour grace period if verifier offline (48h total)

## Test Fixture Behavior

The test fixtures in `tests/tools/tiers/conftest.py` handle missing/invalid licenses gracefully:

- **If valid license found**: Uses real license via `CODE_SCALPEL_LICENSE_PATH` env var
- **If no valid license**: Falls back to mocking `_get_current_tier()` function
- **Both approaches work**: Tier feature tests pass with either real or mocked tiers

## Generating Valid Test Licenses

To generate test licenses that validate against `vault-prod-2026-01.pem`:

1. **Use the corresponding private key** that matches the public key
2. **Sign with RS256 algorithm**
3. **Include all required claims** (see above)
4. **Set far-future expiration** (e.g., 2027+)

Example JWT structure:
```json
{
  "tier": "pro",
  "sub": "test-customer-001",
  "iss": "code-scalpel",
  "aud": "code-scalpel-users",
  "exp": 1798823075,
  "iat": 1767287075,
  "jti": "unique-token-id",
  "nbf": 1767287075,
  "org": "Test Organization",
  "seats": 1
}
```

## Local Development Setup

**For local tier testing, you have two options:**

### Option 1: Place Test Licenses in `tests/licenses/` (Recommended)

1. Generate valid test licenses signed with `vault-prod-2026-01.pem`:
   ```bash
   # Generate Pro tier license
   python -m code_scalpel.licensing.generate_license \
     --tier pro \
     --customer "local-dev" \
     --output tests/licenses/code_scalpel_license_pro_20260101_190345.jwt
   
   # Generate Enterprise tier license
   python -m code_scalpel.licensing.generate_license \
     --tier enterprise \
     --customer "local-dev" \
     --output tests/licenses/code_scalpel_license_enterprise_20260101_190754.jwt
   ```

2. The `conftest.py` fixtures will automatically detect and use these licenses
3. These files are git-ignored and safe for local development

### Option 2: Use Environment Variable

Set `CODE_SCALPEL_LICENSE_PATH` in your `.env` file:
```bash
CODE_SCALPEL_LICENSE_PATH=/path/to/your/test/license.jwt
```

### Option 3: Rely on Mock Fallback

If no valid license is found, `conftest.py` automatically falls back to mocking `_get_current_tier()`.
This is acceptable for tier feature testing but doesn't test actual JWT validation.

## GitHub CI/CD Integration

**Test licenses are NOT committed to the repository** to prevent license copying and protect tier monetization.

Instead, test licenses are stored as GitHub Secrets and injected during CI/CD:

1. **GitHub Secrets Required:**
   - `TEST_PRO_LICENSE_JWT` - Pro tier license content
   - `TEST_ENTERPRISE_LICENSE_JWT` - Enterprise tier license content
   - `TEST_PRO_LICENSE_BROKEN_JWT` - Broken Pro license (for validation tests)
   - `TEST_ENTERPRISE_LICENSE_BROKEN_JWT` - Broken Enterprise license (for validation tests)

2. **CI Workflow Injection:**
   The `.github/workflows/ci.yml` creates `tests/licenses/*.jwt` files from secrets before running tests.

3. **License Validation:**
   CI tests use real JWT validation against `vault-prod-2026-01.pem` public key.

## Security Note

⚠️ **Never commit ANY license files to this repository**

The `.gitignore` file blocks all `*.jwt` files in `tests/licenses/` to prevent:
- License copying (undermines tier monetization)
- Unauthorized use of Pro/Enterprise features
- Accidental commits of production licenses

Test licenses should:
- Use test customer IDs (e.g., "test-pro-001")
- Use test organizations (e.g., "Test Organization")
- Be clearly marked as test licenses in metadata
- Have far-future expiration dates (2027+)
- **Only exist in GitHub Secrets, never in git history**
