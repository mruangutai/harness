# QA test_matrix gate — BUG-1305-run-state-clobber (cycle 1)

**VERDICT: PASS.** Both suites measured green, every live task verify replayed clean, every
redproof section credible, both trust probes fired as designed, and every automated SC is
MET with a named test and assertion. HEAD `dee707e9` (worktree started at `c569d8a9`; T-08's
note landed as commit `dee707e9` — the dispatch's premise that it was uncommitted did not
hold at measurement time; `git status --porcelain` is otherwise clean, see below).

## 1. Matrix floor

Diff: 42 files, +5216/-179 (`git diff --stat origin/main...HEAD`). Live (non-abandoned) tasks
and their plan-declared `change_type`: T-01 `logic`, T-03 `logic` → `always: [unit]`. T-02,
T-05, T-06, T-09 `bugfix` → `when: unit if touches_runtime_code` fires (all four rewrite
`check-domain.sh`/`check-state.sh`/`bash-write-guard.sh`/`harness_boundary.py`/
`validate-digest.py`); `fix_confined_to_tests_and_contract_docs` does NOT fire (production
shell/py is touched, not tests-only), so `integration` is not matrix-obligated for `bugfix`
by that clause; `__bug_class__` is a repo-known unresolvable placeholder (no bug-class entry
fires — repo Expertise G-08). T-08, T-11 `docs` → `always: []`.
**Matrix-only floor: `unit`.** I ADD `integration` as a floor the diff plainly warrants: every
bugfix task's own files list and verify block requires `tests/integration/*.py`, and the
BRIEF's own Constraints section mandates the full integration suite before signing off REQ-07.
Both kinds resolved **satisfied** (below); no kind is missing, not-applicable, locally-run, or
misconfigured.

## 2. Suites — measured this run

| kind | cmd | files | `^FAIL ` lines | exit |
|---|---|---|---|---|
| unit | `env -u HARNESS_AGENT_TYPE .agents/skills/harness/bin/run-unit-tests.sh --kind unit` | 28 | 0 | 0 |
| integration | `env -u HARNESS_AGENT_TYPE .agents/skills/harness/bin/run-unit-tests.sh --kind integration` | 46 | 0 | 0 |

Runner's own exit captured into a variable before any pipe; `grep -c '^FAIL '` run over the
full captured output, not `tail`. Matches the main session's claim (28/0, 46/0) — independently
reproduced, not accepted on report.

## 3. Per-task verify (verbatim from plan.yaml, byte-checked against the dispatch strings — all match)

| task | exit | notes |
|---|---|---|
| T-01 | 0 | 28/28 unit cases pass |
| T-02 | 0 | boundary/domain/state/bash-guard all green |
| T-03 | 0 | includes new INV-36 case |
| T-05 | 0 | validate-digest full pass |
| T-06 | 0 | check-domain full pass, guard-comment greps satisfied |
| T-09 | 0 | check-domain full pass, `run_uid` present in harness-team/SKILL.md |
| T-11 | 0 | both grep lines present in probe note |
| T-08 | 0 (**INFORMATIONAL**) | note headings present; 6 suites re-run clean. Attributed to T-08 being in-flight per dispatch, though at measurement time the note was already committed at HEAD — contrary to the dispatch's premise; reported as observed, not treated as a defect of this feature |

T-04, T-07, T-10, T-12 correctly abandoned (`status: abandoned`), not run.

## 4. Redproof credibility (`notes/redproof-BUG-1305.md`)

All six claimed headings present: `## T-01`, `## SC-04`, `## SC-01`, `## SC-10`, `## SC-02`,
`## SC-01-identity`, `## SC-05` (T-09's `baseline_sha: 592e88d…` line present and matches the
required `^baseline_sha: [0-9a-f]{7,40}$` shape). Every section is **credible**: each shows a
*named* case failing for a reason that is the behavior under test (e.g. SC-01 shows
`4/15 BUG-1305 marker cases passed` with named FAILs for witness/refusal cases, not an
import/collection error; SC-01-identity shows `6/9` with the three new refusal cases red and
the untouched cases already green, plus an explicit note that the precedence case exits 2 on
*both* trees because the pre-existing Issue 1124 branch answers first — exactly the deferral
proof REQ-01 requires, not a blanket "everything was red" overclaim). No section is vacuous.

## 5. Grading automated SCs

| SC | verdict | test / assertion |
|---|---|---|
| SC-01 | MET | `test-check-domain.py::run_bug1305_identity_cases` + `run_bug1305_marker_cases`: (a) witness-only refusal — `run_bug1305_marker_cases` "foreign first Write/Edit refused by witness"; (b)/(c) modal collision — `_bug1305_identity_refusal_cases` "modal collision Write/Edit omitting uid", "different minted uid"; (d) both recovering-owner forms — `_bug1305_identity_allow_cases` "absent"/"zero-byte" cases exit 0; (e) resumed owner — "DEC-154 resumed owner…S2" exit 0; (f) both precedence halves — `run_bug1305_identity_cases` "run_id disagreement keeps Issue 1124 precedence" + `run_bug1305_marker_cases` "witness outranks legacy run_id ladder". Red-proof pins (a)/(b)/(c)/(f) at redproof `## SC-01`/`## SC-01-identity`. |
| SC-02 | MET | `test-check-state.py::case_bug1305_run_identity_invariant` — reports the disagreeing fixture, silent on the agreeing one; red-proofed at `## SC-02` (pinned pre-change checker only rejected `run_uid` as an unknown key, never reported the witness disagreement). |
| SC-04 | MET | `test-validate-digest.py::run_bug1305_artifact_resolution_cases` — refuses the no-`digest.md` fixture at exit 2 naming the run directory and "missing"; compliant fixture unaffected. Red-proofed at `## SC-04` (old exit 0 fail-open). |
| SC-05 | MET | `test-check-domain.py::run_bug1305_digest_repair_cases` — append-Edit repair allowed, cross-run replacement still refused; red-proofed at `## SC-05` (old insertion case lacked the append-route remedy line). |
| SC-09 | MET | `test-check-state.py` — witness-absent silence, witness-with-no-uid-checkpoint silence, unreadable-witness report, seed-field-disagreement report are all present in `case_bug1305_run_identity_invariant`'s fixture set (verified live in this run's suite pass, all four paths exercised without a FAIL); regression-delta records the control-plane-root run at exit 0 with no INV-36 finding. |
| SC-10 | MET | `test-check-domain.py::run_bug1305_marker_cases` — "POST mints uid and matching witness", "second POST is byte stable", "POST preserves supplied uid bytes" all pass; red-proofed at `## SC-10` (pre-change: 0 minted). |
| SC-13 | MET | `test-check-domain.py::run_bug1305_marker_cases` (Write/Edit route denials of the witness, sibling state.yaml/digest.md unaffected) + `test-bash-write-guard.py` "overwriting"/"removing the write-once identity witness is refused" (Bash route). All four route refusals present; scoping (state.yaml/digest.md unaffected) asserted. |

SC-03, SC-06, SC-11 read `verify: inspection` in the BRIEF as stated (confirmed directly, not
trusted from the parenthetical) — out of this gate's automated scope; SC-07 also reads
`verify: inspection` (confirmed) and is graded via T-08's note, not a standalone automated
test. No criterion whose line reads `automated` was found ungraded.

## 6. Probes — driven directly, in `$TMPDIR`, never in a real `runs/` tree, no guard edited

**(a) Refusal probe.** Fixture: fresh `$TMPDIR` root, `.harness/harness/features/F/runs/r1/state.yaml`
carrying `run_id: A, run_uid: U1`, witness carrying `run_uid: U1`; incoming Write payload
carries `run_id: A` (same seed fields) but `run_uid: U2`.
`echo <payload> | check-domain.sh` (env `CLAUDE_PROJECT_DIR`/`HARNESS_PROJECT_DIR` = fixture root)
→ **exit 2**: `state.yaml run identity (Issue 1305). the incoming checkpoint belongs to run_uid
'U2', a different run than existing run_uid 'U1'. Write this cycle's state into a run directory
of its own.` Refused as required.

**(b) Permission probe**, same hook, four fixtures: ordinary same-session upsert (exit 0),
later-session resume same `run_uid` different `session_id` (exit 0), rewrite over a ZEROED
prior with witness present (exit 0), rewrite over an ABSENT prior with witness present (exit
0). All four permitted as required. Full JSON of both probes and exact commands captured
during this run; probe script and its `$TMPDIR` fixtures were removed after use.

## 7. Tree state

`git -C <wt> status --porcelain` (final check, after cleanup of my own scratch): shows two
untracked receipt files NOT created by me —
`notes/receipt-harness-backend-dev-simplify-reuse-c1.md` and
`notes/receipt-harness-dev-ops-simplify-efficiency-c1.md` — evidently written by a concurrent
sibling simplify-pass dispatch running in the same worktree. I created and removed my own
scratch (`/tmp/qa_probe_bug1305.py`, its `$TMPDIR` fixtures, and suite-log tempfiles); none of
my scratch remains and I wrote no file under this worktree except this artifact.

## Open questions

- None blocking. The T-08/regression-delta uncommitted-vs-committed discrepancy in the
  dispatch's framing is noted above as observed fact, not escalated — it does not change any
  verdict.
