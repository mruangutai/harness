# Handoff — FEAT-40 plan phase → signature

## Next

**One blocking plan edit, then the operator signs.** T-11 pins the accepted red-suite set to FIVE
script names (`plan.yaml:1044` `want=`, restated `:1006`). The true set is **SEVEN**: add
`test-hooks-install.py` and `test-post-merge-sweep.py` everywhere that literal appears — T-11's
verify and the pinned-set clause in T-04, T-05, T-06, T-07, T-08, which all now depend on T-11
(`:285, :499, :605, :651, :756`). Each compares the runner's actual `FAIL test-` lines to that set by
string equality, so until it lands **T-11 and all five dependents cannot pass**. pm's edit, not the
main session's; mechanical, fully specified, no re-derivation.

Then: main session adds the `approval:` block (no agent may write it), settles the three blocking
questions, signs BRIEF and plan together.

## Trust

- 11 tasks, 15 SCs, `source_issues: [842]`, every task `main-session-direct` with a reason — read at 09:19.
- Mandated ordering edge encoded: T-06 depends on T-02 ("prove the sweep fires") — `plan.yaml:605`.
- `check-plan-routes.py` exits 0, 0 violations, 7 informational DEVIATIONs — I ran it.
- **Suite red at base: EIGHT scripts** — validate-feature-json, inject-expertise, factory-config,
  layout-migration, branch-create-gate, board-lifecycle, hooks-install, post-merge-sweep. **All eight
  reproduced in the MAIN CLONE**, per script, not inferred. `--kind unit`: 18 PASS / 6 FAIL / exit 1.
- `#728` has THIRTEEN children `#818`–`#830`, all closed, all at `Review` — `gh api .../sub_issues`.
  Under the new rule all are OPEN, so acceptance exercises the open-child skip, not the trivial path.
- `Auto-close issue` detected PRESENT on board 3 — `board_lifecycle.py audit`, no `WORKFLOW:` class
  (2 LABEL, 13 STATION, 1 STATUS). **Name-only detection**, so T-01's live probe still settles it.
- Constraint 5's env marker cannot work — hook gets only `tool_input.command`
  (`branch-create-gate.sh:49`); `gh-sync.py` reaches `gh` via `subprocess.run` (`:147`).
- `core.hooksPath` = `.../.git/hooks`, samples only; tracked `post-merge` is mode 755. Only the
  config is missing. `.agents/...` and `.claude/...` bin dirs are the **same inode** — one file.
- **UNVERIFIED — the feature rests on it:** that a `Done` write closes the issue. Probe `#807` cannot
  settle it; its close reads `actor=mruangutai state_reason=None`, the signature a hand close and a
  keyword close both produce (`#840`: PR `#841` merged 14:45:01Z, closed 14:45:02Z). T-01 measures it.

## Dead ends

- **The actor/reason discriminator is useless** — hand, keyword and workflow closes are identical.
  The hand-close finding rests on its other leg, verified: PR `#837` has no `Closes` lines and merged
  13:55:59Z, while the sub-issues closed 00:44 and 04:00, in two bursts, before it.
- **The red suite is not a worktree or FEAT-40 artifact** — ruled out per script in the main clone. I
  first blamed my own `HARNESS_PROJECT_DIR` leaking into `test-hooks-install`'s scratch clone; that
  was plausible and wrong.
- **No `check-state.sh` invariant for closed-but-not-`Done`** — `board_lifecycle.py audit` already
  detects it (13 STATION findings = FEAT-34's stranded cards). Missing a runner, not a detector.
- **Do not scope `visual-designer`/`ui-reviewer` out.** I did; the lead reversed me correctly. Four of
  nine adopted findings came from them, including that the gate refusal routed *finished* work to
  `abandon`.
- **No `SendMessage` tool exists here** — a running lead cannot be corrected mid-flight.

## Working set

- `.harness/harness/features/FEAT-40-harness-writes-done/plan.yaml` (T-11 `:1030`, `want=` `:1044`)
- `.harness/harness/features/FEAT-40-harness-writes-done/BRIEF.md`
- `.harness/harness/features/FEAT-40-harness-writes-done/runs/2026-08-25-01-product/digest.md`
- `.harness/harness/features/FEAT-40-harness-writes-done/observations/harness-orchestrator.md`
- `.harness/notes/grilling-board-done-and-parent-close-2026-08-25.md` (untracked; commit with feature)
