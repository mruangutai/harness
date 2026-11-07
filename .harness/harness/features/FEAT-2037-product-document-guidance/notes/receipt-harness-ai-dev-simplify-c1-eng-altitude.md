# Receipt — harness-ai-dev — SIMPLIFY c1 ALTITUDE — FEAT-2037-product-document-guidance

**Verdict: PASS.** Reported 1 / accepted 0 / skipped 1-by-recommendation (finding is `leave`, with a documented optional fold-in). No production edits; no checks run.

## Evidence
- Diff read: `git -C <worktree> diff 37cfcfd4 HEAD -- <4 paths>` (+33/-3); elided hunks read at HEAD (`harness-principles/SKILL.md:15-43`, `SPEC.md:1119-1131`). Plan T-01 intent and BRIEF read. Angle: `harness-simplify/references/angle-altitude.md`; craft leaf `delete-first.md` read.

## Altitude assessment
- **One authority:** the consultation rule is stated once in full at `.claude/skills/harness-principles/SKILL.md:17-26`. This is the resident skill all 16 roles preload (DEC-158), so it sits at the right home; no per-persona copies.
- **Pointers, not copies:** `harness-spec-driven/SKILL.md` (+4) and `harness-zero-micro-management/SKILL.md` (+4) each say only what their handoff must carry and defer to `harness-principles`. Right depth; the real dispatch seam is the only thing they add.
- **Ownership/governance intact:** read inputs, not `files:`; Harness DECISIONS/SPEC distinct. Residual (no enforcement beyond prose) is accepted by settled scope and compensated by the SC-01–03 UAT.
- The `docs/PRINCIPLES.md` -> `<HARNESS_CONTROL_PLANE_ROOT>/docs/PRINCIPLES.md` anchoring is a 2-line disambiguation needed so lowercase `docs/` is not read as product docs. Leave.

## Findings
**A-01 (low) — `.harness/harness/docs/SPEC.md:1122-1131`: SPEC §6 paragraph restates the full rule (3 paths, on-demand, gap-reporting triad, precedence, ownership) already authoritative in `harness-principles:17-26`.**
- Cost: a second ~10-line statement that can drift when the skill rule is amended; no test cross-checks them (same shape as repository G-02).
- Recommendation: **leave.** The plan's T-01 intent explicitly requires SPEC to carry "concise supporting guidance" with those elements, SPEC is explanatory, not loaded at runtime, and trimming reopens settled scope.
- Optional alternative if MAIN wants it later (not required) — replace lines 1122-1131 with:
  > **Product guidance is read input, not a Harness rule overlay.** Planning, implementation and review consult the assigned PRODUCT checkout's `docs/spec.md`, `docs/decisions.md` and `docs/architecture.md` on demand; the rule lives in `harness-principles`, and task intent and nested dispatch preserve checkout identity and pointers as read inputs, never owned files. Neither Harness root supplies these paths; Harness governance is unchanged (DEC-70, DEC-158, DEC-214).
  Saves ~5 lines; classified fold-in-if-desired, default **leave**.

No other findings: no registry/injection/new layer introduced, no bolt-on to a caller, no special case in shared infrastructure.
