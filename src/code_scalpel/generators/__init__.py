"""Code generators for Code Scalpel.

This module provides code generation capabilities:
- TestGenerator: Generate unit tests from symbolic execution results
- RefactorSimulator: Simulate code changes and verify safety
"""

# TODO [CORE] Add GeneratorFactory class for creating generators by type
# TODO [CORE] Add TemplateRegistry for managing code templates
# TODO [CORE] Add CodeGenerationConfig dataclass for configuration
# TODO [CORE] Add get_generator(generator_type) factory method
# TODO [CORE] Add register_custom_generator(name, generator_class) extensibility
# TODO [CORE] Add list_available_generators() enumeration
# TODO [CORE] Add validate_generator_output(code) validation
# TODO [CORE] Add format_generated_code(code, style) formatter
# TODO [CORE] Add get_supported_languages() for language detection
# TODO [CORE] Add get_supported_frameworks() for framework support
# TODO [CORE] Add merge_generated_code(base, generated) merger
# TODO [CORE] Add compare_generators(generator1, generator2) comparison
# TODO [CORE] Add generator_statistics(generator) metrics
# TODO [CORE] Add export_generator_config(config, format) exporter
# TODO [CORE] Add import_generator_config(data, format) importer
# TODO [CORE] Add GeneratorResult dataclass for all results
# TODO [CORE] Add GeneratorError exception class
# TODO [CORE] Add GeneratorWarning warning class
# TODO [CORE] Add create_empty_template() factory
# TODO [CORE] Add validate_template(template) checker
# TODO [CORE] Add list_generator_dependencies() dependency finder
# TODO [CORE] Add get_generator_version(generator) versioning
# TODO [CORE] Add generator_compatibility_check(generator1, generator2) checker
# TODO [CORE] Add reset_generator_cache() cache management
# TODO [CORE] Add get_generator_metrics() performance metrics
# TODO [PRO] Add async test generation for large codebases
# TODO [PRO] Add incremental test generation (only changed functions)
# TODO [PRO] Add test generation caching for repeated runs
# TODO [PRO] Add batch test generation for multiple functions
# TODO [PRO] Add test template customization and DSL
# TODO [PRO] Add property-based test generation (hypothesis)
# TODO [PRO] Add mutation testing integration
# TODO [PRO] Add performance regression test generation
# TODO [PRO] Add security-focused test generation
# TODO [PRO] Add ML-based test prioritization
# TODO [PRO] Add test clustering and grouping
# TODO [PRO] Add test dependency graph visualization
# TODO [PRO] Add cross-module test generation
# TODO [PRO] Add API contract test generation
# TODO [PRO] Add database migration test generation
# TODO [PRO] Add test coverage gap analysis
# TODO [PRO] Add test redundancy detection
# TODO [PRO] Add test execution parallelization hints
# TODO [PRO] Add test result aggregation
# TODO [PRO] Add custom assertion generation
# TODO [PRO] Add fixture generation from fixtures
# TODO [PRO] Add mock/stub generation
# TODO [PRO] Add test data generation from schemas
# TODO [PRO] Add performance profiling in generated tests
# TODO [PRO] Add code complexity metrics in test selection
# TODO [ENTERPRISE] Add distributed test generation across agents
# TODO [ENTERPRISE] Add federated test generation across organizations
# TODO [ENTERPRISE] Add test generation work queue management
# TODO [ENTERPRISE] Add test generation load balancing
# TODO [ENTERPRISE] Add multi-region test generation coordination
# TODO [ENTERPRISE] Add test generation caching across regions
# TODO [ENTERPRISE] Add federated generator training (ML)
# TODO [ENTERPRISE] Add test generation cost tracking per org
# TODO [ENTERPRISE] Add test generation quota enforcement
# TODO [ENTERPRISE] Add test generation SLA monitoring
# TODO [ENTERPRISE] Add test generation audit logging
# TODO [ENTERPRISE] Add test generation compliance checking (SOC2/HIPAA/GDPR)
# TODO [ENTERPRISE] Add test generation encryption for sensitive code
# TODO [ENTERPRISE] Add test generation access control (RBAC)
# TODO [ENTERPRISE] Add test generation encryption key management
# TODO [ENTERPRISE] Add test generation multi-tenancy isolation
# TODO [ENTERPRISE] Add test generation disaster recovery
# TODO [ENTERPRISE] Add test generation failover mechanisms
# TODO [ENTERPRISE] Add test generation data retention policies
# TODO [ENTERPRISE] Add test generation billing integration
# TODO [ENTERPRISE] Add test generation executive reporting
# TODO [ENTERPRISE] Add test generation anomaly detection
# TODO [ENTERPRISE] Add test generation circuit breaker
# TODO [ENTERPRISE] Add test generation rate limiting
# TODO [ENTERPRISE] Add test generation health monitoring

from .refactor_simulator import RefactorResult, RefactorSimulator
from .test_generator import GeneratedTestSuite, TestGenerator

__all__ = [
    "TestGenerator",
    "GeneratedTestSuite",
    "RefactorSimulator",
    "RefactorResult",
]
