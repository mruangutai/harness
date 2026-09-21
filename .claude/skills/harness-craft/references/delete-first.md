---
name: delete-first
title: Delete First
description: "Apply when refactoring, sequencing an addition or rewrite, judging diff size, or tempted to add a layer, abstraction, or threaded signal. Remove before you build, and make the smallest change that solves the problem."
seats: [dev, eng-lead, code-reviewer]
---
# Delete First

Aim for the most result with the least code. When evolving a system, remove complexity first, then build on the simpler base.

**Why:** Adding to a complex system compounds complexity. Removing first leaves less code, reveals the essential structure, and usually makes the next design obvious.

**The pattern:**
- **Prefer deletion.** When asked to refactor or improve, look for removals before additions. Sequence removal before construction; cut before you polish.
- **Minimize the diff.** Make the smallest change that solves the problem. Fewer lines beat "elegant" boilerplate.
- **Keep the call hierarchy flat.** If answering a question means tracing more than three files or layers, flatten it. A rich interface that hides substantial work is not a deep call chain.
- **Consolidate decisions.** Do not repeat the same choice in several places. Put it behind one source of truth and pass the result as a simple flag.
- **Question the threading.** If a task asks you to pass a new signal through types, schemas, and pipelines, stop and look for a more direct path.
- **Sweat the small leaks.** Remove tiny pass-throughs, representation leaks, and duplicated choices before they spread; small leaks compound into permanent coordination costs.
- **Design for observed usage.** No speculative validators, parsers, or guards beyond what the spec demands. The same goes for prompts and templates: redundant instructions are dead weight. A reference with no novel content is deleted, not left as a stub.

Simplification is a continual investment: leave the design slightly simpler and more capable, behind the same or smaller surface, than you found it.

**The test:** If a human developer would find the code exhausting to maintain, it is a bad solution.

Subtraction comes before scaffolding (`references/foundational-thinking.md`). The reader-side of the same instinct lives in `harness-codebase-design`.
