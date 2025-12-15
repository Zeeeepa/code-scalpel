# Code Scalpel v2.0.0 Release Notes - "Polyglot"

**Release Date:** December 15, 2025  
**Version:** 2.0.0  
**Codename:** Polyglot  
**Maintainer:** 3D Tech Solutions LLC

---

## Executive Summary

Code Scalpel v2.0.0 "Polyglot" is a **major release** that extends all MCP tools to support **TypeScript, JavaScript, and Java** with the same surgical precision as Python. AI agents can now work on full-stack projects - Python backends, TypeScript frontends, Java microservices - with consistent, language-aware analysis.

### Key Highlights

- **Multi-Language Extraction**: `extract_code` works identically across Python, TypeScript, JavaScript, and Java
- **Polyglot Security Scanning**: 100+ new sink patterns for DOM XSS, prototype pollution, Node.js injection, Java vulnerabilities
- **Unified IR Architecture**: Language-specific normalizers convert AST to common Intermediate Representation
- **JSX/TSX Support**: Full React component extraction and analysis
- **ES6+ Module Support**: Import/export, switch, ternary, try/catch handlers

---

## What's New

### 1. Multi-Language Code Extraction

The `extract_code` MCP tool now supports surgical extraction across four languages:

```python
# Python (existing)
extract_code(file_path="utils.py", target_type="function", target_name="calculate_tax")

# JavaScript (NEW)
extract_code(file_path="utils.js", target_type="function", target_name="fetchUser")

# TypeScript (NEW)
extract_code(file_path="services.ts", target_type="class", target_name="UserService")

# Java (NEW)
extract_code(file_path="UserController.java", target_type="method", target_name="getUser")
```

**Language Auto-Detection**: Automatically detects language from file extension or content patterns.

### 2. JavaScript/TypeScript Security Patterns (100+ New Sinks)

#### DOM XSS Detection (CWE-79)
```javascript
// DETECTED: DOM XSS vulnerabilities
element.innerHTML = userInput;        // innerHTML sink
document.write(userControlled);       // document.write sink
$('.content').html(data);            // jQuery.html sink
dangerouslySetInnerHTML={{__html: x}} // React danger prop
```

#### Eval Injection Detection (CWE-94)
```javascript
// DETECTED: Code injection vulnerabilities
eval(userInput);                      // eval sink
new Function(userCode);               // Function constructor
setTimeout(userString, 1000);         // setTimeout with string
vm.runInThisContext(code);           // Node.js vm module
```

#### Prototype Pollution Detection (CWE-1321)
```javascript
// DETECTED: Prototype pollution vulnerabilities
Object.assign(target, userInput);     // Object.assign
_.merge(target, untrusted);           // Lodash merge
$.extend(true, {}, userObject);       // jQuery extend
```

#### Node.js Command Injection (CWE-78)
```javascript
// DETECTED: Command injection vulnerabilities
child_process.exec(userCommand);      // exec with user input
spawn(cmd, { shell: true });         // spawn with shell
execSync(userControlled);            // synchronous execution
```

#### Node.js SQL Injection (CWE-89)
```javascript
// DETECTED: SQL injection vulnerabilities
connection.query(`SELECT * FROM users WHERE id=${userId}`);
knex.raw(userQuery);                 // Knex raw queries
sequelize.query(userInput);          // Sequelize raw
prisma.$queryRaw(untrusted);         // Prisma raw
```

### 3. Java Security Patterns (50+ New Sinks)

#### JDBC SQL Injection
```java
// DETECTED: SQL injection
Statement.executeQuery("SELECT * FROM users WHERE id=" + userId);
jdbcTemplate.query(userQuery);
entityManager.createNativeQuery(userInput);
```

#### Java Command Injection
```java
// DETECTED: Command injection
Runtime.getRuntime().exec(userCommand);
new ProcessBuilder(userArgs).start();
```

#### Java XXE Detection
```java
// DETECTED: XXE vulnerabilities
DocumentBuilderFactory.newInstance().newDocumentBuilder().parse(input);
SAXParserFactory.newInstance().newSAXParser().parse(xmlInput, handler);
```

#### Java Deserialization
```java
// DETECTED: Insecure deserialization
new ObjectInputStream(inputStream).readObject();
XStream.fromXML(userInput);
```

### 4. JavaScript Normalizer Enhancements

New handlers for complete JavaScript/TypeScript support:

| Handler | Description | Example |
|---------|-------------|---------|
| `import_statement` | ES6 module imports | `import { x } from 'module'` |
| `export_statement` | ES6 module exports | `export default function` |
| `switch_statement` | Switch/case blocks | `switch(x) { case 1: ... }` |
| `try_statement` | Try/catch/finally | `try { } catch(e) { }` |
| `throw_statement` | Exception throwing | `throw new Error()` |
| `ternary_expression` | Ternary operator | `x ? a : b` |

### 5. TSX/JSX Support

Full React component extraction:

```typescript
// JSX elements become IRCall nodes for analysis
<UserProfile userId={props.id} />   // Analyzed as JSX:UserProfile call
<>Fragment content</>               // Analyzed as JSX:Fragment
{expression}                        // Embedded JS properly handled
```

### 6. Java Normalizer Enhancements

| Handler | Description | Example |
|---------|-------------|---------|
| `import_declaration` | Java imports | `import java.util.List` |
| `package_declaration` | Package statements | `package com.example` |
| `try_statement` | Try/catch/finally | `try { } catch(E e) { }` |
| `throw_statement` | Exception throwing | `throw new Exception()` |
| `switch_statement` | Switch expressions | `switch(x) { case 1: }` |
| `for_statement` | Traditional for loops | `for(int i=0; i<n; i++)` |
| `enhanced_for_statement` | For-each loops | `for(String s : list)` |
| `object_creation_expression` | New instances | `new ArrayList<>()` |

---

## Metrics

### Test Suite
| Metric | Value |
|--------|-------|
| Total Tests | 2,581 |
| Pass Rate | 100% (2,580 passed, 1 xfailed expected) |
| Security Tests | 156 |
| IR/Normalizer Tests | 97 |
| Polyglot Tests | 63 |

### Security Coverage
| Category | Python | JavaScript | TypeScript | Java |
|----------|--------|------------|------------|------|
| SQL Injection | 15 sinks | 12 sinks | 12 sinks | 10 sinks |
| XSS/DOM XSS | 8 sinks | 15 sinks | 15 sinks | 4 sinks |
| Command Injection | 5 sinks | 12 sinks | 12 sinks | 4 sinks |
| Path Traversal | 4 sinks | 12 sinks | 12 sinks | 8 sinks |
| Code Injection | 3 sinks | 10 sinks | 10 sinks | 4 sinks |
| Prototype Pollution | N/A | 12 sinks | 12 sinks | N/A |
| SSRF | 10 sinks | 14 sinks | 14 sinks | 8 sinks |
| XXE | 14 sinks | N/A | N/A | 6 sinks |
| Deserialization | 6 sinks | 6 sinks | 6 sinks | 6 sinks |

### New IR Nodes (v2.0.0)
| Node | Description |
|------|-------------|
| `IRImport` | ES6/Python/Java import statements |
| `IRExport` | ES6 export statements |
| `IRSwitch` | Switch/case statements |
| `IRTry` | Try/catch/finally blocks |
| `IRRaise` | Throw/raise statements |
| `IRTernary` | Ternary conditional expressions |

### New SecuritySink Types
| Sink | CWE | Description |
|------|-----|-------------|
| `DOM_XSS` | CWE-79 | DOM-based Cross-Site Scripting |
| `PROTOTYPE_POLLUTION` | CWE-1321 | JavaScript Prototype Pollution |

---

## Architecture

### Unified IR (Intermediate Representation)

All languages normalize to the same IR, enabling:
- **Cross-language analysis:** Same security rules work across languages
- **Consistent MCP interface:** AI agents use identical tool signatures
- **Code comparison:** Compare implementations across languages

```
Source Code (Python/TS/JS/Java)
           |
   Language-Specific Parser
   (ast/tree-sitter)
           |
   Normalizer (per language)
           |
   Unified IR (IRModule, IRFunctionDef, etc.)
           |
   Analysis Tools (PDG, Security, Symbolic)
```

---

## Migration Guide

### For Python Users
No changes required. All existing Python functionality remains unchanged.

### For Multi-Language Projects
1. Install tree-sitter language packages:
```bash
pip install tree-sitter-javascript tree-sitter-typescript tree-sitter-java
```

2. Use `extract_code` with auto-detection or explicit language:
```python
# Auto-detect from file extension
result = extract_code(file_path="api.js", target_type="function", target_name="handler")

# Explicit language override
result = extract_code(code=js_code, target_type="function", target_name="handler", language="javascript")
```

---

## Breaking Changes

None. v2.0.0 is fully backward compatible with v1.5.x.

---

## Known Limitations

### JavaScript/TypeScript
- `this` keyword not yet tracked in data flow analysis
- `await_expression` normalization incomplete (parsed but simplified)
- Dynamic imports (`import()`) detected but not fully resolved

### Java
- Spring annotations (@RequestParam, etc.) detected as taint sources but not fully traced
- Lambda expressions have limited support
- Generic types not fully preserved in IR

### Cross-Language
- Cross-file taint tracking only works within same language
- No Python - JavaScript interop analysis

---

## Acceptance Criteria Verification

### P0 Requirements (All Complete)

- [x] `extract_code`: Works for TypeScript functions/classes
- [x] `extract_code`: Works for JavaScript functions/classes
- [x] `extract_code`: Works for Java methods/classes
- [x] `extract_code`: Auto-detects language from file extension

- [x] TypeScript AST: Parses .ts files correctly
- [x] TypeScript AST: Parses .tsx files correctly
- [x] TypeScript AST: Handles type annotations
- [x] TypeScript AST: Handles interfaces and types

- [x] JavaScript AST: Parses .js files correctly
- [x] JavaScript AST: Parses .jsx files correctly
- [x] JavaScript AST: Handles ES6+ syntax
- [x] JavaScript AST: Handles CommonJS and ESM imports

- [x] `security_scan`: Detects DOM XSS (innerHTML, document.write)
- [x] `security_scan`: Detects eval injection
- [x] `security_scan`: Detects prototype pollution
- [x] `security_scan`: Detects Node.js command injection
- [x] `security_scan`: Detects Node.js SQL injection

- [x] Java: Parses .java files correctly
- [x] Java: Detects SQL injection in JPA queries
- [x] Java: Detects command injection

### Adversarial Hardening (All Complete)

- [x] Deeply nested extraction (10+ levels)
- [x] Java record class (Java 16+)
- [x] Java pattern matching switch (Java 21+)
- [x] TSX generic component with JSX auto-detection
- [x] Cross-file import chain taint (3+ files)
- [x] Cross-file callback taint tracking
- [x] 88 adversarial tests (100% pass rate)

### Quality Gates (All Met)

- [x] All MCP tools work identically across languages
- [x] All 2,669 tests passing (100% pass rate)
- [x] Code coverage maintained at 95%+
- [x] No regressions in Python functionality

---

## Contributors

- Development: 3D Tech Solutions LLC
- Architecture: Unified IR with Language-Specific Normalizers
- Testing: Comprehensive polyglot test suite

---

## What's Next (v2.1.0 Preview)

**Theme:** AI Verification - Behavior-preserving refactoring checks

- `verify_behavior` MCP tool for AI-assisted refactoring verification
- `suggest_fix` MCP tool for automated vulnerability remediation
- `apply_verified_fix` for safe, verified security fixes
- Batch verification for multi-file changes

---

*Code Scalpel - Surgical Precision for AI Agents*
