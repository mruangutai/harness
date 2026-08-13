# Handoff — FEAT-16-factory-per-repo-board, validate → ship — written at 2e3b7bc, seq-2

## Next

**The operator runs SC-06's UAT**, then takes the ship decision. Protocol is `BRIEF.md ##
Constraints`: create a throwaway kaya-ai issue, leave it unlabelled/open/unassigned, add it to board
2 at `Ready`, run `factory_claim`, read `Status` back off the board and confirm `Building`; clean up
by deleting `refs/heads/factory/issue-N`, removing `factory:claimed` and closing the issue. Stop
after claim — do NOT continue to `factory_land`, which would open a PR against kaya's `master`.
No agent work is outstanding. On the operator's acceptance: close-out is ONE turn, two concurrent
dispatches — ship-refresh and distillation — then the CEO briefing. Not before: those fire after the
SCs pass, and SC-06 gates that on the operator.

## Trust

- 12 of 13 SCs met at `2e3b7bc`, each re-run by pm under its own declared method —
  `notes/uat-goalcheck-c0.md` — verified-at 2e3b7bc
- qa gate `matrix_ok: true`, unit exit 0, integration exit 0 — `notes/qa-c0.md` — verified-at 2e3b7bc
- Panel `severity_max: med`, `must_fix: []`, below the `advisory_unless_high` bar so no cycle owed —
  `notes/review-harness-*.md` — verified-at 2e3b7bc
- `review_sha` `ec195ec` CONTAINS all eleven tasks plus both post-plan fixes; later commits are
  bookkeeping and reviewer artifacts only — `feature.json` — verified-at 2e3b7bc
- **SC-10 holds on intent and false-positives on its letter.** `a29ad06..HEAD` returns all four
  carve-out scripts (FEAT-17's mainline work; `a29ad06` IS an ancestor); `a7c429c..ec195ec` returns
  empty. I ran both — verified-at 2e3b7bc
- **SC-13's rationale is falsified**: `factory_claim.py:293` is the sole `no work available` site and
  is aggregate, after the loop, so its named mutant kills C1 too. Coverage is real and
  mutation-proved; only the justification is wrong — `notes/qa-c0.md` — verified-at 2e3b7bc
- Five criteria (SC-03, SC-06, SC-07, SC-10, SC-12) are correct today and pinned by NOTHING. A
  station rename or reorder on board 2 or 3 breaks the feature's promise silently — verified-at 2e3b7bc
- **The first code review's findings survive only in a GITIGNORED run digest**
  (`runs/2026-08-12-02-validator/digest.md`, `.gitignore:7`), because a redundant re-dispatch
  overwrote its artifact. They are restated in STATE.md and in my return — verified-at 2e3b7bc

## Dead ends

- **Do not fix the P5 de-dup test here.** It is `med`, `must_fix` is empty, and test code landing now
  lands AFTER the pin — post-panel churn that evades review is worse than a named backlog row. It
  closes only with a fixture that fails pre-change, never a rewrite — panel digest — verified-at 2e3b7bc
- **Do not edit `BRIEF.md` or `plan.yaml`.** Both signed; the two defects above are the operator's to
  amend or wave through — verified-at 2e3b7bc
- **`gh-sync.py open` is blocked by the permission classifier**, not the environment. Never a gate;
  raise it, do not retry blind — observed this run — verified-at 2e3b7bc
- **Do not delete `notes/review-harness-code-reviewer-c0-ui-scope.md`.** It belongs to no panel step
  but CORRECTS its sibling's file count (32 stated, 38 actual) — verified-at 2e3b7bc
- Never re-add `mruangutai/harness` to `repos:`; the four DEC-174 carve-out scripts stay untouchable
  — `fleet.yaml` comment block, SC-10 — verified-at 2e3b7bc

## Working set

- `.harness/features/FEAT-16-factory-per-repo-board/STATE.md` — the full current picture
- `.harness/features/FEAT-16-factory-per-repo-board/notes/uat-goalcheck-c0.md` — the per-SC table
- `.harness/features/FEAT-16-factory-per-repo-board/BRIEF.md` — `## Constraints` holds the UAT protocol
- `.harness/features/FEAT-16-factory-per-repo-board/notes/qa-c0.md` — the gate and its three mutants
- `.harness/features/FEAT-16-factory-per-repo-board/feature.json` — 11 runs, 4 cycles, the pin
