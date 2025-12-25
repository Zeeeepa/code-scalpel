"""Code generators for Code Scalpel.

This module provides code generation capabilities:
- TestGenerator: Generate unit tests from symbolic execution results
- RefactorSimulator: Simulate code changes and verify safety

TODO ITEMS: generators/__init__.py
======================================================================
COMMUNITY TIER - Core Generator Infrastructure
======================================================================
1. Add GeneratorFactory class for creating generators by type
2. Add TemplateRegistry for managing code templates
3. Add CodeGenerationConfig dataclass for configuration
4. Add get_generator(generator_type) factory method
5. Add register_custom_generator(name, generator_class) extensibility
6. Add list_available_generators() enumeration
7. Add validate_generator_output(code) validation
8. Add format_generated_code(code, style) formatter
9. Add get_supported_languages() for language detection
10. Add get_supported_frameworks() for framework support
11. Add merge_generated_code(base, generated) merger
12. Add compare_generators(generator1, generator2) comparison
13. Add generator_statistics(generator) metrics
14. Add export_generator_config(config, format) exporter
15. Add import_generator_config(data, format) importer
16. Add GeneratorResult dataclass for all results
17. Add GeneratorError exception class
18. Add GeneratorWarning warning class
19. Add create_empty_template() factory
20. Add validate_template(template) checker
21. Add list_generator_dependencies() dependency finder
22. Add get_generator_version(generator) versioning
23. Add generator_compatibility_check(generator1, generator2) checker
24. Add reset_generator_cache() cache management
25. Add get_generator_metrics() performance metrics

======================================================================
PRO TIER - Advanced Generator Features
======================================================================
26. Add async test generation for large codebases
27. Add incremental test generation (only changed functions)
28. Add test generation caching for repeated runs
29. Add batch test generation for multiple functions
30. Add test template customization and DSL
31. Add property-based test generation (hypothesis)
32. Add mutation testing integration
33. Add performance regression test generation
34. Add security-focused test generation
35. Add ML-based test prioritization
36. Add test clustering and grouping
37. Add test dependency graph visualization
38. Add cross-module test generation
39. Add API contract test generation
40. Add database migration test generation
41. Add test coverage gap analysis
42. Add test redundancy detection
43. Add test execution parallelization hints
44. Add test result aggregation
45. Add custom assertion generation
46. Add fixture generation from fixtures
47. Add mock/stub generation
48. Add test data generation from schemas
49. Add performance profiling in generated tests
50. Add code complexity metrics in test selection

======================================================================
ENTERPRISE TIER - Distributed & Federated Generators
======================================================================
51. Add distributed test generation across agents
52. Add federated test generation across organizations
53. Add test generation work queue management
54. Add test generation load balancing
55. Add multi-region test generation coordination
56. Add test generation caching across regions
57. Add federated generator training (ML)
58. Add test generation cost tracking per org
59. Add test generation quota enforcement
60. Add test generation SLA monitoring
61. Add test generation audit logging
62. Add test generation compliance checking (SOC2/HIPAA/GDPR)
63. Add test generation encryption for sensitive code
64. Add test generation access control (RBAC)
65. Add test generation encryption key management
66. Add test generation multi-tenancy isolation
67. Add test generation disaster recovery
68. Add test generation failover mechanisms
69. Add test generation data retention policies
70. Add test generation billing integration
71. Add test generation executive reporting
72. Add test generation anomaly detection
73. Add test generation circuit breaker
74. Add test generation rate limiting
75. Add test generation health monitoring
"""

from .test_generator import TestGenerator, GeneratedTestSuite
from .refactor_simulator import RefactorSimulator, RefactorResult

__all__ = [
    "TestGenerator",
    "GeneratedTestSuite",
    "RefactorSimulator",
    "RefactorResult",
]
