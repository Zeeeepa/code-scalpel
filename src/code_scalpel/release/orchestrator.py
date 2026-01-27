"""Release orchestrator - coordinates the entire release process.

Orchestrates version bumping, changelog updates, release notes generation,
and package publishing.
"""

from __future__ import annotations

import re
from pathlib import Path

from code_scalpel.release.git_history import GitHistoryAnalyzer
from code_scalpel.release.notes import ChangelogManager, ReleaseNotesGenerator
from code_scalpel.release.versioning import SemanticVersioner


class ReleaseOrchestrator:
    """Orchestrates the complete release process."""

    def __init__(
        self,
        repo_path: str = ".",
        pyproject_path: str = "pyproject.toml",
        changelog_path: str = "CHANGELOG.md",
    ):
        """Initialize orchestrator.

        Args:
            repo_path: Path to git repository
            pyproject_path: Path to pyproject.toml
            changelog_path: Path to CHANGELOG.md
        """
        self.repo_path = repo_path
        self.pyproject_path = pyproject_path
        self.changelog_path = changelog_path
        self.git = GitHistoryAnalyzer(repo_path)

    def get_current_version(self) -> str:
        """Get current version from pyproject.toml.

        Returns:
            Version string (e.g., "1.2.3")
        """
        pyproject = Path(self.pyproject_path)
        if not pyproject.exists():
            raise FileNotFoundError(
                f"pyproject.toml not found at {self.pyproject_path}"
            )

        content = pyproject.read_text()
        match = re.search(r'version\s*=\s*["\']([^"\']+)["\']', content)

        if not match:
            raise ValueError("Could not find version in pyproject.toml")

        return match.group(1)

    def set_version(self, version: str) -> None:
        """Update version in pyproject.toml.

        Args:
            version: New version string
        """
        pyproject = Path(self.pyproject_path)
        content = pyproject.read_text()

        # Replace version
        new_content = re.sub(
            r'version\s*=\s*["\']([^"\']+)["\']',
            f'version = "{version}"',
            content,
        )

        pyproject.write_text(new_content)

    def should_release(self) -> bool:
        """Check if a release should be performed.

        Returns:
            True if there are unreleased commits

        Checks:
        - Working directory is clean
        - There are commits since last tag
        """
        # Check working directory
        if self.git.is_dirty():
            print("❌ Working directory has uncommitted changes")
            return False

        # Check for commits since last tag
        latest_tag = self.git.get_latest_tag()
        commits = self.git.get_commits_since_tag(
            latest_tag.name if latest_tag else None
        )

        if not commits:
            print("❌ No commits since last release")
            return False

        return True

    def prepare_release(self) -> dict[str, str]:
        """Prepare release by determining new version and generating release notes.

        Returns:
            Dict with keys:
            - current_version: Current version
            - new_version: New version to release
            - bump_type: MAJOR, MINOR, or PATCH
            - release_notes: Generated release notes
        """
        current_version = self.get_current_version()
        latest_tag = self.git.get_latest_tag()

        # Get commits since last release
        commits = self.git.get_commits_since_tag(
            latest_tag.name if latest_tag else None
        )

        if not commits:
            raise ValueError("No commits to release")

        # Determine new version
        versioner = SemanticVersioner(current_version)
        version_bump = versioner.analyze_commits(commits)

        # Generate release notes
        notes_gen = ReleaseNotesGenerator(version_bump.new_version)
        release_notes = notes_gen.generate(commits)

        return {
            "current_version": current_version,
            "new_version": version_bump.new_version,
            "bump_type": version_bump.bump_type,
            "release_notes": release_notes,
            "commits_count": str(len(commits)),
        }

    def execute_release(self, dry_run: bool = False) -> dict[str, str]:
        """Execute the complete release.

        Args:
            dry_run: If True, don't actually modify files or create tag

        Returns:
            Dict with release information

        Steps:
        1. Check preconditions
        2. Determine new version
        3. Generate release notes
        4. Update CHANGELOG.md
        5. Update pyproject.toml
        6. Create git tag
        """
        print("🚀 Starting release process...\n")

        # Step 1: Check preconditions
        print("1️⃣  Checking preconditions...")
        if not self.should_release():
            raise RuntimeError("Release preconditions not met")
        print("   ✅ Preconditions met\n")

        # Step 2-4: Prepare release
        print("2️⃣  Preparing release...")
        prep = self.prepare_release()
        print(f"   📦 Current version: {prep['current_version']}")
        print(f"   📦 New version: {prep['new_version']}")
        print(f"   📦 Bump type: {prep['bump_type']}")
        print(f"   📦 Commits: {prep['commits_count']}\n")

        # Step 5: Update files
        print("3️⃣  Updating files...")

        if not dry_run:
            # Update version
            self.set_version(prep["new_version"])
            print("   ✅ Updated version in pyproject.toml")

            # Update CHANGELOG
            changelog = ChangelogManager(self.changelog_path)
            changelog.insert_release(prep["release_notes"])
            print("   ✅ Updated CHANGELOG.md")

        # Step 6: Create tag
        print("4️⃣  Creating tag...")
        tag_name = f"v{prep['new_version']}"

        if not dry_run:
            if self.git.tag_exists(tag_name):
                raise RuntimeError(f"Tag {tag_name} already exists")

            self.git.create_tag(tag_name, f"Release {prep['new_version']}")
            print(f"   ✅ Created tag: {tag_name}\n")
        else:
            print(f"   [DRY RUN] Would create tag: {tag_name}\n")

        print("✅ Release process complete!\n")

        return prep

    def print_release_plan(self) -> None:
        """Print what would be released without executing.

        Useful for review before actual release.
        """
        prep = self.prepare_release()

        print("📋 Release Plan")
        print(f"Current version: {prep['current_version']}")
        print(f"New version: {prep['new_version']}")
        print(f"Bump type: {prep['bump_type']}")
        print(f"Commits: {prep['commits_count']}")
        print("\n📝 Release Notes Preview:\n")
        print(prep["release_notes"])
