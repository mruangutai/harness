# QA — test_matrix gate re-run at pinned SHA 29b612e

## Tree check
`git rev-parse HEAD` = `29b612e398d6651964e9d4626ed8070c5ab7bd7d`, branch
`feat/FEAT-07-verify-teeth-batch-probe`. Correct tree confirmed before anything else ran.

## Matrix, per task (re-derived from PLAN, not taken on trust)
`grep -n "^  change_type:" PLAN.md` → T-01 `logic` (:494); T-02..T-10 all `docs`
(:634,:694,:739,:772,:801,:835,:868,:952,:1003).

`harness.json` `test_matrix`: `logic.always = ["unit"]` (verified via `json.load`), `docs.always = []`.

| Task | change_type | Required kinds |
|---|---|---|
| T-01 | logic | unit |
| T-02..T-10 (9 tasks) | docs | none |

## Diff scope
`git diff --stat main..29b612e`: 13 files, +671/-18 — matches. Files: `harness-dev-ops.md`,
`harness-qa.md`, `commands/harness.md`, `harness-digest-dev/SKILL.md`,
`harness-tdd-enforcement/SKILL.md`, `harness-verification-rules/SKILL.md`,
`harness-zero-micro-management/SKILL.md`, `harness/SKILL.md`, `test-validate-digest.py` (+257),
`validate-digest.py` (+161), `DECISIONS-INDEX.md`, `DECISIONS.md`, `SPEC.md`. Only
`validate-digest.py` + `test-validate-digest.py` are T-01's `logic` files; the remaining 11 are all
`.md` — no executable surface outside the two `logic` files (not verified as ownership per-task,
only that none is code).

## Kind: unit — T-01
- **Presence**: `.claude/skills/harness/bin/test-validate-digest.py` is in the diff itself (+257
  lines), not an unrelated pre-existing test. `grep` confirms named cases matching PLAN T-01 step
  (11)/(12) enumeration verbatim: `dev task_verify: fail + PASS is rejected` (:1110),
  `dev task: none with task_verify omitted is accepted` (:1155), `dev-ops task: none...` (:1157),
  `dev task: bogus is rejected` (:1174), `dev task: none + task_verify: fail is rejected as a
  contradiction` (:1180), `dev task: none + task_verify: n/a is accepted` (:1184), `qa matrix_ok:
  false + PASS is rejected` (:1208), `joint hint followability` (:1283) — this is the change
  exercising *this* diff, not a stand-in.
- **Ran**: `.claude/skills/harness/bin/run-unit-tests.sh` from repo root (required per PLAN T-01
  verify clause, issue #36 — script aborts elsewhere). Exit 0.
- **Result**: `test-validate-digest.py` block reports `57/57 CLI cases passed`, `14/14 hook cases
  passed`, `2/2 template cases passed`, plus the new joint-hint case, all `ok`, ending `ALL PASSED` /
  `PASS test-validate-digest.py`. No failing assertion, no load/import/collection error.
  **Counted, not recalled:** `git diff main..29b612e -- .../test-validate-digest.py | grep -c
  '^+case('` = **19** new cases added by this diff.
- **State: satisfied.**

## Kind: unit — docs tasks (T-02..T-10)
Matrix requires nothing (`docs.always = []`). No unit kind demanded; nothing to find missing.
**State: not applicable by matrix (docs → `[]`), not a gap.**

## Other kinds (functional, integration, component, ui, eval, typecheck)
Not required by either `logic` or `docs` in `test_matrix`. All have `cmd: null` in `harness.json`
(re-verified via `json.load`, unchanged from BRIEF's own `## Verification gaps` accounting).
**State: not applicable — soft skip, consistent with the pinned BRIEF's own accepted residue, not a
new finding.**

## Full suite
`run-unit-tests.sh` ran ALL project test scripts (test-validate-digest.py, test-gh-sync.py,
test-check-state.py, test-check-expertise.py, test-gen-decisions-index.py, test-bash-write-guard.py,
test-check-domain.py, test-render-brief.py, test-cost-report.py, test-harness-yaml.py,
test-harness-yaml-corpus.py, test-upgrade-config.py, test-team-catalog.py). All reported `PASS` /
`ALL PASSED`. Overall script exit 0. No load/import/collection errors anywhere in the run.

## matrix_ok
**true.** T-01 (`logic`) required `unit`; satisfied by named, passing, diff-specific tests. The nine
`docs` tasks required nothing; nothing is missing because nothing is required. No kind resolves to
`missing` or `misconfigured`.

## Coverage gaps
- **SC-06 is under-covered relative to its own stated scope.** BRIEF SC-06 asserts the honest-refusal
  shape is accepted "with `VERDICT: BLOCKED` (and with `VERDICT: FAIL`)… for both `dev` and
  `dev-ops`" (four combinations: {dev, dev-ops} x {BLOCKED, FAIL}). `grep -n 'dev-ops'
  test-validate-digest.py` and inspection of the new-case block (:1100-1240) show exactly ONE
  matching case: `dev task_verify: n/a + BLOCKED is the honest refusal, accepted` (:1132). No case
  asserts `dev-ops` + `task_verify: n/a` + `BLOCKED`/`FAIL` accepted, and no case asserts `dev` +
  `task_verify: n/a` + `VERDICT: FAIL` accepted. Three of the four combinations SC-06 names have no
  fixture. This does not fail the matrix — `unit` presence for T-01 is still satisfied by the cases
  that do exist — but pm citing SC-06 evidence should know only one quarter of the criterion is
  proven.
- Otherwise `[]` beyond what BRIEF's own `## Verification gaps` already discloses and accepts
  (SC-07..SC-12, SC-16 are `verify: inspection` with no runner on markdown rule surfaces; stated
  residue at BRIEF sign-off, not a new matrix gap).

## SC evidence pointers (for pm's goal-check — not a re-verdict)
SC-01..SC-05, SC-13..SC-15, SC-17, SC-18 (`verify: automated, unit`) — all traced to named cases in
`.claude/skills/harness/bin/test-validate-digest.py`, enumerated above and in PLAN T-01 steps
(9)-(12); all measured passing at `29b612e`. **SC-06 — partial:** only the `dev` + `BLOCKED` quarter
is evidenced (`test-validate-digest.py:1132`, case name "dev task_verify: n/a + BLOCKED is the
honest refusal, accepted"); the `dev-ops` half and the `FAIL` half are unevidenced (see coverage
gap above). SC-07..SC-12, SC-16 (`verify: inspection`) carry no automated evidence by design — the
matrix does not require it (`docs.always = []`) and this gate does not supply inspection judgments.

## Note on my own return contract
Per D-07/REQ-09/the widened fail gate landing in this same SHA: `matrix_ok: true` + `suite: pass` is
the honest state, so `VERDICT: PASS` is the legal spelling here. Had either come out false/fail, the
only legal returns would have been `FAIL` or `BLOCKED` — noted, not triggered.
