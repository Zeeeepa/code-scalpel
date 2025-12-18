# **Code Scalpel: Adversarial Validation Checklist (v2.0.1+)**

Role: Skeptical Senior Engineer / Security Red Team  
Objective: Break the claims of Code Scalpel (v2+ Era).  
Principle: "An agent that works in Java but breaks the Frontend is useless. An agent that guesses is dangerous."

## **REGRESSION BASELINE (v2.0.1 Requirements)**

*These must ALWAYS pass. If any fail, immediate "Stop Ship".*

* \[ \] **Java Generics:** Correctly extracts Repository\<User\> vs Repository\<Order\>.  
* \[ \] **Spring Security:** Accurately identifies LdapTemplate and OAuth2TokenProvider sinks.  
* \[ \] **Determinism:** Re-running analysis on unchanged code yields identical IDs.  
* \[ \] **Performance:** Java parsing remains \< 200ms for standard files.

## **PHASE 4 — The Unified Graph (v2.2.0)**

**Claim:** "Code Scalpel sees one system and admits what it doesn't know."

### **Adversarial Questions**

* If the API route is constructed dynamically ("/api/" \+ version \+ "/user"), does the graph claim a link or flag uncertainty?  
* Can the agent be tricked into refactoring a "guessed" dependency?

### **[COMPLETE] Must‑Pass Checklist**

**Explicit Uncertainty**

* \[ \] **Confidence Scores:** Every heuristic link (e.g., String matching routes) has a confidence \< 1.0.  
* \[ \] **Threshold Enforcement:** Agents are BLOCKED from acting on confidence \< 0.8 links without human approval.  
* \[ \] **Evidence:** The tool returns *why* it linked two nodes (e.g., "Matched string literal on line 42").

**Cross-Boundary Linking**

* \[ \] **HTTP Links:** Graph connects fetch (JS) to @RequestMapping (Java).  
* \[ \] **Type Synching:** Changing a Java Class field flags the corresponding TypeScript Interface as "Stale".

[DEPRECATED] Fail Condition:  
If the tool presents a "Best Guess" as a "Fact" (Silent Hallucination).

## **PHASE 5 — Governance & Policy (v2.5.0)**

**Claim:** "You can enforce 'Thou Shalt Not' rules on the Agent."

### **Adversarial Questions**

* Can an agent bypass a "No SQL" policy by using a String Builder?  
* Does the policy engine fail "Open" or "Closed"? (Must fail Closed).
* Can an agent bypass policy files via chmod/chown? (Must verify cryptographic signatures)
* Does confidence decay for deep dependency chains? (10+ hops should trigger low-confidence warning)
* Does graph explosion occur with large call graphs? (Must have neighborhood pruning)

### **[COMPLETE] Must‑Pass Checklist**

**Enforcement**

* \[ \] **Semantic Blocking:** Blocks logic that *looks* like a disallowed pattern even if syntax varies.  
* \[ \] **Path Protection:** DENY rules apply to file *content* identity, not just names.  
* \[ \] **Budgeting:** Edits exceeding max\_complexity are strictly rejected.

**Tamper Resistance**

* \[ \] Policy files are read-only to the Agent.  
* \[ \] Override codes require Human-in-the-loop approval.
* \[ \] **Cryptographic Verification:** Policy files signed with SHA-256; invalid signature → fail closed.
* \[ \] **chmod Bypass Prevention:** Policy integrity verified regardless of file permissions.

**Confidence & Scaling (3rd Party Review)**
<!-- [20251216_DOCS] Added per 3rd party security review -->

* \[ \] **Confidence Decay:** Results at depth 10+ marked as "low confidence" (formula: C_effective = C_base × 0.9^depth).
* \[ \] **Graph Neighborhood View:** k-hop subgraph extraction with max 100 nodes.
* \[ \] **Truncation Warning:** When graph is pruned, return explicit warning to agent.

[DEPRECATED] Fail Condition:  
If an agent can execute a forbidden action by "tricking" the parser.

## **PHASE 6 — The Self-Correction Loop (v3.0.0)**

**Claim:** "The system teaches the agent how to fix itself."

### **Adversarial Questions**

* If the agent enters a fix-break-fix loop, does Scalpel stop it?  
* Are the "Fix Hints" actually valid code?
* Can an agent submit a "hollow fix" (`def test(): pass`) and claim success?
* Does reverting a fix cause tests to fail again? (Mutation Test Gate)

### **[COMPLETE] Must‑Pass Checklist**

**Feedback Quality**

* \[ \] Error messages contain valid diffs or specific AST operations to correct the issue.  
* \[ \] Feedback loop terminates (fails) after N attempts.

**Simulation**

* \[ \] simulate\_edit correctly predicts test failures without writing to disk.  
* \[ \] Sandbox environment isolates side effects.

**Mutation Test Gate (3rd Party Review)**
<!-- [20251216_DOCS] Added per 3rd party security review -->

* \[ \] **Hollow Fix Detection:** `def test(): pass` pattern rejected.
* \[ \] **Revert Validation:** Fix reversal must cause tests to fail.
* \[ \] **Mutation Score:** At least 80% of mutations caught by tests.
* \[ \] **Weak Test Flagging:** Tests that pass with reversed logic flagged.

[DEPRECATED] Fail Condition:  
If the agent reports "Fixed" but the build fails in CI.