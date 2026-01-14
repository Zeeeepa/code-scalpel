# AI Development Is Getting Easier — and More Fragile

**Document type:** LinkedIn tease article (draft)

AI development is getting “easier” — and simultaneously more fragile.

We have more models, more frameworks, more agents, more automation… yet many teams still feel like they’re building on shifting sand. The hard part isn’t writing code anymore. It’s proving the code is correct, safe, and maintainable when AI is in the loop.

Below are the problems I keep seeing (and what I think actually helps).

## 1) “It works on my prompt” isn’t a QA strategy

AI-assisted changes often look plausible, compile, and even pass a few happy-path tests—while subtly changing behavior at the edges. Refactors “for readability” can alter ordering, error handling, defaults, and security assumptions.

**What helps:**

- Behavior validation as a first-class check (diff-aware, not vibes-aware)
- Small, reviewable change sets with clear intent
- Guardrails that flag semantic drift early (before it lands in `main`)

## 2) Codebase context is the real bottleneck

AI is strongest when it has accurate, scoped context. But large repos + partial context = confident mistakes. Developers then spend time verifying whether the generated code is even connected to reality.

**What helps:**

- Surgical context retrieval (the smallest necessary slice of code)
- Call-graph and reference awareness so changes are scoped correctly
- A workflow that forces “show me the definition + usages” before rewriting

## 3) Security regressions are easy to introduce, hard to notice

One new string format, one convenience helper, one “quick” `eval`/`subprocess` call, one unvalidated boundary… and you’ve created an incident. AI can inadvertently recommend patterns that are unsafe in your environment or threat model.

**What helps:**

- Automated sink detection and taint-style reasoning on changed code
- Policies that are executable, versioned, and enforceable
- A workflow that treats security like a compile step, not a postmortem

## 4) Type systems evaporate at runtime boundaries

Types in TypeScript don’t validate JSON from the network. Dataclasses don’t validate external payloads. “It’s typed” becomes a false sense of safety right where you need it most: serialization boundaries.

**What helps:**

- Runtime validation (schemas) at all untrusted boundaries
- Contract checks across frontend ↔ backend
- Automated detection of “trusted type assertions” with no validation behind them

## 5) Teams are drowning in “AI output,” starving for “AI accountability”

The next wave isn’t bigger prompts. It’s reproducibility: why a change was made, what it impacted, what it could break, and whether it violates policy.

**What helps:**

- Traceable checks (policy integrity, signed rules, auditable results)
- Deterministic analysis steps that run the same way in CI and locally
- A focus on verification tooling, not just generation tooling

---

My take: the next competitive advantage in AI engineering won’t be who generates code fastest. It’ll be who can verify changes fastest—with confidence.

That’s exactly the direction we’ve been building toward with **Code Scalpel**: tools designed to make AI-assisted development safer, more deterministic, and easier to validate (behavior, security, and policy integrity included).

We’re nearing release at the end of the month. If you’re shipping AI-assisted code into real systems and want fewer surprises, follow along—more details soon.
