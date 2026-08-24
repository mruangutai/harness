# QA gate — FEAT-26 pr-linkage-recorded — GATE-ONLY test-matrix re-run at `bad32441dfc0`

## Verdict: PASS with two coverage findings (not gating)

matrix_ok: true. `unit` and `integration` both required for `api` change type (T-01..T-04),
per the qa-classification-ruling — confirmed at plan level: T-01..T-04 are all `change_type: api`.
Both kinds ran green.

## Live claim registry — NOT `{}` (issue #741)

`.harness/.inflight-claims.json` holds three live claims (`harness-code-reviewer`,
`harness-qa`, `harness-security-reviewer`, all this worktree). Per #741,
`test-validate-digest.py`'s hook cases read this live registry and report false failures
while agents are in flight. **Excluded that one script from the integration run rather than
attribute its failures to this feature.** Its exclusion is an honest exception, not a silent
drop — 21 of 22 registered integration scripts ran.

## Per-kind results (Phase 2, against `bad32441dfc0`)

- **unit** — `run-unit-tests.sh --kind unit`: 19/19 scripts discovered and run, all green
  (rc=0). Includes `test-validate-feature-json.py` (T-01's file, 5/5 new cases:
  `accepted_source_issues_list_of_integers`, `rejected_source_issues_non_integer`,
  `rejected_source_issues_quoted_number`, `rejected_undeclared_sibling_of_source_issues`,
  `accepted_github_block_without_source_issues` — all `PASS`).
- **integration** — 21/22 registered scripts run (1 excluded, see above), all green.
  - `test-gh-sync.py` (slow: ~2.5 min real time, not hung — explains the earlier 2-minute
    Bash-tool timeout on the combined run): all named T-02/T-03/T-04 checks present and `ok`
    — `open records source_issues from plan.yaml`, `source_issues survives every save during
    a full open run`, `open on a plan with no source_issues records none and still succeeds`,
    `save_recorded refuses when feature.json is absent`, all 7 `record-pr` checks, all 4
    `closes` checks, plus `record-pr --pr abc exits non-zero with no traceback`. `ALL PASSED`.
  - `test-check-state.py`: all 6 named INV-28 checks present and `ok`.

No `misconfigured`/`BLOCKED` kind. No `not applicable` kind (both required kinds are `active`
with real `cmd`s).

## Phase 1 vs Phase 2 — no gap found

BRIEF SC-01..SC-11 map cleanly onto T-01..T-05's named checks (SC evidence table below); no
Phase-1-expected test is missing from the diff.

## SC evidence

| SC | Test |
|---|---|
| SC-01 | `test-gh-sync.py`: `record-pr writes the number when the branch has exactly one merged PR` |
| SC-02 | `test-gh-sync.py`: `record-pr leaves pr null when the branch has no merged PR` / `...two merged PRs` |
| SC-03 | `test-gh-sync.py`: `record-pr never overwrites a pr that is already an integer` |
| SC-04 | `test-gh-sync.py`: `source_issues survives every save during a full open run` |
| SC-05 | `test-validate-feature-json.py`: the 5 `case_*source_issues*` cases |
| SC-06 | `test-gh-sync.py`: the 4 `closes ...` cases |
| SC-07 | `test-check-state.py`: `INV-28 warns...` / `INV-28 is silent on a Done feature whose pr is an integer` |
| SC-08, SC-09, SC-10 | `verify: inspection` — no automated test claimed; not this gate's evidence to supply |
| SC-11 | `test-gh-sync.py`: `open on a plan with no source_issues records none and still succeeds` |

## Adequacy — the four questions

**1. `_record_pr` refusal paths — bound or happy-path only?**
All bound, by name, in `test-gh-sync.py`:
- zero merged PRs → `record-pr leaves pr null when the branch has no merged PR` (:1462)
- two merged PRs → `record-pr leaves pr null when the branch has two merged PRs` (:1475, uses
  the real ambiguous branch `feat/harness-native-foundation`)
- `pr` already recorded → `record-pr never overwrites a pr that is already an integer` (:1490),
  fake gh deliberately returns a *different* number (999 vs disk's 314) so a coincidental pass
  is impossible, and asserts no `pr list` call was even made
- `--pr` given **and differs** from a value gh would return — NOT directly bound as its own
  case. The `--pr` case (:1504) is on a feature whose `pr` is `None`, so it tests "supplied
  beats derived," not "supplied is rejected/ignored when a recorded int already differs from
  it." That specific cell (`--pr N` on a feature whose `pr` is already a *different* int) has
  no named test — the never-overwrite case and the `--pr`-writes case never combine. Given
  `_record_pr`'s existing-int check runs before `pr_arg` is even read (line 565 gates before
  562's guard fires first), this is very likely covered by the code's structure, but it is not
  independently asserted.
- `--pr` non-integer → `record-pr --pr abc exits non-zero with no traceback` (:1547)

**2. `gh-sync.py:597`** — confirmed unbound by measurement. That branch fires when `found`
has exactly one element but its `number` field is missing or not a plain int. Grepped every
`PR_LIST_JSON` value across all 7 record-pr cases (:1447/1462/1476/1490/1505/1521/1535) — every
single-element case supplies `{"number": <int>}`; none supplies a malformed element
(`{}`, `{"number": "abc"}`, `{"number": true}`). A mutant deleting the `isinstance(number, int)
and not isinstance(number, bool)` guard at 596 would pass the entire suite unchanged — nothing
exercises that shape.

**3. INV-28's four silence cases — can each go red?** Confirmed by live perturbation (not
reasoning alone): copied `check-state.sh` to a disposable scratch path, mutated INV-28's block
to always warn unconditionally (removed the `github.sync` gate, the `status == Done` check,
and the `pr`-is-int check), pointed `test-check-state.py` at the mutant via its own
`CHECK_STATE_BIN` env-var seam (no source edit, no worktree needed for this one — the seam
exists for exactly this), and reran. Result: 4/4 silence cases flipped to `FAIL` against the
always-warn mutant (`is silent on ... integer`, `... Abandoned`, `... not terminal`,
`... sync off`), while the two presence cases stayed sane (`warns` and `names each` also
flipped, confirming the block ran at all). None of the four is vacuous — each fixture tree is
non-empty and shaped exactly as the offending case, so a broken implementation is caught, not
passed by an empty tree. Restored: deleted the scratch copy and its fixture dir; `git status
--porcelain` on `check-state.sh` in the worktree confirms untouched.

**4. `pr: true`** — coverage finding, confirmed by grep. No case in `test-gh-sync.py` asserts
that a boolean `pr` is not read as a recorded PR number, even though `_record_pr` (gh-sync.py
:562) and INV-28 (check-state.sh :1078, with its own comment noting the exclusion is
"load-bearing") both carry an explicit `isinstance(existing, int) and not isinstance(existing,
bool)` guard. `test-check-state.py`'s `_inv28_fixture` helper never emits a `pr: true`
fixture either. A mutant dropping the bool exclusion in either file would pass both suites
unchanged.

## Coverage gaps (findings, not gating)

1. `--pr N` where `N` differs from an already-recorded integer `pr` — no independent test;
   inferred safe from code order but not measured directly.
2. `gh-sync.py:597` (malformed single-element `pr list` result) — unbound.
3. `pr: true` boolean-exclusion guard in both `_record_pr` and INV-28 — unbound in both files.

None of these three block the gate: matrix presence is satisfied (unit + integration both ran,
named checks exist for every required SC), and the ruling classification stands. They are
handed back as findings for a dev to close with new named cases, not authored here per the
GATE-ONLY, no-source-access instruction.

## Open questions

None blocking.
