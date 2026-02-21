"""
Tests for config loader - TOML-based tier limits.

[20251225_FEATURE] v3.3.0 - Externalized tier limits configuration.
"""

import tempfile
from pathlib import Path

import pytest

from code_scalpel.licensing.config_loader import (
    clear_cache,
    get_cached_limits,
    get_tool_limits,
    load_limits,
    merge_limits,
    reload_config,
)
from code_scalpel.licensing.features import get_tool_capabilities


def test_load_limits_from_default_location():
    """Test that default config loads from package."""
    clear_cache()
    limits = load_limits()

    # Should have tier sections
    assert isinstance(limits, dict)
    # May be empty if no config found, or have tier data
    if limits:
        assert "community" in limits or "pro" in limits or "enterprise" in limits


def test_load_limits_with_explicit_path(tmp_path):
    """Test loading from explicit path."""
    config_file = tmp_path / "test_limits.toml"
    config_file.write_text(
        """
[pro.extract_code]
max_depth = 999
cross_file_deps = true

[community.security_scan]
max_findings = 123
"""
    )

    limits = load_limits(config_file)

    assert limits["pro"]["extract_code"]["max_depth"] == 999
    assert limits["pro"]["extract_code"]["cross_file_deps"] is True
    assert limits["community"]["security_scan"]["max_findings"] == 123


def test_get_tool_limits():
    """Test extracting limits for specific tool/tier."""
    with tempfile.TemporaryDirectory() as tmpdir:
        config_file = Path(tmpdir) / "limits.toml"
        config_file.write_text(
            """
[pro.extract_code]
max_depth = 42
"""
        )

        limits_config = load_limits(config_file)
        tool_limits = get_tool_limits("extract_code", "pro", limits_config)

        assert tool_limits["max_depth"] == 42


def test_merge_limits():
    """Test merging config overrides into defaults."""
    defaults = {"max_depth": 2, "cross_file_deps": True, "max_size": 10}
    overrides = {"max_depth": 999}

    merged = merge_limits(defaults, overrides)

    assert merged["max_depth"] == 999  # Overridden
    assert merged["cross_file_deps"] is True  # Preserved
    assert merged["max_size"] == 10  # Preserved


def test_get_tool_capabilities_with_config_override(tmp_path, monkeypatch):
    """Test that get_tool_capabilities picks up a custom limits file."""
    config_file = tmp_path / "limits.toml"
    config_file.write_text(
        """
[pro.extract_code]
max_depth = 555
include_cross_file_deps = true
"""
    )

    # Redirect the bundled-file resolver to our test file
    monkeypatch.setattr(
        "code_scalpel.licensing.config_loader._find_config_file",
        lambda: config_file,
    )
    clear_cache()

    caps = get_tool_capabilities("extract_code", "pro")

    assert caps["limits"]["max_depth"] == 555
    assert "include_cross_file_deps" in caps["limits"]


def test_load_limits_explicit_path(tmp_path):
    """Test that load_limits honours an explicit config_path argument."""
    config_file = tmp_path / "custom.toml"
    config_file.write_text(
        """
[community.extract_code]
max_depth = 777
"""
    )

    limits = load_limits(config_path=config_file)

    assert limits["community"]["extract_code"]["max_depth"] == 777


def test_cached_limits():
    """Test that config is cached after first load."""
    clear_cache()

    # First call loads
    limits1 = get_cached_limits()

    # Second call returns same object
    limits2 = get_cached_limits()

    assert limits1 is limits2


def test_reload_config():
    """Test that reload_config clears cache and reloads."""
    clear_cache()
    get_cached_limits()

    # Reload should give us a fresh load
    limits2 = reload_config()

    # May be same data but different load
    assert isinstance(limits2, dict)


def test_missing_config_returns_empty():
    """Test that missing config returns empty dict, not error."""
    with tempfile.TemporaryDirectory() as tmpdir:
        nonexistent = Path(tmpdir) / "nope.toml"
        limits = load_limits(nonexistent)

        assert limits == {}


def test_invalid_toml_returns_empty(tmp_path):
    """Test that invalid TOML returns empty dict gracefully."""
    config_file = tmp_path / "bad.toml"
    config_file.write_text("this is [ not valid toml")

    limits = load_limits(config_file)

    assert limits == {}


def test_null_values_in_config(tmp_path):
    """Test that null values (unlimited) are preserved."""
    config_file = tmp_path / "limits.toml"
    # TOML uses 'inf' or omit the key for unlimited; null is not valid TOML
    # Instead, test that we can handle the Python None from omitted values
    config_file.write_text(
        """
[enterprise.extract_code]
cross_file_deps = true
"""
    )

    limits = load_limits(config_file)

    # Verify the config loaded
    assert "enterprise" in limits
    assert limits["enterprise"]["extract_code"]["cross_file_deps"] is True

    # Verify that -1 sentinel in limits.toml is converted to None at runtime.
    # enterprise.update_symbol has max_updates_per_call = -1 in the bundled file.
    clear_cache()
    caps = get_tool_capabilities("update_symbol", "enterprise")
    assert caps["limits"]["max_updates_per_call"] is None


def test_array_values_in_config(tmp_path):
    """Test that array limit values work."""
    config_file = tmp_path / "limits.toml"
    config_file.write_text(
        """
[pro.symbolic_execute]
constraint_types = ["int", "bool", "string"]
"""
    )

    limits = load_limits(config_file)

    assert limits["pro"]["symbolic_execute"]["constraint_types"] == [
        "int",
        "bool",
        "string",
    ]


def test_load_limits_custom_path(tmp_path):
    """Test that load_limits reads correctly from an arbitrary path."""
    custom_config = tmp_path / "custom.toml"
    custom_config.write_text(
        """
[pro.extract_code]
max_depth = 999
"""
    )

    limits = load_limits(config_path=custom_config)

    assert limits["pro"]["extract_code"]["max_depth"] == 999


@pytest.mark.parametrize(
    "tier,expected_max_depth",
    [
        ("community", 1),
        ("pro", None),  # -1 sentinel in limits.toml → None
        ("enterprise", None),  # -1 sentinel in limits.toml → None
    ],
)
def test_default_extract_code_limits(tier, expected_max_depth):
    """Test that extract_code max_depth matches limits.toml, including -1 sentinel."""
    clear_cache()
    caps = get_tool_capabilities("extract_code", tier)

    limits = caps.get("limits", {})
    assert "max_depth" in limits
    assert limits["max_depth"] == expected_max_depth


def test_full_integration_workflow(tmp_path, monkeypatch):
    """Test full workflow: custom limits file loaded, tools read correct values."""
    deployed_config = tmp_path / "limits.toml"
    deployed_config.write_text(
        """
[pro.extract_code]
max_depth = 5
cross_file_deps = true
max_extraction_size_mb = 20

[community.security_scan]
max_findings = 100
"""
    )

    monkeypatch.setattr(
        "code_scalpel.licensing.config_loader._find_config_file",
        lambda: deployed_config,
    )
    clear_cache()

    caps = get_tool_capabilities("extract_code", "pro")
    limits = caps["limits"]

    assert limits["max_depth"] == 5
    assert limits["cross_file_deps"] is True
    assert limits["max_extraction_size_mb"] == 20

    community_caps = get_tool_capabilities("security_scan", "community")
    assert community_caps["limits"]["max_findings"] == 100
