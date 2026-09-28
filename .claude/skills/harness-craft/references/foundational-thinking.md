---
name: foundational-thinking
title: Foundational Thinking
description: "Apply before writing logic: choosing core types and data structures, sequencing scaffold against feature work, or asking what concurrent actors share. Get the data structures right so the downstream code becomes obvious."
seats: [harness-frontend-dev, harness-backend-dev, harness-ai-dev, harness-data-engineer, harness-dev-ops, harness-eng-lead]
---
# Foundational Thinking

Structural decisions protect option value; code-level decisions protect simplicity. Get the data shape right before writing logic.

**Why:** Logic written against the right structure is short and obvious; logic written against the wrong one accumulates special cases that no local cleanup removes.

**The pattern:**
- **Data structures first.** Define core types early, trace every access pattern, and choose structures that match the dominant paths (`references/model-the-domain.md`).
- **DRY the structure, not every line.** Types and data models should converge. Three similar statements still beat a premature abstraction. Prefer explicit over clever. Test behavior and edge cases, not line counts.
- **Ask the concurrency question.** Before sharing state between actors, ask "what happens if another actor modifies this concurrently?" If the answer is not "nothing", isolate (`references/separate-before-serializing-shared-state.md`).
- **Scaffold first.** If something helps every later phase, do it first: CI, linting, test infrastructure, shared types. Sequence for option value: setup before features, tests before fixes.
- **Land coherent increments.** Each increment lands a coherent abstraction or deepens one that exists. Do not spread a new capability across callers as special-case coordination. Keep commits small and single-purpose.
- **Subtract before scaffolding.** Remove dead code first, then lay foundations (`references/delete-first.md`).

**The test:** "Does every subsequent phase benefit from this existing?" If yes, it is scaffold and goes first.

This governs the *sequence* of work; `references/experience-first.md` governs the target.
