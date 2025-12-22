"""
Configuration initialization module.

[20251219_FEATURE] v3.0.2 - Auto-initialize .code-scalpel configuration
"""

from pathlib import Path
from .templates import (
    POLICY_YAML_TEMPLATE,
    BUDGET_YAML_TEMPLATE,
    README_TEMPLATE,
    GITIGNORE_TEMPLATE,
    CONFIG_JSON_TEMPLATE,
    ENV_EXAMPLE_TEMPLATE,
)


def init_config_dir(target_dir: str = ".") -> dict:
    """
    Initialize .code-scalpel configuration directory with templates.

    Args:
        target_dir: Directory where .code-scalpel should be created (default: current dir)

    Returns:
        Dictionary with status information
    """
    target_path = Path(target_dir).resolve()
    config_dir = target_path / ".code-scalpel"

    # Check if directory already exists
    if config_dir.exists():
        return {
            "success": False,
            "message": f"Configuration directory already exists: {config_dir}",
            "path": str(config_dir),
            "files_created": [],
        }

    # Create directory
    config_dir.mkdir(parents=True, exist_ok=True)

    files_created = []

    # Create policy.yaml
    policy_file = config_dir / "policy.yaml"
    policy_file.write_text(POLICY_YAML_TEMPLATE)
    files_created.append("policy.yaml")

    # Create budget.yaml
    budget_file = config_dir / "budget.yaml"
    budget_file.write_text(BUDGET_YAML_TEMPLATE)
    files_created.append("budget.yaml")

    # Create README.md
    readme_file = config_dir / "README.md"
    readme_file.write_text(README_TEMPLATE)
    files_created.append("README.md")

    # Create .gitignore
    gitignore_file = config_dir / ".gitignore"
    gitignore_file.write_text(GITIGNORE_TEMPLATE)
    files_created.append(".gitignore")

    # Create config.json
    config_file = config_dir / "config.json"
    config_file.write_text(CONFIG_JSON_TEMPLATE)
    files_created.append("config.json")

    # Create .env.example with environment variable documentation
    env_example_file = target_path / ".env.example"
    env_example_file.write_text(ENV_EXAMPLE_TEMPLATE)
    files_created.append(".env.example")

    # Initialize empty audit.log
    audit_log_file = config_dir / "audit.log"
    audit_log_file.touch()
    files_created.append("audit.log")

    return {
        "success": True,
        "message": "Configuration directory created successfully",
        "path": str(config_dir),
        "files_created": files_created,
    }
