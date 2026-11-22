---
name: model-the-domain
title: Model the Domain
description: "Apply when writing stateful logic, or when code branches a lot or repeats a shape assumption across files. Encode the domain in a structure instead of scattered conditionals."
seats: [harness-frontend-dev, harness-backend-dev, harness-ai-dev, harness-data-engineer, harness-eng-lead, harness-code-reviewer]
---
# Model the Domain

Encode the real domain in a data structure instead of scattering it across conditionals.

**Why:** Scattered booleans, repeated shape assumptions, and branching spread across files are accidental complexity. A structure that matches the domain makes invalid states unrepresentable and deletes branches. Choosing it at write time is cheap; recovering it later reads as a refactor and gets deferred.

Name the structure in the domain's own vocabulary — the target project's glossary or BRIEF where it has one; when the domain is harness itself, `<HARNESS_CONTROL_PLANE_ROOT>/.harness/glossary.md` (`harness-spec-driven`). A structure named in terms the next reader already knows needs no comment.

The same rule applies to the constants and patterns that name the domain:
- **Spell flags out:** `re.IGNORECASE`, never an alias such as `_I`. The behaviour belongs on the declaration line.
- **One pattern per path concept:** its variants are named groups (`phase`, an optional `cycle`), not a second pattern that must keep the same flags and anchors in lockstep. Consumers that need different flags compile the one pattern text with their own documented flags.
- **Name constants for what they mean, not how they're built:** `SHAPE_DIAGNOSTIC_LABEL`, not `VERB`.

A justified bootstrap respelling is the exception: where importing would break repair independence (a gate that must still load when the module it would import is broken) or no import seam exists, restate the pattern verbatim, say why beside it, and keep a test that asserts the two stay equal.

**Reach for structures like these:**
- A state machine instead of scattered booleans, phases, or lifecycle checks.
- A typed object or model instead of loose parameters or repeated shape assumptions.
- A map, registry, lookup table, or discriminated union instead of branching spread across files.
- A reducer or command/event model instead of ad hoc state mutations.
- A module organized around one body of domain knowledge instead of a sequence such as load, validate, transform, save. Execution order is not ownership.
- A small module boundary that gathers repeated behavior, ownership, or invariants.
- A queue, cache, index, graph/tree, or normalized collection where the access pattern calls for it.
- Any other structure that fits. When none does, work out what the code must never allow and how the data gets read, then find the structure that encodes exactly that.

Do not force an abstraction. Prefer boring code when the current shape is already clear, local, and unlikely to grow. Be skeptical of an abstraction that adds indirection without removing branches, duplicated rules, invalid states, or lifecycle risk.

**The test:** A new feature that grows an existing if/else chain by one more branch, or a second boolean that must stay in sync with the first, means this was skipped. Phase-named modules that repeat the same domain rules across steps are the same sign.

The compile-time form of the structure is `references/type-system-discipline.md`.
