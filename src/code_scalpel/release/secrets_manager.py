"""GitHub Actions secrets management and validation.

Handles management of secrets required for automated releases including:
- PyPI tokens
- VS Code Marketplace tokens
- Docker registry credentials
- GitHub tokens

Features:
- Secret validation
- Environment variable management
- Secret rotation tracking
- Secure credential handling
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional


@dataclass
class Secret:
    """Represents a secret with metadata.

    Attributes:
        name: Name of the secret
        value: Secret value (masked in logs)
        type: Type of secret (pypi, vscode, docker, github)
        created_at: When the secret was created
        expires_at: When the secret expires (optional)
        environment: GitHub environment (prod, staging)
    """

    name: str
    value: str
    type: str
    created_at: datetime
    expires_at: Optional[datetime] = None
    environment: str = "prod"

    def __str__(self) -> str:
        """Return masked representation of secret."""
        if len(self.value) > 8:
            masked = self.value[:4] + "*" * (len(self.value) - 8) + self.value[-4:]
        else:
            masked = "*" * len(self.value)
        return f"{self.name} ({self.type}): {masked}"

    def is_expired(self) -> bool:
        """Check if secret has expired."""
        if not self.expires_at:
            return False
        return datetime.now() > self.expires_at

    def days_until_expiry(self) -> Optional[int]:
        """Get days until secret expires."""
        if not self.expires_at:
            return None
        delta = self.expires_at - datetime.now()
        return max(0, delta.days)


class SecretsManager:
    """Manage GitHub Actions secrets for release automation.

    Attributes:
        project_dir: Root directory of the project
        secrets: Dictionary of managed secrets
    """

    # Required secrets for releases
    REQUIRED_SECRETS = {
        "PYPI_TOKEN": ("pypi", "PyPI publishing token"),
        "VSCE_PAT": ("vscode", "VS Code Marketplace token"),
        "DOCKER_USERNAME": ("docker", "Docker Hub username"),
        "DOCKER_PASSWORD": ("docker", "Docker Hub password"),
        "GITHUB_TOKEN": ("github", "GitHub API token"),
    }

    # Optional secrets
    OPTIONAL_SECRETS = {
        "GHCR_TOKEN": ("docker", "GitHub Container Registry token"),
        "SLACK_WEBHOOK": ("notification", "Slack webhook for notifications"),
        "EMAIL_SERVICE_TOKEN": ("notification", "Email service token"),
    }

    def __init__(self, project_dir: str = "."):
        """Initialize secrets manager.

        Args:
            project_dir: Root directory of the project
        """
        self.project_dir = Path(project_dir).resolve()
        self.secrets: dict[str, Secret] = {}
        self._load_secrets_from_env()

    def _load_secrets_from_env(self) -> None:
        """Load secrets from environment variables."""
        all_secrets = {**self.REQUIRED_SECRETS, **self.OPTIONAL_SECRETS}

        for secret_name, (secret_type, description) in all_secrets.items():
            value = os.getenv(secret_name, "")
            if value:
                self.secrets[secret_name] = Secret(
                    name=secret_name,
                    value=value,
                    type=secret_type,
                    created_at=datetime.now(),
                    environment=os.getenv("GITHUB_ENVIRONMENT", "prod"),
                )

    def validate_secrets(self) -> dict[str, list[str]]:
        """Validate all required secrets are present.

        Returns:
            Dictionary with validation results:
                - missing: List of missing required secrets
                - present: List of present secrets
                - optional: List of optional secrets
                - invalid: List of secrets with issues
        """
        missing = []
        present = []
        optional = []
        invalid = []

        for secret_name, (secret_type, description) in self.REQUIRED_SECRETS.items():
            if secret_name not in self.secrets:
                missing.append(f"{secret_name} ({description})")
            else:
                if self.secrets[secret_name].is_expired():
                    invalid.append(f"{secret_name} (expired)")
                else:
                    present.append(secret_name)

        for secret_name, (secret_type, description) in self.OPTIONAL_SECRETS.items():
            if secret_name in self.secrets:
                if self.secrets[secret_name].is_expired():
                    invalid.append(f"{secret_name} (optional, expired)")
                else:
                    optional.append(secret_name)

        return {
            "missing": missing,
            "present": present,
            "optional": optional,
            "invalid": invalid,
        }

    def get_secret(self, name: str) -> Optional[str]:
        """Get a secret value by name.

        Args:
            name: Name of the secret

        Returns:
            Secret value or None if not found

        Raises:
            ValueError: If secret is expired
        """
        if name not in self.secrets:
            return None

        secret = self.secrets[name]
        if secret.is_expired():
            raise ValueError(f"Secret {name} has expired")

        return secret.value

    def set_secret(
        self,
        name: str,
        value: str,
        secret_type: str,
        expires_at: Optional[datetime] = None,
        environment: str = "prod",
    ) -> Secret:
        """Set a secret value.

        Args:
            name: Name of the secret
            value: Secret value
            secret_type: Type of secret
            expires_at: Expiration time (optional)
            environment: GitHub environment

        Returns:
            The created Secret object

        Raises:
            ValueError: If secret value is empty
        """
        if not value:
            raise ValueError(f"Secret value for {name} cannot be empty")

        secret = Secret(
            name=name,
            value=value,
            type=secret_type,
            created_at=datetime.now(),
            expires_at=expires_at,
            environment=environment,
        )

        self.secrets[name] = secret
        return secret

    def add_to_env(self, name: str) -> bool:
        """Add a secret to environment variables.

        Args:
            name: Name of the secret

        Returns:
            True if successful

        Raises:
            ValueError: If secret not found
        """
        if name not in self.secrets:
            raise ValueError(f"Secret {name} not found")

        secret = self.secrets[name]
        os.environ[name] = secret.value
        return True

    def export_secrets(self) -> dict[str, str]:
        """Export all non-expired secrets as environment dict.

        Returns:
            Dictionary of secret names to values
        """
        exported = {}
        for name, secret in self.secrets.items():
            if not secret.is_expired():
                exported[name] = secret.value
        return exported

    def get_expiry_report(self) -> dict[str, list[dict]]:
        """Get report of secrets expiring soon.

        Returns:
            Dictionary with expiry information:
                - expiring_soon: Secrets expiring within 30 days
                - expired: Expired secrets
                - valid: Secrets with no expiry or far in future
        """
        expiring_soon = []
        expired = []
        valid = []

        for name, secret in self.secrets.items():
            if secret.is_expired():
                expired.append(
                    {
                        "name": name,
                        "type": secret.type,
                        "expired_at": (
                            secret.expires_at.isoformat()
                            if secret.expires_at
                            else "unknown"
                        ),
                    }
                )
            elif secret.expires_at:
                days_left = secret.days_until_expiry()
                if days_left is not None and days_left < 30:
                    expiring_soon.append(
                        {
                            "name": name,
                            "type": secret.type,
                            "days_until_expiry": days_left,
                            "expires_at": secret.expires_at.isoformat(),
                        }
                    )
                else:
                    valid.append(
                        {
                            "name": name,
                            "type": secret.type,
                            "days_until_expiry": days_left,
                        }
                    )
            else:
                valid.append({"name": name, "type": secret.type, "expires": "never"})

        return {
            "expiring_soon": expiring_soon,
            "expired": expired,
            "valid": valid,
        }

    def get_status(self) -> dict[str, str | int]:
        """Get current secrets status.

        Returns:
            Dictionary with status information:
                - total_secrets: Total number of secrets
                - required_present: Number of required secrets present
                - required_total: Total required secrets
                - optional_present: Number of optional secrets present
                - validation_status: Overall validation status
        """
        validation = self.validate_secrets()

        return {
            "total_secrets": len(self.secrets),
            "required_present": len(validation["present"]),
            "required_total": len(self.REQUIRED_SECRETS),
            "optional_present": len(validation["optional"]),
            "invalid_count": len(validation["invalid"]),
            "validation_status": (
                "valid"
                if not validation["missing"] and not validation["invalid"]
                else "invalid"
            ),
        }
