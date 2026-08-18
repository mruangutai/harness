# Handoff — FEAT-24, ship cutover → ship continuation — written at 7a00255, seq-3

## Next

**Assume the lockout is live and check it first**: run any trivial `Write`. If it is refused with
`the fleet declaration does not load`, the operator has not yet deleted the `board:` block from
`.harness/factory/fleet.yaml`'s kaya entry — stop and ask for it, nothing else is possible. Once
writes work, discharge the three debts my session could not: add the `2026-08-18-5-eng` run entry to
`feature.json`, set `plan.yaml` T-02 to `done`, then run `gh-sync.py close-task T-02` in that order.
Then dispatch the T-02 continuation run to `harness-eng-lead` for the post-migration mutation proofs
(mutate the new `factory_config.py`, observe each named case redden, restore, verify byte-identical),
then T-03 and T-06, then T-04. T-04 must NOT be committed without T-05, which is the operator's.

## Trust

- T-01 `000934b`, T-08 `22814c7`, T-09 kaya PR #335 merged `692672d` — I re-ran all three verifies
  myself on disk rather than taking them on report: `T-01 GREEN`, `T-08 GREEN`, `T-09 GREEN` —
  verified-at 7a00255
- D-10's outage window is ZERO, not merely short: kaya's `master` declares its own board before
  anything removes the fleet copy — T-09's verify reads it remotely — verified-at 7a00255
- The cutover trap: `harness_boundary.py:263` (`resolve_fleet` first in `classify`), `:157-169`
  (`load_fleet` then `sys.exit(2)`), `factory_config.py:151-156` (board REQUIRED today), T-02 item 3
  (board REJECTED after), `fleet.yaml:26` (a board is there) — verified-at 7a00255
- `git add`/`git commit` SURVIVE the lockout while `Write`/`Edit` do not: `bash-write-guard.sh:375`
  records that `git` produces no findings, `classify` runs per finding at `:551` behind the
  `if not findings` exit at `:475` — verified-at 7a00255
- The main session is ungoverned and can cross the window: `check-domain.sh:271`,
  `_governed = bool(agent) and agent.startswith("harness-")` — verified-at 7a00255
- Q3 and Q4 of the earlier lists are CLOSED, not outstanding — a pm pass applied both before
  signature: `grep -c "nothing in this repository can enforce" plan.yaml` returns 0, and the
  replacements sit at `plan.yaml:246` and `:290` — verified-at 7a00255
- That the write LANDING the new loader is itself permitted (PreToolUse imports the pre-edit module)
  is **UNVERIFIED** — inferred from hook ordering. If wrong, the write is refused and nothing is
  half-done.
- Cycles 1 of 10, runs 7 recorded of 20 — `feature.json` — verified-at 7a00255

## Dead ends

- Do not try to `Write` state after T-02's commit lands — that is the whole reason this note and
  STATE.md were written BEFORE the dispatch — source: this session, route A step 1
- Do not edit `check-state.sh`, `check-domain.sh`, `bash-write-guard.sh` or `validate-digest.py`
  through a team run; T-05 is the operator's — source: DEC-174 carve-out
- Do not pull T-07 Part A items 4 and 5 forward; only item 1, the board deletion, unblocks the
  loader — source: notes/segment-02-ordering-decision.md, route A
- Do not re-raise D-10's `because` or D-06's reversibility cost — both applied pre-signature — source: above
- Do not touch `FEAT-25-claim-feature-root`, `FEAT-25-expertise-repository-tier`,
  `FEAT-26-pr-linkage-recorded`, `FEAT-27-expertise-repository-tier` — source: this dispatch
- Do not add `harness` to `fleet.yaml`; `test-no-distribution.py:160` must keep passing — verified-at ada8e99
- `review_sha` stays `none` until the build ends; FEAT-24's single `check-state.sh` violation is
  expected until then — source: INV-6

## Working set

- `.harness/harness/features/FEAT-24-config-responsibility-split/STATE.md`
- `.harness/harness/features/FEAT-24-config-responsibility-split/notes/segment-02-ordering-decision.md`
- `.harness/harness/features/FEAT-24-config-responsibility-split/plan.yaml`
- `.harness/harness/features/FEAT-24-config-responsibility-split/runs/2026-08-18-5-eng/digest.md`
- `.harness/harness/features/FEAT-24-config-responsibility-split/notes/ship-review-2026-08-18-ship-01.md`
