"""
Configuration initialization module.

[20251219_FEATURE] v3.0.2 - Auto-initialize .code-scalpel configuration
[20251222_FEATURE] v3.1.0 - Complete governance structure with policies
"""

from pathlib import Path
from .templates import (
    POLICY_YAML_TEMPLATE,
    BUDGET_YAML_TEMPLATE,
    README_TEMPLATE,
    GITIGNORE_TEMPLATE,
    CONFIG_JSON_TEMPLATE,
    ENV_EXAMPLE_TEMPLATE,
    DEV_GOVERNANCE_YAML_TEMPLATE,
    PROJECT_STRUCTURE_YAML_TEMPLATE,
    POLICIES_README_TEMPLATE,
    ARCHITECTURE_README_TEMPLATE,
    DEVOPS_README_TEMPLATE,
    DEVSECOPS_README_TEMPLATE,
    PROJECT_README_TEMPLATE,
    LAYERED_ARCHITECTURE_REGO_TEMPLATE,
    DOCKER_SECURITY_REGO_TEMPLATE,
    SECRET_DETECTION_REGO_TEMPLATE,
    PROJECT_STRUCTURE_REGO_TEMPLATE,
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

    # ========================================================================
    # v3.1.0+ Governance Structure
    # ========================================================================

    # Create dev-governance.yaml
    dev_governance_file = config_dir / "dev-governance.yaml"
    dev_governance_file.write_text(DEV_GOVERNANCE_YAML_TEMPLATE)
    files_created.append("dev-governance.yaml")

    # Create project-structure.yaml
    project_structure_file = config_dir / "project-structure.yaml"
    project_structure_file.write_text(PROJECT_STRUCTURE_YAML_TEMPLATE)
    files_created.append("project-structure.yaml")

    # Create policies directory structure
    policies_dir = config_dir / "policies"
    policies_dir.mkdir(exist_ok=True)

    # Policies main README
    policies_readme = policies_dir / "README.md"
    policies_readme.write_text(POLICIES_README_TEMPLATE)
    files_created.append("policies/README.md")

    # Architecture policies
    arch_dir = policies_dir / "architecture"
    arch_dir.mkdir(exist_ok=True)
    (arch_dir / "README.md").write_text(ARCHITECTURE_README_TEMPLATE)
    (arch_dir / "layered_architecture.rego").write_text(LAYERED_ARCHITECTURE_REGO_TEMPLATE)
    files_created.append("policies/architecture/README.md")
    files_created.append("policies/architecture/layered_architecture.rego")

    # DevOps policies
    devops_dir = policies_dir / "devops"
    devops_dir.mkdir(exist_ok=True)
    (devops_dir / "README.md").write_text(DEVOPS_README_TEMPLATE)
    (devops_dir / "docker_security.rego").write_text(DOCKER_SECURITY_REGO_TEMPLATE)
    files_created.append("policies/devops/README.md")
    files_created.append("policies/devops/docker_security.rego")

    # DevSecOps policies
    devsecops_dir = policies_dir / "devsecops"
    devsecops_dir.mkdir(exist_ok=True)
    (devsecops_dir / "README.md").write_text(DEVSECOPS_README_TEMPLATE)
    (devsecops_dir / "secret_detection.rego").write_text(SECRET_DETECTION_REGO_TEMPLATE)
    files_created.append("policies/devsecops/README.md")
    files_created.append("policies/devsecops/secret_detection.rego")

    # Project structure policies
    project_dir = policies_dir / "project"
    project_dir.mkdir(exist_ok=True)
    (project_dir / "README.md").write_text(PROJECT_README_TEMPLATE)
    (project_dir / "structure.rego").write_text(PROJECT_STRUCTURE_REGO_TEMPLATE)
    files_created.append("policies/project/README.md")
    files_created.append("policies/project/structure.rego")

    return {
        "success": True,
        "message": "Configuration directory created successfully",
        "path": str(config_dir),
        "files_created": files_created,
    }
