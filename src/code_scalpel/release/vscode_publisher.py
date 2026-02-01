"""VS Code extension publishing and automation.

Handles building and publishing VS Code extensions to the marketplace.
Supports version synchronization and automated releases.

Features:
- Build VS Code extensions (VSIX packages)
- Publish to VS Code Marketplace
- Version synchronization with main release
- Dry-run mode for testing
"""

from __future__ import annotations

import subprocess
from pathlib import Path


class VSCodeExtensionPublisher:
    """Build and publish VS Code extensions.

    Attributes:
        project_dir: Root directory of the project
        extension_dir: Directory containing the VS Code extension
        version: Version string (e.g., "1.2.3")
        vsce_token: Personal Access Token for VS Code Marketplace
    """

    def __init__(
        self,
        project_dir: str = ".",
        extension_dir: str = "vscode-extension",
        version: str = "",
        vsce_token: str = "",
    ):
        """Initialize VS Code extension publisher.

        Args:
            project_dir: Root directory of the project (default: current directory)
            extension_dir: Relative path to extension directory
            version: Version string for publishing (e.g., "1.2.3")
            vsce_token: Personal Access Token for VS Code Marketplace

        Raises:
            ValueError: If version is not provided or extension directory not found
        """
        self.project_dir = Path(project_dir).resolve()
        self.extension_dir = self.project_dir / extension_dir
        self.version = version
        self.vsce_token = vsce_token

        # Validate version
        if not version:
            raise ValueError("Version is required for extension publishing")

        # Validate extension directory exists
        if not self.extension_dir.exists():
            raise ValueError(f"Extension directory not found: {self.extension_dir}")

        # Validate package.json exists
        if not (self.extension_dir / "package.json").exists():
            raise ValueError(f"package.json not found in {self.extension_dir}")

    def get_extension_version(self) -> str:
        """Get the version from package.json.

        Returns:
            Version string from package.json

        Raises:
            ValueError: If version cannot be extracted from package.json
        """
        try:
            import json

            package_file = self.extension_dir / "package.json"
            package_data = json.loads(package_file.read_text(encoding="utf-8"))

            if "version" not in package_data:
                raise ValueError("version field not found in package.json")

            return package_data["version"]

        except Exception as e:
            raise ValueError(f"Failed to read version from package.json: {str(e)}")

    def update_extension_version(self, version: str, dry_run: bool = False) -> bool:
        """Update version in package.json.

        Args:
            version: New version to set
            dry_run: If True, don't actually modify the file

        Returns:
            True if successful

        Raises:
            ValueError: If version format is invalid
        """
        try:
            import json

            # Validate version format
            if not self._is_valid_version(version):
                raise ValueError(f"Invalid version format: {version}")

            package_file = self.extension_dir / "package.json"
            package_data = json.loads(package_file.read_text(encoding="utf-8"))

            if dry_run:
                print(
                    f"Would update version from {package_data['version']} to {version}"
                )
                return True

            package_data["version"] = version
            package_file.write_text(
                json.dumps(package_data, indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )

            print(f"Updated package.json to version {version}")
            return True

        except Exception as e:
            raise ValueError(f"Failed to update version: {str(e)}")

    def build_extension(self, dry_run: bool = False) -> dict[str, str]:
        """Build the VS Code extension (VSIX package).

        Args:
            dry_run: If True, print commands but don't execute them

        Returns:
            Dictionary with build information:
                - vsix_file: Path to built VSIX file
                - build_output: Build command output

        Raises:
            RuntimeError: If build fails
            FileNotFoundError: If npm or vsce is not installed
        """
        # First, ensure npm dependencies are installed
        npm_install_cmd = ["npm", "ci"]

        if dry_run:
            print(f"Would run in {self.extension_dir}: {' '.join(npm_install_cmd)}")
        else:
            try:
                result = subprocess.run(
                    npm_install_cmd,
                    capture_output=True,
                    text=True,
                    cwd=str(self.extension_dir),
                )

                if result.returncode != 0:
                    error_msg = result.stderr or result.stdout
                    raise RuntimeError(f"npm ci failed: {error_msg}")

            except FileNotFoundError:
                raise RuntimeError(
                    "npm is not installed or not in PATH. "
                    "Install Node.js to use this feature."
                )

        # Run build scripts if they exist
        build_cmd = ["npm", "run", "vscode:prepublish"]

        if dry_run:
            print(f"Would run in {self.extension_dir}: {' '.join(build_cmd)}")
        else:
            try:
                result = subprocess.run(
                    build_cmd,
                    capture_output=True,
                    text=True,
                    cwd=str(self.extension_dir),
                )

                # Non-zero exit is OK if script doesn't exist
                if result.returncode != 0 and "command not found" not in result.stderr:
                    print("Note: vscode:prepublish script not found or failed (OK)")

            except FileNotFoundError:
                raise RuntimeError(
                    "npm is not installed or not in PATH. "
                    "Install Node.js to use this feature."
                )

        # Package the extension
        package_cmd = ["vsce", "package", "--no-dependencies"]

        if dry_run:
            print(f"Would run in {self.extension_dir}: {' '.join(package_cmd)}")
            return {
                "vsix_file": "",
                "build_output": "",
            }

        try:
            result = subprocess.run(
                package_cmd,
                capture_output=True,
                text=True,
                cwd=str(self.extension_dir),
            )

            if result.returncode != 0:
                error_msg = result.stderr or result.stdout
                raise RuntimeError(f"vsce package failed: {error_msg}")

            # Find the generated VSIX file
            vsix_files = list(self.extension_dir.glob("*.vsix"))
            if not vsix_files:
                raise RuntimeError("No VSIX file generated after packaging")

            vsix_file = vsix_files[-1]  # Get the most recent one

            return {
                "vsix_file": str(vsix_file),
                "build_output": result.stdout,
            }

        except FileNotFoundError:
            raise RuntimeError(
                "vsce is not installed. Install it with: npm install -g @vscode/vsce"
            )

    def publish_extension(
        self,
        dry_run: bool = False,
    ) -> dict[str, str]:
        """Publish the VS Code extension to marketplace.

        Args:
            dry_run: If True, don't actually publish

        Returns:
            Dictionary with publication information:
                - version: Version that was published
                - vsix_file: Path to VSIX file
                - publish_output: Publish command output

        Raises:
            RuntimeError: If publication fails
            ValueError: If VSCE token not provided
        """
        if not self.vsce_token:
            raise ValueError("VSCE_PAT token required for publishing")

        # First build the extension
        build_result = self.build_extension(dry_run=dry_run)

        if not build_result["vsix_file"] and not dry_run:
            raise RuntimeError("Failed to build extension")

        # Publish the extension
        publish_cmd = ["vsce", "publish", "-p", self.vsce_token]

        if dry_run:
            print(f"Would run in {self.extension_dir}: {' '.join(publish_cmd)}")
            return {
                "version": self.version,
                "vsix_file": build_result.get("vsix_file", ""),
                "publish_output": "",
            }

        try:
            result = subprocess.run(
                publish_cmd,
                capture_output=True,
                text=True,
                cwd=str(self.extension_dir),
            )

            if result.returncode != 0:
                error_msg = result.stderr or result.stdout
                raise RuntimeError(f"vsce publish failed: {error_msg}")

            return {
                "version": self.version,
                "vsix_file": build_result.get("vsix_file", ""),
                "publish_output": result.stdout,
            }

        except FileNotFoundError:
            raise RuntimeError(
                "vsce is not installed. Install it with: npm install -g @vscode/vsce"
            )

    def get_publish_status(self) -> dict[str, str]:
        """Check current publication status.

        Returns:
            Dictionary with status information:
                - version: Current version
                - package_version: Version from package.json
                - project_dir: Project directory path
                - extension_dir: Extension directory path
                - has_package_json: Whether package.json exists
                - has_npm: Whether npm is available
        """
        has_npm = False
        try:
            subprocess.run(
                ["npm", "--version"],
                capture_output=True,
                timeout=5,
            )
            has_npm = True
        except (FileNotFoundError, subprocess.TimeoutExpired):
            has_npm = False

        try:
            package_version = self.get_extension_version()
        except Exception:
            package_version = "unknown"

        return {
            "version": self.version,
            "package_version": package_version,
            "project_dir": str(self.project_dir),
            "extension_dir": str(self.extension_dir),
            "has_package_json": str((self.extension_dir / "package.json").exists()),
            "has_npm": str(has_npm),
        }

    @staticmethod
    def _is_valid_version(version: str) -> bool:
        """Check if version string is valid (semantic versioning).

        Args:
            version: Version string to validate

        Returns:
            True if version matches X.Y.Z format
        """
        import re

        return bool(re.match(r"^\d+\.\d+\.\d+$", version))
