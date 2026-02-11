# Demo: "15k Tokens → 200: Extract What You Need"

**Persona**: Vibe Coder
**Pillar**: Cheaper AI
**Tier**: Community (FREE)
**Duration**: 5 minutes
**Fixture**: `tests/fixtures/large_file_2000_lines.py`

## Scenario

Standard agent reads entire 2000-line file (15,000 tokens) to find one function. Code Scalpel uses `extract_code` to pull just the target function (200 tokens). **75x cheaper**.

## Tools Used

- `extract_code`
- `get_file_context` (for comparison)

## Recording Script

### Step 1: Setup Shot (0:00-0:30)

- Show large Python file (2000+ lines) in VS Code
- Highlight: "This file has 2000 lines and 15,000 tokens"
- On-screen text: "Standard AI Agent Approach"

### Step 2: Standard Agent Failure (0:30-1:30)

- Show Claude Code reading entire file
- Terminal command: `wc -l large_file.py` → shows 2000 lines
- Show Claude context window filling up
- On-screen text: "15,000 tokens consumed ❌"
- Voiceover: "Traditional agents read the whole file, wasting tokens and money"

### Step 3: Code Scalpel Approach (1:30-2:30)

- Open Claude Desktop with Code Scalpel MCP
- Prompt: "Extract just the `process_payment` function from large_file.py"
- Show Code Scalpel calling `extract_code` tool
- Tool response returns ONLY the function (50 lines)

### Step 4: Token Comparison (2:30-3:30)

- Split screen:
  - Left: Standard agent (15,000 tokens)
  - Right: Code Scalpel (200 tokens)
- On-screen graphic: "75x cheaper" with $ savings
- Show cost calculation:
  - Standard: $0.45 per request
  - Code Scalpel: $0.006 per request

### Step 5: Live Benefit (3:30-4:30)

- Show real task: "Update this function to add logging"
- Code Scalpel completes in one turn (fits in context)
- Standard agent would need multiple turns or fail

### Step 6: Call to Action (4:30-5:00)

- "Try it yourself: pip install codescalpel"
- Show one-liner setup command
- On-screen: "Community Tier = FREE"

## Expected Outputs

- Token count comparison (15k vs 200)
- Cost savings per API call
- Context window utilization graph

## Key Talking Points

- "Context windows are expensive - only grab what you need"
- "This is free in Community tier"
- "Imagine this across 100 requests per day"

## Before/After Comparison

| Approach | Tokens Used | Cost per Request | Risk |
|----------|-------------|------------------|------|
| Standard Agent | 15,000 | $0.45 | High (context overflow) |
| Code Scalpel | 200 | $0.006 | Low (surgical extraction) |
| **Savings** | **75x less** | **75x cheaper** | **Safe** |
