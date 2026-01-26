# Extraction Tools

Code extraction, refactoring, and symbol management tools for precise code manipulation across single and multiple files.

**Tools in this category:**
- `extract_code` - Extract and analyze code symbols with contextual dependencies
- `rename_symbol` - Rename functions, classes, and methods
- `update_symbol` - Replace code symbols with new implementations

---

## extract_code

Extract code elements (functions, classes, methods) with optional dependency context and cross-file resolution.

### Overview

`extract_code` enables precise extraction of code symbols from source files with optional contextual information. It supports:
- Single-file and cross-file symbol extraction
- Dependency context analysis
- Variable promotion and closure detection
- Microservice generation patterns
- Organization-wide symbol resolution (Enterprise)

**Use cases:**
- Extract a function implementation for reuse or analysis
- Understand symbol dependencies and closure requirements
- Generate microservice definitions from existing code
- Analyze symbol interface and dependencies

### Input Specification

#### Parameters

| Parameter | Type | Required | Community | Pro | Enterprise | Notes |
|-----------|------|----------|-----------|-----|-----------|-------|
| `target_type` | string | Yes | ✓ | ✓ | ✓ | `function`, `class`, `method`, `variable` |
| `target_name` | string | Yes | ✓ | ✓ | ✓ | Symbol name to extract |
| `file_path` | string | No | ✓ | ✓ | ✓ | Path to source file (or use `code` parameter) |
| `code` | string | No | ✓ | ✓ | ✓ | Inline code string (alternative to `file_path`) |
| `language` | string | No | ✓ | ✓ | ✓ | Auto-detected from file ext; or explicit: `python`, `javascript`, `java`, etc. |
| `include_context` | boolean | No | ✓ | ✓ | ✓ | Include surrounding context (imports, class def) |
| `context_depth` | integer | No | ✗ | ✓ | ✓ | Depth of dependency context (1=direct deps only; Pro max=1; Enterprise unlimited) |
| `include_cross_file_deps` | boolean | No | ✗ | ✓ | ✓ | Resolve dependencies across files |
| `include_token_estimate` | boolean | No | ✓ | ✓ | ✓ | Include token count estimate for extracted code |
| `variable_promotion` | boolean | No | ✗ | ✓ | ✓ | Convert local variables to function parameters |
| `closure_detection` | boolean | No | ✗ | ✓ | ✓ | Detect and report closure variables |
| `dependency_injection_suggestions` | boolean | No | ✗ | ✓ | ✓ | Suggest dependency injection patterns |
| `as_microservice` | boolean | No | ✗ | ✓ | ✓ | Generate microservice wrapper code |
| `microservice_host` | string | No | ✗ | ✓ | ✓ | Default host for microservice (127.0.0.1) |
| `microservice_port` | integer | No | ✗ | ✓ | ✓ | Default port for microservice (8000) |
| `organization_wide` | boolean | No | ✗ | ✗ | ✓ | Search entire organization for symbol resolution |
| `workspace_root` | string | No | ✗ | ✓ | ✓ | Root directory for workspace scan |

#### Tier-Specific Constraints

**Community:**
- Single-file extraction only
- No cross-file dependency resolution
- Max extraction size: 1 MB
- Basic symbols only (functions, classes, methods)
- Context limited to same file

**Pro:**
- Cross-file dependency resolution (depth=1, direct dependencies only)
- Max extraction size: 10 MB
- All advanced features available
- Variable promotion and closure detection
- Microservice wrapper generation

**Enterprise:**
- Unlimited context depth across codebase
- Organization-wide symbol resolution
- Max extraction size: 100 MB
- Custom extraction patterns
- Dockerfile generation
- Service boundary detection

### Output Specification

#### Response Structure (All Tiers)

```json
{
  "tier": "community|pro|enterprise",
  "tool_version": "1.x.x",
  "tool_id": "extract_code",
  "request_id": "uuid-v4",
  "capabilities": ["envelope-v1"],
  "duration_ms": 1234,
  "error": null,
  "warnings": [],
  "upgrade_hints": [],
  "data": {
    "success": true,
    "target_name": "function_name",
    "target_code": "def function_name():\n    ...",
    "context_code": "import os\n...",
    "full_code": "import os\n\ndef function_name():\n    ...",
    "error": null,
    "dependencies": {
      "direct": ["os", "sys"],
      "transitive": ["json", "urllib"],
      "closure_variables": ["x", "y"],
      "promoted_variables": ["config"]
    },
    "token_estimate": {
      "target": 45,
      "context": 120,
      "full": 165
    },
    "microservice_wrapper": null,
    "metadata": {
      "language": "python",
      "file_path": "/src/utils.py",
      "line_range": [42, 58],
      "decorators": ["@staticmethod"]
    }
  }
}
```

#### Tier-Specific Output Variations

**Community:**
- Returns only: `success`, `target_name`, `target_code`, `context_code`, `full_code`, `error`, `metadata`
- No dependency analysis
- No token estimates
- No advanced features

**Pro:**
- Adds: `dependencies`, `token_estimate`, `microservice_wrapper` (if requested)
- Cross-file dependencies with depth tracking
- Closure detection and variable promotion suggestions
- Microservice wrapper code generation

**Enterprise:**
- Adds: `organization_wide_resolution`, `custom_patterns`, `dockerfile_template`
- Full codebase dependency resolution
- Service boundary detection
- Advanced microservice configuration

### Tier Comparison Matrix

| Feature | Community | Pro | Enterprise |
|---------|-----------|-----|-----------|
| **Single-file extraction** | ✓ | ✓ | ✓ |
| **Cross-file dependencies** | ✗ | ✓ (depth=1) | ✓ (unlimited) |
| **Max extraction size** | 1 MB | 10 MB | 100 MB |
| **Variable promotion** | ✗ | ✓ | ✓ |
| **Closure detection** | ✗ | ✓ | ✓ |
| **Dependency injection suggestions** | ✗ | ✓ | ✓ |
| **Microservice generation** | ✗ | ✓ | ✓ |
| **Organization-wide resolution** | ✗ | ✗ | ✓ |
| **Custom extraction patterns** | ✗ | ✗ | ✓ |
| **Dockerfile generation** | ✗ | ✗ | ✓ |

### Error Handling

#### Standard Error Codes

- `invalid_argument` - Invalid `target_type`, malformed parameters
- `invalid_path` - File path not found
- `not_found` - Symbol not found in file
- `too_large` - Extracted code exceeds tier limit (Community/Pro only)
- `resource_exhausted` - Hit file count or depth limit (Community/Pro only)
- `not_implemented` - Language not supported
- `upgrade_required` - Feature requires higher tier
- `internal_error` - Unexpected error during extraction

#### Example Error Response

```json
{
  "tier": "community",
  "tool_version": "1.0.0",
  "tool_id": "extract_code",
  "request_id": "uuid-v4",
  "duration_ms": 123,
  "error": {
    "error": "Feature 'cross_file_deps' requires Pro tier or higher",
    "error_code": "upgrade_required"
  },
  "data": null,
  "upgrade_hints": [
    "Upgrade to Pro to enable cross-file dependency extraction"
  ]
}
```

### Example Requests & Responses

#### Example 1: Simple Function Extraction (Community)

**Request:**
```json
{
  "target_type": "function",
  "target_name": "calculate_total",
  "file_path": "/src/billing.py"
}
```

**Response:**
```json
{
  "tier": "community",
  "tool_id": "extract_code",
  "duration_ms": 45,
  "data": {
    "success": true,
    "target_name": "calculate_total",
    "target_code": "def calculate_total(items):\n    return sum(item.price for item in items)",
    "context_code": "# No additional context available in Community tier",
    "full_code": "def calculate_total(items):\n    return sum(item.price for item in items)",
    "metadata": {
      "language": "python",
      "file_path": "/src/billing.py",
      "line_range": [42, 43]
    }
  }
}
```

#### Example 2: Function with Cross-File Dependencies (Pro)

**Request:**
```json
{
  "target_type": "function",
  "target_name": "process_payment",
  "file_path": "/src/billing.py",
  "include_context": true,
  "include_cross_file_deps": true,
  "context_depth": 1,
  "variable_promotion": true,
  "closure_detection": true
}
```

**Response:**
```json
{
  "tier": "pro",
  "tool_id": "extract_code",
  "duration_ms": 234,
  "data": {
    "success": true,
    "target_name": "process_payment",
    "target_code": "def process_payment(amount, user_id):\n    gateway = PaymentGateway()\n    return gateway.charge(amount, user_id)",
    "context_code": "from payment import PaymentGateway\nimport logging\n\nlogger = logging.getLogger(__name__)",
    "full_code": "from payment import PaymentGateway\nimport logging\n\nlogger = logging.getLogger(__name__)\n\ndef process_payment(amount, user_id):\n    gateway = PaymentGateway()\n    return gateway.charge(amount, user_id)",
    "dependencies": {
      "direct": ["PaymentGateway"],
      "transitive": ["payment.api.stripe", "payment.api.fallback"],
      "closure_variables": []
    },
    "token_estimate": {
      "target": 28,
      "context": 45,
      "full": 73
    },
    "metadata": {
      "language": "python",
      "file_path": "/src/billing.py",
      "line_range": [25, 28]
    }
  }
}
```

#### Example 3: Class with Microservice Wrapper (Pro)

**Request:**
```json
{
  "target_type": "class",
  "target_name": "UserService",
  "file_path": "/src/services/user.py",
  "include_context": true,
  "as_microservice": true,
  "microservice_host": "0.0.0.0",
  "microservice_port": 5000
}
```

**Response:**
```json
{
  "tier": "pro",
  "tool_id": "extract_code",
  "duration_ms": 156,
  "data": {
    "success": true,
    "target_name": "UserService",
    "target_code": "class UserService:\n    def __init__(self, db):\n        self.db = db\n    def get_user(self, user_id):\n        return self.db.query(User).get(user_id)\n    def create_user(self, user_data):\n        user = User(**user_data)\n        self.db.add(user)\n        self.db.commit()\n        return user",
    "microservice_wrapper": "from flask import Flask, jsonify, request\nfrom user import UserService\n\napp = Flask(__name__)\nservice = UserService(db)\n\n@app.route('/users/<int:user_id>', methods=['GET'])\ndef get_user(user_id):\n    return jsonify(service.get_user(user_id).to_dict())\n\n@app.route('/users', methods=['POST'])\ndef create_user():\n    data = request.get_json()\n    user = service.create_user(data)\n    return jsonify(user.to_dict()), 201\n\nif __name__ == '__main__':\n    app.run(host='0.0.0.0', port=5000)",
    "metadata": {
      "language": "python",
      "file_path": "/src/services/user.py",
      "line_range": [10, 35]
    }
  }
}
```

#### Example 4: Organization-Wide Resolution (Enterprise)

**Request:**
```json
{
  "target_type": "function",
  "target_name": "validate_api_key",
  "file_path": "/src/auth/middleware.py",
  "include_context": true,
  "include_cross_file_deps": true,
  "context_depth": 5,
  "organization_wide": true,
  "workspace_root": "/src"
}
```

**Response:**
```json
{
  "tier": "enterprise",
  "tool_id": "extract_code",
  "duration_ms": 892,
  "data": {
    "success": true,
    "target_name": "validate_api_key",
    "dependencies": {
      "direct": ["auth.jwt", "auth.redis_cache"],
      "transitive": ["redis", "PyJWT", "cryptography"],
      "closure_variables": [],
      "organization_wide_usages": 47
    },
    "dockerfile_template": "FROM python:3.11-slim\nWORKDIR /app\nCOPY requirements.txt .\nRUN pip install -r requirements.txt\nCOPY src/auth ./auth\nCMD [\"python\", \"-m\", \"auth.service\"]"
  }
}
```

### Performance Considerations

#### Latency

- **Community** (single-file): 30-100ms
- **Pro** (cross-file, depth=1): 150-500ms
- **Enterprise** (org-wide, unlimited depth): 500-3000ms

#### Throughput Limits

- No per-minute rate limits
- Max concurrent requests: 10 (Community), 50 (Pro), 100 (Enterprise)

#### Memory Usage

- Community: ~50-200 MB (1 MB extraction limit)
- Pro: ~200-500 MB (10 MB limit, cross-file analysis)
- Enterprise: ~500MB-2GB (100 MB limit, org-wide resolution)

### Upgrade Paths

**Community → Pro:**
- Enables cross-file dependency resolution
- Unlocks variable promotion and closure detection
- Adds microservice generation
- Increases extraction size from 1MB to 10MB

**Pro → Enterprise:**
- Organization-wide symbol resolution
- Unlimited context depth
- Custom extraction patterns
- Dockerfile generation
- Increases extraction size to 100MB

---

## rename_symbol

Rename functions, classes, methods, and variables with scope-aware cross-file updates.

### Overview

`rename_symbol` safely renames code symbols, automatically updating references across files based on tier capabilities. Features:
- Definition-only rename (Community)
- Cross-file reference updates (Pro)
- Organization-wide rename (Enterprise)
- Automatic backup creation
- Path security validation

**Use cases:**
- Rename a function with automatic cross-file reference updates
- Standardize naming conventions across a project
- Refactor class names with import updates

### Input Specification

#### Parameters

| Parameter | Type | Required | Community | Pro | Enterprise | Notes |
|-----------|------|----------|-----------|-----|-----------|-------|
| `file_path` | string | Yes | ✓ | ✓ | ✓ | Path to file containing the symbol |
| `target_type` | string | Yes | ✓ | ✓ | ✓ | `function`, `class`, `method`, `variable` |
| `target_name` | string | Yes | ✓ | ✓ | ✓ | Current symbol name |
| `new_name` | string | Yes | ✓ | ✓ | ✓ | Desired new name |
| `create_backup` | boolean | No | ✓ | ✓ | ✓ | Create .bak backup file (default: true) |

#### Tier-Specific Constraints

**Community:**
- Definition-only rename (no reference updates)
- Max files searched: 0
- Max files updated: 0 (only definition file)
- Single file operation
- Creates backup automatically

**Pro:**
- Cross-file reference and import updates
- Max files searched: 500
- Max files updated: 200
- Conservative matching (avoids false positives)
- Path security validation

**Enterprise:**
- Organization-wide rename capability
- Unlimited files searched and updated
- Aggressive cross-file matching
- Custom renaming rules
- Rollback support

### Output Specification

#### Response Structure (All Tiers)

```json
{
  "tier": "community|pro|enterprise",
  "tool_version": "1.x.x",
  "tool_id": "rename_symbol",
  "request_id": "uuid-v4",
  "duration_ms": 1234,
  "error": null,
  "data": {
    "success": true,
    "file_path": "/src/utils.py",
    "target_name": "old_name",
    "target_type": "function",
    "new_name": "new_name",
    "files_updated": 1,
    "references_updated": 0,
    "imports_updated": 0,
    "backup_created": true,
    "backup_path": "/src/utils.py.bak",
    "error": null,
    "details": {
      "definition_updated": true,
      "references": [],
      "imports": []
    }
  }
}
```

#### Tier-Specific Output Variations

**Community:**
- Only `definition_updated` and `references[]` (empty)
- No cross-file updates
- `files_updated` = 1, `references_updated` = 0

**Pro:**
- Includes cross-file references and imports
- `files_updated` can be 1-200
- `references_updated` includes all matched references
- `imports_updated` includes updated import statements

**Enterprise:**
- Unlimited files updated
- Includes organization-wide reference tracking
- Detailed rollback plan

### Tier Comparison Matrix

| Feature | Community | Pro | Enterprise |
|---------|-----------|-----|-----------|
| **Definition rename** | ✓ | ✓ | ✓ |
| **Cross-file references** | ✗ | ✓ | ✓ |
| **Import updates** | ✗ | ✓ | ✓ |
| **Backup creation** | ✓ | ✓ | ✓ |
| **Max files searched** | 0 | 500 | Unlimited |
| **Max files updated** | 0 | 200 | Unlimited |
| **Organization-wide** | ✗ | ✗ | ✓ |

### Error Handling

#### Standard Error Codes

- `invalid_argument` - Invalid `target_type` or `new_name`
- `invalid_path` - File path not found
- `forbidden` - Permission denied (read/write)
- `not_found` - Symbol not found in file
- `resource_exhausted` - Exceeded file search limit (Pro only)
- `upgrade_required` - Feature requires higher tier
- `internal_error` - Unexpected error during rename

### Example Requests & Responses

#### Example 1: Definition-Only Rename (Community)

**Request:**
```json
{
  "file_path": "/src/utils.py",
  "target_type": "function",
  "target_name": "calculate_sum",
  "new_name": "sum_values"
}
```

**Response:**
```json
{
  "tier": "community",
  "tool_id": "rename_symbol",
  "duration_ms": 45,
  "data": {
    "success": true,
    "file_path": "/src/utils.py",
    "target_name": "calculate_sum",
    "new_name": "sum_values",
    "target_type": "function",
    "files_updated": 1,
    "references_updated": 0,
    "imports_updated": 0,
    "backup_created": true,
    "backup_path": "/src/utils.py.bak",
    "details": {
      "definition_updated": true,
      "references": [],
      "imports": []
    }
  }
}
```

#### Example 2: Cross-File Rename with Imports (Pro)

**Request:**
```json
{
  "file_path": "/src/services/payment_service.py",
  "target_type": "class",
  "target_name": "PaymentProcessor",
  "new_name": "TransactionProcessor"
}
```

**Response:**
```json
{
  "tier": "pro",
  "tool_id": "rename_symbol",
  "duration_ms": 234,
  "data": {
    "success": true,
    "file_path": "/src/services/payment_service.py",
    "target_name": "PaymentProcessor",
    "new_name": "TransactionProcessor",
    "target_type": "class",
    "files_updated": 5,
    "references_updated": 12,
    "imports_updated": 3,
    "backup_created": true,
    "backup_path": "/src/services/payment_service.py.bak",
    "details": {
      "definition_updated": true,
      "references": [
        {"file": "/src/handlers/payment_handler.py", "line": 42, "context": "processor = PaymentProcessor()"},
        {"file": "/src/tests/test_payment.py", "line": 15, "context": "assert isinstance(obj, PaymentProcessor)"}
      ],
      "imports": [
        {"file": "/src/handlers/payment_handler.py", "updated": "from services.payment_service import TransactionProcessor"},
        {"file": "/src/api/routes.py", "updated": "from services.payment_service import TransactionProcessor"}
      ]
    }
  }
}
```

### Performance Considerations

- **Community**: 30-80ms (single-file only)
- **Pro**: 200-2000ms (depends on project size, ~500 files limit)
- **Enterprise**: 500-5000ms (unlimited scope)

### Upgrade Paths

**Community → Pro:**
- Cross-file reference and import updates
- Increases file search limit from 0 to 500
- Increases file update limit from 0 to 200

**Pro → Enterprise:**
- Organization-wide rename capability
- Unlimited file search and update
- Custom renaming rules

---

## update_symbol

Replace functions, classes, methods, and variables with new code implementations.

### Overview

`update_symbol` safely replaces code symbols with new implementations, with support for:
- Syntax validation (all tiers)
- Semantic validation and multi-file updates (Pro+)
- Atomic operations with rollback (Pro+)
- Pre/post-update hooks (Pro+)
- Formatting preservation (Pro+)

**Use cases:**
- Replace a function implementation with an optimized version
- Update class methods across multiple files
- Refactor symbol definitions with automatic rollback on failure

### Input Specification

#### Parameters

| Parameter | Type | Required | Community | Pro | Enterprise | Notes |
|-----------|------|----------|-----------|-----|-----------|-------|
| `file_path` | string | Yes | ✓ | ✓ | ✓ | Path to file containing the symbol |
| `target_type` | string | Yes | ✓ | ✓ | ✓ | `function`, `class`, `method`, `variable` |
| `target_name` | string | Yes | ✓ | ✓ | ✓ | Symbol name to update |
| `new_code` | string | No | ✓ | ✓ | ✓ | New code to replace the symbol |
| `operation` | string | No | ✓ | ✓ | ✓ | `replace` (default), `prepend`, `append` |
| `new_name` | string | No | ✗ | ✓ | ✓ | Rename symbol during update (Pro+) |
| `create_backup` | boolean | No | ✓ | ✓ | ✓ | Create .bak backup file (default: true) |

#### Tier-Specific Constraints

**Community:**
- Single file updates only
- Syntax validation only
- Max updates per call: 10
- Languages: Python, JavaScript, TypeScript, Java
- Basic replacement only

**Pro:**
- Multi-file cross-file updates
- Semantic validation (symbol name verification)
- Atomic all-or-nothing updates
- Automatic rollback on failure
- Pre/post-update hooks
- Formatting preservation
- Import auto-adjustment
- Max updates per call: Unlimited
- All Community languages + more

**Enterprise:**
- All Pro features
- Custom validation rules
- Advanced hooks (custom scripts)
- Compliance checks
- Unlimited scope

### Output Specification

#### Response Structure (All Tiers)

```json
{
  "tier": "community|pro|enterprise",
  "tool_version": "1.x.x",
  "tool_id": "update_symbol",
  "request_id": "uuid-v4",
  "duration_ms": 1234,
  "error": null,
  "data": {
    "success": true,
    "file_path": "/src/utils.py",
    "target_name": "old_name",
    "target_type": "function",
    "new_name": "new_name",
    "files_updated": 1,
    "backup_created": true,
    "backup_path": "/src/utils.py.bak",
    "error": null,
    "validation_results": {
      "syntax_valid": true,
      "semantic_valid": true,
      "warnings": []
    }
  }
}
```

#### Tier-Specific Output Variations

**Community:**
- Basic validation results (syntax only)
- Single file update only
- Simple success/error status

**Pro:**
- Semantic validation results
- Multi-file update status
- Hook execution results
- Detailed validation warnings
- Rollback plan available

**Enterprise:**
- All Pro features
- Compliance check results
- Custom rule results
- Advanced hook outputs

### Tier Comparison Matrix

| Feature | Community | Pro | Enterprise |
|---------|-----------|-----|-----------|
| **Basic replacement** | ✓ | ✓ | ✓ |
| **Syntax validation** | ✓ | ✓ | ✓ |
| **Semantic validation** | ✗ | ✓ | ✓ |
| **Multi-file updates** | ✗ | ✓ | ✓ |
| **Atomic operations** | ✗ | ✓ | ✓ |
| **Rollback support** | ✗ | ✓ | ✓ |
| **Pre-update hooks** | ✗ | ✓ | ✓ |
| **Post-update hooks** | ✗ | ✓ | ✓ |
| **Formatting preservation** | ✗ | ✓ | ✓ |
| **Import auto-adjustment** | ✗ | ✓ | ✓ |
| **Max updates per call** | 10 | Unlimited | Unlimited |
| **Custom validation rules** | ✗ | ✗ | ✓ |

### Error Handling

#### Standard Error Codes

- `invalid_argument` - Invalid parameters or malformed code
- `invalid_path` - File path not found
- `forbidden` - Permission denied
- `not_found` - Symbol not found in file
- `too_large` - Code exceeds size limits (Community only)
- `resource_exhausted` - Exceeded update limit (Community: max 10/call)
- `upgrade_required` - Feature requires higher tier
- `internal_error` - Unexpected error during update

### Example Requests & Responses

#### Example 1: Simple Function Replacement (Community)

**Request:**
```json
{
  "file_path": "/src/math_utils.py",
  "target_type": "function",
  "target_name": "add_numbers",
  "new_code": "def add_numbers(a, b):\n    \"\"\"Add two numbers efficiently.\"\"\"\n    return a + b\n"
}
```

**Response:**
```json
{
  "tier": "community",
  "tool_id": "update_symbol",
  "duration_ms": 56,
  "data": {
    "success": true,
    "file_path": "/src/math_utils.py",
    "target_name": "add_numbers",
    "target_type": "function",
    "files_updated": 1,
    "backup_created": true,
    "backup_path": "/src/math_utils.py.bak",
    "validation_results": {
      "syntax_valid": true,
      "warnings": []
    }
  }
}
```

#### Example 2: Multi-File Update with Rollback (Pro)

**Request:**
```json
{
  "file_path": "/src/database/connection.py",
  "target_type": "function",
  "target_name": "connect",
  "new_code": "def connect(url, timeout=30, retries=3):\n    \"\"\"Establish database connection with retry logic.\"\"\"\n    for attempt in range(retries):\n        try:\n            return Database(url, timeout)\n        except ConnectionError:\n            if attempt == retries - 1:\n                raise\n    return None\n",
  "operation": "replace"
}
```

**Response:**
```json
{
  "tier": "pro",
  "tool_id": "update_symbol",
  "duration_ms": 345,
  "data": {
    "success": true,
    "file_path": "/src/database/connection.py",
    "target_name": "connect",
    "target_type": "function",
    "files_updated": 3,
    "backup_created": true,
    "backup_path": "/src/database/connection.py.bak",
    "validation_results": {
      "syntax_valid": true,
      "semantic_valid": true,
      "warnings": [
        "Signature changed: new parameter 'retries' added",
        "Return type changed: now returns Database|None"
      ]
    },
    "multi_file_updates": [
      {
        "file": "/src/api/routes.py",
        "imports_adjusted": true,
        "references_updated": 2
      },
      {
        "file": "/src/tests/test_db.py",
        "imports_adjusted": false,
        "references_updated": 4
      }
    ]
  }
}
```

### Performance Considerations

- **Community**: 50-150ms (syntax validation only)
- **Pro**: 200-1000ms (includes semantic validation and multi-file ops)
- **Enterprise**: 500-3000ms (custom rules and compliance)

### Upgrade Paths

**Community → Pro:**
- Enables multi-file updates
- Adds semantic validation
- Unlocks atomic operations and rollback
- Increases max updates per call from 10 to unlimited
- Pre/post-update hooks

**Pro → Enterprise:**
- Custom validation rules
- Advanced hook support
- Compliance checks
- Organization-wide scope

---

## Response Envelope Specification

All tools in this category return responses wrapped in a standard envelope:

```json
{
  "tier": "community|pro|enterprise|null",
  "tool_version": "1.x.x",
  "tool_id": "extract_code|rename_symbol|update_symbol",
  "request_id": "uuid-v4",
  "capabilities": ["envelope-v1"],
  "duration_ms": 1234,
  "error": null,
  "warnings": [],
  "upgrade_hints": [],
  "data": { /* tool-specific */ }
}
```

See `README.md` for complete envelope specification.

## Related Tools

- **`get_symbol_references`** (context-tools.md) - Find all references to a symbol
- **`analyze_code`** (analysis-tools.md) - Analyze code structure and complexity
- **`get_call_graph`** (graph-tools.md) - Visualize function call relationships
