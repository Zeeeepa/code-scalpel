# PyPI Trusted Publisher Setup for v1.1.0 Release

## Current Status

The v1.1.0 release is **ready to publish** but is blocked by a missing PyPI Trusted Publisher configuration.

**What's Done:**
- ✅ All code fixes complete (4 fixes applied)
- ✅ Documentation generated (MCP tools reference)
- ✅ Version updated to 1.1.0
- ✅ Tag created and pushed to GitHub
- ✅ Build succeeds locally and in CI
- ✅ GitHub Actions workflow triggers correctly

**What's Blocking:**
- ❌ PyPI does not have a Trusted Publisher configured for this repository
- The workflow runs successfully but fails at the PyPI authentication step

## Error Details

```
Trusted publishing exchange failure:
Token request failed: the server refused the request for the following reasons:
* `invalid-publisher`: valid token, but no corresponding publisher 
  (Publisher with matching claims was not found)
```

**Current Claims from GitHub Actions:**
```
* repository: 3D-Tech-Solutions/code-scalpel
* repository_owner: 3D-Tech-Solutions
* workflow_ref: 3D-Tech-Solutions/code-scalpel/.github/workflows/publish-pypi.yml@refs/tags/v1.1.0
* environment: release
```

## Solution: Configure PyPI Trusted Publisher

### Step 1: Log Into PyPI

1. Go to: https://pypi.org/account/login/
2. Log in with the account that owns the `codescalpel` project
   - **Note:** This must be the account that originally created the `codescalpel` package

### Step 2: Navigate to Project Publishing Settings

1. Go to the PyPI project page: https://pypi.org/project/codescalpel/
2. Click on your username/account menu (top right)
3. Select "Account"
4. Look for "Publishing" section on the left sidebar
5. OR directly visit: https://pypi.org/manage/project/codescalpel/publishing/

### Step 3: Add a New Trusted Publisher

1. Click "Add a new trusted publisher" (or similar button)
2. Select "GitHub" as the publisher type
3. Fill in the following fields **EXACTLY as shown**:
   ```
   GitHub Owner:      3D-Tech-Solutions
   Repository Name:   code-scalpel
   Workflow Name:     publish-pypi.yml
   Environment Name:  release
   ```

**Important:** 
- The field names may vary slightly (e.g., "Organization" vs "Owner", "Repo" vs "Repository Name")
- Match the values EXACTLY as shown above
- All four fields are required

### Step 4: Save the Configuration

1. Click "Save" or "Add Publisher"
2. You should see a confirmation that the trusted publisher was created
3. The publisher should now appear in a list with status "Active"

### Step 5: Verify the Configuration

Once saved, the page should show something like:

```
GitHub Trusted Publisher
├─ Owner: 3D-Tech-Solutions
├─ Repository: code-scalpel
├─ Workflow: publish-pypi.yml
└─ Environment: release
   Status: Active
```

## Step 6: Re-run the Failed Workflow

Now that the trusted publisher is configured, re-run the failed workflow:

### Option A: GitHub CLI (Recommended)
```bash
gh run rerun 21372178996
```

### Option B: GitHub Web UI
1. Go to: https://github.com/3D-Tech-Solutions/code-scalpel/actions
2. Find the "Publish to PyPI" workflow run that failed
3. Click "Re-run failed jobs"
4. Click "Re-run jobs" in the dialog

### Option C: Wait for Auto-Retry
GitHub Actions may automatically retry after ~5-10 minutes. Check the workflow status.

## What Happens After Configuration

Once the trusted publisher is configured and the workflow re-runs:

1. **PyPI Publication (~1-2 minutes)**
   - The `codescalpel` package version 1.1.0 will be published to PyPI
   - Artifact: `codescalpel-1.1.0-py3-none-any.whl` and `codescalpel-1.1.0.tar.gz`

2. **GitHub Release (Automatic)**
   - A GitHub release page will be created at: https://github.com/3D-Tech-Solutions/code-scalpel/releases/tag/v1.1.0
   - Release notes will be included from: `docs/release_notes/RELEASE_NOTES_v1.1.0.md`

3. **VS Code Extension (Automatic)**
   - The VS Code extension will be published to the marketplace
   - Users can install it directly from VS Code

## Verification Checklist

After the workflow completes successfully:

- [ ] Check PyPI package page: https://pypi.org/project/codescalpel/
- [ ] Verify version 1.1.0 is listed
- [ ] Test local installation: `pip install codescalpel==1.1.0`
- [ ] Check GitHub Release: https://github.com/3D-Tech-Solutions/code-scalpel/releases/tag/v1.1.0
- [ ] Verify release notes are populated
- [ ] Check VS Code Marketplace (if applicable)

## Troubleshooting

### "Add trusted publisher" button not found
- Make sure you're logged in as the account that owns the `codescalpel` project
- You need to have admin or owner permissions for the project
- Check that you're on the correct PyPI project page

### Still getting "invalid-publisher" error after adding the trusted publisher
1. Double-check all field values match exactly (case-sensitive):
   - Owner: `3D-Tech-Solutions` (with hyphens, capital D and T)
   - Repository: `code-scalpel` (with hyphen)
   - Workflow: `publish-pypi.yml` (exact name)
   - Environment: `release` (lowercase)

2. Wait 1-2 minutes after saving for the configuration to propagate in PyPI's systems

3. Check that GitHub Actions can access the repository (usually automatic)

4. View the workflow logs for the exact claims being sent from GitHub Actions

### PyPI shows "invalid-publisher" but the fields look correct
- The configuration may not have been saved properly
- Try deleting and re-adding the trusted publisher
- Verify you clicked "Save" or "Add" and received a confirmation

## Important Notes

- **One-time setup:** This configuration only needs to be done once. All future releases to v2.0.0+, v3.0.0+, etc., will reuse this trusted publisher.
- **Package name:** PyPI package is `codescalpel` (no hyphen), but GitHub repo is `code-scalpel` (with hyphen)
- **Security:** Using Trusted Publishers is more secure than storing PyPI API tokens as GitHub Secrets

## References

- PyPI Trusted Publishing Docs: https://docs.pypi.org/trusted-publishers/
- PyPI Trusted Publishing Troubleshooting: https://docs.pypi.org/trusted-publishers/troubleshooting/
- GitHub Actions OIDC Configuration: https://docs.github.com/en/actions/deployment/security-hardening-your-deployments/about-security-hardening-with-openid-connect

## Support

If you encounter any issues:

1. Check the PyPI troubleshooting guide: https://docs.pypi.org/trusted-publishers/troubleshooting/
2. Review the GitHub Actions workflow logs: https://github.com/3D-Tech-Solutions/code-scalpel/actions/runs/21372178996
3. Verify the workflow YAML configuration: `.github/workflows/publish-pypi.yml`
