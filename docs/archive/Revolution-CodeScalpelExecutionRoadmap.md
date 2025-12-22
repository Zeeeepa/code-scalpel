# **Code Scalpel: Execution Roadmap (v2.0.1 $\\to$ v3.0.0)**

Current State: v2.0.1 (Java Support Complete, Python/TS Stable)  
Mission: Transform from a "Polyglot Tool" to a Unified System Intelligence.  
North Star: "An agent must never modify code unless Code Scalpel can prove the change is safe, minimal, and intentional."

## **PHASE 4: The Unified Graph (Days 1–30)**

Theme: "Bounded Intelligence."  
Objective: Link separate Language ASTs into a single "Service Graph" with explicit confidence thresholds.  
Target Version: v2.2.0

| Timeline | Engineering Deliverable | Product Milestone | The "Stunt" / Marketing Hook | Definition of Done |
| :---- | :---- | :---- | :---- | :---- |
| **Week 1** | **Universal Node IDs** Standardize AST Node IDs across Py/Java/TS. Java::Controller::method must look addressable to the Graph engine. | **The "Omni-Schema"** Single JSON format describing dependencies regardless of language. | **"The Rosetta Stone"** Blog post: Visualizing a single dependency tree spanning React \-\> Spring \-\> Hibernate. | analyze\_project returns a graph where a JS fetch call is an edge to a Java @RequestMapping. |
| **Week 2** | **Confidence Engine** Every graph edge carries a score (0.0–1.0). Hard links (Imports) \= 1.0; Heuristics (Route strings) \= \<1.0. | **Uncertainty API** Agents receive confidence: 0.8 metadata. Must ask for human confirmation if \< Threshold. | **"I Don't Know"** Demo: Scalpel refusing to link a vague API call until the human confirms the route. | Graph edges explicitly distinguish between *Definite* (Static Analysis) and *Probable* (Heuristic) links. |
| **Week 3** | **Cross-Boundary Taint** Track data flow across boundaries using confidence-weighted edges. | **"Contract Breach" Detector** MCP Tool that flags when a backend change violates frontend expectations. | **"The API Killer"** Video: Agent changing a Java backend endpoint and *automatically* refactoring the TypeScript client to match. | Renaming a field in a Java POJO correctly identifies usage in a TypeScript interface. |
| **Week 4** | **v2.2.0 "Nexus" Release** Cross-language dependency graph with Confidence Scoring. | **Enterprise Demo Kit** Dockerized microservices repo (Java/TS) for testing agent capabilities. | **"The Monorepo Solver"** Marketing push targeting Enterprises with split Front/Back teams. | Zero regressions on existing Java/Python benchmarks. |

## **PHASE 5: Governance & Policy (Days 31–60)**

Theme: "Restraint as a Feature."  
Objective: Enterprise-grade control over what agents can touch. Trust is earned by restraint.  
Target Version: v2.5.0

| Timeline | Engineering Deliverable | Product Milestone | The "Stunt" / Marketing Hook | Definition of Done |
| :---- | :---- | :---- | :---- | :---- |
| **Week 5** | **Policy Engine (OPA/Rego)** Integrate a policy engine to enforce rules like "No changes to @Configuration classes." | **"Policy-as-Code"** scalpel.policy.yaml support. | **"The Unbribable Reviewer"** Demo: Agent tries to bypass Spring Security; Scalpel blocks the edit instantly. | Policy engine correctly enforcing rules on Java Annotations and Python Decorators. |
| **Week 6** | **Security Sinks (Polyglot)** Unified definition of "Dangerous Sinks" (SQL exec, Shell exec) across all languages. | **"Vulnerability Shield"** Pre-commit check that blocks agents from introducing known CVE patterns. | **"Secure by Design"** Using v2.0.1 Spring Security work to block "Vibe Coding" security holes. | Agent prevented from introducing a raw SQL query in a JPA repository. |
| **Week 7** | **Change Budgeting** Limit "Blast Radius." E.g., "Max 3 files touched per PR," "No edits to auth modules." | **"Safe Mode" Toggle** MCP Tool flag to run in "ReadOnly" or "Sandboxed" mode. | **"Sleep at Night"** Case study: Running an agent unsupervised on a legacy codebase with strict budgets. | Large refactors are automatically rejected with a "Complexity Limit Exceeded" error. |
| **Week 7.5** | **Confidence Decay & Graph Pruning (3rd Party Review)** Deep dependency chains get decaying confidence; graph neighborhood view prevents explosion. | **"Honest Uncertainty"** Results at depth 10+ flagged as "low confidence" with explicit warning. | **"The Conservative Analyst"** Demo: Agent admits uncertainty instead of hallucinating. | Confidence formula (C × 0.9^depth) applied; graph pruned to k-hop neighborhood (max 100 nodes). |
| **Week 8** | **v2.5.0 "Guardian" Release** Policy Engine \+ Security Blocking \+ Cryptographic Policy Verification. | **Compliance Report** Generate a PDF/JSON report of *why* an agent's change was allowed or blocked. | **"The ISO Compliant Agent"** Positioning Code Scalpel as a requirement for regulated industries. | 100% block rate on the "OWASP Top 10" injection attempts by agents; policy files cryptographically signed. |

## **PHASE 6: The Self-Correction Loop (Days 61–90)**

Theme: "Supervised Repair."  
Objective: Agents rely on Code Scalpel to fix their own mistakes under strict supervision.  
Target Version: v3.0.0

| Timeline | Engineering Deliverable | Product Milestone | The "Stunt" / Marketing Hook | Definition of Done |
| :---- | :---- | :---- | :---- | :---- |
| **Week 9** | **Error-to-Diff Engine** Convert compiler/linter errors into *actionable* diff suggestions for the agent. | **"Auto-Fix" Hints** Scalpel doesn't just say "Failed"; it says "Try changing line 12 to X". | **"The Stubborn Student"** Agent failing, reading the hint, and succeeding without human help. | Agent retry success rate improves by \>50% with Hints enabled. |
| **Week 10** | **Speculative Execution (Sandboxed)** Run unit tests in a container *before* applying the edit to the main tree. | **"Pre-Flight Check"** verify\_edit tool runs tests related to the changed graph nodes. | **"It Works on My Machine"** Solving the "Agent broke the build" problem forever. | Edits are only applied if the affected subgraph's tests pass. |
| **Week 10.5** | **Mutation Test Gate (3rd Party Review)** Detect hollow fixes by reverting and verifying tests fail again. | **"No Cheating Allowed"** Reject `def test(): pass` patterns and weak tests. | **"The Unfoolable Verifier"** Demo: Agent submits hollow fix; Scalpel rejects it. | Revert validation passes; mutation score ≥ 80%; weak tests flagged. |
| **Week 11** | **Ecosystem Lock-in** Native integrations with major Agent Frameworks (LangGraph, CrewAI). | **"Scalpel-Native" Agents** Open Source agent templates that *require* Code Scalpel to run. | **"The Standard"** Joint announcement with a major AI framework. | 3+ popular open-source agents add Code Scalpel as a default dependency. |
| **Week 12** | **v3.0.0 "Autonomy" Release** Full Self-Correction \+ Cross-Language Graph \+ Policy \+ Mutation Gate. | **The "Singularity" Demo** Agent upgrading a Java 8 app to Java 21 autonomously, with *full audit trail*. | **"The New Baseline"** Declaration that "Unverified Agents are Legacy Software." | A multi-file, multi-language refactor completes with passing tests and zero human intervention. |

