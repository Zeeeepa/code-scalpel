"""Shared helpers for populating subprocess env dicts for license testing.

Use `populate_subprocess_env` in tests that spawn subprocesses and require a
particular license state. This keeps subprocess env setup consistent across
the test suite.
"""

from __future__ import annotations

from pathlib import Path
from typing import Literal

Tier = Literal[
    "community",
    "pro",
    "enterprise",
    "valid",
    "expired",
    "revoked",
    "missing",
]


def _find_test_license(tier: str) -> Path | None:
    from pathlib import Path

    project_root = Path(__file__).resolve().parents[2]
    license_dir = project_root / "tests" / "licenses"
    mapping = {
        "pro": ["code_scalpel_license_pro_20260101_190345.jwt"],
        "enterprise": ["code_scalpel_license_enterprise_20260101_190754.jwt"],
    }
    candidates = mapping.get(tier, [])
    for name in candidates:
        p = license_dir / name
        if p.exists():
            return p
    return None


def populate_subprocess_env(env: dict, tmp_path: Path, *, state: str = "valid") -> None:
    """Populate minimal license env vars for subprocesses.

    Args:
        env: dict passed to subprocess via `env=` parameter
        tmp_path: pytest tmp_path fixture to write transient license files if needed
        state: one of the Tier values
    """
    state = (state or "valid").lower()

    # Missing -> disable discovery and ensure no license path
    if state == "missing":
        env.pop("CODE_SCALPEL_LICENSE_PATH", None)
        env["CODE_SCALPEL_DISABLE_LICENSE_DISCOVERY"] = "1"
        env["CODE_SCALPEL_ALLOW_HS256"] = "0"
        env.pop("CODE_SCALPEL_SECRET_KEY", None)
        return

    # Revoked/expired require a signed JWT; generate simple HS256 test tokens using built-in generator
    from code_scalpel.licensing.jwt_generator import generate_license

    secret = "test-secret"
    algorithm = "HS256"

    if state in {"valid", "pro", "enterprise"}:
        tier = "enterprise" if state == "enterprise" else "pro"
        token = generate_license(
            tier=tier,
            customer_id="tests@example.com",
            duration_days=7,
            algorithm=algorithm,
            secret_key=secret,
            jti=f"subproc-{tier}",
        )
    elif state == "expired":
        token = generate_license(
            tier="pro",
            customer_id="tests@example.com",
            duration_days=-1,
            algorithm=algorithm,
            secret_key=secret,
            jti="subproc-expired",
        )
    elif state == "revoked":
        token = generate_license(
            tier="pro",
            customer_id="tests@example.com",
            duration_days=7,
            algorithm=algorithm,
            secret_key=secret,
            jti="subproc-revoked",
        )
    else:
        token = generate_license(
            tier="pro",
            customer_id="tests@example.com",
            duration_days=7,
            algorithm=algorithm,
            secret_key=secret,
            jti="subproc-valid",
        )

    lic_path = tmp_path / f"license_{state}.jwt"
    lic_path.write_text(token + "\n", encoding="utf-8")

    env["CODE_SCALPEL_ALLOW_HS256"] = "1"
    env["CODE_SCALPEL_SECRET_KEY"] = secret
    env["CODE_SCALPEL_LICENSE_PATH"] = str(lic_path)
    env.setdefault("CODE_SCALPEL_DISABLE_LICENSE_DISCOVERY", "1")
