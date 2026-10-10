# Receipt — harness-ai-dev — SIMPLIFY c1 — simplification angle — FEAT-2037

**Verdict: PASS** (advisory only). Reported 2 · recommended-accept 1 (low) · skipped 1. Read-only; nothing applied, no checks run.

Evidence: `git -C <root> diff 37cfcfd4 HEAD -- .claude/skills/harness-principles/SKILL.md .claude/skills/harness-spec-driven/SKILL.md .claude/skills/harness-zero-micro-management/SKILL.md .harness/harness/docs/SPEC.md` (+33/-3); files read at HEAD (principles 14-26, SPEC 1116-1131). Angle: `angle-simplification.md`; craft: `delete-first.md` (applied: redundant instructions are dead weight; one rule in two places can drift).

## Findings

### F1 — SPEC paragraph restates the principles rule (plan/prose surface: one rule in two places) — recommend ACCEPT, low
- File/lines: `.harness/harness/docs/SPEC.md` 1122-1131.
- Cost: the doc-role mapping, on-demand read, and the missing/unresolved/conflict reporting rule are spelled out here and again in `harness-principles/SKILL.md` 17-26 (wording already differs: "unresolved guidance with the section" vs "unresolved sections and questions"). Two copies can drift; deletion test: removing the SPEC detail loses nothing, since the authority is the skill.
- Alternative — replace lines 1122-1131 with:
  `**Product guidance is read input, not a Harness rule overlay.** Planning, implementation and review consult the assigned PRODUCT checkout's `docs/spec.md`, `docs/decisions.md` and `docs/architecture.md` on demand, as `harness-principles` defines; `spec-driven` and `zero-micro-management` carry the pointers into task intent and nested dispatch as read inputs, not owned files. Neither Harness root supplies these paths by default; Harness governance (DECISIONS-INDEX/DECISIONS, SPEC) is unchanged (DEC-70, DEC-158, DEC-214).`
  Saves ~4 lines; keeps consultation, payload preservation and the product/Harness distinction.

### F2 — principles rule is long for a universal-load skill — SKILL, no change
- File/lines: `.claude/skills/harness-principles/SKILL.md` 17-26 (+10 lines in a skill SPEC 1116 says to keep shortest, loaded on all 16 agents).
- Cost: reader load on every spawn.
- Alternative considered: move the three-way reporting sentence (23-25) to a leaf. Skipped: settled that resident guidance carries the shared rule; the leaf would add a layer/read for a seam every consulting agent needs at point of use, and removing it weakens consultation. Not a deletion candidate.

## Clean checks
- spec-driven 50-53 and zero-micro-management 29-32 additions are pointers to `harness-principles`, not restatements; each carries the distinct payload-preservation duty at its own seam. No pass-through.
- No dead references, no change-narrating comments, no signed fields changed.

## Counts
reported 2 · accepted (recommended) 1 (F1) · skipped 1 (F2) · files_touched [].
