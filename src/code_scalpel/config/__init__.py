# [20251218_FEATURE] Governance configuration module for v3.0.0 "Autonomy"

"""
Configuration module for Code Scalpel.
"""

# TODO [COMMUNITY] Add ConfigFactory class for creating config by type
# TODO [COMMUNITY] Add ConfigRegistry for managing configuration classes
# TODO [COMMUNITY] Add ConfigValidator dataclass for validation rules
# TODO [COMMUNITY] Add get_config(config_type) factory method
# TODO [COMMUNITY] Add register_custom_config(name, config_class) extensibility
# TODO [COMMUNITY] Add list_available_configs() enumeration
# TODO [COMMUNITY] Add validate_config(config) validation
# TODO [COMMUNITY] Add merge_configs(config1, config2) merger
# TODO [COMMUNITY] Add compare_configs(config1, config2) comparison
# TODO [COMMUNITY] Add config_statistics(config) metrics
# TODO [COMMUNITY] Add export_config(config, format) exporter
# TODO [COMMUNITY] Add import_config(data, format) importer
# TODO [COMMUNITY] Add ConfigError exception class
# TODO [COMMUNITY] Add ConfigWarning warning class
# TODO [COMMUNITY] Add create_default_config() factory
# TODO [COMMUNITY] Add validate_config_schema(config) schema checker
# TODO [COMMUNITY] Add list_config_dependencies() dependency finder
# TODO [COMMUNITY] Add get_config_version(config) versioning
# TODO [COMMUNITY] Add config_compatibility_check(config1, config2) checker
# TODO [COMMUNITY] Add reset_config_cache() cache management
# TODO [COMMUNITY] Add get_config_metrics() performance metrics
# TODO [COMMUNITY] Add config_to_dict(config) serialization
# TODO [COMMUNITY] Add config_from_dict(data) deserialization
# TODO [COMMUNITY] Add load_config_from_file(filepath) file loader
# TODO [COMMUNITY] Add save_config_to_file(config, filepath) file saver
# TODO [PRO] Add config environment variable expansion
# TODO [PRO] Add config file encryption/decryption
# TODO [PRO] Add config versioning and migrations
# TODO [PRO] Add config hot reload without restart
# TODO [PRO] Add config diff and change tracking
# TODO [PRO] Add config templates and DSL
# TODO [PRO] Add config validation with JSON Schema
# TODO [PRO] Add config inheritance/composition
# TODO [PRO] Add config profiles (dev, staging, prod)
# TODO [PRO] Add config secrets management
# TODO [PRO] Add config audit logging
# TODO [PRO] Add config access control (RBAC)
# TODO [PRO] Add config change notifications
# TODO [PRO] Add config performance profiling
# TODO [PRO] Add config optimization recommendations
# TODO [PRO] Add config debugging/tracing
# TODO [PRO] Add config dry-run mode
# TODO [PRO] Add config rollback capabilities
# TODO [PRO] Add config backup and restore
# TODO [PRO] Add config documentation generation
# TODO [PRO] Add config example generation
# TODO [PRO] Add config validation errors reporting
# TODO [PRO] Add config partial loading
# TODO [PRO] Add config conditional sections
# TODO [PRO] Add config macro expansion
# TODO [ENTERPRISE] Add distributed config sync across agents
# TODO [ENTERPRISE] Add federated config management across orgs
# TODO [ENTERPRISE] Add multi-region config coordination
# TODO [ENTERPRISE] Add config replication and failover
# TODO [ENTERPRISE] Add config consensus and voting
# TODO [ENTERPRISE] Add config distributed locking
# TODO [ENTERPRISE] Add config event streaming
# TODO [ENTERPRISE] Add config monitoring and alerting
# TODO [ENTERPRISE] Add config cost tracking per org
# TODO [ENTERPRISE] Add config quota enforcement
# TODO [ENTERPRISE] Add config SLA monitoring
# TODO [ENTERPRISE] Add config audit trail logging
# TODO [ENTERPRISE] Add config compliance checking (SOC2/HIPAA/GDPR)
# TODO [ENTERPRISE] Add config encryption for sensitive data
# TODO [ENTERPRISE] Add config access control (RBAC)
# TODO [ENTERPRISE] Add config encryption key management
# TODO [ENTERPRISE] Add config multi-tenancy isolation
# TODO [ENTERPRISE] Add config disaster recovery
# TODO [ENTERPRISE] Add config failover mechanisms
# TODO [ENTERPRISE] Add config data retention policies
# TODO [ENTERPRISE] Add config billing integration
# TODO [ENTERPRISE] Add config executive reporting
# TODO [ENTERPRISE] Add config anomaly detection
# TODO [ENTERPRISE] Add config circuit breaker
# TODO [ENTERPRISE] Add config health monitoring

# [20251225_DEPRECATE] Governance config moved to code_scalpel.governance
# For backward compatibility, import from new location
from code_scalpel.governance import (
    AuditConfig,
    AutonomyConstraintsConfig,
    BlastRadiusConfig,
    ChangeBudgetingConfig,
    GovernanceConfig,
    GovernanceConfigLoader,
)

# [20251219_FEATURE] v3.0.2 - Configuration initialization
from .init_config import init_config_dir

__all__ = [
    "ChangeBudgetingConfig",
    "BlastRadiusConfig",
    "AutonomyConstraintsConfig",
    "AuditConfig",
    "GovernanceConfig",
    "GovernanceConfigLoader",
    "init_config_dir",
]
