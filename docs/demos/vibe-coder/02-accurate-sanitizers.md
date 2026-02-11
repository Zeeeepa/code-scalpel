# Demo: "Stop Hallucinating: Detect Fake Sanitizers"

**Persona**: Vibe Coder
**Pillar**: Accurate AI
**Tier**: Community (FREE)
**Duration**: 7 minutes
**Fixture**: From `test_ninja_anti_hallucination.py` - "sanitize_input that doesn't sanitize"

## Scenario

Function named `sanitize_input` returns input unchanged. Standard LLM sees the name and assumes it's safe. Code Scalpel analyzes AST and data flow, correctly identifies XSS vulnerability.

## Tools Used

- `security_scan`
- `analyze_code`

## Recording Script

### Step 1: Setup: The Trap (0:00-1:00)

- Show code:
  ```python
  def sanitize_input(user_data):
      """Sanitizes user input for safe use."""
      return user_data  # Does nothing!

  def handler(user_input):
      safe = sanitize_input(user_input)
      return f"<div>{safe}</div>"
  ```
- On-screen text: "Can you spot the bug?"
- Voiceover: "This is a real pattern from production codebases"

### Step 2: Standard LLM Hallucination (1:00-2:30)

- Ask standard Claude (without tools): "Is this code safe?"
- Show response: "Yes, the input is sanitized by the `sanitize_input` function before rendering"
- Highlight: LLM trusted the function name ❌
- On-screen: "Hallucination: Name ≠ Behavior"

### Step 3: Code Scalpel Analysis (2:30-4:30)

- Prompt: "Check this code for XSS vulnerabilities"
- Show Code Scalpel calling `security_scan`
- Tool performs taint analysis:
  - Traces `user_input` → `sanitize_input` → `safe` → HTML sink
  - Detects that `sanitize_input` is identity function (no transformation)
- Result: "XSS vulnerability detected at line 7"

### Step 4: Visual Explanation (4:30-5:30)

- Show data flow diagram (Mermaid)
- Highlight: user input flows unchanged to HTML output
- On-screen: "Graph-based analysis sees through lies"

### Step 5: Real-World Impact (5:30-6:30)

- Show Stage 10 adversarial fixture with 10+ similar patterns:
  - `dangerous_do_not_use` (actually safe - parameterized query)
  - `clean_input` (returns unchanged)
  - `validate_email` (no validation)
- Run batch scan: Code Scalpel correctly classifies all
- Standard LLM gets 6/10 wrong

### Step 6: Key Takeaway (6:30-7:00)

- "Code Scalpel analyzes behavior, not names"
- "AST + PDG = Ground truth"
- "Free in Community tier"

## Expected Outputs

- Security scan JSON with taint path
- Confidence score: "HIGH (95%)"
- Suggested fix: Use `html.escape()`

## Before/After Comparison

| Approach | Verdict | Accuracy | Method |
|----------|---------|----------|--------|
| Standard LLM | "Safe ✓" | **Wrong** | Name-based trust |
| Code Scalpel | "XSS Detected ⚠" | **Correct** | Graph-based analysis |

## Key Talking Points

- "LLMs hallucinate - they trust function names"
- "Code Scalpel analyzes actual behavior through AST and data flow"
- "Graph facts, not language model guesses"
- "Free in Community tier - accurate security scanning for everyone"
