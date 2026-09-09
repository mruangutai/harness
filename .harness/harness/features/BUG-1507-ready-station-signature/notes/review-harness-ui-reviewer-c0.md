# UI Review — BUG-1507-ready-station-signature — Mode B — cycle 0

## Verdict: PASS — no rendered UI surface in scope; advisory-only note on operator-facing text clarity

## Census (measured, not inferred)

`git -C <worktree> diff --stat 4b5dbb23 ac5e24e5` on the full range returns 21 files, but the bulk
(BRIEF.md, STATE.md, feature.json, plan.yaml, notes/*, observations/*) is this feature's own harness
bookkeeping, not code under review. Restricting to the five files named in the dispatch as THE DIFF
UNDER REVIEW:

```
git diff --stat 4b5dbb23 ac5e24e5 -- \
  .claude/commands/harness-plan.md \
  .claude/skills/harness/references/github-mirror.md \
  .claude/skills/harness/SKILL.md \
  .claude/skills/harness/bin/gh-sync.py \
  tests/integration/test-station-argument-spelling.py
```
→ exactly 5 files, 175 insertions(+), 6 deletions(-). Confirmed identical to the dispatch's file list
(no elided sixth file, no drift).

- `.claude/commands/harness-plan.md` — 2 lines changed (`Plan`→`plan`, `Ready`→`ready` in two CLI
  invocation examples). Markdown prose, no HTML/CSS/JS/JSX/TSX/Vue/Svelte.
- `.claude/skills/harness/references/github-mirror.md` — 4 lines changed: one case fix (`Review`→
  `review`), the Building row of the who-writes-each-station table rewritten to name two writers.
  Markdown prose.
- `.claude/skills/harness/SKILL.md` — 4 lines inserted, new instruction to the orchestrator persona.
  Markdown prose.
- `.claude/skills/harness/bin/gh-sync.py` — 16 lines inserted, entirely inside `cmd_status`'s Python
  docstring (confirmed by hunk context: all additions land between existing docstring lines, zero
  code-body changes). Source-code documentation, not user-facing at runtime — it is read by a
  developer opening the file, never rendered to an operator or into any UI.
- `tests/integration/test-station-argument-spelling.py` — new pytest module. Test code, no rendered
  surface; its assertions are about string literals in the doc files above, not about anything a
  human sees at runtime beyond pass/fail.

**DESIGN.md check:** `.harness/harness/features/BUG-1507-ready-station-signature/` contains no
`DESIGN.md` (confirmed by directory listing: BRIEF.md, STATE.md, feature.json, feature.json.lock,
notes/, observations/, plan.yaml, plan.yaml.lock, runs/ — no design contract). Consistent with there
being no rendered surface for this bugfix to specify.

**Extension census:** zero `.html/.css/.scss/.tsx/.jsx/.vue/.svelte/.less` files anywhere in the
21-file range (verified by the file list above and the full `git diff --stat` in the raw dispatch
context — no such extension appears in either the 5-file code set or the 16-file bookkeeping set).

## Scope decision

`in_scope: false` for formal Mode B design-contract review — none of the five files renders to a
screen, and no `DESIGN.md` exists for this feature to audit against. This is BUG-1507's own stated
shape: fixing a case-sensitivity mismatch between documented CLI examples/table cells and the actual
lowercase argument spellings the tools accept, plus a docstring clarification and a spelling-witness
test. Nothing here is a UI change by any definition this role's rubric uses.

**The one surface a reader might argue for — operator-facing instruction text — I DO consider**, per
the dispatch's explicit instruction, restricted strictly to: is the edited wording UNAMBIGUOUS to the
human or agent following it? Not spacing, not tone, not completeness beyond that.

- `harness-plan.md`: the two case fixes (`Plan`→`plan`, `Ready`→`ready`) sit in unchanged sentences;
  no new ambiguity — they now match the actual accepted argument spelling (which T-05's test verifies
  against `factory_config`).
- `github-mirror.md` line 55-56 case fix: same shape, no ambiguity introduced.
- `github-mirror.md` Building row — **the one place two writers are named for one label** — is clear
  on read. It states, in order: (1) the task CARDS are written by `gh-sync.py start-task`, and
  explicitly adds "it writes the TASK's station, never the feature's"; (2) the FEATURE's own station
  is written separately, in `plan.yaml`, by `plan-merge.py set-feature-station --station building`,
  naming who runs it (the orchestrator) and when (when the eng segment starts dispatching build
  work). Each writer's target object (task card vs. feature's plan.yaml field) and its exclusion
  ("never the feature's") are stated in the same clause as the writer — a reader does not have to
  infer which writer owns which. No ambiguity found.
- `SKILL.md` new segment-1 instruction: names the exact command
  (`plan-merge.py set-feature-station --station building`), the timing ("as the segment starts
  dispatching — not after it finishes"), and the reason ("without this write nothing advances the
  feature"). Consistent with the github-mirror.md row above — no cross-document contradiction found.

## Findings

None. No must_fix items. Severity: n/a (scoped out of formal Mode B on the rendered-surface test);
the advisory clarity check on operator-facing text above found the wording unambiguous with no
concrete failure scenario to report.

## Not evaluated

Anything beyond literal clarity-as-read of the three prose edits (accuracy of the underlying
station-write logic itself, whether `cmd_status`'s docstring correctly describes `gh-sync.py`'s
runtime behavior, spec fidelity of T-05's test) — those are code-reviewer / QA lens, not this role's.
