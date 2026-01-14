#!/usr/bin/env python3
"""
Example: Creating and using cryptographic policy verification.

This demonstrates the administrator workflow for signing policy files
and the agent workflow for verifying them.

[20260114_BUGFIX] Uses temp directory to avoid conflicts with real .code-scalpel/ config.
"""

import os
import tempfile
from pathlib import Path
from code_scalpel.policy_engine.crypto_verify import (
    CryptographicPolicyVerifier,
    SecurityError,
)

# Use a temp directory for the demo to avoid permission issues
_TEMP_DIR = None


def get_demo_dir():
    """Get or create temp directory for demo."""
    global _TEMP_DIR
    if _TEMP_DIR is None:
        _TEMP_DIR = tempfile.mkdtemp(prefix="code_scalpel_demo_")
    return Path(_TEMP_DIR)


def admin_workflow():
    """
    Administrator workflow: Sign policy files.

    This should be run by a human administrator with access to the signing secret.
    """
    print("=" * 70)
    print("ADMINISTRATOR WORKFLOW: Sign Policy Files")
    print("=" * 70)

    # Set up policy directory (in temp location for demo)
    policy_dir = get_demo_dir() / ".code-scalpel"
    policy_dir.mkdir(exist_ok=True)

    # Create example policy files
    (policy_dir / "policy.yaml").write_text(
        """
# Code Scalpel Policy Configuration
version: "1.0"

rules:
  - id: no_sql_injection
    severity: high
    message: "SQL injection patterns detected"
  
  - id: no_command_injection
    severity: high
    message: "Command injection patterns detected"
"""
    )

    (policy_dir / "budget.yaml").write_text(
        """
# Budget constraints for agent operations
max_files_read: 100
max_tokens_per_session: 50000
max_api_calls_per_hour: 1000
"""
    )

    print(f"✓ Created policy files in {policy_dir}/")

    # Get or generate signing secret
    secret = os.environ.get("SCALPEL_MANIFEST_SECRET")
    if not secret:
        import secrets

        secret = secrets.token_urlsafe(32)
        print("\n⚠️  No SCALPEL_MANIFEST_SECRET set. Generated new secret:")
        print(f"   {secret}")
        print("\n   Save this secret securely! Add to environment:")
        print(f"   export SCALPEL_MANIFEST_SECRET='{secret}'")

    # Create signed manifest
    manifest = CryptographicPolicyVerifier.create_manifest(
        policy_files=["policy.yaml", "budget.yaml"],
        secret_key=secret,
        signed_by="admin@example.com",
        policy_dir=str(policy_dir),
    )

    # Save manifest
    manifest_path = CryptographicPolicyVerifier.save_manifest(
        manifest,
        str(policy_dir),
    )

    print(f"\n✓ Created signed manifest: {manifest_path}")
    print(f"  Version: {manifest.version}")
    print(f"  Signed by: {manifest.signed_by}")
    print("  Files:")
    for filename, file_hash in manifest.files.items():
        if isinstance(file_hash, dict):
            file_hash = file_hash["hash"]
        print(f"    - {filename}: {file_hash[:48]}...")
    print(f"  Signature: hmac-sha256:{manifest.signature[:32]}...")

    print(f"\n✓ Manifest saved to {manifest_path}")
    print("\n📋 Next steps:")
    print(
        f"   1. Commit the manifest to git: git add {manifest_path} && git commit -m 'Add signed policy manifest'"
    )
    print("   2. Set SCALPEL_MANIFEST_SECRET in agent environment (CI/CD secret)")
    print("   3. Agents will verify policy integrity before operations")

    return manifest


def agent_workflow(manifest_source="file"):
    """
    Agent workflow: Verify policy integrity before operations.

    This would be run by an AI agent before performing any operations.
    """
    print("\n" + "=" * 70)
    print("AGENT WORKFLOW: Verify Policy Integrity")
    print("=" * 70)

    # Check for signing secret
    if "SCALPEL_MANIFEST_SECRET" not in os.environ:
        print("❌ SCALPEL_MANIFEST_SECRET not set. Cannot verify policies.")
        print("   Operations DENIED (fail closed).")
        return False

    print("✓ Signing secret found in environment")

    # Use demo directory
    policy_dir = get_demo_dir() / ".code-scalpel"

    try:
        # Create verifier
        verifier = CryptographicPolicyVerifier(
            manifest_source=manifest_source,  # "file", "git", or "env"
            policy_dir=str(policy_dir),
        )

        print(f"✓ Loaded manifest from source: {manifest_source}")

        # Verify all policies
        result = verifier.verify_all_policies()

        if result.success:
            print("\n✅ Policy integrity verified successfully!")
            print(f"   Files verified: {result.files_verified}")
            print(f"   Manifest valid: {result.manifest_valid}")
            print("\n   Agent may proceed with operations.")
            return True
        else:
            print("\n❌ Policy verification FAILED!")
            print(f"   Error: {result.error}")
            print("   Operations DENIED (fail closed).")
            return False

    except SecurityError as e:
        print(f"\n❌ SECURITY ERROR: {e}")
        print("   Operations DENIED (fail closed).")
        return False


def tamper_detection_demo():
    """
    Demonstrate tamper detection.

    This shows what happens when someone modifies a policy file.
    """
    print("\n" + "=" * 70)
    print("TAMPER DETECTION DEMO")
    print("=" * 70)

    # Use demo directory
    policy_dir = get_demo_dir() / ".code-scalpel"
    policy_file = policy_dir / "policy.yaml"

    # Save original content
    original_content = policy_file.read_text()

    try:
        # Tamper with policy
        policy_file.write_text(original_content + "\n# TAMPERED BY ATTACKER\n")
        print("⚠️  Simulating attacker tampering with policy.yaml...")

        # Try to verify
        print("\nAgent attempting to verify policy integrity...")

        try:
            verifier = CryptographicPolicyVerifier(
                manifest_source="file",
                policy_dir=str(policy_dir),
            )
            result = verifier.verify_all_policies()

            print("❌ ERROR: Tamper should have been detected!")

        except SecurityError as e:
            print("\n✅ Tamper detected correctly!")
            print(f"   {e}")
            print("\n   Agent operations blocked (fail closed).")

    finally:
        # Restore original content
        policy_file.write_text(original_content)
        print("\n✓ Restored original policy file")


if __name__ == "__main__":
    # Step 1: Administrator signs policies
    manifest = admin_workflow()

    # Step 2: Agent verifies policies
    agent_workflow("file")

    # Step 3: Demonstrate tamper detection
    tamper_detection_demo()

    print("\n" + "=" * 70)
    print("EXAMPLE COMPLETE")
    print("=" * 70)
    print("\n📚 Key Takeaways:")
    print("   • Administrators sign policy files with HMAC-SHA256")
    print("   • Manifests track file hashes and are cryptographically signed")
    print("   • Agents verify integrity before operations (fail closed)")
    print("   • Any tampering is immediately detected")
    print("   • Works across all tiers (Community/Pro/Enterprise)")
