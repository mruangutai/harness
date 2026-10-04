---
name: attack-the-premise
title: Attack the Premise
description: "Apply when two or more fixes that share one premise have failed the same gate. Take a census of which actors hold the imbalance, then question the premise instead of writing another fix that assumes it."
seats: [harness-frontend-dev, harness-backend-dev, harness-ai-dev, harness-data-engineer, harness-dev-ops, harness-eng-lead, harness-pm]
---
# Attack the Premise

When two or more fixes that share one premise have failed the same gate, suspect the premise, not the fixes.

**Why:** Each failure under a shared premise is evidence about the premise.

**Pattern:**
- **Write the premise down.** The premise is the one sentence every failed fix assumed.
- **Take a census before the next fix.** Count the imbalance per actor. The census shows which actors hold the imbalance, not how large it is. Write it as a rerunnable script (`references/build-the-lever.md`); this is shell work, so a lead or pm hands it to a dev with a shell rather than estimating it.
- **Read the skew.** If the same few actors hold most of the imbalance on every run, something assigns them that role. Find what assigns the role; that assignment is the next "why" (`harness-systematic-debugging`).
- **Remove the asymmetry instead of compensating for it** (`references/delete-first.md`). Rotate the role between actors, randomize the assignment, or move the role, so that no actor holds it on every run. A return path, a shared pool, a batched hand-off, or a periodic rebalance leaves the assignment in place and adds work on every run.

**Stop:**
- Do not start the next fix before the premise is written down and the census exists.
- If the census is even across actors, the premise is not the cause. Look for the cause elsewhere and keep the census as evidence.

Distinct from `references/redesign-from-first-principles.md`, which rebuilds a design around a new requirement; this questions a fact the current design assumes.
