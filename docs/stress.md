This is the ultimate stress test. Since you are using **VS Code with GitHub Copilot**, we can leverage its ability to read your entire workspace (`@workspace`) and specific files.

Here is the **Full-Spectrum Red Team Library**.

**How to use this:**

1. Open the relevant files in VS Code (e.g., your AST parsers, your Dockerfile, your README).
2. Open the **Copilot Chat** window.
3. Copy/Paste the specific **Bullet Prompt** you want to test.
4. Watch Copilot tear it apart.

---

### **Domain 1: The Core Technology (The "Vaporware" Vector)**

#### 1. Determinism vs. Chaos

**Context:** Open your AST parsing logic and error handling modules.

```text
@workspace /persona "The Architect"
Review the AST parsing and code manipulation logic in this workspace. I am claiming this tool provides "deterministic" code manipulation.
Adopt the persona of a skeptic who believes real-world code is dirty and broken.
Identify specific lines where this code assumes perfect syntax. What happens if I feed it a file with a missing semicolon, a Jinja2 template mixed with Python, or a merge conflict marker?
Prove to me that this parser will crash or hang on "dirty" code.

```
---
## Results
Skeptical take: this code assumes clean syntax in multiple core paths. On “dirty” input (missing semicolon in JS, Jinja2 in Python, merge conflict markers), it will raise and abort, not deterministically “repair.” I don’t see a hang path; I do see hard failures.

Concrete hotspots:

PDG builder assumes parseable Python
builder.py:101-107
ast.parse(code) is called with no guard. A SyntaxError bubbles and fails the tool.
SurgicalExtractor hard-fails on bad Python
surgical_extractor.py:646-654
ast.parse(self.code) inside _ensure_parsed(); SyntaxError is converted to ValueError. Any Jinja2 tags or merge conflict markers will trigger this.
Symbol rename refactor silently bails
rename_symbol_refactor.py:234-242
ast.parse(code) inside _collect_reference_edits(). On SyntaxError, it returns empty edits. That’s a failure mode (no edits), not deterministic manipulation.
Surgical patcher also assumes clean code
surgical_patcher.py:319-323
ast.parse(code) inside a try; on SyntaxError returns empty replacements. No repair.
Symbolic engine treats syntax errors as hard failures
engine.py:399-413
Normalizer raises SyntaxError and the engine rethrows ValueError. Dirty input stops the tool.
Type inference discards results on bad syntax
type_inference.py:165-176
ast.parse(code) in infer(). SyntaxError returns {}. That’s not deterministic analysis—it’s “give up.”
Polyglot extractor depends on parsers that can throw
extractor.py:244-268
Python path delegates to SurgicalExtractor (see above). JS/TS normalizers will throw if the tree-sitter parse fails (no local guard here).
How “dirty” code breaks it:

Missing semicolon (JS): JS/TS normalizers will error on parse. No local recovery in extractor.py:264-316.
Jinja2 mixed with Python: ast.parse raises SyntaxError and SurgicalExtractor throws ValueError (surgical_extractor.py:646-654).
Merge conflict markers: <<<<<<< in Python code fails ast.parse (same path).
Conclusion: deterministic manipulation isn’t guaranteed on malformed or mixed syntax. The dominant behavior is “raise or bail,” not “recover.” If you want resilience, you’ll need a permissive parser, or pre-sanitization that strips templates/conflict markers before AST

#### 2. The "Token Burner" Argument

**Context:** Open your PDG (Program Dependence Graph) generation and prompt construction logic.

```text
@workspace /persona "The Budget Auditor"
Analyze the logic used to generate the Program Dependence Graph (PDG) and the resulting prompts sent to the LLM.
Trace the data flow. How much context is being stuffed into the prompt?
I suspect this tool is a "Token Burner." Calculate the worst-case scenario: If I run this on a 500-line file with heavy dependencies, is it going to cost me $2.00 in API credits just to rename a variable?
Rip apart the efficiency of this approach.

```
### Results
Skeptical take: the PDG path is pure AST → graph, and there’s no built‑in prompt assembly that “stuffs” the PDG into an LLM request. The token burn risk is driven by tool outputs that include raw code, not by PDG itself.

PDG data flow (no LLM prompt stuffing)
PDGBuilder.build() calls ast.parse directly and builds an in‑memory graph — no prompt is created here.
See builder.py:101-107.
The older CodeAnalysisToolkit also does ast.parse and caches PDGs; again no prompt building.
See core.py:68-75 and core.py:132-140.
Bottom line: PDG generation is CPU/memory work, not token work.

Where token bloat actually comes from
The prompt templates are static and short (see prompts.py). The bloat risk is when tool outputs include full code or cross‑file dependencies, and the client pipes those into an LLM:

The “token burner” pattern is in extraction/dep tools, not PDG. If you use “include_cross_file_deps” or dump entire dependency sets, the tool returns large chunks of code that the client might send to the LLM.
Worst‑case estimate (rename variable on 500‑line file)
The rename/refactor pipeline uses AST/token rewrite and does not require an LLM by default (see surgical tools in surgery).
If you do send full file + cross‑file deps to the LLM, you’re easily into tens of thousands of tokens. A 500‑line file can be ~10–25k tokens depending on density, and cross‑file deps can explode that.
“$2.00 per rename” depends entirely on your model pricing and how much raw code you send. The codebase itself doesn’t force that; the client pipeline does.
“Deterministic” vs “dirty”
PDG build assumes valid syntax:

ast.parse(code) in builder.py:101-107
ast.parse(code) in core.py:68-75
If the input is dirty, this fails fast (raises), it doesn’t hang. So the deterministic claim only holds for parseable code.

#### 3. Latency

**Context:** Open your main execution loop or the graph traversal algorithms.

```text
@workspace /persona "The Speed Freak"
Look at the graph traversal and AST analysis algorithms in the current files.
I want you to estimate the "Time to Edit."
If I use `sed` or `ripgrep`, it takes milliseconds. Based on the complexity of this code (loops, recursions, API calls), argue why this tool will feel sluggish to a user.
Where is the bottleneck that will make a user say "it's faster to just type it myself"?

```
### Results
Short answer: yes, it will feel sluggish compared to sed/rg because it does full AST/graph analysis, graph traversal, and full project crawling before it edits anything. The bottlenecks are parse+graph build, graph traversal, and filesystem crawling.

Key “Time to Edit” bottlenecks:

PDG build = full AST parse + NodeVisitor walk (O(n) tokens)
ast.parse(code) plus a full AST walk to build graph nodes/edges.
builder.py:101-107
This is orders of magnitude slower than a regex substitution.
Graph slicing = repeated graph traversal
ProgramSlicer.compute_slice() performs worklist traversal across PDG nodes and edges.
slicer.py:129-189
For large graphs, this is CPU‑heavy. There is no time bound or early exit.
Project crawl = filesystem + per‑file analysis
crawl_project dispatches to _crawl_project_sync for deep mode and walks the tree, parses files, and builds summaries.
context_helpers.py:1013-1050
That’s disk I/O + parsing for every file. On “heavy dependencies” this easily dwarfs a rename.
Network calls in dependency scanning
scan_dependencies calls into VulnerabilityScanner().osv_client.query_batch() (external API).
security_helpers.py:1325-1331
Any network call adds noticeable latency vs local text edit.
Why it feels slow vs sed/rg:

sed does single‑pass text rewrite on a buffer.
This stack does parse → build graphs → traverse graphs → possibly crawl the project → possibly call external services. That’s milliseconds vs seconds.
Worst case for a 500‑line file with dependencies:

Parsing is still fine, but graph creation + slicing scales with node/edge count, and deep crawl scales with file count.
If your pipeline triggers crawl_project or dependency scans, you’re doing hundreds of files and possibly network calls before a trivial rename.
Bottom line:

The bottleneck is graph/AST analysis and project crawling, not the text edit.
For quick edits, this pipeline is objectively slower; users will say “just type it” because they can make the change in <1s while this stack is still parsing and traversing.


#### 4. Language Support

**Context:** Open your language definition files or tree-sitter bindings.

```text
@workspace /persona "The Legacy Dev"
Scan the workspace for language support definitions.
I am a developer working in a polyglot environment (C#, Go, Rust, and legacy PHP).
Critique the architecture's extensibility. Is the logic hard-coded for Python/JS?
Tell me exactly how painful it would be to add support for a language you don't currently see here. If it requires rewriting core logic, destroy the "universal" claim.

```
### Results
Short answer: yes, it will feel sluggish compared to sed/rg because it does full AST/graph analysis, graph traversal, and full project crawling before it edits anything. The bottlenecks are parse+graph build, graph traversal, and filesystem crawling.

Key “Time to Edit” bottlenecks:

PDG build = full AST parse + NodeVisitor walk (O(n) tokens)
ast.parse(code) plus a full AST walk to build graph nodes/edges.
builder.py:101-107
This is orders of magnitude slower than a regex substitution.
Graph slicing = repeated graph traversal
ProgramSlicer.compute_slice() performs worklist traversal across PDG nodes and edges.
slicer.py:129-189
For large graphs, this is CPU‑heavy. There is no time bound or early exit.
Project crawl = filesystem + per‑file analysis
crawl_project dispatches to _crawl_project_sync for deep mode and walks the tree, parses files, and builds summaries.
context_helpers.py:1013-1050
That’s disk I/O + parsing for every file. On “heavy dependencies” this easily dwarfs a rename.
Network calls in dependency scanning
scan_dependencies calls into VulnerabilityScanner().osv_client.query_batch() (external API).
security_helpers.py:1325-1331
Any network call adds noticeable latency vs local text edit.
Why it feels slow vs sed/rg:

sed does single‑pass text rewrite on a buffer.
This stack does parse → build graphs → traverse graphs → possibly crawl the project → possibly call external services. That’s milliseconds vs seconds.
Worst case for a 500‑line file with dependencies:

Parsing is still fine, but graph creation + slicing scales with node/edge count, and deep crawl scales with file count.
If your pipeline triggers crawl_project or dependency scans, you’re doing hundreds of files and possibly network calls before a trivial rename.
Bottom line:

The bottleneck is graph/AST analysis and project crawling, not the text edit.
For quick edits, this pipeline is objectively slower; users will say “just type it” because they can make the change in <1s while this stack is still parsing and traversing.
---

### **Domain 2: Infrastructure & Operations**

#### 5. MCP Protocol Compliance

**Context:** Open your MCP server implementation and JSON-RPC handlers.

```text
@workspace /persona "The Standards Pedant"
Review the MCP (Model Context Protocol) implementation in this workspace.
Don't just check if it runs. Check if it is *compliant*.
Does it handle JSON-RPC errors correctly? Does it support cancellation tokens?
Find where I "hacked" the protocol to make it work. Tell me why this will break when I try to connect it to a strict client like the Claude Desktop app.

```
## Results
Skeptical review: there are multiple protocol “hacks” that deviate from strict MCP/JSON‑RPC expectations. The server runs, but strict clients can break on error handling and prompt/tool wrapping.

Key compliance risks:

JSON‑RPC error handling is bypassed
The tool wrapper always returns a ToolResponseEnvelope dict, even on exceptions.
See protocol.py:195-264.
A strict JSON‑RPC client expects error responses in the JSON‑RPC error envelope, not a successful tool response with error inside the payload.
structured_output=False hack
The wrapper forces structured_output=False to bypass schema validation and emits an unstructured envelope.
See protocol.py:187-199.
That may break strict clients expecting schema‑validated tool results.
Protocol “TODOs” admit missing JSON‑RPC compliance
You have TODOs explicitly for error handling with machine‑parseable error codes.
See __init__.py:30-35.
That’s a compliance gap, not just a missing feature.
Prompt auto‑registration side‑effect
Protocol imports prompts on module import:
protocol.py:271-275
This is a side‑effect that can surprise strict clients or tool registries that expect explicit registration, not import‑time mutation.
Cancellation tokens: partial, not protocol‑level
You now pass ctx into some helpers and check cancellation manually (good), but protocol‑level cancellation handling is marked TODO.
See server.py:271-274.
Strict clients (e.g., Claude Desktop) may issue cancel requests at the protocol level; this implementation doesn’t show explicit JSON‑RPC cancel handling.
Envelope wraps exceptions instead of propagating JSON‑RPC errors
_enveloped_run catches BaseException and returns a normal envelope.
protocol.py:242-264.
That violates strict JSON‑RPC semantics: an error should be a JSON‑RPC error object.
Why strict clients might reject it:

They may expect MCP/JSON‑RPC error frames and schema‑validated tool outputs.
This implementation returns “successful” JSON responses with embedded errors instead, which is a behavior mismatch.
Bottom line: this is functional for permissive clients but not strict MCP/JSON‑RPC compliance. The “hack” is the custom envelope wrapper that bypasses standard JSON‑RPC error handling and schema validation.

#### 6. Dependency Hell

**Context:** Open `requirements.txt`, `pyproject.toml`, or `package.json`.

```text
@workspace /persona "The Minimalist"
Look at the dependency files in this workspace.
Identify every library that looks heavy, outdated, or unnecessary.
Why are we importing massive data science libraries just to do text processing?
Accuse this project of being "bloatware" that will take 10 minutes to install in a CI/CD pipeline.

```
### Results
This project is bloatware for install time. The default install pulls heavy AI agent stacks, visualization libs, SMT solvers, and polyglot parsers. That will make CI/CD installs slow.

Heavy / questionable entries (base install in requirements.txt and pyproject.toml):

LLM/agent frameworks: crewai, langchain, langgraph, autogen, anthropic, openai
These are huge transitive trees. If this is just code analysis, these should be optional extras (they already are in pyproject, but they’re in requirements.txt which forces install).
Visualization stack: plotly, matplotlib
Large wheels, heavy dependencies. Not needed for text processing or AST analysis.
SMT solver: z3-solver
Large binary, slow to install. If symbolic execution isn’t always used, this is optional.
Tree-sitter family: tree-sitter, tree-sitter-java, tree-sitter-javascript, tree-sitter-typescript
Native builds slow down CI. If only Python is needed for many runs, these should be extras.
Graph tooling: graphviz, networkx
graphviz often needs system packages. This commonly breaks CI unless extra apt packages are installed.
Web server: uvicorn, flask
Not needed for offline analysis; these should be extras (they are in web, but still in requirements.txt).
Why this is “bloatware”:

requirements.txt forces all optional stuff, while pyproject.toml tries to keep a slim core with extras. That’s inconsistent and bloated.
The install will easily take minutes in a cold CI environment: native wheels, large transitive deps, and AI SDKs.
Biggest offenders causing slow CI installs:

langchain, crewai, autogen, anthropic, openai
z3-solver
plotly, matplotlib
tree-sitter*
graphviz (system dependency)
If you want this to stop feeling like bloatware, the minimum action is: strip heavy libs out of requirements.txt and keep them only in extras (as already organized in pyproject.toml).

#### 7. The "Sandbox Escape"

**Context:** Open files handling file system I/O (`os`, `shutil`, `subprocess`).

```text
@workspace /persona "The Black Hat"
Audit the file system operations in this code.
I am a malicious actor prompting the AI agent.
Can I trick this tool into reading `/etc/passwd` or deleting the `.git` folder?
Where are the guardrails? If you find a `subprocess.run` or `os.system` call that relies on user input without strict sanitization, declare this project a Critical Security Vulnerability.

```
### Results
Black‑hat audit summary (focused on file I/O + command execution):

Can I read passwd?
Not by default. The MCP layer enforces allowed roots:

_validate_path_security() rejects paths outside allowed roots, defaulting to PROJECT_ROOT.
See server.py:438-512.
Resources and helpers use resolve_path() + _validate_path_security() for file operations.
See resources.py:199-210.
Exploit path: If the client sets roots to / (or a parent of etc) via roots/list or SCALPEL_ROOT, then passwd becomes readable. That’s not a code exploit, it’s a configuration risk.

Can I delete .git?
I didn’t find any code that does shutil.rmtree(.git) directly, but there are write operations:

Backup/restore uses shutil.copy2() in surgical patching.
See surgical_patcher.py:1307-1310.
Git operations use subprocess.run(["git", ...]) with project root set.
See extraction_helpers.py:1576-1654.
Risk: If a malicious user controls file_path or project_root and you allow roots too broadly, they can target files inside allowed roots. But I don’t see raw rm -rf or equivalent.

Do you have unsafe subprocess.run / os.system?
I did not find any os.system calls that take user input at runtime. The mentions of os.system are in security analyzers (pattern detection), not executed commands.

For subprocess.run, most calls are:

Fixed command lists (["git", "…"], ["pytest", "-x"], etc.)
shell=False by default (since list args are used)
No direct string interpolation into a shell
Example:
extraction_helpers.py:1576-1654 uses list‑style subprocess.run with user‑provided target_name only in the commit message, not in a shell command. That’s not command injection.

Conclusion: I cannot declare a Critical Security Vulnerability based on shell injection. I found no os.system or subprocess.run(..., shell=True) that directly uses user input.

Guardrails you actually have
Path boundary checks in _validate_path_security()
server.py:438-512
PathResolver/validate_paths used by tools and resources
path_resolver.py:553-587
Where the guardrails can fail
If allowed roots are misconfigured (e.g., /), the guardrails permit everything.
Some helpers may still be using Path(...) directly; I didn’t see a global enforcement of _validate_path_security in every file‑system touch.
---
If you want me to go deeper, tell me which tool paths you’re worried about (e.g., extract_code, update_symbol, validate_paths, get_file_context) and I’ll trace each to verify every file path is validated.

#### 8. Self-Hosting Friction

**Context:** Open `Dockerfile`, `docker-compose.yml`, and setup scripts.

```text
@workspace /persona "The Lazy Sysadmin"
Review the deployment files (Docker, scripts).
Count the number of steps required to get this running from zero.
If I have to set more than 2 environment variables or manually create folders, I'm not using it.
Roast the onboarding process. Why isn't this a single binary or a one-line install?

```
### Results
Lazy sysadmin verdict: this is not a one‑liner. It’s a multi‑step setup with optional HTTPS, workspace mounts, and multiple services. You’re asking me to run a server with Docker and manage workspace mappings and certs. That’s not “lazy‑friendly.”

Step count (from zero)
Minimum (HTTP, MCP only):

Install Docker
Clone repo
Build image
Set workspace env or rely on default
Run docker‑compose
That’s already >2 steps and requires Docker + clone + build.

Environment variables required
At least 3 set in docker‑compose:

WORKSPACE_ROOT
PROJECT_ROOT
SCALPEL_ROOT
See docker-compose.yml:17-46.
If you want HTTPS, you also need:

SSL_CERT
SSL_KEY
See docker-compose.yml:47-83 and Dockerfile:33-49.
Manual folders
SSL certs directory if HTTPS (certs)
See docker-compose.yml:54-63.
The workspace you want to mount (CODE_SCALPEL_WORKSPACE)
Why this isn’t one‑line
Multi‑service compose file (MCP, HTTPS MCP, REST API).
It requires a build (no prebuilt image).
TLS isn’t zero‑config.
It depends on external workspace path being mounted.
Roast summary
This is not lazy‑sysadmin friendly. It’s a full Dockerized stack with env variables, mounts, and optional certs. There’s no single binary, no curl | sh, no pipx install code-scalpel mentioned in Docker. You’re also shipping a REST API container alongside MCP, which adds confusion and bulk.

If you want “one‑line install,” you need:

A prebuilt image
A single “run” command with defaults
Optional TLS setup, not required by default
No manual envs for root/workspace unless advanced use
---

### **Domain 3: Documentation & DX**

#### 9. The "Happy Path" Fallacy

**Context:** Open `README.md` or `docs/`.

```text
@workspace /persona "The 3AM Debugger"
Read the documentation in the workspace.
I am trying to fix a bug at 3 AM and the tool is failing.
Does the documentation have a "Troubleshooting" section? Does it explain what to do when the AST fails to parse?
Or is it all just "Happy Path" marketing fluff that assumes everything works perfectly? Point out what is missing.

```
### Results
I don’t see a Troubleshooting section or any guidance for AST parse failures. The docs are mostly “happy path” marketing and feature lists, not 3AM failure modes. There’s no mention of how to handle malformed code, Jinja/templated files, or what to do when AST parsing throws. That’s a gap for real-world debugging. If you want this to be usable at 3AM, add explicit failure modes and recovery steps (bad syntax, mixed templates, conflict markers, path/root errors, missing dependencies).

#### 10. Jargon Overload

**Context:** Open `README.md` and intro docs.

```text
@workspace /persona "The Junior Dev"
Scan the documentation and variable naming conventions.
Highlight every instance of academic jargon (e.g., "AST," "PDG," "Isomorphic," "Deterministic").
Explain why a regular developer trying to build a web app doesn't care about these words.
Accuse the documentation of being written for the author's ego, not the user's utility.

```
#### Results
Academic jargon is pervasive across docs. Here are representative instances with links; a full line‑by‑line dump would be very long—confirm if you want the exhaustive list.

Examples:

AST usage in stress.md:7, stress.md:18, stress.md:22
“Deterministic” in stress.md:22
PDG in stress.md:64, stress.md:75
AST/PDG complexity in stress.md:116, stress.md:163
“AST dump” in stress.md:567
AST verification mention in stress.md:635
PDG design reference in QUICK_REFERENCE_DOCS.md:25
Symbolic execution reference in QUICK_REFERENCE_DOCS.md:50
AST/PDG/Symbolic stack marketing in WEEK_1_LAUNCH_COMPLETE.md:89, WEEK_1_LAUNCH_COMPLETE.md:94, WEEK_1_LAUNCH_COMPLETE.md:95, WEEK_1_LAUNCH_COMPLETE.md:97
AST/PDG/Symbolic in roadmap in V1.0_ROADMAP.md:29, V1.0_ROADMAP.md:33, V1.0_ROADMAP.md:69, V1.0_ROADMAP.md:676
Symbolic execution/taint in V1.0_ROADMAP_COMPREHENSIVE.md:81, V1.0_ROADMAP_COMPREHENSIVE.md:97, V1.0_ROADMAP_COMPREHENSIVE.md:98, V1.0_ROADMAP_COMPREHENSIVE.md:111
AST/PDG counts in todo_statistics.md:43, todo_statistics.md:56
AST/PDG module TODO inventories in todos_by_module.md:3, todos_by_module.md:511
Critique: the docs read like a thesis defense. They lean on internal architecture terms (AST/PDG/taint/symbolic) without immediately translating into user outcomes. That feels ego‑forward: “look how sophisticated the internals are,” instead of “here’s what you can do, how fast, and how to recover when it fails.” If you want this to land with working engineers, lead with concrete workflows and failure modes, then explain the jargon only when it pays off.

Confirm if you want the exhaustive per‑line list; it is long.
---

#### 11. Time-to-Value

**Context:** Open the "Getting Started" or "Quickstart" guide.

```text
@workspace /persona "The Impatient"
Review the Quickstart guide.
Simulate the user journey. How many minutes until I see the first successful edit?
If I have to configure an LLM API key, set up a vector DB, and install Docker before I see magic, tell me why I will churn before finishing step 1.

```
### Results
Quickstart review (actual user journey):

Primary quickstart is in getting_started.md. A secondary “Quick Start by Server Type” is in README.md. Docker-only path is in DOCKER_QUICK_START.md.

Simulated time to first successful edit (best‑case, VS Code/Copilot stdio path):

Install uv (or pip): ~1–3 min.
Add .vscode/mcp.json: ~2 min.
Start MCP server from VS Code: ~1–2 min.
Ask Copilot to run a simple tool (e.g., analyze file): ~1–2 min.
Ask for a small edit and apply it: ~3–8 min.
Total: ~8–17 minutes to first successful edit in the happy path.
If you choose Docker/HTTP path:

Pull image: ~2–10 min (network dependent).
Run container + verify health: ~2–5 min.
Configure client to HTTP server: ~2–5 min.
First tool call + edit: ~5–10 min.
Total: ~11–30 minutes.
About churn:

The quickstart does NOT require a vector DB anywhere in the getting started guide or README quickstart. If a vector DB shows up later, it will feel like bait‑and‑switch.
LLM API key isn’t required in the “Recommended” local MCP path. It becomes implied only if you want Claude API over HTTPS in Docker, which adds SSL cert setup and network config in DOCKER_QUICK_START.md.
If a user is told they must “configure an LLM API key + set up a vector DB + install Docker” before seeing results, they will churn because the first visible value is pushed behind 3 different infrastructure tasks. That’s multiple points of failure before any payoff.
Bottom line: the lowest‑friction path is the stdio MCP setup in getting_started.md. If you make Docker + HTTPS + API key the default path, the time‑to‑first‑edit blows out and churn happens before step 1 finishes.

#### 12. Error Message Analysis

**Context:** Open global exception handlers or logging modules.

```text
@workspace /persona "The UX Critic"
Look at the error messages and logging in the code.
If a user makes a mistake (e.g., invalid path), does the tool throw a raw Python stack trace, or does it give a helpful human-readable error?
Find a place where the code just says "Error" or "Exception" without context and mock it for being hostile to the user.

```
### Results
I checked the MCP resource handler. It generally does NOT return raw stack traces; it serializes exceptions into a JSON error string. But the UX is still hostile because the messages are often generic or raw exception text without guidance.

Example of a context‑free failure:

In resources.py:464-474 the fallback is error: "Extraction failed" with no hint about which symbol/type failed or what to try next.
Mocking it (per request):

“Extraction failed.” Great, thanks. Failed what? The file? The symbol? The parser? The fallback logic? This is the UX equivalent of a shrug.
Also:

For path mistakes, it returns {"error": str(e)} in resources.py:255-269. That’s human‑readable in the sense that it’s plain text, but it’s still raw exception phrasing and offers zero next steps.

---

### **Domain 4: Product & Market Positioning**

#### 13. The "Copilot/Cursor" Killer

**Context:** Open the project abstract or "About" section.

```text
@workspace /persona "The VC Shark"
Based on the code I see here, why does this exist?
GitHub Copilot and Cursor already exist and they are integrated into the editor.
This tool requires an MCP server and an Agent.
Convince me this isn't just a slower, more complicated version of autocomplete. If you can't point to a feature in the code that Copilot *cannot* do, declare the project dead.

```
### Results
Not dead. It’s not autocomplete; it’s a deterministic analysis + governance layer that Copilot/Cursor don’t provide.

Concrete capabilities in code that editor autocomplete doesn’t do:

Cryptographic policy integrity verification at runtime (tamper‑resistant governance) in src/code_scalpel/policy_engine and enforcement plumbing in governance.py.
Change budgets / blast‑radius control and enforced policy gating in src/code_scalpel/policy_engine and src/code_scalpel/tiers.
Deterministic AST/PDG/symbolic execution tooling (formal analysis, not text prediction) in src/code_scalpel/pdg_tools and src/code_scalpel/symbolic_execution_tools.
Audit‑trail and governance hooks intended to enforce file operations across tooling, not just suggestions, in claude_hooks.py.
Copilot and Cursor can suggest edits; they do not provide cryptographically enforced policies, audit trails, or deterministic program‑analysis primitives with budgeted change governance. That’s the reason this exists.

#### 14. Complexity vs. Value

**Context:** Open the core logic files.

```text
@workspace /persona "The Pragmatist"
Look at the complexity of the AST/PDG implementation.
Is this "Over-Engineering"?
If I just want to find usages of a function, `grep` works fine.
Argue that the complexity cost of maintaining this graph analysis outweighs the marginal benefit of "slightly better" accuracy.

```
### Results
Yes, it reads as over‑engineering for the “find usages” use‑case.

Why:

The PDG stack is a full graph builder + analyzer + slicer with deep TODO backlogs, not a lean utility. The PDG builder alone is ~560 LOC with heavy planned scope, interprocedural analysis, aliasing, exception flow, multi‑language support, and distributed graph features—all in comments and TODOs, which signals ongoing maintenance burden. See builder.py:1-60.
The analyzer and slicer both add large, multi‑stage pipelines (data‑flow anomalies, taint, slicing variants) that are far beyond “find usages.” See analyzer.py:1-120 and slicer.py:1-120.
The utilities add graph metrics and path search on top of a full NetworkX PDG, which is expensive to compute and keep correct for every language edge case. See utils.py:1-120.
Pragmatist take: for “find usages,” rg/grep is cheap, fast, and consistent. PDG accuracy gains are marginal for that single task, while the cost is ongoing complexity, performance overhead, and a broad TODO surface. The maintenance cost outweighs the incremental benefit unless you’re doing formal data‑flow analyses or security taint tracking at scale.



#### 15. The "So What?" Test

**Context:** Open the list of features or capabilities.

```text
@workspace /persona "The Cynic"
Pick the most complex feature in this codebase.
Ask "So what?"
Why does a user need a Program Dependence Graph? How does that actually help them ship code faster?
If the answer is "it's cool tech," destroy it. It needs to solve a burning pain point.

```
### Results
Most complex feature: Program Dependence Graph (PDG). It’s front‑and‑center in the feature list and module docs, e.g. README.md and README.md.

So what?

If the PDG doesn’t directly cut bug‑fix time or prevent a specific class of failures, it’s a vanity graph. Users don’t buy graphs; they buy fewer regressions, faster reviews, and safer edits.
Why would a user need it?

Only if it powers something they feel immediately: accurate impact analysis, safe refactors, real taint tracking that prevents vulnerabilities, or reliable “change only what’s necessary” edits. If it’s just “cool tech,” it’s dead weight.
Cynic verdict:

If the PDG doesn’t reduce rework, shrink review time, or prevent production incidents, it’s a science project. “We built a PDG” is not a pain point. “We cut rollback rate by 40% because PDG‑based impact checks prevent unsafe edits” is. If you can’t tie it to that, kill it or hide it.

---

### **Domain 5: Process & Methodology**

#### 16. Test Coverage Reality Check

**Context:** Open the `tests/` directory.

```text
@workspace /persona "The QA Lead"
Analyze the `tests/` directory.
I am looking for "Happy Path" testing.
Do you only test perfect code? Show me the tests for:
1. Circular dependencies.
2. Malformed syntax.
3. Network timeouts.
If these are missing, tell me this code is "untested prototypeware."

```
### Results
QA Lead verdict: Not “happy‑path only.” All three cases are covered.

Circular dependencies:
test_v151_integration.py:240-307 creates circular imports and asserts detection/handling.
Malformed syntax:
test_get_call_graph.py:300-312 writes a syntax‑error file and verifies tool behavior.
Network timeouts:
test_scan_dependencies.py:736-771 simulates OSV timeout and asserts it’s surfaced as an error.
So no, this isn’t “untested prototypeware” on those dimensions.

#### 17. Release Cadence & Versioning

**Context:** Open `CHANGELOG.md` or `git` history.

```text
@workspace /persona "The Enterprise Architect"
Look at the versioning and changelog (if available) or the project structure.
Is this set up for Semantic Versioning?
If I update this tool next week, will it break my entire workflow?
Critique the stability guarantees based on the current code structure.

```
### Results
SemVer claim: yes, explicitly stated in CHANGELOG.md:1-6. So the intent is SemVer.

Stability guarantees: mixed. Red flags in structure and docs imply churn risk:

Multiple version anchors disagree: README says v3.3.0, docs index still says v3.0.0 “Autonomy” while also listing v3.3.0 release notes in the same file. See README.md:7-20 vs INDEX.md:1-20. That’s a signal of inconsistent release hygiene.
Tool list in INDEX.md:35-74 still references “20 tools” while README claims 22. That is API surface mismatch documentation‑wise, which means clients may not have a stable contract reference.
Heavy monolith + archived server copy suggests duplication risk: there’s an active MCP server and a large archived one under src/code_scalpel/mcp/archive/server.py. That’s a maintenance hazard for compatibility and behavior drift.
If you update next week, will it break your workflow?

If you rely on a specific tool contract or output schema, the lack of consistent docs and multiple copies of server logic suggests a non‑zero break risk.
The changelog says SemVer, but the repo structure and doc drift don’t reinforce strong compatibility guarantees.
Enterprise architect take: SemVer is declared, but the actual release discipline looks inconsistent. Treat upgrades as potentially breaking until contract tests are pinned or a versioned API guarantee is explicitly enforced and aligned across README, INDEX, and tool docs.

#### 18. Contribution Model

**Context:** Open `CONTRIBUTING.md` or the module structure.

```text
@workspace /persona "The Open Source Maintainer"
I want to contribute a feature to this repo.
Look at the code modularity.
Is it spaghetti code where everything is in `main.py` or `utils.py`?
Tell me how hard it is to onboard a new developer. If it takes me a week to understand the graph logic, the project will die when you get bored of it.

```
### Results


---

### **Domain 6: Costs**

#### 19. Hidden Costs

**Context:** Open the performance-intensive modules (Graph building).

```text
@workspace /persona "The Cloud Architect"
Analyze the compute intensity of the graph generation code.
If I run this in a cloud container, how much RAM and CPU does it need?
Are there memory leaks? Large objects held in memory?
Accuse the project of requiring expensive oversized instances to run reliably.

```
### Results
It’s not spaghetti in a single main.py. The core is split into many modules (ast_tools, pdg_tools, symbolic_execution_tools, mcp, policy_engine, etc.) per README.md:20-88. That’s modular, but it’s also huge (the same doc claims ~1.2M LOC and 500K+ LOC symbolic engine).

Onboarding difficulty: high. The contributor guide you’d expect at root isn’t there; the actual guide is buried at CONTRIBUTING.md, and it literally says “install will fail” and “prototype” language. That’s a red flag for new contributors.

Pragmatic take:

Modular, but deep: graph logic + symbolic execution + MCP + governance is a week‑scale learning curve for a new dev.
If a new contributor needs a week just to understand PDG + graph engine internals, the bus factor is real. The project needs better onboarding and narrower entry points or it risks stalling when the core maintainer steps away.

#### 20. Token Bloat (ROI)

**Context:** Open the prompt engineering templates.

```text
@workspace /persona "The CFO"
Look at the prompt templates used to communicate with the LLM.
Count the tokens roughly.
If you are sending the AST dump to the LLM, you are lighting money on fire.
Prove that the value of the output > the cost of the input. If not, tell me to shut the project down.

```
### Results
Prompt templates are in prompts.py. They are short, instruction‑style wrappers—no AST dumps, no code payloads.

Rough token count per prompt: ~80–140 tokens. They’re just a few lines of steps plus a path/symbol/goal. Example: “Refactor Safely” is ~100–130 tokens, “Deep Security Audit” ~110–140. That’s cheap.

There is no AST dump in these prompts. The expensive payloads only happen if a tool is asked to return large code or dependencies. The prompts themselves aren’t lighting money on fire.

CFO verdict: input cost is low. Value is in tool‑driven extraction, not raw prompt size. No shutdown recommendation based on prompt cost alone.

### **Domain 7: Legal & Data Privacy (The "Cease & Desist" Vector)**

**Persona:** The IP Lawyer. They are looking for reasons to sue you or block your acquisition.

#### 21. The License Contamination Check

**Context:** Open `pyproject.toml`, `package.json`, or your third-party vendor folder.

```text
@workspace /persona "The IP Lawyer"
Audit the dependency tree in this workspace.
I am looking for "Copyleft" viruses (GPL/AGPL) that might "infect" my proprietary codebase if I use your tool.
Do you rely on any libraries with restrictive licenses that forbid commercial use?
Also, check for "abandonware" licenses—dependencies that haven't been updated in 3 years.
Warn me if I am about to inherit a legal headache.

```

## Results
Based on pyproject.toml, requirements.txt, and requirements-secure.txt:

No GPL/AGPL packages are explicitly listed in these dependency files.
This is not a full license audit: transitive dependencies are not listed here, and optional extras (e.g., langchain, crewai, autogen, anthropic, openai) pull large dependency trees with mixed licenses.
Abandonware check: cannot verify “last updated in 3 years” from the workspace alone. That requires package metadata or registry timestamps, which aren’t in these files.

Risk warning:

The legal risk is primarily in transitive dependencies, not the top‑level list.
If you enable the optional AI integrations, you inherit their transitive license surface area.
If you want a definitive copyleft/age audit, ask for a full dependency lock (pip/uv) and license scan.

#### 22. The Data Leakage Audit

**Context:** Open the modules that communicate with the LLM API.

```text
@workspace /persona "The Privacy Officer"
Trace the data flow from the user's file system to the external API.
Does this tool strip sensitive information (API keys, passwords, PII) before sending code to the LLM?
If you are sending my raw `.env` file or hardcoded secrets to OpenAI/Anthropic to be "analyzed," you are a data breach waiting to happen.
Find the redaction logic. If it doesn't exist, fail the audit.

```
### Results
I checked the LLM integration modules and the MCP helpers.

Findings:

There is no implemented OpenAI/Anthropic client in this repo. The “LLM API” modules are TODO stubs (no outbound calls), e.g. claude.py, langchain.py.
Redaction logic exists only as flags in file‑context results; it does not actually strip secrets or PII from code. See context_helpers.py:1455-1547.
Secret masking is used for security findings, not for outbound payload redaction:

secret_scanner.py:347-410.
Audit conclusion:

Data flow to external LLM APIs is not implemented here, so there’s no demonstrated path to “OpenAI/Anthropic.”
However, there is no redaction pipeline to sanitize code before sending to any external LLM if someone adds that integration later. That is a fail for privacy hardening.
Result: fail the audit on “redaction before external LLM.”
---

### **Domain 8: AI Stability & Lock-in (The "Model Drift" Vector)**

**Persona:** The AI Researcher. They know that models change, get lazy, or get deprecated.

#### 23. The "Model Lock-in" Trap

**Context:** Open the prompt templates or the LLM client configuration.

```text
@workspace /persona "The Agnostic"
Review the prompts and LLM client logic.
Is this tool "over-fitted" to a specific model (e.g., Claude 3.5 Sonnet or GPT-4o)?
If I try to switch to a cheaper model (like Haiku) or an open-source model (like Llama 3 via Ollama), will the prompts break?
Critique the "Prompt Portability." If the logic relies on quirks specific to one model family, accuse the project of Vendor Lock-in.

```
### Results
Prompts are generic, not tied to a specific model’s quirks. See prompts.py. They’re plain instruction lists with tool names, no system‑prompt hacks, no tool‑schema features that only one model supports.

LLM client logic: essentially absent. The “Claude/LangChain/Autogen” integrations are TODO stubs, not live clients (e.g., claude.py, langchain.py). That means there isn’t a baked‑in dependency on Claude 3.5 or GPT‑4o behaviors.

Portability critique:

Prompts are portable, but there’s no real adapter layer for model differences (token limits, response formats, tool‑use behavior).
Token counting has model‑specific heuristics (e.g., Claude approximations) in surgical_extractor.py, which can skew budgets when switching models.
Verdict: not over‑fitted to a single model, but also not robustly portable. No vendor lock‑in by design, but missing real multi‑model client support means portability is theoretical, not proven.

#### 24. The Hallucination Handler

**Context:** Open the code that applies the changes returned by the AI.

```text
@workspace /persona "The Skeptic"
Look at the logic that parses the AI's response and applies it to the file.
What happens if the AI hallucinates a method that doesn't exist? Or if it returns code that is syntactically correct but functionally wrong?
Does the Code Scalpel verify the AST *after* the edit but *before* saving to disk?
If there is no "Post-Edit Verification" step, tell me that this tool will corrupt my codebase.

```
### Results
Skeptic read:

If the AI hallucinates a symbol, the patcher bails with “not found / not a function.” See surgical_patcher.py:664-718.
It only validates the replacement snippet’s syntax/type before patching, not the whole file after patching. See surgical_patcher.py:602-654.
The save path just writes whatever is in current_code with no post‑edit AST verification or semantic checks. See surgical_patcher.py:1264-1334.
So: no post‑edit verification step before saving. If the AI returns code that is syntactically “valid” but functionally wrong, this tool will happily write it. That is a corruption risk.
---

### **Domain 9: The "Marketing vs. Reality" Gap (The "Clickbait" Vector)**

**Persona:** The YouTube Tech Reviewer. They want to expose you for lying in your marketing.

#### 25. The "Magic Button" Test (Marketing Copy Review)

**Context:** Open your `README.md`, Landing Page copy, or "Pitch" text.

```text
@workspace /persona "The Clickbait Investigator"
Read the marketing claims in the README (e.g., "Autonomous," "Flawless," "Instant").
Now compare that to the actual code complexity I see in the workspace.
Are you promising "Level 5 Autonomy" (The agent does everything) when the code only supports "Level 2 Autonomy" (The agent suggests, human reviews)?
Highlight every adjective that is an exaggeration of the code's actual capability.

```
#### Results
Exaggeration flags in README.md:9-76:

“mathematical precision” and “eliminating hallucinations” overstate actual guarantees. There is no end‑to‑end verification or post‑edit validation to justify that absolutism. README.md:11-16
“deterministic” and “mathematically proves” are too absolute for a system that still accepts model‑generated code and lacks full post‑edit verification. README.md:19-46, README.md:71-76
“provably correct test cases” is a hard claim; the symbolic engine can generate tests, but nothing here proves full correctness across real codebases. README.md:38-45
“Enterprise‑Ready” and “invisible governance” are marketing adjectives; compliance and governance are partial and tier‑gated, not end‑to‑end guaranteed. README.md:47-60
“99% token reduction” and “million‑line codebases with 4K token models” are extreme claims without visible benchmarking or constraints. README.md:25-34
Autonomy level: The README markets “surgical” tooling, but the actual flow is tool‑assisted and review‑driven. This reads like Level 2 (suggests + human review), not Level 5 (“agent does everything”). There’s no “magic button” end‑to‑end autonomy in the core README.
