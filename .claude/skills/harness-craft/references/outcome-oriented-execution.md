---
name: outcome-oriented-execution
title: Outcome-Oriented Execution
description: "Apply during planned rewrites and migrations with explicit phase boundaries. Converge on the target architecture; do not preserve smooth intermediate states with throwaway compatibility code."
seats: [harness-backend-dev, harness-data-engineer, harness-dev-ops, harness-eng-lead, harness-pm]
---
# Outcome-Oriented Execution

Optimize for the intended, verifiable end state rather than preserving smooth intermediate states.

**Why:** Keeping every intermediate step fully stable creates temporary compatibility code that becomes long-lived debt. Converge on the target architecture and prove correctness at explicit verification boundaries.

**Core rule:**
- Prioritize end-state integrity over transitional stability.
- Intermediate breakage is acceptable when it is planned, scoped, and reversible.
- Always run final verification before declaring done (`harness-principles` rule 7).

**Guardrails:**
- Use this for planned rewrites and migrations with explicit phase boundaries. The plan names the phases; the success criteria describe the end state, not the intermediate ones.
- Declare where temporary breakage is acceptable, in the plan, before it happens.
- Keep high-signal checks for actively touched areas while migrating.
- Require full static and runtime verification at plan completion.

**The test:** Would this compatibility code survive plan completion? If it exists only to keep an intermediate phase green, it is the debt this principle forbids.

`references/migrate-callers-then-delete.md` applies the same stance to a single API.
