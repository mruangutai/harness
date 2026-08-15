# UI review — FEAT-21-features-layout-migration — range 62fef85..b1d3925 — Mode B

## Verdict

Out of scope for Mode B UI audit (no rendered surface, no DESIGN.md contract, nothing to grade
fidelity/theme/interaction against). One narrow accessibility sub-check on operator-facing CLI
text was performed per this run's explicit instruction and came back clean. See "the seam" below
for what this review does not cover.

## What I looked at (measured, not inferred)

- Full commit range confirmed: `git log --oneline 62fef85..b1d3925` returns 8 commits, not 5 —
  the 3 extra (`3df7002`, `649b36b`, `5c39f8c`) are FEAT-21 bookkeeping/orchestrator-state commits
  (`STATE.md`, `feature.json`, `plan.yaml`, `notes/`, `observations/` only — confirmed via
  `git show --stat` on each). Same category the dispatch already named for `4b16f47`/`ea937b1`; no
  discrepancy of concern.
- File-extension census across the full range (`git diff --name-only 62fef85..b1d3925 | grep -iE
  '\.(html|css|scss|less|tsx|jsx|vue|svelte)$'`): 11 `.html` matches, all under
  `.harness/*/features/*/notes/` or `BRIEF.html`. Confirmed via `git diff --summary -M` that every
  one is a **100% rename** (`.harness/{ => harness}/features/...`), zero content change — these are
  historical ship-review artifacts riding the directory migration, not markup being authored or
  modified. No design contract governs them and there is nothing to diverge from.
- DESIGN.md/mockup/prototype census (the filename this role exists to audit, not just an
  extension): `git diff --name-status -M 62fef85..b1d3925 | grep -iE 'DESIGN\.md|mockup|prototype'`
  returns 5 matches — `FEAT-02` mockup ruling, `FEAT-10`/`FEAT-11`/`FEAT-19` `DESIGN.md`, `FEAT-17`
  mockup pass. **All `R100`, zero content change.** No design contract was touched by this range.
- The two files carrying `frontend-dev`/`visual-designer` in their names
  (`.claude/agents/harness-frontend-dev.md`, `.claude/agents/harness-visual-designer.md`): read the
  diffs directly rather than assuming. Both are single-line path-literal updates
  (`.harness/features/<FEAT>/DESIGN.md` → `.harness/harness/features/<FEAT>/DESIGN.md`) inside
  agent-instruction prose — no DESIGN.md content, no markup, no styling, no a11y tree. Mechanical
  reference-path fix, consistent with the feature's stated goal.
- `BRIEF.md` read directly: FEAT-21's own scope statement is exclusively about path-migration
  mechanics (`check-state.sh` discovery sites, `check-domain.sh` sweep globs, `check-plan-routes.py`,
  team-config grants, `branch-create-gate.sh`) — no UI/visual/interaction goal anywhere in it.

Conclusion: this diff has no rendered UI surface and no design contract was touched, checked at both
the extension level and the specific filename (`DESIGN.md`/mockup/prototype) this role audits.
`in_scope: false` for the standard Mode B dimensions (fidelity, states-via-rendering, interaction,
theme parity) is a measured result, not an assumption from the feature title.

## The one surface I did look at for real — operator-facing terminal output

Read `check-state.sh` diff in full and `test-layout-migration.py:300-380` (case 20).

**Remit call, with reasoning:** operator-facing CLI/terminal text is **outside my remit** for the
dimensions that define this role — fidelity to a design contract, rendered layout, focus/interaction
state, theme parity — because none of those concepts apply to stdout text and no `DESIGN.md`
governs it. There is nothing here to grade against a contract.

One narrow slice **is** inside my remit per this repo's own accumulated practice (Expertise G-02:
batch/CLI text gets its accessibility sub-check — "state not conveyed by colour alone" — stated
explicitly rather than skipped). I ran that check and audited what my lens covers:

- `grep -niE '\\033|\\x1b|ansi|color|colour'` across `check-state.sh` at `b1d3925`: **zero
  matches**. The script emits plain, uncoloured text throughout — before and after this diff. No
  colour-only state encoding exists to regress. Clean, but low-value: the property held trivially
  because the script never used colour at all.
- The 18 finding-label call sites (`bad.append`/`warn.append` matching `{feat}/`) were all migrated
  to the new `fpath()` helper (`check-state.sh:55-59`) — confirmed zero remaining raw `{feat}/`
  path-prefix literals in the file at `b1d3925`. Consistent conversion, not a partial migration
  that would leave some labels stale.
- `test-layout-migration.py` case 20 (`:329-368`) now invokes `check-state.sh` via `subprocess.run`
  against a built fixture tree and compares its real stdout to `layout_migration.render()` over the
  same tree — confirmed no second hand-written mirror remains in this file at `b1d3925`, consistent
  with commit `3df7002`'s stated fix (parity pinned against the real gate, not a copy).

**What I did NOT check and is explicitly outside my lens:** whether `fpath()`'s path arithmetic is
*correct* in every discovery branch, whether the 18 rewritten messages are *semantically* accurate
for every code path that reaches them, and whether case 20's parity assertion actually catches the
class of drift it claims to (i.e., mutation-style proof of the test itself). Those are code/test
correctness questions — code-reviewer's lens, not a design-contract-fidelity question mine is built
to answer.

**Seam flagged, framed as timing not as a gap:** the code-reviewer note in this feature's `notes/`
dir (`review-harness-code-reviewer-2026-08-14-precommit.md`, timestamped 22:58) predates the SC-10
fix commit `3df7002` (23:47) that touches this exact file pair. This run's directory
(`runs/2026-08-14-3-panel-validator/`) held only `state.yaml` when I looked, which is consistent with
a panel still in flight — code-reviewer may be running concurrently at this same pin. I cannot
confirm coverage from my own remit either way; raising as a non-blocking confirmation request so the
orchestrator can check rather than either of us assuming.

## Prior UI-reviewer notes in this feature

Two earlier UI-reviewer passes exist in this feature's `notes/` (`review-harness-ui-reviewer-
2026-08-14-1.md`, `-2.md`) — not re-litigated here; this review re-took the file-set-content
measurement fresh at the current pin per this run's dispatch instruction, rather than inheriting
either prior result.
