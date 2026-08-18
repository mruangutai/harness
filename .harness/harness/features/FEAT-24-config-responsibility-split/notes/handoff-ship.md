# Handoff — FEAT-24, ship build segment → ship cutover segment — written at 22814c7, seq-2

## Next

Read the operator's ruling on `notes/segment-02-ordering-decision.md` (options A/B/C for the T-02
cutover) and confirm T-09 has merged before acting. Under **A**, in this order: write `STATE.md`,
`feature.json` and this note describing the post-T-02 state BEFORE dispatching, because a governed
agent cannot `Write` once the window opens; dispatch T-02 alone to `harness-eng-lead` with the
member's tests and receipt written before its FINAL write, which is
`.claude/skills/harness/bin/factory_config.py`; commit on its return (commits survive the window) and
return to the operator for the `fleet.yaml` deletion — T-07 Part A item 1 only. Then a continuation
run for T-02's post-migration mutation proofs, then T-03, T-06, T-04.

## Trust

- T-01 and T-08 are committed and independently re-verified by me on disk, not taken on report:
  `000934b`, `22814c7`; `T-01 GREEN`, `T-08 GREEN` — verified-at 22814c7
- The cutover trap is real and I re-read every link myself, not just the lead's account:
  `harness_boundary.py:263` (`resolve_fleet` first in `classify`), `:157-169` (`load_fleet` then
  `sys.exit(2)`), `factory_config.py:151-156` (board REQUIRED today), T-02 item 3 (board REJECTED
  after), `fleet.yaml:26` (a board is there) — verified-at 22814c7
- The main session is ungoverned and can cross the window: `check-domain.sh:271`
  `_governed = bool(agent) and agent.startswith("harness-")`, and the domain phase is gated on it
  at `:310-332` — verified-at 22814c7
- T-09 has NOT merged: kaya's `master` still carries `project_number`, `project_id`, `status_field`
  and `in_progress_option` — `gh api repos/mruangutai/kaya-ai/contents/.harness/harness.json?ref=master`
  — verified-at 22814c7
- `git add`/`git commit` SURVIVE the lockout while `Write`/`Edit` do not: `bash-write-guard.sh:375`
  records that `git` produces no findings, and `classify` runs per finding at `:551` — verified-at 202cbc5
- That the write LANDING the new loader is itself permitted (PreToolUse imports the pre-edit module)
  is **UNVERIFIED** — inferred from hook ordering. Probing it would lock the prober out. If wrong,
  the write is refused and nothing is half-done.
- `plan.yaml` now matches what ran: T-01/T-08 `done`, T-02/T-03/T-04/T-06 back to `pending`, and
  their four board cards returned to `Backlog` with `board-station.py` — verified-at 202cbc5
- Cycles 1 of 10 (zero send-backs this run), runs 7 of 20 — `feature.json` — verified-at 22814c7

## Dead ends

- Do not dispatch T-02, T-03, T-06 or T-04 before the fleet/loader question is settled — the run is
  refused at exit 2 and the tree is left half-migrated — source: runs/2026-08-18-4-eng/digest.md
- Do not "write `factory_config.py` last" as a rescue on its own: T-02's post-migration mutate and
  restore cycle is itself a write and is refused — source: same digest
- Do not edit `check-state.sh`, `check-domain.sh`, `bash-write-guard.sh` or `validate-digest.py`
  through a team run — source: DEC-174 carve-out
- Do not touch `FEAT-25-claim-feature-root`, `FEAT-25-expertise-repository-tier`,
  `FEAT-26-pr-linkage-recorded`, `FEAT-27-expertise-repository-tier` — six of `check-state.sh`'s
  seven violations are theirs — source: this feature's dispatch
- Do not add `harness` to `fleet.yaml`; `test-no-distribution.py:160` must keep passing — verified-at ada8e99
- Do not re-open placement, D-01, D-02, D-03, D-04, D-06, D-07 — source: #493 comment, 2026-08-18
- `review_sha` stays `none` until the build ends; the FEAT-24 violation in `check-state.sh` is
  expected until then — source: INV-6

## Working set

- `.harness/harness/features/FEAT-24-config-responsibility-split/notes/segment-02-ordering-decision.md`
- `.harness/harness/features/FEAT-24-config-responsibility-split/notes/segment-01-main-session.md`
- `.harness/harness/features/FEAT-24-config-responsibility-split/runs/2026-08-18-4-eng/digest.md`
- `.harness/harness/features/FEAT-24-config-responsibility-split/plan.yaml`
- `.harness/harness/features/FEAT-24-config-responsibility-split/STATE.md`
