"""Release command implementation for Code Scalpel CLI.

Provides commands for managing the release process:
- release plan: Preview the next release
- release prepare: Prepare release (dry-run)
- release execute: Execute the full release
- release publish: Publish to PyPI and GitHub
"""

from __future__ import annotations

import sys
from typing import Optional


def release_plan(
    repo_path: str = ".",
    changelog_path: str = "CHANGELOG.md",
) -> int:
    """Preview the next release plan.

    Shows what will be released without making changes.

    Args:
        repo_path: Path to git repository
        changelog_path: Path to CHANGELOG.md

    Returns:
        Exit code (0 = success)
    """
    try:
        from code_scalpel.release.orchestrator import ReleaseOrchestrator

        orchestrator = ReleaseOrchestrator(
            repo_path=repo_path,
            changelog_path=changelog_path,
        )
        orchestrator.print_release_plan()
        return 0

    except ValueError as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Unexpected error: {str(e)}", file=sys.stderr)
        return 1


def release_prepare(
    repo_path: str = ".",
    changelog_path: str = "CHANGELOG.md",
) -> int:
    """Prepare release in dry-run mode.

    Performs all release steps except writing files or creating tags.

    Args:
        repo_path: Path to git repository
        changelog_path: Path to CHANGELOG.md

    Returns:
        Exit code (0 = success)
    """
    try:
        from code_scalpel.release.orchestrator import ReleaseOrchestrator

        orchestrator = ReleaseOrchestrator(
            repo_path=repo_path,
            changelog_path=changelog_path,
        )

        result = orchestrator.execute_release(dry_run=True)

        print("\n✅ Dry-run preparation successful!")
        print(f"Release would be: {result['new_version']}")
        print(f"Commits: {result['commits_count']}")

        return 0

    except ValueError as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Unexpected error: {str(e)}", file=sys.stderr)
        return 1


def release_execute(
    repo_path: str = ".",
    changelog_path: str = "CHANGELOG.md",
    skip_github: bool = False,
    skip_pypi: bool = False,
) -> int:
    """Execute the complete release process.

    Performs:
    1. Version determination from commits
    2. Changelog updates
    3. Git tagging
    4. GitHub release creation (if not skipped)
    5. PyPI publishing (if not skipped)

    Args:
        repo_path: Path to git repository
        changelog_path: Path to CHANGELOG.md
        skip_github: Skip GitHub release creation
        skip_pypi: Skip PyPI publishing

    Returns:
        Exit code (0 = success)
    """
    try:
        from code_scalpel.release.orchestrator import ReleaseOrchestrator
        from code_scalpel.release.github_releases import GitHubReleaseManager
        from code_scalpel.release.pypi_publisher import PyPIPublisher

        # Step 1: Execute core release
        print("🚀 Starting release process...\n")
        orchestrator = ReleaseOrchestrator(
            repo_path=repo_path,
            changelog_path=changelog_path,
        )

        release_info = orchestrator.execute_release(dry_run=False)

        if release_info["bump_type"] == "NONE":
            print("No changes to release")
            return 0

        version = release_info["new_version"]
        tag = f"v{version}"

        # Step 2: Publish to PyPI (if not skipped)
        if not skip_pypi:
            print("\n📦 Publishing to PyPI...\n")
            try:
                publisher = PyPIPublisher(project_dir=repo_path)
                publisher.upload_to_pypi()
                print(f"✅ Published to PyPI: {version}\n")
            except Exception as e:
                print(f"⚠️  PyPI publishing failed: {str(e)}", file=sys.stderr)
                if not skip_github:
                    print("Continuing with GitHub release...", file=sys.stderr)
                else:
                    return 1

        # Step 3: Create GitHub release (if not skipped)
        if not skip_github:
            print("📤 Creating GitHub release...\n")
            try:
                github = GitHubReleaseManager()
                github.create_release(
                    tag=tag,
                    title=f"Release {version}",
                    body=release_info["release_notes"],
                    prerelease=False,
                )
                print(f"✅ Created GitHub release: {tag}\n")
            except Exception as e:
                print(f"⚠️  GitHub release creation failed: {str(e)}", file=sys.stderr)
                return 1

        print(f"✅ Release {version} complete!")
        return 0

    except ValueError as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Unexpected error: {str(e)}", file=sys.stderr)
        return 1


def release_publish(
    repo_path: str = ".",
    tag: Optional[str] = None,
    skip_github: bool = False,
    skip_pypi: bool = False,
) -> int:
    """Publish a release to PyPI and GitHub.

    Use this to publish an existing release that was prepared separately.

    Args:
        repo_path: Path to git repository
        tag: Git tag to publish (e.g., "v1.2.3"). If None, uses latest tag.
        skip_github: Skip GitHub release creation
        skip_pypi: Skip PyPI publishing

    Returns:
        Exit code (0 = success)
    """
    try:
        from code_scalpel.release.git_history import GitHistoryAnalyzer
        from code_scalpel.release.github_releases import GitHubReleaseManager
        from code_scalpel.release.pypi_publisher import PyPIPublisher

        git = GitHistoryAnalyzer(repo_path)

        # Determine tag to publish
        if not tag:
            latest = git.get_latest_tag()
            if not latest:
                print("Error: No tags found. Create a release first.", file=sys.stderr)
                return 1
            tag = latest.name

        print(f"📤 Publishing {tag}...\n")

        # Publish to PyPI
        if not skip_pypi:
            print("📦 Publishing to PyPI...\n")
            try:
                publisher = PyPIPublisher(project_dir=repo_path)
                publisher.upload_to_pypi()
                print("✅ Published to PyPI\n")
            except Exception as e:
                print(f"⚠️  PyPI publishing failed: {str(e)}", file=sys.stderr)
                if not skip_github:
                    print("Continuing with GitHub release...", file=sys.stderr)
                else:
                    return 1

        # Create GitHub release
        if not skip_github:
            print("🐱 Creating GitHub release...\n")
            try:
                github = GitHubReleaseManager()
                release = github.get_release(tag)
                print(f"✅ Release already exists: {release['url']}\n")
            except Exception:
                # Release doesn't exist, would need release notes
                print(
                    f"Error: Release {tag} not found on GitHub.",
                    file=sys.stderr,
                )
                print(
                    "Use 'release execute' to create releases with release notes.",
                    file=sys.stderr,
                )
                return 1

        print(f"✅ Published {tag}!")
        return 0

    except Exception as e:
        print(f"Unexpected error: {str(e)}", file=sys.stderr)
        return 1
