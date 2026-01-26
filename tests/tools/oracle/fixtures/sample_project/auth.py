"""Sample auth module for testing Oracle."""

from typing import Optional
from datetime import datetime


class User:
    """User model."""

    def __init__(self, id: int, email: str):
        """Initialize user.

        Args:
            id: User ID
            email: User email
        """
        self.id = id
        self.email = email
        self.created_at = datetime.utcnow()

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "email": self.email,
            "created_at": self.created_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "User":
        """Create from dictionary."""
        return cls(id=data["id"], email=data["email"])


def get_user_by_id(user_id: int) -> Optional[User]:
    """Get user by ID.

    Args:
        user_id: User ID to lookup

    Returns:
        User if found, None otherwise
    """
    # Placeholder
    return None


def validate_email(email: str) -> bool:
    """Validate email format.

    Args:
        email: Email to validate

    Returns:
        True if valid
    """
    return "@" in email and "." in email.split("@")[1]


def hash_password(password: str) -> str:
    """Hash a password.

    Args:
        password: Password to hash

    Returns:
        Hashed password
    """
    # Placeholder
    return password
