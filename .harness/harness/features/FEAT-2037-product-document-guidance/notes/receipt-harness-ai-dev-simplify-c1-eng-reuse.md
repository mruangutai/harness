# Receipt — harness-ai-dev — SIMPLIFY c1 reuse angle — FEAT-2037 T-01

**Verdict: PASS (advisory).** Reported 2 · accepted 2 (both advisory, low) · skipped 0. Read-only; no checks run, nothing edited.

Evidence: `git -C <worktree> diff 37cfcfd4 HEAD -- <4 files>` (HEAD caedd74d, +33/-3); angle-reuse.md and delete-first.md read; `grep docs/(spec|decisions|architecture).md` over `.claude/skills` shows the three product paths spelled in `harness-principles/SKILL.md:19-21` (canonical) and again in `harness-spec-driven/SKILL.md:50-51`. SPEC.md:1122-1131 restates the rule in prose. `.claude/agents` does not exist in the worktree, so no agent prompts carry a copy.

## R-1 — spec-driven re-enumerates the three product paths (accepted, low)
- File/lines: `.claude/skills/harness-spec-driven/SKILL.md:50-53`
- Existing thing: `.claude/skills/harness-principles/SKILL.md:19-21` already names all three paths, and spec-driven line 52 already defers to it.
- Cost: two spellings of the path set. If a path is renamed or a fourth document is added, principles gets edited and spec-driven stays stale. The spelled-out list is also the only reason line 52 has to say "defines product-relative consultation".
- Alternative (replace 50-53):
```
   Carry the assigned PRODUCT checkout identity and the applicable product-document pointers
   (`harness-principles` names them) in this actual `intent:`, not just the BRIEF, notes or
   parent context. These are read inputs, not owned `files:` unless the task changes them.
```
  Saves about 1 line and one lockstep site. The zero-micro-management hunk (29-32) already uses this pointer-only form and is the convention to match.

## R-2 — SPEC.md paragraph re-states the principles rule (accepted, low)
- File/lines: `.harness/harness/docs/SPEC.md:1122-1131`
- Existing thing: `harness-principles/SKILL.md:17-26`. The same path-to-purpose mapping, the consult-on-demand rule, the report-missing/unresolved/conflict triad, and the "not task-owned files" rule appear in both places.
- Cost: 10 lines of near-verbatim prose, so behavior edits to the resident rule must be made twice. SPEC is the design doc and not loaded at spawn, so drift would go unnoticed.
- Alternative (replace 1122-1131; keeps the rationale and the DEC cites):
```
**Product guidance is read input, not a Harness rule overlay.** The behavior is stated once,
in `harness-principles`: planning, implementation and review consult the assigned PRODUCT
checkout's `docs/spec.md`, `docs/decisions.md` and `docs/architecture.md` on demand, and task
`intent:` and nested dispatch carry the pointers (`harness-spec-driven`,
`harness-zero-micro-management`). Neither Harness root supplies these paths. Harness
governance, including its DECISIONS-INDEX/DECISIONS and SPEC, is unchanged (DEC-70, DEC-158,
DEC-214).
```
  Main may judge that SPEC should keep a self-contained statement of the rule; if so, skip it, because the cost is lockstep editing only.

## Checked, no finding
- `harness-principles` path changes (`<HARNESS_CONTROL_PLANE_ROOT>/docs/PRINCIPLES.md`) match the existing anchored-path convention used elsewhere in the skills. No reuse issue.
- zero-micro-management hunk (29-32) correctly points to the shared rule and does not restate the paths.
- No new script, validator, eval or schema was added, so nothing re-implements an existing check.
- Size note, out of this angle: the new principles paragraph loads on all agents at every spawn (SPEC.md:1116). That belongs to the simplification/altitude angle, not reuse.
