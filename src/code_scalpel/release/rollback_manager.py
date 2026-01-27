"""Release rollback and hotfix workflow management.

Provides rollback and hotfix functionality for release automation including:
- Rollback to previous versions
- Hotfix workflow support
- Rollback point management
- Hotfix tracking and history
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Optional


class RollbackStatus(str, Enum):
    """Status of a rollback operation."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"


@dataclass
class RollbackPoint:
    """Represents a point in history that can be rolled back to.

    Attributes:
        version: Version number
        commit_hash: Git commit hash
        timestamp: When this version was released
        description: Release description
        is_stable: Whether this is a stable release
    """

    version: str
    commit_hash: str
    timestamp: datetime
    description: str = ""
    is_stable: bool = True

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "version": self.version,
            "commit_hash": self.commit_hash,
            "timestamp": self.timestamp.isoformat(),
            "description": self.description,
            "is_stable": self.is_stable,
        }


@dataclass
class Hotfix:
    """Represents a hotfix for a released version.

    Attributes:
        hotfix_version: Hotfix version (e.g., 1.0.1)
        target_version: Version being fixed (e.g., 1.0.0)
        created_at: When hotfix was created
        branch_name: Git branch name for hotfix
        status: Current status
        description: Hotfix description
    """

    hotfix_version: str
    target_version: str
    created_at: datetime
    branch_name: str = ""
    status: str = "created"
    description: str = ""

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "hotfix_version": self.hotfix_version,
            "target_version": self.target_version,
            "created_at": self.created_at.isoformat(),
            "branch_name": self.branch_name,
            "status": self.status,
            "description": self.description,
        }


class RollbackManager:
    """Manage release rollbacks and hotfix workflows.

    Provides methods for:
    - Rolling back to previous versions
    - Managing rollback points
    - Creating and tracking hotfixes
    - Hotfix workflow management
    """

    def __init__(self, project_dir: str = "."):
        """Initialize rollback manager.

        Args:
            project_dir: Root directory of the project
        """
        self.project_dir = Path(project_dir).resolve()
        self.rollback_points: list[RollbackPoint] = []
        self.hotfixes: list[Hotfix] = []
        self.rollback_history: list[dict] = []

    def add_rollback_point(
        self,
        version: str,
        commit_hash: str,
        description: str = "",
        is_stable: bool = True,
    ) -> RollbackPoint:
        """Add a rollback point.

        Args:
            version: Version number
            commit_hash: Git commit hash
            description: Optional description
            is_stable: Whether this is a stable release

        Returns:
            Created rollback point
        """
        point = RollbackPoint(
            version=version,
            commit_hash=commit_hash,
            timestamp=datetime.now(),
            description=description,
            is_stable=is_stable,
        )
        self.rollback_points.append(point)
        return point

    def list_rollback_points(self, stable_only: bool = False) -> list[RollbackPoint]:
        """List available rollback points.

        Args:
            stable_only: Only return stable releases

        Returns:
            List of rollback points sorted by timestamp (newest first)
        """
        points = self.rollback_points
        if stable_only:
            points = [p for p in points if p.is_stable]
        return sorted(points, key=lambda p: p.timestamp, reverse=True)

    def get_rollback_point(self, version: str) -> Optional[RollbackPoint]:
        """Get a specific rollback point.

        Args:
            version: Version to find

        Returns:
            Rollback point if found
        """
        for point in self.rollback_points:
            if point.version == version:
                return point
        return None

    def rollback_to_version(self, version: str, reason: str = "") -> dict:
        """Execute rollback to a specific version.

        Args:
            version: Version to roll back to
            reason: Reason for rollback

        Returns:
            Rollback status information

        Raises:
            ValueError: If version not found
        """
        point = self.get_rollback_point(version)
        if not point:
            raise ValueError(f"No rollback point found for version {version}")

        rollback_info = {
            "from_version": "current",
            "to_version": version,
            "commit_hash": point.commit_hash,
            "timestamp": datetime.now().isoformat(),
            "status": RollbackStatus.COMPLETED.value,
            "reason": reason,
        }

        self.rollback_history.append(rollback_info)
        return rollback_info

    def create_hotfix(
        self,
        target_version: str,
        hotfix_description: str = "",
    ) -> Hotfix:
        """Create a hotfix for a version.

        Args:
            target_version: Version to create hotfix for
            hotfix_description: Description of the hotfix

        Returns:
            Created hotfix

        Raises:
            ValueError: If target version not found
        """
        point = self.get_rollback_point(target_version)
        if not point:
            raise ValueError(f"Target version {target_version} not found")

        # Calculate hotfix version
        parts = target_version.split(".")
        if len(parts) >= 3:
            hotfix_version = f"{parts[0]}.{parts[1]}.{int(parts[2]) + 1}"
        else:
            hotfix_version = f"{target_version}.1"

        hotfix = Hotfix(
            hotfix_version=hotfix_version,
            target_version=target_version,
            created_at=datetime.now(),
            branch_name=f"hotfix/{hotfix_version}",
            description=hotfix_description,
        )

        self.hotfixes.append(hotfix)
        return hotfix

    def apply_hotfix(self, hotfix_version: str) -> dict:
        """Apply a hotfix.

        Args:
            hotfix_version: Version of hotfix to apply

        Returns:
            Application status

        Raises:
            ValueError: If hotfix not found
        """
        hotfix = None
        for h in self.hotfixes:
            if h.hotfix_version == hotfix_version:
                hotfix = h
                break

        if not hotfix:
            raise ValueError(f"Hotfix {hotfix_version} not found")

        hotfix.status = "applied"
        return {
            "hotfix_version": hotfix_version,
            "status": "applied",
            "timestamp": datetime.now().isoformat(),
        }

    def list_hotfixes(self, target_version: Optional[str] = None) -> list[Hotfix]:
        """List hotfixes.

        Args:
            target_version: Optional filter by target version

        Returns:
            List of hotfixes
        """
        hotfixes = self.hotfixes
        if target_version:
            hotfixes = [h for h in hotfixes if h.target_version == target_version]
        return sorted(hotfixes, key=lambda h: h.created_at, reverse=True)

    def get_rollback_history(self) -> list[dict]:
        """Get rollback history.

        Returns:
            List of rollback operations
        """
        return self.rollback_history.copy()

    def can_rollback_to(self, version: str) -> bool:
        """Check if version can be rolled back to.

        Args:
            version: Version to check

        Returns:
            True if rollback is possible
        """
        point = self.get_rollback_point(version)
        return point is not None and point.is_stable

    def get_latest_stable_version(self) -> Optional[RollbackPoint]:
        """Get the latest stable version.

        Returns:
            Latest stable rollback point
        """
        stable_points = [p for p in self.rollback_points if p.is_stable]
        if not stable_points:
            return None
        return max(stable_points, key=lambda p: p.timestamp)

    def clear_history(self) -> None:
        """Clear rollback history."""
        self.rollback_history.clear()
