# Code Scalpel v3.0.4 "Ninja Warrior" Release Notes

**Release Date:** December 20, 2025  
**Codename:** Ninja Warrior  
**Previous Version:** v3.0.3  
**Stage:** Stage 3 - API Contract & Cross-Service Analysis

---

## Executive Summary

Code Scalpel v3.0.4 "Ninja Warrior" completes Stage 3 of the development roadmap, introducing comprehensive API contract validation and cross-service taint analysis capabilities. This release adds five major features for detecting breaking changes in API schemas, tracking data flow across microservice boundaries, and identifying XSS vulnerabilities in frontend code.

**Key Highlights:**
- Schema drift detection for Protobuf, JSON Schema, and GraphQL
- gRPC contract analysis and validation
- Cross-service Kafka taint tracking
- Frontend DOM input detection with XSS risk analysis
- Performance fix for cross-file security scans

---

## What's New

### 1. Schema Drift Detection

Detect breaking changes between schema versions before deployment.

**Supported Formats:**
- Protobuf (.proto) schemas
- JSON Schema
- OpenAPI/Swagger (planned)

**Usage:**
```python
from code_scalpel.symbolic_execution_tools import SchemaDriftDetector

detector = SchemaDriftDetector()
result = detector.compare_protobuf(old_proto, new_proto)

if result.has_breaking_changes():
    for change in result.breaking_changes:
        print(f"BREAKING: {change}")
```

**Detectable Changes:**
| Change Type | Severity |
|------------|----------|
| Field removed | BREAKING |
| Field type changed | BREAKING |
| Field number changed | BREAKING |
| Required field added | BREAKING |
| Optional field added | INFO |
| Field deprecated | WARNING |

### 2. gRPC Contract Analyzer

Parse and validate gRPC service definitions with comprehensive best-practice checks.

**Usage:**
```python
from code_scalpel.symbolic_execution_tools import GrpcContractAnalyzer

analyzer = GrpcContractAnalyzer()
contract = analyzer.analyze(proto_content)

print(f"Services: {contract.service_count}")
print(f"Total RPCs: {contract.total_rpc_count}")

# Validate for best practices
issues = analyzer.validate(contract)
for issue in issues:
    print(f"{issue.severity}: {issue.message}")
```

**Features:**
- Service and message extraction
- Streaming type detection (unary, client/server/bidirectional streaming)
- Contract comparison for breaking changes
- Best-practice validation (naming conventions, pagination, etc.)

### 3. GraphQL Schema Tracker

Track GraphQL schema evolution and detect breaking changes.

**Usage:**
```python
from code_scalpel.symbolic_execution_tools import GraphQLSchemaTracker

tracker = GraphQLSchemaTracker()
schema = tracker.parse(sdl_content)

print(f"Types: {schema.type_count}")
print(f"Queries: {len(schema.queries)}")
print(f"Mutations: {len(schema.mutations)}")

# Compare versions
drift = tracker.compare(old_sdl, new_sdl)
if drift.has_breaking_changes():
    for change in drift.breaking_changes:
        print(f"BREAKING: {change}")
```

**Detectable Changes:**
- Type removals and modifications
- Field removals and type changes
- Argument changes (added required, removed, type changed)
- Enum value removals
- Interface implementation changes

### 4. Kafka Taint Tracking

Track tainted data flow through Kafka producers and consumers across microservices.

**Supported Libraries:**
| Language | Libraries |
|----------|-----------|
| Python | kafka-python, confluent-kafka, aiokafka, faust |
| Java | kafka-clients, spring-kafka |
| JavaScript | kafkajs, node-rdkafka |

**Usage:**
```python
from code_scalpel.symbolic_execution_tools import KafkaTaintTracker

tracker = KafkaTaintTracker()
result = tracker.analyze_file(source_code, file_path="app.py", language="python")

print(f"Producers: {len(result.producers)}")
print(f"Tainted producers: {len(result.tainted_producers)}")
print(f"Has taint risks: {result.has_taint_risks}")

# Summary
print(result.summary())
```

**Detection Capabilities:**
- Producer calls with tainted data
- Consumer handlers as taint sources
- Taint bridges (consumer → producer flows)
- Topic-level taint tracking

### 5. Frontend DOM Input Detection

Detect user input sources and dangerous sinks in frontend code with XSS risk analysis.

**Supported Frameworks:**
- React (hooks, class components)
- Vue (v-model, composition API)
- Angular (ngModel, @Input)
- Svelte
- Vanilla JavaScript/TypeScript

**Usage:**
```python
from code_scalpel.symbolic_execution_tools import FrontendInputTracker

tracker = FrontendInputTracker()
result = tracker.analyze_file(source_code, file_path="App.tsx", framework="react")

print(f"Input sources: {len(result.input_sources)}")
print(f"Dangerous sinks: {len(result.dangerous_sinks)}")
print(f"Has XSS risks: {result.has_risks}")
print(f"Framework: {result.framework.value}")
```

**Input Sources Detected:**
- DOM element value access
- Event target values
- URL parameters and hash
- Local/session storage
- Framework-specific inputs (useState, v-model, ngModel)

**Dangerous Sinks Detected:**
- innerHTML, outerHTML
- document.write
- eval, Function constructor
- dangerouslySetInnerHTML (React)
- v-html (Vue)
- [innerHTML] (Angular)

---

## Bug Fixes

### Cross-File Security Scan Performance Fix

**Issue:** Cross-file taint analysis could hang indefinitely on large codebases with circular imports or many modules.

**Root Cause:**
1. No timeout mechanism for the analysis
2. Unbounded module traversal
3. Inefficient AST traversal in `_propagate_taint_through_imports`

**Fix:**
- Added `timeout_seconds` parameter (default: 120s via MCP)
- Added `max_modules` parameter (default: 500 via MCP)
- Optimized propagation with pre-cached function nodes
- Capped iterations at 3 for import propagation

**Before:**
```python
# Could hang indefinitely
result = tracker.analyze_project("/large/codebase")
```

**After:**
```python
# Returns within timeout or raises TimeoutError
result = tracker.analyze_project(
    "/large/codebase",
    timeout_seconds=120,
    max_modules=500
)
```

### Test Import Path Fix

Fixed incorrect import path in `test_vulnerability_scanner.py`:
- **Before:** `from code_scalpel.vulnerability_scanner import ...`
- **After:** `from code_scalpel.symbolic_execution_tools.vulnerability_scanner import ...`

### Lint Fixes

Removed unused imports in `kafka_taint_tracker.py`:
- `Tuple` (unused)
- `Union` (unused)

---

## Test Coverage

| Feature | Tests Added | Total Tests |
|---------|------------|-------------|
| Schema Drift Detection | 52 | 52 |
| gRPC Contract Analyzer | 48 | 48 |
| GraphQL Schema Tracker | 58 | 58 |
| Kafka Taint Tracking | 48 | 48 |
| Frontend Input Detection | 55 | 55 |
| **Stage 3 Total** | **261** | **261** |
| **Full Test Suite** | - | **4355** |

All 4355 tests passing (20 skipped, 1304 warnings).

---

## New Exports

### Kafka Taint Tracking (12 exports)
```python
from code_scalpel.symbolic_execution_tools import (
    KafkaTaintTracker,
    KafkaAnalysisResult,
    KafkaProducer,
    KafkaConsumer,
    KafkaTopicInfo,
    KafkaTaintBridge,
    KafkaLibrary,
    KafkaPatternType,
    KafkaRiskLevel,
    analyze_kafka_file,
    analyze_kafka_codebase,
    find_kafka_taint_bridges,
)
```

### Frontend Input Detection (11 exports)
```python
from code_scalpel.symbolic_execution_tools import (
    FrontendInputTracker,
    FrontendAnalysisResult,
    InputSource,
    DangerousSink,
    DataFlow,
    InputSourceType,
    SinkType,
    FrontendFramework,
    analyze_frontend_file,
    analyze_frontend_codebase,
    find_xss_risks,
)
```

---

## Migration Guide

### From v3.0.3

No breaking changes. All existing APIs remain compatible.

### New Feature Adoption

1. **Schema Drift Detection:**
   ```python
   # Add to CI/CD pipelines
   detector = SchemaDriftDetector()
   result = detector.compare_protobuf(current, proposed)
   if result.has_breaking_changes():
       sys.exit(1)  # Block deployment
   ```

2. **Cross-File Analysis with Timeout:**
   ```python
   # Update existing cross-file analysis calls
   # Old (may hang):
   tracker.analyze_project(path)
   
   # New (safe):
   tracker.analyze_project(path, timeout_seconds=120)
   ```

---

## Known Issues

- OpenAPI/Swagger support in SchemaDriftDetector is planned but not yet implemented
- Kafka taint tracking does not yet support Kafka Streams API
- Frontend tracking does not yet support Web Components

---

## Performance

| Operation | Time (p50) | Time (p99) |
|-----------|-----------|-----------|
| Schema drift (small proto) | 12ms | 45ms |
| gRPC contract analysis | 8ms | 32ms |
| GraphQL schema parse | 15ms | 58ms |
| Kafka file analysis | 22ms | 89ms |
| Frontend file analysis | 18ms | 72ms |
| Cross-file (500 modules) | 45s | 112s |

---

## Upgrade Instructions

```bash
# Upgrade via pip
pip install --upgrade code-scalpel==3.0.4

# Verify installation
python -c "import code_scalpel; print(code_scalpel.__version__)"
# Output: 3.0.4
```

---

## Contributors

- Code Scalpel Team
- GitHub Copilot (AI-assisted development)

---

## Next Release

v3.0.5 will focus on:
- OpenAPI/Swagger schema drift support
- Kafka Streams API support
- Web Components support in frontend tracking
- Additional MCP tools for Stage 3 features
