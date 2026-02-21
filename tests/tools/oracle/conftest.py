"""Fixtures and configuration for Oracle tests."""

from __future__ import annotations

import pytest
from pathlib import Path
from unittest.mock import patch


@pytest.fixture(autouse=True)
def patch_response_config():
    """Patch response config to use debug profile for oracle tests.

    This ensures that all envelope fields (tool_id, tier, etc.) are included
    in the response, which the oracle tests assert on.
    """
    from code_scalpel.mcp.response_config import ResponseConfig

    class DebugResponseConfig(ResponseConfig):
        def get_envelope_fields(self, tool_name=None):
            return {
                "tier",
                "tool_version",
                "tool_id",
                "request_id",
                "capabilities",
                "duration_ms",
                "error",
                "upgrade_hints",
            }

    with patch(
        "code_scalpel.mcp.contract.get_response_config",
        return_value=DebugResponseConfig(),
    ):
        yield


@pytest.fixture
def sample_auth_file(tmp_path: Path) -> Path:
    """Create a sample auth.py file for testing.

    Returns:
        Path to sample file
    """
    auth_py = tmp_path / "auth.py"
    auth_py.write_text(
        """
from typing import Optional
from datetime import datetime


class User:
    \"\"\"User model.\"\"\"

    def __init__(self, id: int, email: str):
        self.id = id
        self.email = email
        self.created_at = datetime.utcnow()

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "email": self.email,
        }


def validate_email(email: str) -> bool:
    \"\"\"Validate email format.\"\"\"
    return "@" in email


def hash_password(password: str) -> str:
    \"\"\"Hash a password.\"\"\"
    return password
"""
    )
    return auth_py


@pytest.fixture
def sample_models_file(tmp_path: Path) -> Path:
    """Create a sample models.py file for testing.

    Returns:
        Path to sample file
    """
    models_py = tmp_path / "models.py"
    models_py.write_text(
        """
from typing import List


class BaseModel:
    pass


class User(BaseModel):
    \"\"\"User ORM model.\"\"\"

    def __init__(self, id: int, email: str):
        self.id = id
        self.email = email

    @classmethod
    def from_dict(cls, data: dict) -> "User":
        return cls(id=data["id"], email=data["email"])
"""
    )
    return models_py


@pytest.fixture
def sample_project(tmp_path: Path) -> Path:
    """Create a sample project structure.

    Returns:
        Path to project root
    """
    src = tmp_path / "src"
    src.mkdir()

    # Create auth.py
    (src / "auth.py").write_text(
        """
from typing import Optional


def validate_token(token: str) -> Optional[dict]:
    \"\"\"Validate JWT token.\"\"\"
    return None


def encode_token(user_id: int) -> str:
    \"\"\"Encode JWT token.\"\"\"
    return ""
"""
    )

    # Create models.py
    (src / "models.py").write_text(
        """
class User:
    def __init__(self, id: int, email: str):
        self.id = id
        self.email = email
"""
    )

    return tmp_path
