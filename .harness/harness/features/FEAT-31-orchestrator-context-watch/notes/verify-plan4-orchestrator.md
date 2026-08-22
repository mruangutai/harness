# Independent verification of round 3's premises — orchestrator, before the pm returned

All measurements taken in the **FEAT-31 worktree at 7299669** (C-7: every count names its
checkout). Taken DURING the pm's run and deliberately NOT fed into its dispatch, so its receipt
is a check on this one rather than a restatement of it.

## Every operator premise holds

| Premise | Source | Result |
|---|---|---|
| Eight `INTEGRATION_SCRIPTS` entries absent from `test_kinds.integration.detect` | C-2 / D-4 | **CONFIRMED, exactly 8 of 12** |
| Four files sit in both `unit.detect` and `integration.detect` | Q-B | **CONFIRMED, exactly 4** |
| `RE_HANDOFF` at `check-domain.sh:665` in this worktree (not `:706`) | C-6 | **CONFIRMED** |
| `SEAM_NOTES` at `check-state.sh:495` | C-6 | **CONFIRMED** |
| `tests.yml` runs both kinds as required steps (`:78`, `:84`) | C-1 | **CONFIRMED**, no `continue-on-error` |
| One loop both builds the required path AND shape-checks it | C-3 | **CONFIRMED structurally** |
| The three non-seam notes' `## Next` bodies hold 13, 6, 8 non-blank lines | C-5 | **CONFIRMED exactly** |
| Corpus is 69 notes here / 71 in main | C-7 | **CONFIRMED, 69 here** |
| `test-context-watch-cli.py` classifies as `unit`, not `integration` | F-1 | **CONFIRMED** — matches only `unit` via the catch-all `bin/test-*.py` |

The eight absent entries, enumerated: `test-validate-digest.py`, `test-check-expertise.py`,
`test-gen-decisions-index.py`, `test-bash-write-guard.py`, `test-check-domain.py`,
`test-harness-yaml.py`, `test-upgrade-config.py`, `test-merge-settings.py`. The four present:
`test-gh-sync.py`, `test-check-state.py`, `test-check-plan-routes.py`,
`test-factory-integration.py`.

Mechanism confirmed: the drift detector builds `ALL_SCRIPTS` from its own two bash arrays and
never opens `harness.json`, so the disagreement is invisible to every gate. That is D-4's whole
point.

## A-2's migration cost is ZERO across the WHOLE corpus, not just the three measured

The operator measured the 3 non-seam notes. The glob widens INV-17's reach to **all 69**, so all
69 are what must pass. Applying `check-state.sh`'s exact predicates —
`HANDOFF_HEADINGS = ["## next","## trust","## dead ends","## working set"]` matched as
`l.strip().lower()`, the 60-line cap, and T-10's proposed empty-`## Next` rule:

- **fails four headings: 0**
- **fails the 60-line cap: 0**
- **fails the empty-`## Next` rule: 0**

Nothing to migrate and no finding to raise. A-2's zero-cost claim is now asserted over the full
set the glob reaches.

## Two corrections to receipts in the answers file

1. **A-2 names FEAT-24's note as the one sitting exactly on 60. The true count is TEN.** Zero
   headroom on: FEAT-03 `handoff-plan.md`, FEAT-03 `handoff-validate.md`, FEAT-05
   `handoff-validate.md`, FEAT-08 `handoff-build.md`, FEAT-08 `handoff-validate.md`, FEAT-14
   `handoff-plan.md`, FEAT-16 `handoff-build.md`, FEAT-17 `handoff-plan.md`, FEAT-18
   `handoff-plan.md`, FEAT-24 `handoff-ship.md`. Consequence: any future edit adding one line to
   any of the ten turns INV-17 red. Not a blocker — a fragility to know about.
2. **`check-plan-routes.py:265` carries a caveat that is now false.** It reads "THE HONEST
   CAVEAT: `find .harness -name plan.yaml` returns ZERO. This budget has never been applied to a
   real file of the format it governs." There are **21 `plan.yaml` files** on disk here. The
   50-line per-task machine-field cap HAS been applied to real files. A stale measurement standing
   in enforcement-layer code, exactly what DEC-188 says nothing detects. Backlog-shaped.

## Discovery reaches the migrated layout

`check-plan-routes.py`'s `discover_plans()` globs `os.path.join(root, ".harness", "*",
"features")`, which does reach `.harness/harness/features/`. Criterion 3's second clause is
satisfiable; the gate is not dark on the post-FEAT-21 layout.

## C-4 edits SIGNED text, and that is the one thing the operator must see

`BRIEF.md`'s `## Approval` at 7299669 reads `status: approved`, `approved_by: operator`,
`date: 2026-08-21`. So C-4's minimal rewrite of SC-14 changes a criterion inside an **already
approved** artifact. The operator authorised it explicitly, and the stated mitigation — "the
operator must see the diff" — is therefore load-bearing rather than procedural. The baseline
clause being removed, captured from git before any edit: *"asserted by a test that fails before
INV-17's seam table learns the mid-phase stem"* — which is precisely the mechanism A-2 forbids,
so C-4's premise is verified at the byte level.

## The single-writer constraint was breached at the spawn level, with nil damage

`runs/plan4-product/state.yaml` records the product lead spawning a SECOND `harness-pm`
(`mis-spawn-noop`, "LEAD ERROR"). Verified independently at the time: `plan.yaml` was 41503 bytes,
mtime 06:16, and clean-tracked against 7299669 — the mis-spawn wrote nothing. **The constraint
held because the second pm declined to act, not because any mechanism stopped it.** Issue #628
needs a real interlock; prose discipline in a dispatch is demonstrably not one.
