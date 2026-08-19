# Handoff — FEAT-27, validate → ship — written at 3cde944, seq-13

<!-- WRITTEN LATE, and that is the record: the second seam note this feature that I did not
     write at the seam. It records 3cde944 — the commit where the panel's and goal-check's
     artifacts landed and validate's exit predicate was satisfied — not the commit where it
     was typed. Not reconstructed: panel-validator and goalcheck-product are my own runs and
     I held the context. The ship phase has since completed and the feature is merged; that
     outcome is in STATE.md and feature.json, not here. -->

## Next

Close out, then brief. Ship-refresh is a SKIP with reason — `.harness/codebase/` does not exist, so
there is no map to intersect. Dispatch distillation to all three leads in ONE message so they run
cold and concurrently, then write `notes/ship-review-<runid>.md` from the digests on disk and render
it with `bin/render-brief.py`. Do not spawn a report round; every run already wrote a digest.

## Trust

- The panel PASSed with `severity_max: med` and `must_fix: []`, which is ADVISORY under `gates.review: advisory_unless_high` — `runs/panel-validator/digest.md`, and I re-derived the gate value at `harness.json` — verified-at 3cde944
- All eleven criteria are met, nine on measurements pm took itself rather than inherited — `runs/goalcheck-product/digest.md` `sc_status` — verified-at 3cde944
- I independently re-measured SC-02 (sixteen resolves, each returning its own agent, plus a `NOBODY` negative control) and SC-07 (15 craft + 6 repository files each named `OK`) — my own shell — verified-at 3cde944
- Both suites are green at the pin: `--kind unit` exit 0, `--kind integration` exit 0, zero `FAIL` lines, exit status captured in a variable not through a pipe — verified-at 3cde944
- Every commit after the pin `9b929de` touches feature-dir artifacts only, no source — `git diff --name-only 9b929de..HEAD -- .claude/ .harness/team-config.yaml .harness/README.md .harness/harness/docs/` returns empty — verified-at 3cde944
- Six assertions in this repo cannot redden and a seventh was refuted on evidence; all sit outside every SC's text — `runs/qa-final-validator/digest.md` — verified-at 3cde944
- `plan.yaml`'s approval block predates T-07 joining the task set — `plan.yaml` `approval:` — UNVERIFIED, operator only

## Dead ends

- Do not re-pin `review_sha` — the panel and goal-check both graded `9b929de` and nothing since touches source; re-pinning would claim a review that never happened — `git diff` over the source paths — verified-at 3cde944
- Do not re-run the panel or the goal-check — both PASSed and neither has an unresolved `must_fix` — `runs/panel-validator/digest.md`, `runs/goalcheck-product/digest.md` — verified-at 3cde944
- Do not commit Expertise output to this branch — outside every task's `files:` list except T-04's migration, and it repeats FEAT-25's B-18 — source: operator instruction at dispatch
- Do not fold ship-refresh and distillation into one lead prompt — hot routing corrupts a judgement that must be cold — source: playbook close-out, #80
- Do not run `check-state.sh` as a progress poll — ~500 GraphQL points per invocation — source: operator, FEAT-29's measurement

## Working set

- `.harness/harness/features/FEAT-27-expertise-repository-tier/feature.json` — the pin, the counters, the sixteen runs the briefing must cover
- `.harness/harness/features/FEAT-27-expertise-repository-tier/runs/panel-validator/digest.md` — seven findings, ranked, none blocking
- `.harness/harness/features/FEAT-27-expertise-repository-tier/runs/goalcheck-product/digest.md` — the eleven verdicts and their methods
- `.harness/harness/features/FEAT-27-expertise-repository-tier/runs/qa-final-validator/digest.md` — the census and the SC-02 coverage warning
- `.harness/harness/features/FEAT-27-expertise-repository-tier/notes/research-FEAT-27-e1-coverage-gaps.md` — pm's ruling on gaps outside the SCs
