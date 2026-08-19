# Handoff — FEAT-24-config-responsibility-split, plan → ship — written at ada8e99, seq-1

## Next

Take the operator's signature on `BRIEF.md` and `plan.yaml` (both `pending`), then start the ship
phase at **T-01**. Two operator calls ride the signature and change task text if answered "yes":
D-10's `because` still says the merge-before-T-07 ordering is unenforceable, which T-07's own
verify at `plan.yaml:1117-1121` now refutes; and D-06 carries no reversibility cost line (a sixth
station key later is N cross-repository pull requests). Both are decision edits, forbidden to the
squad. **T-09 opens a `mruangutai/kaya-ai` issue and needs an operator merge — start it early;
it is the only human-latency task and it is now `depends_on: []`.**

## Trust

- FEAT-24's plan passes `check-plan-routes.py` with zero violations of its own — the run's single
  `VIOLATION T-04: 52 machine-field lines` belongs to a different, concurrently-planned feature
  (its block carries a `.harness/team-config.yaml` T-01 and an expertise-file T-04; FEAT-24's T-04
  prints `OK`) — `python3 .claude/skills/harness/bin/check-plan-routes.py` — verified-at ada8e99
- `plan.yaml` `safe_load`s clean: 10 tasks, 10 decisions, `approval.status: pending`; `BRIEF.md`
  `## Approval` is `status: pending` at `:156-158` — verified-at ada8e99
- pm's measurements were taken at `ada8e99`, which **is** HEAD — `git log --oneline -1`. The
  earlier "which SHA" question is closed, not merely labelled — verified-at ada8e99
- T-05, T-07, T-08, T-09 are `execution_mode: main-session-direct` and must be executed by hand;
  T-05 is `check-state.sh`, a DEC-174 carve-out — `plan.yaml`, route-checker output — verified-at ada8e99
- **T-04 and T-05 must land in ONE commit.** `check-state.sh` is a single python heredoc from
  `:24` to `:1343`, so T-04's `derive_station` arity change makes it exit 1 with every invariant
  unreported until T-05 lands — `plan.yaml:733-751`, `check-state.sh:24,1180,1343,636` — verified-at ada8e99
- kaya's config is readable with no clone: `gh api repos/mruangutai/kaya-ai/contents/.harness/harness.json`
  returns it; its stale keys nest under `github.*` and include `project_number`, which #493 never
  names — verified-at ada8e99
- The record correction owed by run 2 is settled here because it turns on mtimes: the
  `runs/2026-08-18-2-product/digest.md` account blaming the eng segment's collation for the lost
  T-06 `_note` finding is **wrong**. The dev-ops receipt carrying it was written 06:59; the eng
  digest's first write was 06:57 and could not contain it; its current copy (07:01) carries it as
  F-1 (`grep -c "790-792"` → 2). The eng lead promoted it correctly. **I dropped it, by dispatching
  from a digest whose run had not returned.** pm's "lost to a renumbering" account is wrong for the
  same reason — `ls -la` on those three paths — verified-at ada8e99

## Dead ends

- Do not re-open placement, `D-02`, `D-03`, `D-04`, `D-06` or `D-07` — the operator's 2026-08-18
  ruling on #493 and the plan's own decisions; three squads flagged only how they are specified — source: #493 comment
- Do not split the config consolidation from `load_board`'s silent-`None` removal — `D-01`,
  #350's "any consolidation inherits the silent one unless it is fixed in the same change" — source: #350
- Do not add `harness` to `fleet.yaml`; `test-no-distribution.py:160`
  `case3_absence_harness_is_not_a_fleet_member` must keep passing — verified-at ada8e99
- Do not dispatch or grade from a run digest whose run has not returned — it cost this phase one
  lost finding and two false attributions — source: this phase, Trust §6
- Do not re-verify SC-04, SC-07, SC-10, SC-11 wording against their verifies; they had a dedicated
  pass and each now names one assertion per item — source: runs/2026-08-18-2-product/digest.md

## Working set

- `.harness/harness/features/FEAT-24-config-responsibility-split/plan.yaml`
- `.harness/harness/features/FEAT-24-config-responsibility-split/BRIEF.md`
- `.harness/harness/features/FEAT-24-config-responsibility-split/runs/2026-08-18-2-eng/digest.md`
- `.harness/harness/features/FEAT-24-config-responsibility-split/runs/2026-08-18-3-product/digest.md`
- `.harness/harness/features/FEAT-24-config-responsibility-split/notes/review-harness-ui-reviewer-2026-08-18-prebuild.md`
