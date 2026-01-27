"""Tests for rollback and hotfix workflow system."""

from __future__ import annotations

from datetime import datetime

import pytest

from code_scalpel.release.rollback_manager import (
    Hotfix,
    RollbackManager,
    RollbackPoint,
)


class TestRollbackPoint:
    """Test RollbackPoint class."""

    def test_create_rollback_point(self):
        """Test creating a rollback point."""
        point = RollbackPoint(
            version="1.0.0",
            commit_hash="abc123",
            timestamp=datetime.now(),
        )
        assert point.version == "1.0.0"
        assert point.commit_hash == "abc123"
        assert point.is_stable

    def test_rollback_point_to_dict(self):
        """Test converting rollback point to dict."""
        now = datetime.now()
        point = RollbackPoint(
            version="1.0.0",
            commit_hash="hash123",
            timestamp=now,
            description="Initial release",
        )
        result = point.to_dict()
        assert result["version"] == "1.0.0"
        assert result["commit_hash"] == "hash123"


class TestHotfix:
    """Test Hotfix class."""

    def test_create_hotfix(self):
        """Test creating a hotfix."""
        hotfix = Hotfix(
            hotfix_version="1.0.1",
            target_version="1.0.0",
            created_at=datetime.now(),
        )
        assert hotfix.hotfix_version == "1.0.1"
        assert hotfix.target_version == "1.0.0"
        assert hotfix.status == "created"

    def test_hotfix_to_dict(self):
        """Test converting hotfix to dict."""
        now = datetime.now()
        hotfix = Hotfix(
            hotfix_version="1.0.1",
            target_version="1.0.0",
            created_at=now,
            description="Security fix",
        )
        result = hotfix.to_dict()
        assert result["hotfix_version"] == "1.0.1"
        assert result["target_version"] == "1.0.0"


class TestRollbackManagerInit:
    """Test RollbackManager initialization."""

    def test_init_with_defaults(self):
        """Test initializing with defaults."""
        manager = RollbackManager()
        assert manager.project_dir.is_absolute()
        assert len(manager.rollback_points) == 0
        assert len(manager.hotfixes) == 0

    def test_init_with_custom_project_dir(self, tmp_path):
        """Test initializing with custom project dir."""
        manager = RollbackManager(str(tmp_path))
        assert manager.project_dir == tmp_path.resolve()


class TestRollbackManagerRollbackPoints:
    """Test rollback point management."""

    def test_add_rollback_point(self):
        """Test adding a rollback point."""
        manager = RollbackManager()
        point = manager.add_rollback_point("1.0.0", "abc123")
        assert len(manager.rollback_points) == 1
        assert point.version == "1.0.0"

    def test_add_multiple_rollback_points(self):
        """Test adding multiple rollback points."""
        manager = RollbackManager()
        manager.add_rollback_point("1.0.0", "hash1")
        manager.add_rollback_point("1.1.0", "hash2")
        manager.add_rollback_point("2.0.0", "hash3")
        assert len(manager.rollback_points) == 3

    def test_list_rollback_points(self):
        """Test listing rollback points."""
        manager = RollbackManager()
        manager.add_rollback_point("1.0.0", "hash1")
        manager.add_rollback_point("1.1.0", "hash2")
        points = manager.list_rollback_points()
        assert len(points) == 2
        # Should be sorted newest first
        assert points[0].version == "1.1.0"

    def test_list_stable_rollback_points(self):
        """Test listing only stable rollback points."""
        manager = RollbackManager()
        manager.add_rollback_point("1.0.0", "hash1", is_stable=True)
        manager.add_rollback_point("1.1.0", "hash2", is_stable=False)
        points = manager.list_rollback_points(stable_only=True)
        assert len(points) == 1
        assert points[0].version == "1.0.0"

    def test_get_rollback_point(self):
        """Test getting a specific rollback point."""
        manager = RollbackManager()
        manager.add_rollback_point("1.0.0", "hash1")
        point = manager.get_rollback_point("1.0.0")
        assert point is not None
        assert point.version == "1.0.0"

    def test_get_nonexistent_rollback_point(self):
        """Test getting non-existent rollback point returns None."""
        manager = RollbackManager()
        assert manager.get_rollback_point("1.0.0") is None

    def test_can_rollback_to_stable_version(self):
        """Test checking if can rollback to stable version."""
        manager = RollbackManager()
        manager.add_rollback_point("1.0.0", "hash1", is_stable=True)
        assert manager.can_rollback_to("1.0.0")

    def test_cannot_rollback_to_unstable_version(self):
        """Test checking if cannot rollback to unstable version."""
        manager = RollbackManager()
        manager.add_rollback_point("1.0.0", "hash1", is_stable=False)
        assert not manager.can_rollback_to("1.0.0")

    def test_get_latest_stable_version(self):
        """Test getting latest stable version."""
        manager = RollbackManager()
        manager.add_rollback_point("1.0.0", "hash1", is_stable=True)
        manager.add_rollback_point("1.1.0", "hash2", is_stable=False)
        manager.add_rollback_point("1.2.0", "hash3", is_stable=True)
        latest = manager.get_latest_stable_version()
        assert latest is not None
        assert latest.version == "1.2.0"


class TestRollbackManagerRollback:
    """Test rollback operations."""

    def test_rollback_to_version(self):
        """Test rolling back to a version."""
        manager = RollbackManager()
        manager.add_rollback_point("1.0.0", "abc123")
        result = manager.rollback_to_version("1.0.0", reason="Bug fix")
        assert result["to_version"] == "1.0.0"
        assert result["status"] == "completed"
        assert result["reason"] == "Bug fix"

    def test_rollback_to_nonexistent_version_raises_error(self):
        """Test rolling back to non-existent version raises error."""
        manager = RollbackManager()
        with pytest.raises(ValueError):
            manager.rollback_to_version("1.0.0")

    def test_rollback_adds_to_history(self):
        """Test that rollback is recorded in history."""
        manager = RollbackManager()
        manager.add_rollback_point("1.0.0", "hash1")
        manager.rollback_to_version("1.0.0")
        history = manager.get_rollback_history()
        assert len(history) == 1
        assert history[0]["to_version"] == "1.0.0"

    def test_multiple_rollbacks_recorded(self):
        """Test multiple rollbacks are recorded."""
        manager = RollbackManager()
        manager.add_rollback_point("1.0.0", "hash1")
        manager.add_rollback_point("1.1.0", "hash2")
        manager.rollback_to_version("1.0.0")
        manager.rollback_to_version("1.1.0")
        history = manager.get_rollback_history()
        assert len(history) == 2


class TestRollbackManagerHotfix:
    """Test hotfix management."""

    def test_create_hotfix(self):
        """Test creating a hotfix."""
        manager = RollbackManager()
        manager.add_rollback_point("1.0.0", "hash1")
        hotfix = manager.create_hotfix("1.0.0", "Security patch")
        assert hotfix.hotfix_version == "1.0.1"
        assert hotfix.target_version == "1.0.0"
        assert hotfix.description == "Security patch"

    def test_create_hotfix_for_nonexistent_version_raises_error(self):
        """Test creating hotfix for non-existent version raises error."""
        manager = RollbackManager()
        with pytest.raises(ValueError):
            manager.create_hotfix("1.0.0")

    def test_create_hotfix_calculates_version(self):
        """Test hotfix version is calculated correctly."""
        manager = RollbackManager()
        manager.add_rollback_point("2.3.5", "hash1")
        hotfix = manager.create_hotfix("2.3.5")
        assert hotfix.hotfix_version == "2.3.6"

    def test_create_hotfix_with_two_part_version(self):
        """Test hotfix version calculation for two-part version."""
        manager = RollbackManager()
        manager.add_rollback_point("1.0", "hash1")
        hotfix = manager.create_hotfix("1.0")
        assert hotfix.hotfix_version == "1.0.1"

    def test_list_hotfixes(self):
        """Test listing hotfixes."""
        manager = RollbackManager()
        manager.add_rollback_point("1.0.0", "hash1")
        manager.add_rollback_point("1.1.0", "hash2")
        manager.create_hotfix("1.0.0")
        manager.create_hotfix("1.1.0")
        hotfixes = manager.list_hotfixes()
        assert len(hotfixes) == 2

    def test_list_hotfixes_by_target_version(self):
        """Test listing hotfixes filtered by target version."""
        manager = RollbackManager()
        manager.add_rollback_point("1.0.0", "hash1")
        manager.add_rollback_point("1.1.0", "hash2")
        manager.create_hotfix("1.0.0")
        manager.create_hotfix("1.1.0")
        hotfixes = manager.list_hotfixes(target_version="1.0.0")
        assert len(hotfixes) == 1
        assert hotfixes[0].target_version == "1.0.0"

    def test_apply_hotfix(self):
        """Test applying a hotfix."""
        manager = RollbackManager()
        manager.add_rollback_point("1.0.0", "hash1")
        hotfix = manager.create_hotfix("1.0.0")
        result = manager.apply_hotfix(hotfix.hotfix_version)
        assert result["status"] == "applied"

    def test_apply_nonexistent_hotfix_raises_error(self):
        """Test applying non-existent hotfix raises error."""
        manager = RollbackManager()
        with pytest.raises(ValueError):
            manager.apply_hotfix("1.0.1")


class TestRollbackManagerHistory:
    """Test history management."""

    def test_get_rollback_history(self):
        """Test getting rollback history."""
        manager = RollbackManager()
        manager.add_rollback_point("1.0.0", "hash1")
        manager.rollback_to_version("1.0.0")
        history = manager.get_rollback_history()
        assert len(history) == 1

    def test_clear_history(self):
        """Test clearing rollback history."""
        manager = RollbackManager()
        manager.add_rollback_point("1.0.0", "hash1")
        manager.rollback_to_version("1.0.0")
        assert len(manager.get_rollback_history()) == 1
        manager.clear_history()
        assert len(manager.get_rollback_history()) == 0
