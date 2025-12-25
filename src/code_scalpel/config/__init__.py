# [20251218_FEATURE] Governance configuration module for v3.0.0 "Autonomy"

"""
Configuration module for Code Scalpel.

TODO ITEMS: config/__init__.py
======================================================================
COMMUNITY TIER - Core Configuration Infrastructure
======================================================================
1. Add ConfigFactory class for creating config by type
2. Add ConfigRegistry for managing configuration classes
3. Add ConfigValidator dataclass for validation rules
4. Add get_config(config_type) factory method
5. Add register_custom_config(name, config_class) extensibility
6. Add list_available_configs() enumeration
7. Add validate_config(config) validation
8. Add merge_configs(config1, config2) merger
9. Add compare_configs(config1, config2) comparison
10. Add config_statistics(config) metrics
11. Add export_config(config, format) exporter
12. Add import_config(data, format) importer
13. Add ConfigError exception class
14. Add ConfigWarning warning class
15. Add create_default_config() factory
16. Add validate_config_schema(config) schema checker
17. Add list_config_dependencies() dependency finder
18. Add get_config_version(config) versioning
19. Add config_compatibility_check(config1, config2) checker
20. Add reset_config_cache() cache management
21. Add get_config_metrics() performance metrics
22. Add config_to_dict(config) serialization
23. Add config_from_dict(data) deserialization
24. Add load_config_from_file(filepath) file loader
25. Add save_config_to_file(config, filepath) file saver

======================================================================
PRO TIER - Advanced Configuration Features
======================================================================
26. Add config environment variable expansion
27. Add config file encryption/decryption
28. Add config versioning and migrations
29. Add config hot reload without restart
30. Add config diff and change tracking
31. Add config templates and DSL
32. Add config validation with JSON Schema
33. Add config inheritance/composition
34. Add config profiles (dev, staging, prod)
35. Add config secrets management
36. Add config audit logging
37. Add config access control (RBAC)
38. Add config change notifications
39. Add config performance profiling
40. Add config optimization recommendations
41. Add config debugging/tracing
42. Add config dry-run mode
43. Add config rollback capabilities
44. Add config backup and restore
45. Add config documentation generation
46. Add config example generation
47. Add config validation errors reporting
48. Add config partial loading
49. Add config conditional sections
50. Add config macro expansion

======================================================================
ENTERPRISE TIER - Distributed & Federated Configuration
======================================================================
51. Add distributed config sync across agents
52. Add federated config management across orgs
53. Add multi-region config coordination
54. Add config replication and failover
55. Add config consensus and voting
56. Add config distributed locking
57. Add config event streaming
58. Add config monitoring and alerting
59. Add config cost tracking per org
60. Add config quota enforcement
61. Add config SLA monitoring
62. Add config audit trail logging
63. Add config compliance checking (SOC2/HIPAA/GDPR)
64. Add config encryption for sensitive data
65. Add config access control (RBAC)
66. Add config encryption key management
67. Add config multi-tenancy isolation
68. Add config disaster recovery
69. Add config failover mechanisms
70. Add config data retention policies
71. Add config billing integration
72. Add config executive reporting
73. Add config anomaly detection
74. Add config circuit breaker
75. Add config health monitoring
"""

from .governance_config import (
    ChangeBudgetingConfig,
    BlastRadiusConfig,
    AutonomyConstraintsConfig,
    AuditConfig,
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
