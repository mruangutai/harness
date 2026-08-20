# FEAT-28 — second-pm audit of the drafted BRIEF and plan

**Written by the stray second `harness-pm` spawn** — the one recorded as `S-99-stray-spawn` in
`runs/2026-08-19-01-product/state.yaml`, dispatched with the literal prompt `placeholder`. The
sibling pm (`S-01-pm-plan`) is `in_flight` with no return collected and is actively writing
`BRIEF.md` and `plan.yaml` (`plan.yaml` 06:29:49, `BRIEF.md` 06:31:00, audit 06:31:07). **I wrote
neither file, deliberately** — the race is live per the step status, not merely suspected from
timestamps.

Verdict on the sibling's artifacts: **the design is sound and better than my own draft.** It caught
a fourth false claim I missed (`tests.yml:116` "M IS ASSERTED" is false — `plans` is extracted and
only echoed), and route A's rationale (no new bin file, so no `run-unit-tests.sh` edit, so no
collision with FEAT-27's in-flight edit to the adjacent array line) is measured and sound.
`check-plan-routes.py` on `plan.yaml` exits 0, three tasks OK; `yaml.safe_load` parses it;
`lanes.resolved_at: 8ad7d52` is substantively valid (`git diff --stat 8ad7d52 HEAD --
.harness/team-config.yaml` is empty).

**Four defects remain. The first makes SC-05 unmeetable as specified.**

## D1 — the phantom-citation resolver does not catch `case_25b9`. Measured.

T-01 item (f) specifies: collect `case_[0-9][0-9a-z_]*` from the raw text, truncate each to its
leading `case_NN`, and require `"def " + base_id` in some `bin/test-*.py`. The truncation exists so
`case_19a3b` resolves to `def case_19` — and it resolves the phantom too. Run at `de4b76a`:

```
case_19a3b -> case_19 resolved
case_25b9  -> case_25 resolved
```

Consequences, all three:

- **SC-05 cannot be met as written.** Its stated purpose — "so a phantom citation like `case_25b9`
  cannot survive" — is exactly what this resolver lets survive.
- **`case_26i`'s mutation proof is rigged.** It mutates `case_25a` to `case_99zz`, base `case_99`,
  no `def case_99`, so it reports. The mutant reddens while the real defect passes.
- Resolve against the **emitted assertion name**, not a truncated prefix: require the cited
  identifier to be a prefix of some `check("<name>"` literal in `bin/test-*.py`, or an exact `def`
  name. `case_19a3b` is a prefix of
  `check("case_19a3b_discovery_finds_the_live_plan_and_skips_the_shipped_one"`; `case_25b9` is a
  prefix of nothing.

**Correction to an earlier draft of this note:** I first recorded T-01's verify as red by
construction, on the assumption the resolver would fire on `case_25b9` before T-02 repairs it. It
does not fire, so T-01's verify is green on the pre-T-02 tree and **there is no ordering defect.**
The measurement above overturned my own finding; the earlier claim is struck, not softened.

## D2 — two verify conjuncts assert nothing. Measured.

- T-01: `... && git status --porcelain .github/workflows/tests.yml`. `git status --porcelain`
  **exits 0 whether the path is clean or dirty** — run against both a clean path
  (`.github/workflows/tests.yml`, rc=0) and a dirty one
  (`.harness/harness/features/FEAT-27-expertise-repository-tier/plan.yaml`, rc=0). SC-03 rests on
  this conjunct and it can never fail. Use
  `test -z "$(git status --porcelain .github/workflows/tests.yml)"`.
- T-03: `gen-decisions-index.py && git diff --stat <index>`. Same shape, plus the generator has
  already written the file by then, so the diff is empty by construction. Use the read-only form
  the generator's own docstring prescribes:
  `python3 .claude/skills/harness/bin/gen-decisions-index.py --stdout | diff - <index>`
  (verified: exits 0 on the current tree).

## D3 — T-02's verify is non-discriminating for three of its four sites

With D1 fixed the resolver covers SITE 3 (`case_25b9`). It still never matches `case 25` with a
space (SITE 1), the false "M IS ASSERTED" header (SITE 2), or "Nothing in the repository asserts
this step" (SITE 4). T-02 could leave three sites untouched and pass.

Fix: ban bare-number citations in the predicate — raw text matches no `\bcase[ _]?\d+\b` — and give
T-02 a verify that greps positively for each of the four replacement citations by name.

## D4 — four assertions route B had were dropped when the plan moved to route A

Port each into `ci_wiring_violations` as one table row. Not a reason to switch routes.

1. **`Unit suite` step present**, body contains `run-unit-tests.sh --kind unit`. This is #279's own
   headline surface — "the ONLY runner for eight of this project's success criteria" — and nothing
   this plan builds notices its deletion.
2. **`continue-on-error` absent or falsy on every step.** The silent vector: a step carrying it
   passes every substring check and greens the job regardless of the checker's exit code.
3. **Step-level `if:` absent** on each guarded step.
4. The bare-number citation ban from D3.

## D5 — REQ-02 names five behaviours; the case list mutates only four

REQ-02 enumerates five failure-forcing behaviours of the `Plan-route gate` step. `case_26b`–`26f`
mutate: the step's presence, the `|| rc=$?` capture, the missing-summary `exit 1`, the
`examined == 0` guard, and `exit "$rc"`. **The missing-`examined`-line branch
(`if [ -z "$examined" ]`) has no mutant case**, so one of the five behaviours the predicate checks
is never proven able to redden. Add `case_26j` for it. (Found independently by the sibling pm and
recorded in `observations/harness-pm.md`; reproduced here because observations are never injected.)

## Standing limits, unchanged by any of the above

- The `Integration suite` step carries the predicate into CI and cannot protect itself:
  `pull_request` runs the workflow from the PR's own ref. Correctly recorded as plan D-03 and in the
  brief's verification gaps.
- Nothing here executes a real GitHub Actions run. DEC-183 records the same limit for itself.
- This feature reverses DEC-183's "the step is unguarded, by decision … not pending, settled"
  clause. Amendment, not a DEC-188 strike, is right — the venue ruling and the M ruling stay true.
  The hand-written `::` text on the DEC-183 index row (line 201) says "nothing guards the step
  itself" and must change in the same task. **T-03's intent contradicts itself here**: it says
  "do not hand-edit the index", but `gen-decisions-index.py`'s own docstring states that everything
  right of ` :: ` on a row is hand-written and preserved verbatim across regeneration. Regenerating
  will therefore carry the false row text forward unchanged. T-03 must hand-edit that one row's
  `::` text and regenerate only the generated left-hand side.
