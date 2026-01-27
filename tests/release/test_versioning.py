"""Tests for release pipeline modules."""

from __future__ import annotations


from code_scalpel.release.versioning import (
    ConventionalCommit,
    SemanticVersioner,
    VersionBump,
)


class TestConventionalCommit:
    """Test conventional commit parsing."""

    def test_parse_feat_commit(self):
        """Parse a simple feature commit."""
        msg = "feat: Add new user API\n\nImplements user registration endpoint."
        commit = ConventionalCommit.parse(msg)

        assert commit is not None
        assert commit.type == "feat"
        assert commit.description == "Add new user API"
        assert commit.scope is None
        assert commit.is_feature()

    def test_parse_fix_commit(self):
        """Parse a bug fix commit."""
        msg = "fix: Prevent race condition in auth"
        commit = ConventionalCommit.parse(msg)

        assert commit is not None
        assert commit.type == "fix"
        assert commit.description == "Prevent race condition in auth"
        assert commit.is_fix()

    def test_parse_commit_with_scope(self):
        """Parse commit with scope."""
        msg = "feat(api): Add pagination support"
        commit = ConventionalCommit.parse(msg)

        assert commit is not None
        assert commit.type == "feat"
        assert commit.scope == "api"
        assert commit.description == "Add pagination support"

    def test_parse_breaking_change_with_exclamation(self):
        """Parse breaking change with ! suffix."""
        msg = "feat!: Redesign authentication system"
        commit = ConventionalCommit.parse(msg)

        assert commit is not None
        assert commit.is_breaking()
        assert commit.is_feature()

    def test_parse_breaking_change_with_footer(self):
        """Parse breaking change with BREAKING CHANGE footer."""
        msg = "refactor: Change auth API\n\nBREAKING CHANGE: Old endpoints removed"
        commit = ConventionalCommit.parse(msg)

        assert commit is not None
        assert commit.is_breaking()

    def test_parse_docs_commit(self):
        """Parse documentation commit."""
        msg = "docs: Update API documentation"
        commit = ConventionalCommit.parse(msg)

        assert commit is not None
        assert commit.type == "docs"
        assert not commit.is_feature()
        assert not commit.is_fix()

    def test_parse_style_commit(self):
        """Parse style commit."""
        msg = "style: Format code with black"
        commit = ConventionalCommit.parse(msg)

        assert commit is not None
        assert commit.type == "style"

    def test_parse_test_commit(self):
        """Parse test commit."""
        msg = "test: Add unit tests for auth module"
        commit = ConventionalCommit.parse(msg)

        assert commit is not None
        assert commit.type == "test"

    def test_parse_chore_commit(self):
        """Parse chore commit."""
        msg = "chore: Update dependencies"
        commit = ConventionalCommit.parse(msg)

        assert commit is not None
        assert commit.type == "chore"

    def test_parse_ci_commit(self):
        """Parse CI commit."""
        msg = "ci: Update GitHub Actions workflow"
        commit = ConventionalCommit.parse(msg)

        assert commit is not None
        assert commit.type == "ci"

    def test_parse_invalid_format(self):
        """Parse non-conventional commit returns None."""
        msg = "Some random commit message"
        commit = ConventionalCommit.parse(msg)

        assert commit is None

    def test_parse_missing_colon(self):
        """Parse invalid format without colon."""
        msg = "feat Add new feature"
        commit = ConventionalCommit.parse(msg)

        assert commit is None

    def test_parse_invalid_type(self):
        """Parse with invalid commit type."""
        msg = "whatever: Some message"
        commit = ConventionalCommit.parse(msg)

        assert commit is None

    def test_parse_scope_with_hyphens(self):
        """Parse scope with special characters."""
        msg = "feat(user-auth): Add OAuth2 support"
        commit = ConventionalCommit.parse(msg)

        assert commit is not None
        assert commit.scope == "user-auth"


class TestSemanticVersioner:
    """Test semantic version bumping."""

    def test_initial_version(self):
        """Create versioner with initial version."""
        versioner = SemanticVersioner("1.0.0")
        assert versioner.major == 1
        assert versioner.minor == 0
        assert versioner.patch == 0

    def test_patch_bump_for_fix(self):
        """Patch bump for fix commits."""
        versioner = SemanticVersioner("1.2.3")
        commits = ["fix: Resolve memory leak"]

        bump = versioner.analyze_commits(commits)
        assert bump.new_version == "1.2.4"
        assert bump.bump_type == "PATCH"

    def test_minor_bump_for_feature(self):
        """Minor bump for feature commits."""
        versioner = SemanticVersioner("1.2.3")
        commits = ["feat: Add new endpoint"]

        bump = versioner.analyze_commits(commits)
        assert bump.new_version == "1.3.0"
        assert bump.bump_type == "MINOR"

    def test_major_bump_for_breaking_change(self):
        """Major bump for breaking changes."""
        versioner = SemanticVersioner("1.2.3")
        commits = ["feat!: Redesign API"]

        bump = versioner.analyze_commits(commits)
        assert bump.new_version == "2.0.0"
        assert bump.bump_type == "MAJOR"

    def test_major_bump_overrides_minor(self):
        """Major bump takes precedence over minor."""
        versioner = SemanticVersioner("1.2.3")
        commits = [
            "feat: Add feature 1",
            "feat!: Remove old API",
            "fix: Fix bug",
        ]

        bump = versioner.analyze_commits(commits)
        assert bump.new_version == "2.0.0"

    def test_minor_bump_overrides_patch(self):
        """Minor bump takes precedence over patch."""
        versioner = SemanticVersioner("1.2.3")
        commits = [
            "fix: Fix bug 1",
            "feat: Add feature",
            "fix: Fix bug 2",
        ]

        bump = versioner.analyze_commits(commits)
        assert bump.new_version == "1.3.0"

    def test_no_version_bump_for_docs(self):
        """Docs commits don't bump version."""
        versioner = SemanticVersioner("1.2.3")
        commits = [
            "docs: Update README",
            "style: Format code",
        ]

        bump = versioner.analyze_commits(commits)
        assert bump.new_version == "1.2.3"

    def test_multiple_fixes_single_patch_bump(self):
        """Multiple fixes = single patch bump."""
        versioner = SemanticVersioner("1.2.3")
        commits = [
            "fix: Fix bug 1",
            "fix: Fix bug 2",
            "fix: Fix bug 3",
        ]

        bump = versioner.analyze_commits(commits)
        assert bump.new_version == "1.2.4"

    def test_breaking_change_footer(self):
        """Breaking change via footer."""
        versioner = SemanticVersioner("1.2.3")
        commits = [
            "refactor: Change authentication\n\nBREAKING CHANGE: Old endpoints removed"
        ]

        bump = versioner.analyze_commits(commits)
        assert bump.new_version == "2.0.0"

    def test_classify_commits(self):
        """Test commit classification."""
        versioner = SemanticVersioner("1.2.3")
        commits = [
            "feat: Add feature",
            "fix: Fix bug",
            "docs: Update docs",
            "feat!: Breaking change",
        ]

        classified = versioner.classify_commits(commits)
        assert len(classified["breaking"]) == 1
        assert len(classified["features"]) == 1
        assert len(classified["fixes"]) == 1
        assert len(classified["other"]) == 1

    def test_version_with_two_digits(self):
        """Handle version with multiple digits."""
        versioner = SemanticVersioner("10.20.30")
        assert versioner.major == 10
        assert versioner.minor == 20
        assert versioner.patch == 30

        commits = ["feat: Add feature"]
        bump = versioner.analyze_commits(commits)
        assert bump.new_version == "10.21.0"

    def test_zero_version(self):
        """Handle version starting with 0."""
        versioner = SemanticVersioner("0.1.0")
        assert versioner.major == 0

        commits = ["feat!: Break everything"]
        bump = versioner.analyze_commits(commits)
        assert bump.new_version == "1.0.0"

    def test_invalid_commits_ignored(self):
        """Invalid conventional commits are ignored."""
        versioner = SemanticVersioner("1.2.3")
        commits = [
            "Random commit message",
            "feat: Valid commit",
            "Another random one",
        ]

        bump = versioner.analyze_commits(commits)
        assert bump.new_version == "1.3.0"  # Only feat counted


class TestVersionBump:
    """Test VersionBump data class."""

    def test_bump_properties(self):
        """Test VersionBump properties."""
        bump = VersionBump(major=2, minor=1, patch=3, current="1.2.3")
        assert bump.new_version == "2.1.3"
        assert bump.bump_type == "MAJOR"

    def test_minor_bump_type(self):
        """Test minor bump identification."""
        bump = VersionBump(major=1, minor=3, patch=0, current="1.2.3")
        assert bump.bump_type == "MINOR"

    def test_patch_bump_type(self):
        """Test patch bump identification."""
        bump = VersionBump(major=1, minor=2, patch=4, current="1.2.3")
        assert bump.bump_type == "PATCH"

    def test_no_bump_type(self):
        """Test when no bump happened."""
        bump = VersionBump(major=1, minor=2, patch=3, current="1.2.3")
        assert bump.bump_type == "NONE"
