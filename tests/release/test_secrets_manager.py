"""Tests for GitHub Actions secrets management system."""

from __future__ import annotations

import os
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import patch

import pytest

from code_scalpel.release.secrets_manager import Secret, SecretsManager


class TestSecretDataclass:
    """Test Secret dataclass."""

    def test_secret_creation(self):
        """Test creating a secret."""
        secret = Secret(
            name="TEST_TOKEN",
            value="secret_value_12345",
            type="test",
            created_at=datetime.now(),
        )
        assert secret.name == "TEST_TOKEN"
        assert secret.value == "secret_value_12345"
        assert secret.type == "test"
        assert secret.environment == "prod"

    def test_secret_string_representation_masks_value(self):
        """Test that secret values are masked in string representation."""
        secret = Secret(
            name="TEST_TOKEN",
            value="secret_value_12345",
            type="test",
            created_at=datetime.now(),
        )
        result = str(secret)
        assert "secret" not in result.lower() or "*" in result
        assert "TEST_TOKEN" in result

    def test_secret_short_value_fully_masked(self):
        """Test that short secrets are fully masked."""
        secret = Secret(
            name="SHORT",
            value="abc",
            type="test",
            created_at=datetime.now(),
        )
        result = str(secret)
        assert "***" in result

    def test_secret_is_not_expired_by_default(self):
        """Test that secrets without expiry are not expired."""
        secret = Secret(
            name="TEST",
            value="value",
            type="test",
            created_at=datetime.now(),
        )
        assert not secret.is_expired()

    def test_secret_is_expired_when_past_expiry_date(self):
        """Test that secrets are expired when past expiry date."""
        secret = Secret(
            name="TEST",
            value="value",
            type="test",
            created_at=datetime.now(),
            expires_at=datetime.now() - timedelta(days=1),
        )
        assert secret.is_expired()

    def test_secret_is_not_expired_before_expiry_date(self):
        """Test that secrets are not expired before expiry date."""
        secret = Secret(
            name="TEST",
            value="value",
            type="test",
            created_at=datetime.now(),
            expires_at=datetime.now() + timedelta(days=30),
        )
        assert not secret.is_expired()

    def test_secret_days_until_expiry(self):
        """Test calculating days until secret expiry."""
        secret = Secret(
            name="TEST",
            value="value",
            type="test",
            created_at=datetime.now(),
            expires_at=datetime.now() + timedelta(days=15),
        )
        days_left = secret.days_until_expiry()
        assert days_left is not None and 14 <= days_left <= 15  # Allow for rounding

    def test_secret_days_until_expiry_no_expiry(self):
        """Test that days_until_expiry returns None when no expiry."""
        secret = Secret(
            name="TEST",
            value="value",
            type="test",
            created_at=datetime.now(),
        )
        assert secret.days_until_expiry() is None


class TestSecretsManagerInit:
    """Test SecretsManager initialization."""

    def test_init_with_defaults(self):
        """Test initializing with default values."""
        manager = SecretsManager()
        assert manager.project_dir.exists()
        assert isinstance(manager.secrets, dict)

    def test_init_with_custom_project_dir(self):
        """Test initializing with custom project directory."""
        manager = SecretsManager(project_dir="/tmp")
        assert manager.project_dir == Path("/tmp").resolve()

    @patch.dict(os.environ, {"PYPI_TOKEN": "test_pypi_token"})
    def test_load_secrets_from_env(self):
        """Test loading secrets from environment variables."""
        manager = SecretsManager()
        assert "PYPI_TOKEN" in manager.secrets
        assert manager.secrets["PYPI_TOKEN"].value == "test_pypi_token"

    @patch.dict(
        os.environ,
        {
            "PYPI_TOKEN": "pypi_token",
            "DOCKER_USERNAME": "docker_user",
            "VSCE_PAT": "vsce_token",
        },
    )
    def test_load_multiple_secrets_from_env(self):
        """Test loading multiple secrets from environment."""
        manager = SecretsManager()
        assert len(manager.secrets) == 3
        assert manager.secrets["PYPI_TOKEN"].value == "pypi_token"
        assert manager.secrets["DOCKER_USERNAME"].value == "docker_user"
        assert manager.secrets["VSCE_PAT"].value == "vsce_token"


class TestSecretsManagerValidation:
    """Test SecretsManager validation."""

    @patch.dict(
        os.environ,
        {
            "PYPI_TOKEN": "pypi_token",
            "VSCE_PAT": "vsce_token",
            "DOCKER_USERNAME": "docker_user",
            "DOCKER_PASSWORD": "docker_pass",
            "GITHUB_TOKEN": "github_token",
        },
    )
    def test_validate_all_required_secrets_present(self):
        """Test validation when all required secrets are present."""
        manager = SecretsManager()
        result = manager.validate_secrets()
        assert len(result["missing"]) == 0
        assert len(result["present"]) == 5

    @patch.dict(os.environ, {})
    def test_validate_missing_required_secrets(self):
        """Test validation when required secrets are missing."""
        manager = SecretsManager()
        result = manager.validate_secrets()
        assert len(result["missing"]) > 0
        assert len(result["present"]) == 0

    @patch.dict(os.environ, {"PYPI_TOKEN": "token", "GHCR_TOKEN": "ghcr_token"})
    def test_validate_optional_secrets_present(self):
        """Test validation with optional secrets present."""
        manager = SecretsManager()
        result = manager.validate_secrets()
        assert "GHCR_TOKEN" in result["optional"]

    @patch.dict(os.environ, {"PYPI_TOKEN": "token"})
    def test_validate_expired_secret(self):
        """Test validation with expired secret."""
        manager = SecretsManager()
        manager.secrets["PYPI_TOKEN"].expires_at = datetime.now() - timedelta(days=1)
        result = manager.validate_secrets()
        assert any("PYPI_TOKEN" in item for item in result["invalid"])

    def test_validate_secrets_return_format(self):
        """Test that validate_secrets returns correct format."""
        manager = SecretsManager()
        result = manager.validate_secrets()
        assert "missing" in result
        assert "present" in result
        assert "optional" in result
        assert "invalid" in result


class TestSecretsManagerGetSecret:
    """Test SecretsManager get_secret method."""

    def test_get_existing_secret(self):
        """Test getting an existing secret."""
        manager = SecretsManager()
        manager.set_secret("TEST_SECRET", "secret_value", "test")
        value = manager.get_secret("TEST_SECRET")
        assert value == "secret_value"

    def test_get_nonexistent_secret(self):
        """Test getting a nonexistent secret."""
        manager = SecretsManager()
        value = manager.get_secret("NONEXISTENT")
        assert value is None

    def test_get_expired_secret_raises_error(self):
        """Test that getting an expired secret raises error."""
        manager = SecretsManager()
        manager.set_secret("EXPIRED", "value", "test")
        manager.secrets["EXPIRED"].expires_at = datetime.now() - timedelta(days=1)
        with pytest.raises(ValueError, match="expired"):
            manager.get_secret("EXPIRED")


class TestSecretsManagerSetSecret:
    """Test SecretsManager set_secret method."""

    def test_set_new_secret(self):
        """Test setting a new secret."""
        manager = SecretsManager()
        secret = manager.set_secret("NEW_SECRET", "new_value", "custom")
        assert secret.name == "NEW_SECRET"
        assert secret.value == "new_value"
        assert "NEW_SECRET" in manager.secrets

    def test_set_secret_with_expiry(self):
        """Test setting a secret with expiry date."""
        manager = SecretsManager()
        expires = datetime.now() + timedelta(days=30)
        secret = manager.set_secret(
            "EXPIRING_SECRET", "value", "custom", expires_at=expires
        )
        assert secret.expires_at == expires

    def test_set_secret_empty_value_raises_error(self):
        """Test that setting empty secret value raises error."""
        manager = SecretsManager()
        with pytest.raises(ValueError, match="cannot be empty"):
            manager.set_secret("EMPTY", "", "custom")

    def test_set_secret_overwrites_existing(self):
        """Test that setting a secret overwrites existing one."""
        manager = SecretsManager()
        manager.set_secret("TEST", "value1", "custom")
        manager.set_secret("TEST", "value2", "custom")
        assert manager.get_secret("TEST") == "value2"

    def test_set_secret_with_custom_environment(self):
        """Test setting a secret with custom environment."""
        manager = SecretsManager()
        secret = manager.set_secret(
            "STAGING_SECRET", "value", "custom", environment="staging"
        )
        assert secret.environment == "staging"


class TestSecretsManagerEnvHandling:
    """Test SecretsManager environment variable handling."""

    @patch.dict(os.environ, {}, clear=True)
    def test_add_secret_to_env(self):
        """Test adding a secret to environment variables."""
        manager = SecretsManager()
        manager.set_secret("TEST_ENV_VAR", "test_value", "custom")
        manager.add_to_env("TEST_ENV_VAR")
        assert os.environ["TEST_ENV_VAR"] == "test_value"

    def test_add_nonexistent_secret_to_env_raises_error(self):
        """Test that adding nonexistent secret to env raises error."""
        manager = SecretsManager()
        with pytest.raises(ValueError, match="not found"):
            manager.add_to_env("NONEXISTENT")

    @patch.dict(os.environ, {}, clear=True)
    def test_export_secrets(self):
        """Test exporting secrets."""
        manager = SecretsManager()
        manager.set_secret("SECRET1", "value1", "test")
        manager.set_secret("SECRET2", "value2", "test")
        exported = manager.export_secrets()
        assert "SECRET1" in exported
        assert "SECRET2" in exported
        assert exported["SECRET1"] == "value1"

    def test_export_secrets_excludes_expired(self):
        """Test that export_secrets excludes expired secrets."""
        manager = SecretsManager()
        manager.set_secret("TEST", "value", "test")
        manager.secrets["TEST"].expires_at = datetime.now() - timedelta(days=1)
        exported = manager.export_secrets()
        assert "TEST" not in exported


class TestSecretsManagerReporting:
    """Test SecretsManager reporting methods."""

    def test_get_expiry_report_empty(self):
        """Test expiry report when no secrets."""
        manager = SecretsManager()
        report = manager.get_expiry_report()
        assert "expiring_soon" in report
        assert "expired" in report
        assert "valid" in report

    def test_get_expiry_report_with_valid_secret(self):
        """Test expiry report with valid secret."""
        manager = SecretsManager()
        manager.set_secret("SECRET", "value", "test")
        report = manager.get_expiry_report()
        assert len(report["valid"]) > 0

    def test_get_expiry_report_expiring_soon(self):
        """Test expiry report with secret expiring soon."""
        manager = SecretsManager()
        manager.set_secret(
            "SOON", "value", "test", expires_at=datetime.now() + timedelta(days=15)
        )
        report = manager.get_expiry_report()
        assert len(report["expiring_soon"]) > 0

    def test_get_expiry_report_expired(self):
        """Test expiry report with expired secret."""
        manager = SecretsManager()
        manager.set_secret("EXPIRED", "value", "test")
        manager.secrets["EXPIRED"].expires_at = datetime.now() - timedelta(days=1)
        report = manager.get_expiry_report()
        assert len(report["expired"]) > 0

    @patch.dict(
        os.environ,
        {
            "PYPI_TOKEN": "token1",
            "VSCE_PAT": "token2",
            "DOCKER_USERNAME": "user",
            "DOCKER_PASSWORD": "pass",
            "GITHUB_TOKEN": "ghtoken",
        },
    )
    def test_get_status_all_required_present(self):
        """Test status when all required secrets present."""
        manager = SecretsManager()
        status = manager.get_status()
        assert status["required_present"] == 5
        assert status["required_total"] == 5
        assert status["validation_status"] == "valid"

    def test_get_status_missing_secrets(self):
        """Test status with missing secrets."""
        manager = SecretsManager()
        status = manager.get_status()
        required_present = status["required_present"]
        required_total = status["required_total"]
        assert isinstance(required_present, int) and isinstance(required_total, int)
        assert required_present < required_total
        assert status["validation_status"] == "invalid"

    @patch.dict(os.environ, {"PYPI_TOKEN": "value"})
    def test_get_status_with_invalid_secrets(self):
        """Test status with invalid (expired) secrets."""
        manager = SecretsManager()
        manager.secrets["PYPI_TOKEN"].expires_at = datetime.now() - timedelta(days=1)
        status = manager.get_status()
        invalid_count = status["invalid_count"]
        assert isinstance(invalid_count, int) and invalid_count > 0
        assert status["validation_status"] == "invalid"
