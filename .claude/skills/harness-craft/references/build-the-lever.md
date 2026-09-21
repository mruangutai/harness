---
name: build-the-lever
title: Build the Lever
description: "Apply to any non-trivial work, not just bulk work: edits, migrations, analyses, checks. Build the tool that does it or proves it (codemod, script, generator, or a shared recipe) instead of working by hand; the tool is the artifact a reviewer can rerun."
seats: [dev, qa]
---
# Build the Lever

When the work is not trivial, build the tool that does it instead of doing it by hand.

**Why:** Two payoffs. Throughput: a codemod, generator, or script does the work the same way every time and reruns for free. Confidence: the tool is one artifact a reviewer can read and rerun to check the work. Hand-done changes can only be re-verified by redoing them; a deterministic script turns "trust me" into "run this".

**Pattern:** Default to building the lever. Skip it only when the task is trivial: a couple of obvious edits you can see at a glance.
- Do the first unit by hand to learn the recipe, then build the tool. Prove it by rerunning it on that unit and diffing against the hand-done version. Make the lever safe to rerun (`references/make-operations-idempotent.md`).
- Codemod or script for edits, generator for repetitive files, a dump-to-sqlite query for analysis, a rerunnable check for verification.
- A deterministic lever beats fan-out. If the tool can process every unit in one pass, run it yourself; do not hand parallel workers what a script can do.
- When work is fanned out, write the lever as a recipe every worker reads: the steps, the verification contract, and the do-not-touch fences in one artifact, kept outside the workers' write scope so none can quietly edit the contract.
- Commit the lever when the work outlives the session.

**The test:** Applying this principle produces a file. If you cited it and there is no codemod, script, generator, or shared recipe in the diff, you did not apply it.

**Balance:** The bar is triviality, not repetition. A one-off still earns a lever when the lever is what makes the work checkable. Build the smallest script that does or proves the job, never a framework (`references/delete-first.md`).

Rule 13 in `docs/PRINCIPLES.md` (crystallize repetition into tools) is the factory-level counterpart that turns a *recurring* operation into a durable tool; this is throughput and reviewability on the work in front of you. For scripting the verification itself, see `harness-principles` rule 7.
