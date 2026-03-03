# Demo: "PDGs and Call Graphs: How Code Scalpel Sees Relationships"

**Category**: Program Dependency Graphs (PDGs) and Call Graphs
**Pillar**: Accurate AI
**Tier**: Pro
**Duration**: 12 minutes
**Fixture**: Ninja Warrior Stage 1 (full-stack snap) or Code Scalpel's own call graph

## What Is This Demo About?

A **Program Dependency Graph (PDG)** extends the AST by adding edges that represent how data and control flow between statements and functions. A **Call Graph** is a subset that shows which functions call which other functions. Together, these graphs let Code Scalpel:

- Trace data from an untrusted source through 10 function calls to a dangerous sink
- Find all callers of a function before refactoring it
- Detect circular imports that cause runtime failures
- Understand the blast radius of a change

This demo shows `get_call_graph`, `get_cross_file_dependencies`, `get_graph_neighborhood`, and `get_project_map` in action.

## Tools Used

- `get_call_graph` (Pro) — Function call relationships, entry points, circular imports
- `get_cross_file_dependencies` (Pro) — Cross-module dependency chains with confidence scoring
- `get_graph_neighborhood` (Pro) — k-hop subgraph around any node
- `get_project_map` (Pro) — High-level package hierarchy and complexity hotspots

## Scenario

Your team is about to refactor `UserService.authenticate()`. Before touching it, you need to know: what calls it? What does it call? Are there circular dependencies? Which files will break if you change the signature? Without a call graph, answering these questions means manually tracing through dozens of files.

## Recording Script

### Step 1: The Refactor Risk (0:00-1:30)

- Show `UserService.authenticate()`:
  ```python
  class UserService:
      def authenticate(self, username: str, password: str) -> Optional[User]:
          user = self.db.get_by_username(username)
          if not user or not check_password(password, user.hash):
              return None
          self._log_auth_event(user.id, success=True)
          return user
  ```
- Question: "Is it safe to refactor this function? What depends on it?"
- Traditional answer: "grep for 'authenticate' and hope you find everything"
- On-screen: "grep misses dynamic dispatch, aliases, indirect calls"

### Step 2: Build the Call Graph (1:30-4:00)

- Prompt: "Build a call graph for the entire auth module"
- Tool call: `get_call_graph(project_root="src/", entry_point="auth.py")`
- Output (abbreviated):
  ```
  Entry points: [authenticate, logout, refresh_token]

  Call graph:
  authenticate
  ├── db.get_by_username        [auth.db → database/users.py]
  ├── check_password            [auth.utils → crypto/password.py]
  └── _log_auth_event           [auth.service → logging/audit.py]

  Callers of authenticate:
  ├── api/routes/auth.py:47     login_endpoint()
  ├── api/routes/auth.py:89     sso_callback()
  ├── middleware/jwt.py:31      verify_token()
  └── tests/test_auth.py:12    test_login()

  Circular imports: NONE detected ✓
  ```
- On-screen: "4 callers found. Zero circular imports. Safe to refactor?"

### Step 3: k-Hop Neighborhood Analysis (4:00-6:30)

- Prompt: "Show me everything 2 hops out from authenticate"
- Tool call: `get_graph_neighborhood(center_node_id="UserService.authenticate", k=2, direction="both")`
- Output: Full subgraph showing:
  - Direct callers (hop 1): login_endpoint, sso_callback, verify_token
  - Callers of callers (hop 2): request_handler, oauth_flow, middleware_chain
  - Callees (hop 1): db.get_by_username, check_password, _log_auth_event
  - Callees of callees (hop 2): SQL execute, bcrypt.verify, audit_logger.write
- Visual Mermaid diagram:
  ```
  request_handler → login_endpoint → authenticate → check_password → bcrypt.verify
                                   ↓                → db.get_by_username → SQL execute
                                   → _log_auth_event → audit_logger.write
  ```
- On-screen: "The blast radius: 9 modules affected. Now we know what to test."

### Step 4: Cross-File Dependency Chain (6:30-9:00)

- Prompt: "Trace the complete dependency chain for UserService"
- Tool call: `get_cross_file_dependencies(target_file="src/auth/service.py", target_symbol="UserService")`
- Output includes:
  - Confidence-scored dependency chain (each hop gets a decay factor)
  - Mermaid diagram of the dependency flow
  - Files that would break if `UserService` is removed
- Highlight: `confidence_decay_factor` — deeper hops get lower confidence scores, preventing false positives

### Step 5: Circular Import Detection (9:00-10:30)

- Show a contrived circular import scenario:
  ```
  auth/service.py imports from auth/utils.py
  auth/utils.py imports from auth/service.py  ← circular!
  ```
- Run: `get_call_graph(include_circular_import_check="true")`
- Output:
  ```
  ⚠️  CIRCULAR IMPORT DETECTED:
  auth/service.py → auth/utils.py → auth/service.py

  This will cause ImportError at runtime in Python modules
  loaded before the import cycle resolves.

  Fix: Extract shared types to auth/types.py
  ```
- On-screen: "Caught before deployment. Python circular imports fail silently until they don't."

### Step 6: Project Architecture Map (10:30-12:00)

- Prompt: "Give me the high-level architectural boundaries of this project"
- Tool call: `get_project_map(project_root="src/", detect_service_boundaries=True)`
- Output: Package hierarchy, isolation scores, identified service boundaries
- On-screen: "One command. Full architectural picture. No architecture.md needed."

## Expected Outputs

```
# get_call_graph output
{
  "entry_points": ["authenticate"],
  "edges": [
    {"caller": "UserService.authenticate", "callee": "db.get_by_username", "file": "database/users.py", "line": 23},
    ...
  ],
  "callers": {
    "UserService.authenticate": ["login_endpoint", "sso_callback", "verify_token"]
  },
  "circular_imports": []
}
```

## Key Talking Points

- "A call graph answers 'what breaks if I change this?' in 2 seconds"
- "PDGs track data flow — not just which functions call each other, but what data they share"
- "k-hop analysis gives you the exact blast radius of any change"
- "Circular imports are the #1 Python runtime mystery — catch them before they bite"
- "Pro tier: up to 1,000 files. Enterprise: unlimited."

## Technical Depth: PDG vs Call Graph vs AST

### Three Levels of Code Representation

```
Source code (text)
    ↓ parse
AST (structure)
    ↓ + control flow analysis
CFG (Control Flow Graph) — execution order
    ↓ + data flow analysis
PDG (Program Dependency Graph) — data + control dependencies
    ↓ extract function call edges
Call Graph — who calls whom
```

### PDG Edge Types

| Edge Type | Meaning | Example |
|-----------|---------|---------|
| Control Dependence | A executes only if B | `if user: authenticate()` |
| Data Dependence | A uses data from B | `hash = hash_password(pw); verify(hash)` |
| Call Edge | A invokes B | `service.authenticate(user)` |
| Return Edge | B returns to A | `authenticate → login_endpoint` |

### Why Call Graphs Beat Text Search

| Approach | Finds Dynamic Calls | Cross-File | Accurate | Speed |
|----------|---------------------|------------|----------|-------|
| `grep "authenticate"` | ❌ | ✓ (manual) | 70% | Fast |
| IDE "Find References" | Partial | ✓ | 85% | Medium |
| Code Scalpel Call Graph | ✓ | ✓ | 99% | 3s |

### Confidence Scoring in Cross-File Dependencies

When tracing through 5+ files, certainty decreases. Code Scalpel uses a `confidence_decay_factor` (default: 0.9) to indicate chain reliability:

```
hop 0 (origin):  100% confidence
hop 1:            90% confidence
hop 2:            81% confidence
hop 3:            73% confidence
hop 4:            66% confidence
```

Paths below 50% confidence are flagged as "speculative".
