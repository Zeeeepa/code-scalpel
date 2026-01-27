"""PyPI publishing - Build and upload packages to PyPI.

Handles:
- Building wheel and source distributions
- Uploading to PyPI using twine
- Version verification
- Package metadata validation
"""

from __future__ import annotations

import os
import subprocess
from pathlib import Path
from typing import Optional


class PyPIPublisher:
    """Handles building and publishing packages to PyPI."""

    def __init__(
        self,
        project_dir: str = ".",
        pypi_token: Optional[str] = None,
        pypi_url: str = "https://upload.pypi.org/legacy/",
    ):
        """Initialize PyPI publisher.

        Args:
            project_dir: Path to project directory containing pyproject.toml
            pypi_token: PyPI API token. Defaults to PYPI_TOKEN env var.
            pypi_url: PyPI repository URL

        Raises:
            FileNotFoundError: If pyproject.toml not found
            ValueError: If PyPI token not provided
        """
        self.project_dir = Path(project_dir)
        self.pyproject_path = self.project_dir / "pyproject.toml"

        if not self.pyproject_path.exists():
            raise FileNotFoundError(
                f"pyproject.toml not found at {self.pyproject_path}"
            )

        self.pypi_token = pypi_token or os.environ.get("PYPI_TOKEN")
        if not self.pypi_token:
            raise ValueError(
                "PyPI token required. Pass 'pypi_token' argument or set PYPI_TOKEN "
                "environment variable."
            )

        self.pypi_url = pypi_url
        self.dist_dir = self.project_dir / "dist"

    def get_package_version(self) -> str:
        """Get package version from pyproject.toml.

        Returns:
            Version string (e.g., "1.2.3")

        Raises:
            ValueError: If version not found in pyproject.toml
        """
        try:
            import tomllib  # Python 3.11+
        except ImportError:
            import tomli as tomllib  # type: ignore

        with open(self.pyproject_path, "rb") as f:
            data = tomllib.load(f)

        version = data.get("project", {}).get("version")
        if not version:
            raise ValueError("Version not found in pyproject.toml")

        return version

    def get_package_name(self) -> str:
        """Get package name from pyproject.toml.

        Returns:
            Package name

        Raises:
            ValueError: If name not found in pyproject.toml
        """
        try:
            import tomllib  # Python 3.11+
        except ImportError:
            import tomli as tomllib  # type: ignore

        with open(self.pyproject_path, "rb") as f:
            data = tomllib.load(f)

        name = data.get("project", {}).get("name")
        if not name:
            raise ValueError("Package name not found in pyproject.toml")

        return name

    def clean_dist(self) -> None:
        """Remove old dist files."""
        if self.dist_dir.exists():
            import shutil

            shutil.rmtree(self.dist_dir)

    def build_distributions(self) -> dict[str, str]:
        """Build wheel and source distributions.

        Returns:
            Dict with paths to built distributions:
            - wheel: Path to wheel file
            - sdist: Path to source distribution

        Raises:
            RuntimeError: If build fails
        """
        # Clean old distributions
        self.clean_dist()

        try:
            # Build using hatch or build
            result = subprocess.run(
                ["python", "-m", "build"],
                cwd=self.project_dir,
                capture_output=True,
                text=True,
                timeout=300,
            )

            if result.returncode != 0:
                raise RuntimeError(f"Build failed: {result.stderr}")

            # Find the built files
            wheel_file = None
            sdist_file = None

            if self.dist_dir.exists():
                for file in self.dist_dir.iterdir():
                    if file.suffix == ".whl":
                        wheel_file = file
                    elif file.name.endswith(".tar.gz"):
                        sdist_file = file

            if not wheel_file or not sdist_file:
                raise RuntimeError("Build did not produce expected distribution files")

            return {
                "wheel": str(wheel_file),
                "sdist": str(sdist_file),
            }

        except FileNotFoundError as e:
            if "No such file" not in str(e):
                raise RuntimeError(
                    "Python build module not found. Install with: pip install build"
                )
            raise RuntimeError("Build did not produce expected distribution files")

    def verify_package(self) -> dict[str, str]:
        """Verify package metadata using twine.

        Returns:
            Dict with verification results

        Raises:
            RuntimeError: If verification fails
        """
        try:
            wheel_file = None
            for file in self.dist_dir.iterdir():
                if file.suffix == ".whl":
                    wheel_file = file
                    break

            if not wheel_file:
                raise RuntimeError("No wheel file found in dist/")

            result = subprocess.run(
                ["python", "-m", "twine", "check", str(wheel_file)],
                capture_output=True,
                text=True,
                timeout=30,
            )

            if result.returncode != 0:
                raise RuntimeError(f"Package verification failed: {result.stderr}")

            return {
                "status": "valid",
                "file": wheel_file.name,
                "message": "Package metadata is valid",
            }

        except FileNotFoundError:
            raise RuntimeError("twine not found. Install with: pip install twine")

    def upload_to_pypi(
        self,
        dry_run: bool = False,
        skip_existing: bool = False,
    ) -> dict[str, str]:
        """Upload distributions to PyPI.

        Args:
            dry_run: If True, only simulate upload without actually uploading
            skip_existing: If True, skip packages that already exist on PyPI

        Returns:
            Dict with upload results

        Raises:
            RuntimeError: If upload fails
        """
        try:
            # Build if not already done
            if not self.dist_dir.exists():
                self.build_distributions()

            # Prepare twine command
            cmd = [
                "python",
                "-m",
                "twine",
                "upload",
                "--repository-url",
                self.pypi_url,
            ]

            # Add authentication
            cmd.extend(["--username", "__token__"])
            cmd.extend(["--password", str(self.pypi_token)])

            # Add options
            if dry_run:
                cmd.append("--dry-run")
            if skip_existing:
                cmd.append("--skip-existing")

            # Add distribution files
            for dist_file in self.dist_dir.glob("*"):
                if dist_file.is_file():
                    cmd.append(str(dist_file))

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300,
            )

            if result.returncode != 0:
                raise RuntimeError(f"Upload failed: {result.stderr}")

            # Parse stdout message - get the last meaningful line
            message = "Upload complete"
            if result.stdout:
                lines = result.stdout.strip().split("\n")
                # Get the last non-empty line
                for line in reversed(lines):
                    if line.strip():
                        message = line.strip()
                        break

            return {
                "status": "success" if not dry_run else "dry-run",
                "mode": "dry-run" if dry_run else "production",
                "message": message,
            }

        except FileNotFoundError:
            raise RuntimeError("twine not found. Install with: pip install twine")

    def get_upload_status(self) -> dict[str, str]:
        """Check status of distributions ready for upload.

        Returns:
            Dict with distribution information
        """
        if not self.dist_dir.exists():
            return {
                "status": "no-distributions",
                "count": "0",
            }

        distributions = []
        for file in self.dist_dir.glob("*"):
            if file.is_file():
                distributions.append(
                    {
                        "name": file.name,
                        "size": str(file.stat().st_size),
                    }
                )

        return {
            "status": "ready" if distributions else "empty",
            "count": str(len(distributions)),
            "distributions": str(distributions),
        }

    def publish_version(
        self,
        version: str,
        dry_run: bool = False,
    ) -> dict[str, str]:
        """Complete publish workflow for a specific version.

        Args:
            version: Version string to publish
            dry_run: If True, only simulate publishing

        Returns:
            Dict with publication results

        Steps:
        1. Verify version matches pyproject.toml
        2. Clean and build distributions
        3. Verify package metadata
        4. Upload to PyPI
        """
        print(f"📦 Publishing version {version}...\n")

        # Step 1: Verify version
        print("1️⃣  Verifying version...")
        current_version = self.get_version()
        if current_version != version:
            raise ValueError(
                f"Version mismatch: expected {version}, got {current_version}"
            )
        print(f"   ✅ Version verified: {version}\n")

        # Step 2: Build distributions
        print("2️⃣  Building distributions...")
        build_result = self.build_distributions()
        print(f"   ✅ Built {build_result['wheel']}")
        print(f"   ✅ Built {build_result['sdist']}\n")

        # Step 3: Verify package
        print("3️⃣  Verifying package metadata...")
        verify_result = self.verify_package()
        print(f"   ✅ {verify_result['message']}\n")

        # Step 4: Upload
        print("4️⃣  Uploading to PyPI...")
        upload_result = self.upload_to_pypi(dry_run=dry_run)
        if dry_run:
            print(f"   🔄 [DRY RUN] {upload_result['message']}\n")
        else:
            print(f"   ✅ {upload_result['message']}\n")

        return upload_result

    def get_version(self) -> str:
        """Get current package version.

        Returns:
            Version string
        """
        return self.get_package_version()
