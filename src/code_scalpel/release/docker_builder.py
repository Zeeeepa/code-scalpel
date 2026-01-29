"""Docker image building and publishing for Code Scalpel.

Handles building Docker images with proper tagging and publishing to
Docker registries (Docker Hub, GitHub Container Registry, etc.).

Features:
- Build Docker images with semantic versioning tags
- Tag images with multiple tags (version, latest, etc.)
- Push images to Docker registries
- Support for multiple image names (main, rest-api)
- Authentication with Docker registries
- Dry-run mode for testing
"""

from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Optional


class DockerImageBuilder:
    """Build and publish Docker images for Code Scalpel.

    Attributes:
        project_dir: Root directory of the project
        version: Version string (e.g., "1.2.1")
        registry: Docker registry URL (default: Docker Hub)
        image_names: List of image names to build
        username: Registry username
        password_or_token: Registry password or authentication token
    """

    def __init__(
        self,
        project_dir: str = ".",
        version: str = "",
        registry: str = "docker.io",
        image_names: Optional[list[str]] = None,
        username: str = "",
        password_or_token: str = "",
    ):
        """Initialize Docker image builder.

        Args:
            project_dir: Root directory of the project (default: current directory)
            version: Version string for image tags (e.g., "1.2.1")
            registry: Docker registry URL (default: docker.io for Docker Hub)
            image_names: List of base image names (default: ["code-scalpel"])
            username: Registry username for authentication
            password_or_token: Registry password or token

        Raises:
            ValueError: If version is not provided or if Dockerfile not found
        """
        self.project_dir = Path(project_dir).resolve()
        self.version = version
        self.registry = registry
        self.image_names = image_names or ["code-scalpel"]
        self.username = username
        self.password_or_token = password_or_token

        # Validate version
        if not version:
            raise ValueError("Version is required for image tagging")

        # Validate Dockerfile exists
        if not (self.project_dir / "Dockerfile").exists():
            raise ValueError(f"Dockerfile not found in {self.project_dir}")

    def build_image(
        self,
        dockerfile: str = "Dockerfile",
        image_name: str = "code-scalpel",
        dry_run: bool = False,
    ) -> dict[str, str]:
        """Build Docker image with version tags.

        Builds an image and tags it with:
        - version tag (e.g., "1.2.1")
        - latest tag
        - registry-prefixed tags for pushing

        Args:
            dockerfile: Path to Dockerfile (relative to project_dir)
            image_name: Base image name (e.g., "code-scalpel")
            dry_run: If True, print commands but don't execute them

        Returns:
            Dictionary with build information:
                - image_name: Full image name with registry
                - version_tag: Full tag with version
                - latest_tag: Full tag for "latest"
                - build_output: Build command output (empty if dry_run)

        Raises:
            RuntimeError: If build fails
            FileNotFoundError: If Dockerfile not found
        """
        dockerfile_path = self.project_dir / dockerfile

        if not dockerfile_path.exists():
            raise FileNotFoundError(f"Dockerfile not found: {dockerfile_path}")

        # Build full image names with registry
        full_image_name = f"{self.registry}/{image_name}"
        version_tag = f"{full_image_name}:{self.version}"
        latest_tag = f"{full_image_name}:latest"

        # Build command
        build_cmd = [
            "docker",
            "build",
            "-f",
            str(dockerfile_path),
            "-t",
            version_tag,
            "-t",
            latest_tag,
            str(self.project_dir),
        ]

        if dry_run:
            print(f"Would run: {' '.join(build_cmd)}")
            return {
                "image_name": full_image_name,
                "version_tag": version_tag,
                "latest_tag": latest_tag,
                "build_output": "",
            }

        try:
            result = subprocess.run(
                build_cmd,
                capture_output=True,
                text=True,
                cwd=str(self.project_dir),
            )

            if result.returncode != 0:
                error_msg = result.stderr or result.stdout
                raise RuntimeError(f"Docker build failed: {error_msg}")

            return {
                "image_name": full_image_name,
                "version_tag": version_tag,
                "latest_tag": latest_tag,
                "build_output": result.stdout,
            }

        except FileNotFoundError:
            raise RuntimeError("Docker is not installed or not in PATH. " "Install Docker to use this feature.")

    def authenticate(self, dry_run: bool = False) -> bool:
        """Authenticate with Docker registry.

        Args:
            dry_run: If True, print commands but don't execute them

        Returns:
            True if authentication successful

        Raises:
            RuntimeError: If authentication fails or credentials not provided
        """
        if not self.username or not self.password_or_token:
            raise ValueError("Username and password/token required for authentication")

        # For Docker Hub, use '-'  to read password from stdin
        auth_cmd = [
            "docker",
            "login",
            "-u",
            self.username,
            "--password-stdin",
            self.registry,
        ]

        if dry_run:
            print(f"Would authenticate with {self.registry}")
            return True

        try:
            result = subprocess.run(
                auth_cmd,
                input=self.password_or_token,
                capture_output=True,
                text=True,
            )

            if result.returncode != 0:
                error_msg = result.stderr or result.stdout
                raise RuntimeError(f"Docker authentication failed: {error_msg}")

            return True

        except FileNotFoundError:
            raise RuntimeError("Docker is not installed or not in PATH. " "Install Docker to use this feature.")

    def push_image(
        self,
        image_tag: str,
        dry_run: bool = False,
    ) -> dict[str, str]:
        """Push Docker image to registry.

        Args:
            image_tag: Full image tag to push (e.g., "docker.io/code-scalpel:1.2.1")
            dry_run: If True, print commands but don't execute them

        Returns:
            Dictionary with push information:
                - image_tag: Tag that was pushed
                - push_output: Push command output

        Raises:
            RuntimeError: If push fails
        """
        push_cmd = ["docker", "push", image_tag]

        if dry_run:
            print(f"Would run: {' '.join(push_cmd)}")
            return {
                "image_tag": image_tag,
                "push_output": "",
            }

        try:
            result = subprocess.run(
                push_cmd,
                capture_output=True,
                text=True,
            )

            if result.returncode != 0:
                error_msg = result.stderr or result.stdout
                raise RuntimeError(f"Docker push failed: {error_msg}")

            return {
                "image_tag": image_tag,
                "push_output": result.stdout,
            }

        except FileNotFoundError:
            raise RuntimeError("Docker is not installed or not in PATH. " "Install Docker to use this feature.")

    def publish_release(
        self,
        skip_push: bool = False,
        dry_run: bool = False,
    ) -> dict[str, str | list[str]]:
        """Build and publish Docker images for a release.

        Builds all configured images and optionally pushes them to registry.

        Args:
            skip_push: If True, build images but don't push to registry
            dry_run: If True, print commands but don't execute them

        Returns:
            Dictionary with release information:
                - version: Version that was released
                - images_built: List of built image tags
                - images_pushed: List of pushed image tags

        Raises:
            RuntimeError: If build or push fails
        """
        images_built = []
        images_pushed = []

        print(f"\n🐳 Building Docker images for v{self.version}...\n")

        # Build main image
        build_result = self.build_image(
            dockerfile="Dockerfile",
            image_name="code-scalpel",
            dry_run=dry_run,
        )

        images_built.append(build_result["version_tag"])
        print(f"✅ Built: {build_result['version_tag']}")
        print(f"✅ Tagged: {build_result['latest_tag']}")

        # Build REST API image if Dockerfile.rest exists
        if (self.project_dir / "Dockerfile.rest").exists():
            rest_result = self.build_image(
                dockerfile="Dockerfile.rest",
                image_name="code-scalpel-rest",
                dry_run=dry_run,
            )

            images_built.append(rest_result["version_tag"])
            print(f"✅ Built: {rest_result['version_tag']}")
            print(f"✅ Tagged: {rest_result['latest_tag']}")

        # Push images if not skipped
        if not skip_push:
            print("\n📤 Pushing images to registry...\n")

            # Authenticate if credentials provided
            if self.username and self.password_or_token:
                self.authenticate(dry_run=dry_run)

            # Push all built images
            for image_tag in images_built:
                self.push_image(image_tag, dry_run=dry_run)
                images_pushed.append(image_tag)
                print(f"✅ Pushed: {image_tag}")

            # Also push latest tags
            latest_tag = f"{self.registry}/code-scalpel:latest"
            self.push_image(latest_tag, dry_run=dry_run)
            images_pushed.append(latest_tag)
            print(f"✅ Pushed: {latest_tag}")

        return {
            "version": self.version,
            "images_built": images_built,
            "images_pushed": images_pushed,
        }

    def get_build_status(self) -> dict[str, str]:
        """Check current build status.

        Returns:
            Dictionary with status information:
                - version: Current version
                - project_dir: Project directory path
                - registry: Configured registry
                - has_dockerfile: Whether Dockerfile exists
                - has_rest_dockerfile: Whether Dockerfile.rest exists
        """
        return {
            "version": self.version,
            "project_dir": str(self.project_dir),
            "registry": self.registry,
            "has_dockerfile": str((self.project_dir / "Dockerfile").exists()),
            "has_rest_dockerfile": str((self.project_dir / "Dockerfile.rest").exists()),
        }
