"""Tests for check_configuration() and add_missing_config_files().

[20260224_TEST] Coverage for the check command (integrity checking, --fix flag)
and the safe upgrade helper add_missing_config_files().
"""

import json
import os
import sys

# Ensure src is on the path regardless of how pytest is invoked.
_test_dir = os.path.dirname(os.path.abspath(__file__))
_project_root = os.path.dirname(os.path.dirname(_test_dir))
_src_path = os.path.join(_project_root, "src")
if _src_path not in sys.path:
    sys.path.insert(0, _src_path)

from code_scalpel.cli import check_configuration  # noqa: E402
from code_scalpel.config.init_config import add_missing_config_files  # noqa: E402

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_required(cs_dir):
    """Write the four required .code-scalpel files into *cs_dir*."""
    (cs_dir / "config.json").write_text("{}", encoding="utf-8")
    (cs_dir / "policy.yaml").write_text("rules: []", encoding="utf-8")
    (cs_dir / "budget.yaml").write_text("budget: {}", encoding="utf-8")
    (cs_dir / "response_config.json").write_text("{}", encoding="utf-8")


# ===========================================================================
# check_configuration() tests
# ===========================================================================


class TestCheckConfigurationMissingDir:
    """Behaviour when .code-scalpel does not exist at all."""

    def test_returns_exit_1(self, tmp_path):
        assert check_configuration(str(tmp_path)) == 1

    def test_human_output_mentions_init(self, tmp_path, capsys):
        check_configuration(str(tmp_path))
        captured = capsys.readouterr()
        assert "codescalpel init" in captured.out

    def test_json_error_no_config_dir(self, tmp_path, capsys):
        rc = check_configuration(str(tmp_path), json_output=True)
        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert rc == 1
        assert data["success"] is False
        assert data["error"] == "no_config_dir"


class TestCheckConfigurationRequiredFiles:
    """Presence / absence of required files."""

    def test_all_required_present_returns_0(self, tmp_path):
        cs = tmp_path / ".code-scalpel"
        cs.mkdir()
        _make_required(cs)
        assert check_configuration(str(tmp_path)) == 0

    def test_required_file_missing_returns_1(self, tmp_path):
        cs = tmp_path / ".code-scalpel"
        cs.mkdir()
        # Only 3 of 4 required files — response_config.json absent
        (cs / "config.json").write_text("{}", encoding="utf-8")
        (cs / "policy.yaml").write_text("rules: []", encoding="utf-8")
        (cs / "budget.yaml").write_text("budget: {}", encoding="utf-8")
        assert check_configuration(str(tmp_path)) == 1

    def test_required_file_missing_shows_fail(self, tmp_path, capsys):
        cs = tmp_path / ".code-scalpel"
        cs.mkdir()
        (cs / "config.json").write_text("{}", encoding="utf-8")
        (cs / "policy.yaml").write_text("rules: []", encoding="utf-8")
        (cs / "budget.yaml").write_text("ok: true", encoding="utf-8")
        check_configuration(str(tmp_path))
        captured = capsys.readouterr()
        assert "FAIL" in captured.out

    def test_only_recommended_missing_returns_0(self, tmp_path, capsys):
        """Required files all OK → exit 0 even if recommended are absent."""
        cs = tmp_path / ".code-scalpel"
        cs.mkdir()
        _make_required(cs)
        rc = check_configuration(str(tmp_path))
        captured = capsys.readouterr()
        assert rc == 0
        assert "WARN" in captured.out  # recommended warning present


class TestCheckConfigurationIntegrity:
    """File integrity (parse errors, empty files)."""

    def test_invalid_json_returns_1(self, tmp_path, capsys):
        cs = tmp_path / ".code-scalpel"
        cs.mkdir()
        (cs / "config.json").write_text("{broken", encoding="utf-8")
        (cs / "policy.yaml").write_text("ok: true", encoding="utf-8")
        (cs / "budget.yaml").write_text("ok: true", encoding="utf-8")
        (cs / "response_config.json").write_text("{}", encoding="utf-8")
        rc = check_configuration(str(tmp_path))
        captured = capsys.readouterr()
        assert rc == 1
        assert "PARSE ERROR" in captured.out

    def test_empty_required_file_returns_1(self, tmp_path, capsys):
        cs = tmp_path / ".code-scalpel"
        cs.mkdir()
        (cs / "config.json").touch()  # 0 bytes
        (cs / "policy.yaml").write_text("ok: true", encoding="utf-8")
        (cs / "budget.yaml").write_text("ok: true", encoding="utf-8")
        (cs / "response_config.json").write_text("{}", encoding="utf-8")
        rc = check_configuration(str(tmp_path))
        captured = capsys.readouterr()
        assert rc == 1
        assert "EMPTY FILE" in captured.out

    def test_valid_files_integrity_ok(self, tmp_path):
        cs = tmp_path / ".code-scalpel"
        cs.mkdir()
        _make_required(cs)
        assert check_configuration(str(tmp_path)) == 0


class TestCheckConfigurationJsonOutput:
    """--json / -j output structure."""

    def test_json_has_integrity_key(self, tmp_path, capsys):
        cs = tmp_path / ".code-scalpel"
        cs.mkdir()
        _make_required(cs)
        check_configuration(str(tmp_path), json_output=True)
        data = json.loads(capsys.readouterr().out)
        assert "integrity" in data
        assert data["integrity"]["ok"] is True
        assert "files_validated" in data["integrity"]

    def test_json_per_file_integrity_on_parse_error(self, tmp_path, capsys):
        cs = tmp_path / ".code-scalpel"
        cs.mkdir()
        (cs / "config.json").write_text("{bad", encoding="utf-8")
        (cs / "policy.yaml").write_text("ok: true", encoding="utf-8")
        (cs / "budget.yaml").write_text("ok: true", encoding="utf-8")
        (cs / "response_config.json").write_text("{}", encoding="utf-8")
        check_configuration(str(tmp_path), json_output=True)
        data = json.loads(capsys.readouterr().out)
        cfg = data["files"]["config.json"]["integrity"]
        assert cfg["ok"] is False
        assert cfg["parse_error"] is not None

    def test_json_success_false_when_required_missing(self, tmp_path, capsys):
        cs = tmp_path / ".code-scalpel"
        cs.mkdir()
        _make_required(cs)
        (cs / "config.json").unlink()  # remove a required file
        check_configuration(str(tmp_path), json_output=True)
        data = json.loads(capsys.readouterr().out)
        assert data["success"] is False

    def test_json_success_true_when_only_recommended_missing(self, tmp_path, capsys):
        cs = tmp_path / ".code-scalpel"
        cs.mkdir()
        _make_required(cs)
        check_configuration(str(tmp_path), json_output=True)
        data = json.loads(capsys.readouterr().out)
        assert data["success"] is True


class TestCheckConfigurationFixFlag:
    """--fix flag behaviour."""

    def test_fix_adds_missing_recommended_files(self, tmp_path):
        cs = tmp_path / ".code-scalpel"
        cs.mkdir()
        _make_required(cs)
        # response_config.schema.json is absent before --fix
        assert not (cs / "response_config.schema.json").exists()
        check_configuration(str(tmp_path), fix=True)
        assert (cs / "response_config.schema.json").exists()

    def test_fix_does_not_overwrite_existing_file(self, tmp_path):
        cs = tmp_path / ".code-scalpel"
        cs.mkdir()
        custom = '{"my_custom_setting": true}'
        (cs / "config.json").write_text(custom, encoding="utf-8")
        (cs / "policy.yaml").write_text("rules: []", encoding="utf-8")
        (cs / "budget.yaml").write_text("ok: true", encoding="utf-8")
        (cs / "response_config.json").write_text("{}", encoding="utf-8")
        check_configuration(str(tmp_path), fix=True)
        assert (cs / "config.json").read_text(encoding="utf-8") == custom

    def test_fix_reports_added_files_in_human_output(self, tmp_path, capsys):
        cs = tmp_path / ".code-scalpel"
        cs.mkdir()
        _make_required(cs)
        check_configuration(str(tmp_path), fix=True)
        captured = capsys.readouterr()
        # Should mention FIX in header when files were added
        assert "[FIX]" in captured.out

    def test_fix_json_includes_fix_applied_key(self, tmp_path, capsys):
        cs = tmp_path / ".code-scalpel"
        cs.mkdir()
        _make_required(cs)
        check_configuration(str(tmp_path), json_output=True, fix=True)
        data = json.loads(capsys.readouterr().out)
        assert "fix_applied" in data

    def test_fix_returns_0_after_filling_recommended(self, tmp_path):
        cs = tmp_path / ".code-scalpel"
        cs.mkdir()
        _make_required(cs)
        rc = check_configuration(str(tmp_path), fix=True)
        assert rc == 0


# ===========================================================================
# add_missing_config_files() tests
# ===========================================================================


class TestAddMissingConfigFiles:
    """Tests for the safe upgrade helper."""

    def test_nonexistent_dir_returns_failure(self, tmp_path):
        result = add_missing_config_files(str(tmp_path / "no-such-project"))
        assert result["success"] is False
        assert "files_added" in result

    def test_adds_required_files_to_empty_cs_dir(self, tmp_path):
        cs = tmp_path / ".code-scalpel"
        cs.mkdir()
        result = add_missing_config_files(str(tmp_path))
        assert result["success"] is True
        for name in (
            "config.json",
            "policy.yaml",
            "budget.yaml",
            "response_config.json",
            "response_config.schema.json",
        ):
            assert (cs / name).exists(), f"Expected {name} to be created"

    def test_files_added_list_is_non_empty(self, tmp_path):
        cs = tmp_path / ".code-scalpel"
        cs.mkdir()
        result = add_missing_config_files(str(tmp_path))
        assert len(result["files_added"]) > 0

    def test_skips_existing_files_and_preserves_content(self, tmp_path):
        cs = tmp_path / ".code-scalpel"
        cs.mkdir()
        custom = '{"preserved": true}'
        (cs / "config.json").write_text(custom, encoding="utf-8")
        result = add_missing_config_files(str(tmp_path))
        assert result["success"] is True
        assert "config.json" in result["files_skipped"]
        assert "config.json" not in result["files_added"]
        assert (cs / "config.json").read_text(encoding="utf-8") == custom

    def test_idempotent(self, tmp_path):
        cs = tmp_path / ".code-scalpel"
        cs.mkdir()
        first = add_missing_config_files(str(tmp_path))
        second = add_missing_config_files(str(tmp_path))
        assert second["success"] is True
        assert len(second["files_added"]) == 0
        assert len(second["files_skipped"]) == len(first["files_added"]) + len(
            first["files_skipped"]
        )

    def test_only_adds_specifically_missing_files(self, tmp_path):
        cs = tmp_path / ".code-scalpel"
        cs.mkdir()
        (cs / "config.json").write_text("{}", encoding="utf-8")
        (cs / "policy.yaml").write_text("ok: true", encoding="utf-8")
        result = add_missing_config_files(str(tmp_path))
        assert "config.json" not in result["files_added"]
        assert "policy.yaml" not in result["files_added"]
        assert "budget.yaml" in result["files_added"]
        assert "response_config.json" in result["files_added"]

    def test_creates_nested_policy_dirs(self, tmp_path):
        cs = tmp_path / ".code-scalpel"
        cs.mkdir()
        add_missing_config_files(str(tmp_path))
        assert (cs / "policies" / "architecture" / "layered_architecture.rego").exists()
        assert (cs / "policies" / "devops" / "docker_security.rego").exists()
        assert (cs / "policies" / "devsecops" / "secret_detection.rego").exists()

    def test_result_has_expected_keys(self, tmp_path):
        cs = tmp_path / ".code-scalpel"
        cs.mkdir()
        result = add_missing_config_files(str(tmp_path))
        for key in ("success", "message", "path", "files_added", "files_skipped"):
            assert key in result, f"Missing key: {key}"
