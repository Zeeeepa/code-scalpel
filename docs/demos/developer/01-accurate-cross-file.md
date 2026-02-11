# Demo: "Graph Truth: Cross-File Bug Detective"

**Persona**: Developer
**Pillar**: Accurate AI
**Tier**: Pro ($49/month)
**Duration**: 12 minutes
**Fixture**: Type evaporation scenario from Ninja Warrior Stage 9

## Scenario

FastAPI backend changes user ID from string to int. Frontend still sends string. Standard agent misses this because files are in different directories. Code Scalpel uses graph analysis to detect type mismatch.

## Tools Used

- `type_evaporation_scan` (Pro tier)
- `get_cross_file_dependencies`
- `analyze_code`

## Recording Script

### Step 1: The Setup: Microservice Architecture (0:00-1:30)

- Show repo structure:
  ```
  backend/
    api.py          # FastAPI endpoint
    models.py       # User model
  frontend/
    api_client.ts   # TypeScript API client
  ```
- Explain: Backend and frontend separated by 100+ files

### Step 2: The Breaking Change (1:30-3:00)

- Backend: Change User model
  ```python
  # Before
  class User:
      id: str

  # After
  class User:
      id: int  # Performance optimization
  ```
- Tests pass (backend only tests) ✓
- Deploy to staging...

### Step 3: Production Breaks (3:00-4:00)

- Frontend sends: `{user_id: "12345"}`
- Backend expects: `{user_id: 12345}`
- Error: 500 Internal Server Error ❌
- On-screen: "Type evaporation at network boundary"

### Step 4: Standard Agent Analysis (4:00-5:30)

- Ask Claude Code (without graph tools): "Find type inconsistencies"
- Response: "I don't see any issues in api.py"
- Problem: Context window only saw backend files
- On-screen: "Context blindness = missed bugs"

### Step 5: Code Scalpel Graph Analysis (5:30-8:30)

- Run: `type_evaporation_scan`
- Tool builds cross-file dependency graph:
  1. Parse backend API schema
  2. Find frontend API client calls
  3. Compare TypeScript types to Python types
- **Detection**:
  - Backend: `User.id: int`
  - Frontend: `userId: string`
  - Risk: "HIGH - type mismatch at network boundary"

### Step 6: Visual Graph (8:30-9:30)

- Show Mermaid diagram of data flow:
  ```
  frontend/api_client.ts [string]
      ↓
  HTTP POST
      ↓
  backend/api.py [expects int]
  ```
- Highlight: "Type evaporated at boundary"

### Step 7: Fix Suggestion (9:30-10:30)

- Code Scalpel suggests fixes:
  - Option 1: Update frontend to send `number`
  - Option 2: Add backend coercion
  - Option 3: Generate Zod schema for runtime validation
- Show: Auto-generated Pydantic/Zod models

### Step 8: Enterprise Upgrade Teaser (10:30-11:30)

- Pro: Frontend-backend type checking
- Enterprise: Automatic schema generation, API contract validation
- On-screen: "Never ship type mismatches again"

### Step 9: Wrap-Up (11:30-12:00)

- "Graph analysis sees what context windows miss"
- "Pro tier: 500-1000 files"
- "Enterprise: Unlimited"

## Expected Outputs

- Type evaporation report with confidence scores
- Cross-file dependency diagram
- Fix suggestions with code snippets

## Key Metrics

- Files analyzed: 247
- Type mismatches found: 3
- False positives: 0
- Time: 8 seconds

## Before/After Comparison

| Detection Method | Found Bug | Time | Coverage |
|------------------|-----------|------|----------|
| Manual testing | ❌ After deploy | Days | Single service |
| Standard agent | ❌ Context blind | Minutes | Limited |
| Code Scalpel Pro | ✓ Pre-deploy | 8 seconds | Cross-service |

## Key Talking Points

- "Type evaporation happens at network boundaries"
- "Context windows can't see across 100+ files"
- "Graph analysis builds dependency map - sees the whole picture"
- "Pro tier essential for microservices and full-stack apps"
- "Catch breaking changes before production"
