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

#### 2. The "Token Burner" Argument

**Context:** Open your PDG (Program Dependence Graph) generation and prompt construction logic.

```text
@workspace /persona "The Budget Auditor"
Analyze the logic used to generate the Program Dependence Graph (PDG) and the resulting prompts sent to the LLM.
Trace the data flow. How much context is being stuffed into the prompt?
I suspect this tool is a "Token Burner." Calculate the worst-case scenario: If I run this on a 500-line file with heavy dependencies, is it going to cost me $2.00 in API credits just to rename a variable?
Rip apart the efficiency of this approach.

```

#### 3. Latency

**Context:** Open your main execution loop or the graph traversal algorithms.

```text
@workspace /persona "The Speed Freak"
Look at the graph traversal and AST analysis algorithms in the current files.
I want you to estimate the "Time to Edit."
If I use `sed` or `ripgrep`, it takes milliseconds. Based on the complexity of this code (loops, recursions, API calls), argue why this tool will feel sluggish to a user.
Where is the bottleneck that will make a user say "it's faster to just type it myself"?

```

#### 4. Language Support

**Context:** Open your language definition files or tree-sitter bindings.

```text
@workspace /persona "The Legacy Dev"
Scan the workspace for language support definitions.
I am a developer working in a polyglot environment (C#, Go, Rust, and legacy PHP).
Critique the architecture's extensibility. Is the logic hard-coded for Python/JS?
Tell me exactly how painful it would be to add support for a language you don't currently see here. If it requires rewriting core logic, destroy the "universal" claim.

```

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

#### 6. Dependency Hell

**Context:** Open `requirements.txt`, `pyproject.toml`, or `package.json`.

```text
@workspace /persona "The Minimalist"
Look at the dependency files in this workspace.
Identify every library that looks heavy, outdated, or unnecessary.
Why are we importing massive data science libraries just to do text processing?
Accuse this project of being "bloatware" that will take 10 minutes to install in a CI/CD pipeline.

```

#### 7. The "Sandbox Escape"

**Context:** Open files handling file system I/O (`os`, `shutil`, `subprocess`).

```text
@workspace /persona "The Black Hat"
Audit the file system operations in this code.
I am a malicious actor prompting the AI agent.
Can I trick this tool into reading `/etc/passwd` or deleting the `.git` folder?
Where are the guardrails? If you find a `subprocess.run` or `os.system` call that relies on user input without strict sanitization, declare this project a Critical Security Vulnerability.

```

#### 8. Self-Hosting Friction

**Context:** Open `Dockerfile`, `docker-compose.yml`, and setup scripts.

```text
@workspace /persona "The Lazy Sysadmin"
Review the deployment files (Docker, scripts).
Count the number of steps required to get this running from zero.
If I have to set more than 2 environment variables or manually create folders, I'm not using it.
Roast the onboarding process. Why isn't this a single binary or a one-line install?

```

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

#### 10. Jargon Overload

**Context:** Open `README.md` and intro docs.

```text
@workspace /persona "The Junior Dev"
Scan the documentation and variable naming conventions.
Highlight every instance of academic jargon (e.g., "AST," "PDG," "Isomorphic," "Deterministic").
Explain why a regular developer trying to build a web app doesn't care about these words.
Accuse the documentation of being written for the author's ego, not the user's utility.

```

#### 11. Time-to-Value

**Context:** Open the "Getting Started" or "Quickstart" guide.

```text
@workspace /persona "The Impatient"
Review the Quickstart guide.
Simulate the user journey. How many minutes until I see the first successful edit?
If I have to configure an LLM API key, set up a vector DB, and install Docker before I see magic, tell me why I will churn before finishing step 1.

```

#### 12. Error Message Analysis

**Context:** Open global exception handlers or logging modules.

```text
@workspace /persona "The UX Critic"
Look at the error messages and logging in the code.
If a user makes a mistake (e.g., invalid path), does the tool throw a raw Python stack trace, or does it give a helpful human-readable error?
Find a place where the code just says "Error" or "Exception" without context and mock it for being hostile to the user.

```

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

#### 14. Complexity vs. Value

**Context:** Open the core logic files.

```text
@workspace /persona "The Pragmatist"
Look at the complexity of the AST/PDG implementation.
Is this "Over-Engineering"?
If I just want to find usages of a function, `grep` works fine.
Argue that the complexity cost of maintaining this graph analysis outweighs the marginal benefit of "slightly better" accuracy.

```

#### 15. The "So What?" Test

**Context:** Open the list of features or capabilities.

```text
@workspace /persona "The Cynic"
Pick the most complex feature in this codebase.
Ask "So what?"
Why does a user need a Program Dependence Graph? How does that actually help them ship code faster?
If the answer is "it's cool tech," destroy it. It needs to solve a burning pain point.

```

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

#### 17. Release Cadence & Versioning

**Context:** Open `CHANGELOG.md` or `git` history.

```text
@workspace /persona "The Enterprise Architect"
Look at the versioning and changelog (if available) or the project structure.
Is this set up for Semantic Versioning?
If I update this tool next week, will it break my entire workflow?
Critique the stability guarantees based on the current code structure.

```

#### 18. Contribution Model

**Context:** Open `CONTRIBUTING.md` or the module structure.

```text
@workspace /persona "The Open Source Maintainer"
I want to contribute a feature to this repo.
Look at the code modularity.
Is it spaghetti code where everything is in `main.py` or `utils.py`?
Tell me how hard it is to onboard a new developer. If it takes me a week to understand the graph logic, the project will die when you get bored of it.

```

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

#### 20. Token Bloat (ROI)

**Context:** Open the prompt engineering templates.

```text
@workspace /persona "The CFO"
Look at the prompt templates used to communicate with the LLM.
Count the tokens roughly.
If you are sending the AST dump to the LLM, you are lighting money on fire.
Prove that the value of the output > the cost of the input. If not, tell me to shut the project down.

```
You have covered the Code, Ops, Product, and Money extensively. However, looking at this holistically, there are **three critical blind spots** remaining that could kill the project even if the code is perfect.

These are the **"Silent Killers"**: Legal/IP Risk, AI Model Lock-in, and the "Demo Effect."

Here are the missing prompts to complete the gauntlet.

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

#### 22. The Data Leakage Audit

**Context:** Open the modules that communicate with the LLM API.

```text
@workspace /persona "The Privacy Officer"
Trace the data flow from the user's file system to the external API.
Does this tool strip sensitive information (API keys, passwords, PII) before sending code to the LLM?
If you are sending my raw `.env` file or hardcoded secrets to OpenAI/Anthropic to be "analyzed," you are a data breach waiting to happen.
Find the redaction logic. If it doesn't exist, fail the audit.

```

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

#### 24. The Hallucination Handler

**Context:** Open the code that applies the changes returned by the AI.

```text
@workspace /persona "The Skeptic"
Look at the logic that parses the AI's response and applies it to the file.
What happens if the AI hallucinates a method that doesn't exist? Or if it returns code that is syntactically correct but functionally wrong?
Does the Code Scalpel verify the AST *after* the edit but *before* saving to disk?
If there is no "Post-Edit Verification" step, tell me that this tool will corrupt my codebase.

```

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

### Summary of the "Code Scalpel" Gauntlet

You now have **25 unique adversarial prompts** covering:

1. **Core Tech** (Determinism, Tokens, Speed)
2. **Ops** (MCP, Security, Deploy)
3. **DX** (Docs, Onboarding)
4. **Product** (Value, Use Case)
5. **Process** (Testing, Maintenance)
6. **Costs** (ROI, Compute)
7. **Legal** (Licensing, Privacy)
8. **AI Stability** (Lock-in, Hallucination)
9. **Marketing** (Truth in Advertising)

**Recommendation:**
Start with **Prompt #7 (The Sandbox Escape)** and **Prompt #22 (Data Leakage Audit)**. If you fail those, nothing else matters because the project is dangerous. Would you like to start there?