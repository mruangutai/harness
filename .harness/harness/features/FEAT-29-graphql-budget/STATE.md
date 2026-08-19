# STATE

## Current

- feature: FEAT-29-graphql-budget
- run: none in flight — `runs/2026-08-19-07-validator/` returned ESCALATE
- squad: none
- status: Building — the blocking qa gate reads `matrix_ok: false` on a question no squad can fix

All nine tasks are written. **Both suites are green**, measured by me at the pin: `--kind unit`
exit 0, 0 FAIL, 18 unit scripts all passing; `--kind integration` exit 0, 90 PASS / 0 FAIL. The
INV-26 fixture regression is repaired and 13 INV-26 cases execute again.

**The 164 → 172 "PASS" figure I have been citing is a counting convention, not a suite-native
number.** `run-unit-tests.sh:58-67` emits exactly one `PASS <script>` line per script — 18 for
`--kind unit` — and the rest of the matches come from individual scripts printing their own `PASS`
lines. A second measurer summing per-script totals got 806 on the same suite. **Only the delta is
load-bearing, and it held: +8, exactly the eight new checks.**

`review_sha` pinned at **`3fbfd0a`**, verified equal to the branch tip.

**Q2 is SETTLED by measurement, and it clears the feature's mutation evidence.** qa reported two of
its own members disagreeing about whether `check-domain.sh` permits mutating `factory_gh.py`.
`--resolve` returns `harness-backend-dev, harness-dev-ops` and **not** `harness-qa`. So the denied
member was correctly enforced and the other reached the file through Bash, which the hook cannot see
(DEC-85). Both were honest. **Run 06's three mutation proofs were performed by `harness-backend-dev`,
which IS granted, so they are authorised and admissible** — the doubt does not extend to them.

**THE MIRROR REMAINS FROZEN.** No `start-task`, no `close-task`, until T-07's after-measurement
lands. Seven positive-control lines depend on cards reading `Backlog`.

Three questions block progress and all three are the operator's — see `## Open Questions`. Once they
clear: SIMPLIFY → re-run suites → re-pin → panel → batch B (T-07 then T-09) → goal-check → close-out.

Budget: GraphQL 46 points spent all session; the window has since reset. **5 cycles of 10; 8 runs of
20.** Two runs bought no artifact (a premature close and a duplicate dispatch, both my error).

## Open Questions

- Q1 (blocking, operator): `matrix_ok: false` — integration reads `missing` for T-03. The gate
  resolves each required kind by whether a test covering *this change* exists in it, and all four
  files in `test_kinds.integration.detect` contain zero `gh_cost_log` references. But the signed
  artifacts already nominate unit: `BRIEF.md:83-90` gives SC-05 `evidence: unit`, re-signed in
  amendment 5, and not one `integration.detect` file appears anywhere in `plan.yaml`. Rule the
  criterion satisfied as signed, or amend T-03's `files:` to admit `test-gh-sync.py`.
- Q2 (settled, no longer blocking): see above. Recorded for the panel's benefit.
- Q3 (blocking, operator): a cycle grant. `_cost.returncode = r.returncode` at `factory_gh.py:162`
  is pinned by nothing — deleting it alone leaves `--kind unit` fully green, measured. SC-05
  explicitly requires a failing wrapped invocation be recorded *with its exit code*. Both files are
  inside T-03's `files:`; only the step's `max_cycles: 3` ceiling blocks the fix. The feature has 5
  of 10 cycles left.
- Q4 (non-blocking, harness defect): nothing serialises two leads' members against one checkout.
  `mutates_repo` is per-lead-DAG, so a re-dispatch over a live run put two members mutating the same
  three production files concurrently, leaving a probe unreverted for a window.
- Q5 (non-blocking, config defect, independent of this feature):
  `test_kinds.integration.detect` names 4 files while `INTEGRATION_SCRIPTS` runs 12, and
  `unit.detect` matches all 30 bin test files including every integration one. The gate's discovery
  over-reports unit and under-reports integration.
