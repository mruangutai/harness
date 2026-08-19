# Handoff — FEAT-27, build → validate — written at 252fa72, seq-9

<!-- WRITTEN LATE, and that is the record: I crossed this seam myself and did not write the
     note at the time, so INV-17 reported it missing once status reached Review. Unlike
     handoff-plan.md this is NOT reconstructed from another agent's artifacts — I held the
     context. It is written as of the seam commit 252fa72 (all seven tasks committed, qa
     green, nothing yet pinned for the panel), because that is the moment it records. The
     validate phase has since completed; its outcome is in STATE.md, not here. -->

## Next

Re-pin `review_sha` at the branch tip, then dispatch the review panel (`review.yaml`, validator
squad) and pm's goal-check over SC-01..SC-11 (`BRIEF.md ## Success Criteria`) — concurrently, since
they are different squads and both read-only. The pin must move first: `feature.json` still carries
`2117a46` here, seven tasks behind, and a panel run against it grades a tree the work is absent
from.

## Trust

- All seven tasks are committed and each closed its own sub-issue after its `plan.yaml` status was set to `done` — `feature.json` `runs:`, `git log b4659cd..252fa72` — verified-at 252fa72
- The blocking `test_matrix` gate PASSed for the whole feature, `matrix_ok: true` — `runs/qa-final-validator/digest.md` — verified-at 252fa72
- Both suites are green: `--kind unit` exit 0 / 137 PASS, `--kind integration` exit 0 / 90 PASS, zero `FAIL` lines — I ran both myself with exit status captured in a variable — verified-at 252fa72
- SIMPLIFY ran as four independent read-only angles and applied NOTHING, so the tree is unchanged by it and the pin is not invalidated — `runs/simplify-eng/digest.md` — verified-at 252fa72
- Six assertions in this repo cannot redden, and one handed-down seventh was refuted on evidence — `runs/qa-final-validator/digest.md` `adequacy_notes` — verified-at 252fa72
- T-07's `case13` is mutation-proven: 18/19 against a guard-removed copy, `case13` the sole FAIL, and `inject-expertise.sh` byte-identical afterwards — I checked the restore with `git diff` — verified-at 252fa72
- `plan.yaml`'s approval block predates T-07 joining the task set; the artifact cannot evidence its own amendment — `plan.yaml` `approval:` — UNVERIFIED, operator only

## Dead ends

- Do not re-run SIMPLIFY — it returned an empty apply by design, and re-running it after the pin would move the tip and invalidate the panel's verdict — `runs/simplify-eng/digest.md` — verified-at 252fa72
- Do not treat the six could-not-fail assertions as `must_fix` — every one sits outside every SC's text, and pm already ruled that class neither a delivery gap nor a blocker — `notes/research-FEAT-27-e1-coverage-gaps.md` — verified-at 252fa72
- Do not edit `DECISIONS.md` or `DECISIONS-INDEX.md` to strike DEC-27 — both carry another flow's uncommitted DEC-174 amendment and editing them collides with live work — `git status --porcelain` — verified-at 252fa72
- Do not commit Expertise output to this branch — it falls outside every task's `files:` list except T-04's migration, and repeats FEAT-25's B-18 — source: operator instruction at dispatch
- Do not run `check-state.sh` as a progress poll — INV-26 reads every board card at ~500 GraphQL points per invocation — source: operator, FEAT-29's measurement

## Working set

- `.harness/harness/features/FEAT-27-expertise-repository-tier/feature.json` — the pin, the counters, the run list
- `.harness/harness/features/FEAT-27-expertise-repository-tier/BRIEF.md` — `## Success Criteria`, what the goal-check binds
- `.harness/harness/features/FEAT-27-expertise-repository-tier/runs/qa-final-validator/digest.md` — the blocking gate and the census
- `.harness/harness/features/FEAT-27-expertise-repository-tier/runs/simplify-eng/digest.md` — the last build step's findings, none applied
- `.harness/harness/features/FEAT-27-expertise-repository-tier/notes/research-FEAT-27-e1-coverage-gaps.md` — pm's ruling on coverage gaps outside the SCs
