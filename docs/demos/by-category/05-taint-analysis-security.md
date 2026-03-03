# Demo: "Taint Analysis: Tracking Untrusted Data to Dangerous Sinks"

**Category**: Security Scanning and Taint Analysis
**Pillar**: Accurate AI + Safer AI
**Tier**: Community → Enterprise
**Duration**: 12 minutes
**Fixture**: Ninja Warrior anti-hallucination fixture + OWASP Top 10 examples

## What Is This Demo About?

**Taint analysis** is the technique behind virtually all professional security scanners. The concept:

1. **Sources**: Where untrusted data enters (user input, HTTP requests, file reads, env vars)
2. **Sinks**: Where data must never reach untouched (SQL queries, shell commands, HTML output, file paths)
3. **Taint propagation**: Tracking data through assignments, function calls, returns, and data structures
4. **Sanitizers**: Functions that clean or validate data (making it "untainted")

Code Scalpel implements taint analysis via three tools: `security_scan` (single-file), `unified_sink_detect` (pattern-based), and `cross_file_security_scan` (multi-file, tracking taint through modules).

## Tools Used

- `security_scan` (Community) — Taint analysis in a single file
- `unified_sink_detect` (Community) — Pattern-based dangerous sink detection
- `cross_file_security_scan` (Pro/Enterprise) — Taint tracking across module boundaries

## Scenario

You're reviewing a FastAPI web application for security vulnerabilities. A junior developer added a search endpoint last week. It looks clean at first glance — the code even has a sanitizer call. But is the sanitizer actually effective? Does the user input reach the SQL query? Taint analysis answers these questions formally.

## Recording Script

### Step 1: The Deceptively Clean Code (0:00-2:00)

- Show the search endpoint:
  ```python
  from fastapi import FastAPI
  import database

  app = FastAPI()

  def sanitize_input(query: str) -> str:
      """Remove special characters."""
      return query.replace("'", "").replace(";", "")

  @app.get("/search")
  def search_users(q: str):
      clean = sanitize_input(q)
      results = database.execute(f"SELECT * FROM users WHERE name LIKE '%{clean}%'")
      return results
  ```
- Ask: "Is this safe?"
- First glance: sanitize_input removes `'` and `;` — looks protected
- On-screen: "But is this sanitizer actually effective?"

### Step 2: What Taint Analysis Sees (2:00-4:00)

- Explain the mental model:
  ```
  SOURCE: q (HTTP query parameter — untrusted)
     ↓ taint propagates
  sanitize_input(q) — is this a real sanitizer?
     ↓ still tainted? Let's find out
  clean = sanitize_input(q)
     ↓ assigned to 'clean'
  f"SELECT * FROM users WHERE name LIKE '%{clean}%'"
     ↓ tainted data in SQL string
  database.execute(...)  ← SINK: SQL execution
  ```
- Key question: Does `sanitize_input` fully neutralize the taint?
- Answer: NO — it misses `--` (SQL comment), `UNION`, `OR 1=1`, backticks, hex encoding

### Step 3: Run `security_scan` (4:00-6:30)

- Prompt: "Scan this endpoint for SQL injection vulnerabilities"
- Tool call: `security_scan(file_path="api/search.py")`
- Output:
  ```
  SECURITY SCAN RESULTS — api/search.py
  ======================================

  🔴 HIGH: SQL Injection (CWE-89) — line 15
    Source: q (HTTP parameter at line 10)
    Sink: database.execute() (line 15)
    Sanitizer: sanitize_input() — INEFFECTIVE
    Confidence: 0.91

    Taint path:
    [10] q (source: HTTP GET param)
      → [12] clean = sanitize_input(q)  ← sanitizer detected
      → [13] f"...{clean}..."           ← string interpolation
      → [15] database.execute(sql)      ← SQL sink reached

    Sanitizer weakness: sanitize_input() removes ' and ; but
    does NOT prevent:
      • UNION-based injection: q="admin UNION SELECT ..."
      • Comment injection: q="--"
      • Boolean injection: q=" OR 1=1 --"

    Recommendation: Use parameterized queries:
    database.execute("SELECT ... WHERE name LIKE ?", ('%' + q + '%',))

  0 XSS vulnerabilities
  0 Command injection vulnerabilities
  1 Path traversal warnings (minor)
  ```
- On-screen: "The sanitizer was there. But it was fake. Taint analysis caught it."

### Step 4: Sink Pattern Detection with `unified_sink_detect` (6:30-8:00)

- Prompt: "Find all dangerous sinks in this codebase — SQL, shell, path, HTML"
- Tool call: `unified_sink_detect(code="<code>", language="python")`
- Shows dangerous sink patterns matched:
  ```
  Dangerous Sinks Detected:
  ─────────────────────────
  SQL sinks:    cursor.execute(), db.raw(), engine.execute()
  Shell sinks:  subprocess.run(), os.system(), eval()
  Path sinks:   open(user_input), os.path.join(base, input)
  HTML sinks:   Markup(input), render_template_string(input)
  SSRF sinks:   requests.get(url), urllib.request.urlopen(url)
  ```
- Highlight: detects SSRF (Server-Side Request Forgery) sinks that LLMs often miss
- On-screen: "17 sink patterns across SQL, shell, path, HTML, and network. All checked automatically."

### Step 5: Cross-File Taint Tracking (8:00-10:30)

- Show a more complex scenario: taint flows across modules:
  ```
  # routes/search.py
  def search(q: str):
      result = service.find_users(q)  # passes tainted input

  # services/user_service.py
  def find_users(name: str):
      query = QueryBuilder.build_search(name)  # still tainted

  # db/query_builder.py
  def build_search(term: str):
      return f"SELECT * FROM users WHERE name='{term}'"  # SINK!
  ```
- Run: `cross_file_security_scan(project_root="src/")`
- Output shows:
  ```
  Cross-file taint path detected:
  routes/search.py:8 → services/user_service.py:23 → db/query_builder.py:15

  Taint travels 3 hops across 3 files
  Final sink: SQL string interpolation in query_builder.py
  ```
- On-screen: "Standard scanners miss cross-file taint. Code Scalpel follows the data."

### Step 6: False Positive Prevention (10:30-11:30)

- Show a legitimate sanitizer that works:
  ```python
  def html_escape(user_input: str) -> str:
      return html.escape(user_input)  # Python stdlib — safe!

  def render(q: str) -> str:
      safe = html_escape(q)
      return f"<p>Results for: {safe}</p>"  # Not XSS — properly escaped
  ```
- Run `security_scan` — no XSS reported ✓
- On-screen: "Code Scalpel recognizes effective sanitizers. No false positives for stdlib escaping."

### Step 7: OWASP Top 10 Coverage (11:30-12:00)

Show full coverage matrix:

| OWASP Category | Tool | Status |
|----------------|------|--------|
| A01: Broken Access Control | `code_policy_check` | ✓ |
| A02: Cryptographic Failures | `security_scan` | ✓ |
| A03: Injection (SQL, Shell, LDAP) | `security_scan`, `unified_sink_detect` | ✓ |
| A04: Insecure Design | `symbolic_execute` | Partial |
| A05: Security Misconfiguration | `code_policy_check` | ✓ |
| A06: Vulnerable Components | `scan_dependencies` | ✓ |
| A07: Auth Failures | `symbolic_execute`, `security_scan` | ✓ |
| A08: Data Integrity Failures | `verify_policy_integrity` | ✓ |
| A09: Logging Failures | `code_policy_check` | ✓ |
| A10: SSRF | `unified_sink_detect` | ✓ |

## Expected Outputs

```json
{
  "vulnerabilities": [
    {
      "type": "SQL_INJECTION",
      "severity": "HIGH",
      "cwe": "CWE-89",
      "confidence": 0.91,
      "source": {"file": "search.py", "line": 10, "variable": "q"},
      "sink": {"file": "search.py", "line": 15, "function": "database.execute"},
      "sanitizer": {"name": "sanitize_input", "effective": false, "reason": "incomplete pattern removal"},
      "taint_path": [...]
    }
  ]
}
```

## Key Talking Points

- "Fake sanitizers are the #1 cause of SQL injection in 'sanitized' codebases"
- "Taint analysis follows data flow — not just text patterns"
- "Cross-file tracking catches vulnerabilities that span multiple modules"
- "Community: single-file. Pro: cross-file with 500-1000 file limit. Enterprise: unlimited."
- "9/10 OWASP categories covered — one tool to rule your security posture"

## Technical Depth: Taint Propagation Rules

### Propagation Through Language Constructs

```python
# Direct assignment: taint propagates
a = source()      # a is tainted
b = a             # b is tainted

# Function call: output tainted if input tainted
c = process(a)    # c is tainted (unless process is a sanitizer)

# String interpolation: always propagates
d = f"prefix_{a}"  # d is tainted

# Concatenation: propagates
e = "safe" + a    # e is tainted

# Key/value extraction: propagates
f = {"key": a}["key"]  # f is tainted
```

### Sanitizer Recognition

Code Scalpel recognizes sanitizers in three ways:
1. **Allowlist**: Known safe functions (`html.escape`, `bleach.clean`, parameterized queries)
2. **Signature analysis**: Functions that return a cleaned version of input
3. **Policy-defined**: Custom sanitizers registered via `.code-scalpel/policies/`

### Confidence Scoring

| Factor | Effect |
|--------|--------|
| Direct source → sink | +0.3 |
| Through 1 function call | -0.05 |
| Through 2+ function calls | -0.1 each |
| Sanitizer present (effective) | -0.5 |
| Sanitizer present (ineffective) | -0.1 |
| Minimum confidence threshold | 0.7 (configurable) |
