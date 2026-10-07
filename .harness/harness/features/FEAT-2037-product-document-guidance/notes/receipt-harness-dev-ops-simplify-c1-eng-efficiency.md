# Receipt — harness-dev-ops — SIMPLIFY c1 — efficiency angle — FEAT-2037 T-01

**Verdict: PASS.** Reported 1 / accepted 0 / skipped 1 (advisory only). Read-only; no checks run, no files changed besides this receipt.

## Evidence
- `git diff 37cfcfd4 HEAD` over the four scoped files (HEAD `caedd74d`, +33/-3 confirmed by `--stat`); angle rule read from `.agents/skills/harness-simplify/references/angle-efficiency.md`; delete-first leaf read.
- `wc -c` on `.claude/skills/harness-principles/SKILL.md`: 1771 → 2829 bytes (+1058, +60%); the new paragraph is ~1004 bytes (~250 tokens).
- spec-driven (+4 lines) and zero-micro-management (+4 lines) are loaded on demand by planner / domain leads. SPEC.md (+11 lines) is not spawn-injected. None is a hot path.

## Finding 1 (advisory, SKIPPED)
- File/lines: `.claude/skills/harness-principles/SKILL.md` lines ~17-26 (the "Consult the assigned product" paragraph).
- Summary: `harness-principles` is loaded by all 16 agents at every spawn (its own description), so the +~250 tokens apply to every spawn, including agents that never touch a product repo.
- Cost: ~250 tokens per spawn × every spawn. No hot-path milliseconds, no I/O, and well under a minute per feature. Real but small.
- Alternative if MAIN wants it smaller: drop the sentence "Read relevant sections on demand, not whole product documents by default" only if it duplicates SPEC (it does not; SPEC says "on demand"). Otherwise trim nothing: each remaining clause (three-way report shapes, no Harness fallback, reviewers judge conformance) is a settled acceptance behavior and the resident copy is the point of the task. No replacement text offered.
- Skip reason: below the minutes threshold, and settled scope requires resident guidance. The paragraph does not duplicate itself (SPEC states the rule once for governance; the skill states it once for agents).

## Checked, no finding
- Description line: +29 bytes (`<HARNESS_CONTROL_PLANE_ROOT>/` prefix), negligible.
- Path-prefix edits to `docs/PRINCIPLES.md`: no cost.
- The new paragraph says on-demand section reads, so it does not instruct whole-document reads on every task. That is the one place the change could have created repeated I/O.
- spec-driven and zero-micro-management add pointers, not reads. Sequential tasks carry pointers, not repeated whole-file reads.
- No code surface, no suite added or re-run by the diff. Deliberate boundary suites are settled and not flagged.

## Principles applied
- Delete First (read this run): checked for removable redundancy in added prose; found none that is not acceptance content.
