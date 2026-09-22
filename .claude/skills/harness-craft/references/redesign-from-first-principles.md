---
name: redesign-from-first-principles
title: Redesign From First Principles
description: "Apply when integrating a new requirement into an existing design. Redesign as if the requirement had been a foundational assumption from day one instead of bolting it on."
seats: [harness-frontend-dev, harness-backend-dev, harness-ai-dev, harness-data-engineer, harness-eng-lead, harness-pm]
---

# Redesign From First Principles

When integrating a change, do not bolt it onto the existing design. Redesign as if the requirement had been there from the start.

**Why:** A bolted-on requirement leaves the old assumptions standing beside the new one, and every later change must satisfy both; redesigning is how option value survives integration.

**The pattern:**

- **Read all affected files** and understand the current design before touching it.
- **Ask the from-scratch question:** "if we were writing this from scratch with this requirement, what would we build?"
- **Propagate through every reference:** types, docs, examples, rationale sections, tests. A requirement that lives in one file and not the others is bolted on.
- **Think about the whole redesign, then deliver it incrementally** (`references/outcome-oriented-execution.md`).

**The test:** Could a reader of the finished code tell which requirement arrived last? If yes, the seam is still showing.

For a pm the same move applies to the brief: fold the new requirement into the perspectives rather than appending an exception to them.

This rebuilds a design around a new requirement. `references/attack-the-premise.md` questions a fact the current design already assumes.
