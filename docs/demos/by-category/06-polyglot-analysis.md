# Demo: "7-Language Polyglot Analysis: One Tool, Every Language"

**Category**: Polyglot / Multi-Language Support
**Pillar**: Accurate AI + Cheaper AI
**Tier**: Community → Pro
**Duration**: 10 minutes
**Fixture**: Mixed-language monorepo (Python backend + TypeScript frontend + C++ game engine + C# Unity)

## What Is This Demo About?

Code Scalpel v2.0 supports **7 languages** with production-quality parsers — not naive text matching, but genuine language-specific AST parsing that understands the unique constructs of each language:

| Language | Extensions | Key Constructs |
|----------|-----------|---------------|
| Python | `.py` | Decorators, comprehensions, async/await, dataclasses |
| JavaScript | `.js`, `.jsx` | Prototypes, closures, React components, arrow functions |
| TypeScript | `.ts`, `.tsx` | Generics, interfaces, type guards, React Server Components |
| Java | `.java` | Generics, annotations, inner classes, checked exceptions |
| **C** *(v2.0)* | `.c`, `.h` | Pointers, structs, unions, enums, macros, bitfields |
| **C++** *(v2.0)* | `.cpp`, `.hpp`, `.cc` | Templates, namespaces, RAII, operator overloading |
| **C#** *(v2.0)* | `.cs` | Records, interfaces, generics, LINQ, async/await, attributes |

This demo shows all 23 MCP tools working uniformly across all 7 languages with a single, consistent API.

## Tools Used

- `analyze_code` — Parse any file into structured metadata
- `extract_code` — Surgically extract any named symbol
- `security_scan` — Taint analysis across languages
- `crawl_project` — Multi-language project analysis
- `generate_unit_tests` — Test generation in any supported language

## Scenario

You're a staff engineer at a gaming company. Your stack: Python ML pipeline, TypeScript web dashboard, C++ game engine, C# Unity scripts. You've been using four separate tools for each language. Code Scalpel consolidates all of them into one consistent MCP interface, with one config and one audit trail.

## Recording Script

### Step 1: The Multi-Language Reality (0:00-1:30)

- Show monorepo structure:
  ```
  game-studio/
  ├── ml-pipeline/     (Python)
  ├── dashboard/       (TypeScript/React)
  ├── game-engine/     (C++)
  ├── unity-scripts/   (C#)
  └── android-sdk/     (Java)
  ```
- On-screen: "5 languages. Historically: 5 tools. Today: 1."

### Step 2: Python Analysis (1:30-2:30)

```python
# ml-pipeline/trainer.py
class ModelTrainer:
    def train(self, dataset: Dataset, epochs: int = 10) -> Model:
        """Train ML model on provided dataset."""
        ...
```

- Tool call: `extract_code(file_path="ml-pipeline/trainer.py", target_type="class", target_name="ModelTrainer")`
- Output:
  ```json
  {
    "name": "ModelTrainer",
    "language": "python",
    "methods": [{"name": "train", "params": ["dataset: Dataset", "epochs: int = 10"], "returns": "Model"}],
    "docstrings": {"train": "Train ML model on provided dataset."}
  }
  ```

### Step 3: TypeScript/React Analysis (2:30-3:30)

```typescript
// dashboard/components/PlayerStats.tsx
export async function PlayerStats({ playerId }: { playerId: string }) {
  const stats = await fetchStats(playerId);
  return <div className="stats">{stats.score}</div>;
}
```

- Tool call: `extract_code(file_path="dashboard/components/PlayerStats.tsx", target_type="function", target_name="PlayerStats", language="tsx")`
- Output:
  ```json
  {
    "name": "PlayerStats",
    "language": "typescript",
    "component_type": "functional",
    "is_server_component": true,
    "props": {"playerId": "string"},
    "jsx_elements": ["div"],
    "async": true
  }
  ```
- Highlight: `is_server_component: true` — detected from `async function` pattern (Next.js convention)
- On-screen: "React Server Components detected automatically — critical for Next.js architecture."

### Step 4: C++ Analysis (3:30-5:00)

```cpp
// game-engine/physics/RigidBody.cpp
template<typename T>
class RigidBody {
public:
    Vector3<T> position;
    float mass;

    void apply_force(const Vector3<T>& force, float dt) {
        acceleration += force / mass;
        position += velocity * dt;
    }
};
```

- Tool call: `analyze_code(file_path="game-engine/physics/RigidBody.cpp")`
- Output:
  ```json
  {
    "language": "cpp",
    "classes": [{
      "name": "RigidBody",
      "template_params": ["T"],
      "members": [
        {"name": "position", "type": "Vector3<T>", "access": "public"},
        {"name": "mass", "type": "float", "access": "public"}
      ],
      "methods": [{
        "name": "apply_force",
        "params": ["force: const Vector3<T>&", "dt: float"],
        "returns": "void"
      }]
    }]
  }
  ```
- Highlight: Template parameters extracted, `const` ref semantics preserved
- On-screen: "Templates, namespaces, RAII — C++ parsed properly, not just as text."

### Step 5: C# Analysis (5:00-6:30)

```csharp
// unity-scripts/GameManager.cs
public record PlayerState(
    string PlayerId,
    int Score,
    Vector3 Position
);

public class GameManager : MonoBehaviour
{
    private async Task<bool> SaveProgress(PlayerState state)
    {
        await CloudSave.Instance.SaveAsync(state.PlayerId, state);
        return true;
    }
}
```

- Tool call: `analyze_code(file_path="unity-scripts/GameManager.cs")`
- Output:
  ```json
  {
    "language": "csharp",
    "records": [{
      "name": "PlayerState",
      "properties": ["PlayerId: string", "Score: int", "Position: Vector3"]
    }],
    "classes": [{
      "name": "GameManager",
      "base_class": "MonoBehaviour",
      "methods": [{
        "name": "SaveProgress",
        "async": true,
        "returns": "Task<bool>",
        "params": ["state: PlayerState"]
      }]
    }]
  }
  ```
- Highlight: `record` type (C# 9+), `async Task`, base class `MonoBehaviour` all correctly parsed

### Step 6: C Analysis (6:30-7:30)

```c
// android-sdk/native/audio.h
typedef struct {
    uint32_t sample_rate;
    uint8_t channels;
    uint16_t bit_depth;
    int32_t *buffer;
} AudioConfig;

int audio_init(AudioConfig *config, size_t buffer_size);
```

- Tool call: `analyze_code(file_path="android-sdk/native/audio.h")`
- Output:
  ```json
  {
    "language": "c",
    "structs": [{
      "name": "AudioConfig",
      "fields": [
        {"name": "sample_rate", "type": "uint32_t"},
        {"name": "channels", "type": "uint8_t"},
        {"name": "bit_depth", "type": "uint16_t"},
        {"name": "buffer", "type": "int32_t*", "is_pointer": true}
      ]
    }],
    "functions": [{
      "name": "audio_init",
      "params": ["config: AudioConfig*", "buffer_size: size_t"],
      "returns": "int"
    }]
  }
  ```
- Highlight: Pointer types correctly identified, `typedef struct` resolved

### Step 7: Cross-Language Security Scan (7:30-9:00)

- Run security scan across the entire monorepo:
  - `crawl_project(root_path="game-studio/", pattern="*.{py,ts,cpp,cs,c,java}")`
  - Reports: 5 files scanned, 2 security warnings (a Python SQL injection, a C++ buffer handling warning)
- On-screen: "One scan. Five languages. Zero configuration per language."

### Step 8: The Consolidation Win (9:00-10:00)

Show the old tool stack vs Code Scalpel:

| Language | Old Tool | New Tool |
|----------|----------|----------|
| Python | Bandit + Semgrep | Code Scalpel |
| TypeScript | ESLint security + Semgrep | Code Scalpel |
| C++ | Cppcheck + Coverity | Code Scalpel |
| C# | Roslyn analyzer + NDepend | Code Scalpel |
| Java | SpotBugs + PMD | Code Scalpel |

- On-screen: "5 tools → 1. 5 configs → 1. 5 CI steps → 1. 5 learning curves → 0."

## Expected Outputs

All tools return the same JSON schema regardless of language, with a `"language"` field identifying the source. Language-specific fields (like `template_params` for C++, `component_type` for TSX, `record` for C#) appear as optional extensions.

## Key Talking Points

- "v2.0 adds C, C++, and C# — 7 languages, all 23 MCP tools"
- "Same API, same JSON schema, same audit trail across all languages"
- "C++ templates and C# generics are fully parsed — not just identified as 'unknown'"
- "React Server Components detected in TSX — critical for Next.js teams"
- "Replace your per-language static analysis tools with one MCP server"

## Technical Depth: Language-Specific Parser Implementations

### Parser Technology per Language

| Language | Parser | AST Standard |
|----------|--------|-------------|
| Python | `tree-sitter-python` | Python CST |
| JavaScript | `tree-sitter-javascript` | ESTree |
| TypeScript | `tree-sitter-typescript` | TSTree |
| Java | `tree-sitter-java` | JavaTree |
| C | `tree-sitter-c` | C ISO standard |
| C++ | `tree-sitter-cpp` | C++17 standard |
| C# | `tree-sitter-c-sharp` | ECMA-334 |

### Polyglot Normalizer

Code Scalpel uses a **normalizer layer** (`src/code_scalpel/ir/normalizers/`) that converts each language's AST into a common **Intermediate Representation (IR)**:

```
Python AST  ─┐
Java AST    ─┤   Language-specific    Common IR    Analysis
C++ AST     ─┤   normalizers       →  (JSON)    →  Tools
C# AST      ─┤
TS AST      ─┘
```

This means tools like `security_scan` and `analyze_code` implement their logic **once** against the IR, not once per language.

### New in v2.0: C/C++/C# Constructs

**C**:
- Bitfields (`uint8_t flags : 3`)
- Preprocessor macros (expansion-aware)
- Function pointer typedefs
- `static`, `extern`, `register` qualifiers

**C++**:
- Template parameter packs (`typename... Args`)
- Operator overloading detection
- RAII patterns (constructor/destructor pairing)
- `constexpr`, `noexcept`, `[[nodiscard]]` attributes
- Namespace hierarchy

**C#**:
- Record types (C# 9+) with positional parameters
- Primary constructors (C# 12)
- `async`/`await` with `Task<T>` return types
- LINQ expression analysis
- Attribute metadata (`[Serializable]`, `[ApiController]`)
- Interface default methods (C# 8+)
