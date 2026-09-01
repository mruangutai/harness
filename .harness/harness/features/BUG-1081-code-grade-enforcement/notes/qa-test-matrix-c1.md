# QA — test_matrix gate — BUG-1081-code-grade-enforcement — cycle 1

**VERDICT: PASS.** Both required kinds (`unit`, `integration`) satisfied; both suites green
(exit 0, 0 `^FAIL ` lines each). SC-01..SC-12 each have a named committed test/inspection.
No under-fixtured criterion found. One reachability finding, already closed by the diff itself
(`check_malformed_test_kinds`) — reported for the record, not gating.

## Phase 1 (pre-code, from BRIEF.md + plan.yaml only)

Expected before reading any implementation: (a) a unit-level test proving the shared
classification seam's bars (3/test, 4/prod) and fail>grade_2>pass precedence; (b) an
integration-level test driving the REAL `validate-digest.py --hook` path with a purpose-built
git repo, covering accept+reject for all four enum values with named mismatches; (c) explicit
fail-closed coverage for a broken canonical range (unresolvable default branch, no merge base,
missing/malformed test policy, syntax error); (d) proof that plan review still bypasses grading;
(e) proof that reviewer judgment (must_fix/severity) still overrides a clean mechanical grade;
(f) a doc/inspection check that the SKILL.md text and DECISIONS.md entry are literally true, not
just present. All six materialized in the actual suite (Phase 2 below) — no gap between what was
expected and what was built.

## Matrix resolution

| change_type | tasks | required (floor) | resolved |
|---|---|---|---|
| `cross_module` | T-01 | `unit`, `integration` (always) | both satisfied |
| `bugfix` | T-02 | `unit` (always) + `when: __bug_class__/match_bug_class` | `unit` satisfied; `__bug_class__` names no `test_kinds` entry in this project's `harness.json` — documented placeholder that never resolves (DEC-35/DEC-187; consistent with every prior feature's qa gate in this repo, e.g. FEAT-17/FEAT-25/FEAT-44) — correctly not fired |
| `docs` | T-03, T-04 | none | n/a by matrix; each covered anyway by its own inspection `verify:` |

Union across the diff: `{unit, integration}`. Both active, both run directly (not inferred from a
task-local `verify:` — G-04).

`component`, `ui`, `eval`, `typecheck`: `status: unresolved`, `cmd: null`. This diff touches no
UI, service API, database, or model behavior (pure Python CLI/gate/doc changes) — matches the
BRIEF's own `## Verification gaps` claim, confirmed by inspection of the four changed files.
Recorded as **not applicable**, not a soft-skip guess.

## Suite runs — exact results, exit status captured in a variable, `^FAIL ` counted

```
$ .agents/skills/harness/bin/run-unit-tests.sh --kind unit
exit=0   grep -c '^FAIL ' = 0
tail confirms real completion: "PASS test-gate-policy.py" (last of 31 UNIT_SCRIPTS)

$ .agents/skills/harness/bin/run-unit-tests.sh --kind integration
exit=0   grep -c '^FAIL ' = 0
tail confirms real completion: "PASS test-check-decision-anchors.py" (last of 27
INTEGRATION_SCRIPTS), includes "PASS test-code-grade-cli.py" and (from prior line) validate-digest
suite output
```

`test-code-grade.py` is registered in `UNIT_SCRIPTS` (run-unit-tests.sh:30); `test-code-grade-cli.py`
and `test-validate-digest.py` are registered in `INTEGRATION_SCRIPTS` (line 31) — confirmed by
reading the arrays directly, not inferred from the `detect` glob (P-14/G-03 class check). The
KIND-DRIFT cross-check (script lines 76–140) ran on both invocations and passed (script would exit 2
otherwise), so the two files agree.

## Kind states

| kind | state | evidence |
|---|---|---|
| unit | **satisfied** | `run-unit-tests.sh --kind unit`, exit 0, 0 FAIL, `test-code-grade.py` present and PASS |
| integration | **satisfied** | `run-unit-tests.sh --kind integration`, exit 0, 0 FAIL, `test-code-grade-cli.py` and `test-validate-digest.py` present and PASS |
| functional | excluded (DEC-187) — not evaluated |
| component/ui/eval/typecheck | **not applicable** — unresolved tooling, and the diff touches no surface any of them would cover |

`matrix_ok: true`.

## Test-first compliance, per task

- **T-01** (`receipt-harness-backend-dev-T-01-c1.md`, `-c2.md`): RED narrated in the receipts —
  `AttributeError: module 'code_grade' has no attribute 'classify'/'TestKindsError'` against the
  unmodified tree, then 16 named-reason failures in `test-code-grade-cli.py`. **I could not
  independently reproduce this RED run** (`cp`/scratch-mutation tooling is blocked for qa by
  `bash-write-guard`, and DEC-153 requires a disposable worktree I was not asked to create). I
  did independently confirm the claimed *end state* matches: `code_grade.py` has `classify`,
  `TestKindsError`, `_is_test_path`, `_blocks` exactly as described (bars 3/4, `fail`>`grade_2`>`pass`
  precedence read verbatim from `classify()`'s body), and the cycle-2 addition
  `test_rename_diff_paths` is committed (`test-code-grade-cli.py:291`) and wired into `main()`
  (line 350) so it actually runs under `--kind integration`. Named as unverified-by-me, not as a
  finding — the receipt's forensic method (md5 before/after, restore-and-confirm) is sound on its
  face.
- **T-02** (`receipt-harness-orchestrator-T-02.md`): RED block **independently confirmed committed
  verbatim** — `git show HEAD:.claude/skills/harness/bin/test-validate-digest.py` contains the
  exact "BUG-1081: the mechanical code-grade result is COMPUTED" section (line 2215) with the
  identical two pre-fix acceptances (blocking-function-accepted-as-pass, syntax-error-accepted) the
  receipt quotes. This is the strongest of the three — RED evidence lives in the shipped test file
  itself, not only in a receipt.
- **T-04** (`receipt-harness-documentor-T-04.md`): all three `V1`/`V2`/`V3` verify commands
  **re-run by me directly**, same result (exit 0 / empty diff / exit 0) as the receipt claims.
  `T-03`'s inspection command also re-run directly (exit 0).

No task's RED evidence is missing outright; T-01's is receipt-narrated and not independently
reproducible under my write constraints — flagged, not failing.

## Reachability / assertion-strength audit

- **`check_plan_review_never_grades`** — traced live, not vacuous. `_fresh_validator()` returns a
  freshly `importlib`-loaded module object; `validator.gated_set = lambda...` replaces the
  module-global name that `_classify_canonical_range` calls unqualified
  (`gated_set(root, base_oid, head_oid)`, `validate-digest.py:721`) — so the monkeypatch genuinely
  intercepts the real call site. `validate()` at line 1314 gates the whole enforcement block behind
  `not _is_plan_review(reviewed)` (line 1052/1314), confirmed by direct read — the plan branch really
  cannot reach `gated_set`. The test asserts BOTH that `calls` stays empty AND that the plan review
  still validates cleanly, so a validator wired to unconditionally refuse would not pass this check
  vacuously.
- **`test-code-grade-cli.py::test_rename_diff_paths`** — confirmed discriminating: T-01 c2's receipt
  shows RED (`expected ['src/moved.py'], got ['src/mover.py']`) with a hash-verified restore, and the
  test is committed and wired into `main()` (verified above). The pre-existing rename fixture in
  `test_diff_and_determinism` cannot see this class of bug because it changes file content alongside
  the `git mv`, dropping similarity below the rename threshold — a real, not incidental, gap the new
  fixture closes.
- **`check_unresolvable_default_branch` / `check_no_merge_base`** — both use **real** git repos (no
  origin remote at all; a genuine `--orphan` branch sharing no history), never a stub of
  `_default_branch_or_none`/`_merge_base_or_none`. Each iterates all four `("pass","fail","grade_2",
  "n_a")` values via `_assert_grade_refused`, which requires the refusal to name the specific
  cause-substring (`"default branch"` / `"no merge base"`) — not merely "an error occurred" — so a
  refusal for the wrong reason would not pass. `check_unresolvable_default_branch` additionally
  asserts the repair text (`"repair origin/HEAD"`). This reasoning is **not backed by my own
  mutation run** (blocked by `bash-write-guard`, no worktree provisioned for the purpose); T-02's
  own receipt covers an adjacent mutation (M4, "fall back to a digest-reachable base", 2 new
  failures) but does not name these two checks by ID. Labeled **reasoned, not measured** (O-03).
- **`check_malformed_test_kinds`** — genuinely closes the gap its own docstring names. Read directly:
  `_load_test_kinds` (validate-digest.py:686) validates only that `test_kinds` is a non-empty dict —
  it never inspects an individual kind's `"detect"` key — so `{"unit": {"status": "active"}}` (no
  `detect`) passes `_load_test_kinds` and reaches `classify()` in `code_grade.py`, which raises
  `TestKindsError` for exactly that shape (confirmed by reading `code_grade.py`'s `_is_test_path`
  requiring `kind["detect"]`). That exception is caught by `_classify_canonical_range`'s generic
  `except Exception` (validate-digest.py:728-730) — the same catch-all the T-02 receipt says a
  mutation (M2, `return "pass", None`) first reddened nothing against, before this fixture was added.
  I did not re-run M2 myself (write-guard blocks scratch mutation for qa); the reachability claim is
  confirmed by direct code trace, which is sufficient to establish the branch is live, not proof it
  reds on every possible bypass.

## SC-by-SC evidence table

| SC | Evidence (committed test/inspection) | Note |
|---|---|---|
| SC-01 | `check_hook_rejects_false_pass` (test-validate-digest.py:2397) — real `--hook`, exit 2 pre-fix-shaped false pass, exit 0 honest fail | |
| SC-02 | same function, second half: `code_grade='fail'` with `VERDICT: FAIL` accepted at exit 0 | |
| SC-03 | `check_mechanical_result_discrimination` (2367) over `GRADE_FIXTURES` (2359–2363): **all four** results `pass`/`fail`/`grade_2`/`n_a`, each with one wrong claim, each mismatch asserted to name the expected value | fully fixtured — not under-fixtured; `n_a` is present (`("na", ..., "n_a", "pass")`, easy to miss on a partial read |
| SC-04 | `check_committed_syntax_error` (2424) — exit 2, "does not parse" named, no Traceback | |
| SC-05 | `check_digest_base_cannot_move_result` (2443) | |
| SC-06 | `test-code-grade.py::check_classify_bars/_grade_two_is_reasoned/_precedence` (unit) for bars+precedence; the pre-existing (unmodified by this diff — confirmed via `git diff` context lines) `grade_2_reasons` non-empty check in `validate-digest.py:1323-1328` for the reason requirement | three sub-clauses, three independent assertions — none masked by aggregation |
| SC-07 | `check_plan_review_never_grades` (2579) — see reachability audit above | |
| SC-08 | `check_judgment_outranks_clean_grade` (2554) | |
| SC-09 | inspection of `.claude/skills/harness-code-review/SKILL.md` — re-run token check (exit 0) plus direct prose read (lines 64-90): states independence, `n_a` rule, deletion-is-pass, and that mismatches name the expected value, in real sentences, not just matching tokens | |
| SC-10 | `git show HEAD:test-validate-digest.py` — RED block independently confirmed committed verbatim (line 2215) | |
| SC-11 | `check_unresolvable_default_branch`, `check_no_merge_base`, `check_derived_base_range`'s degenerate case, `check_missing_test_kinds`, `check_malformed_test_kinds` — five checks for "unresolvable default branch, missing merge base, degenerate range" (three named clauses); each clause has its own dedicated fixture, not one aggregate | not under-fixtured; two extra availability checks (test_kinds) beyond the three literal clauses |
| SC-12 | inspection of `DECISIONS.md`/`DECISIONS-INDEX.md` via T-04's three verify commands, re-run directly by me (exit 0 each) | |

## Coverage gaps

None found against Phase 1 expectations or the BRIEF's own criteria.

## Open questions

- Q1 (non-blocking, inherited from `receipt-harness-documentor-T-04.md`): the only protection
  against a wrong-tree doc edit was a manual `git status` check in both trees — worth a harness-side
  guard, not this feature's scope.
- Q2 (non-blocking): I could not independently reproduce T-01's RED runs or run my own mutation
  probes against `check_unresolvable_default_branch`/`check_no_merge_base`/`check_malformed_test_kinds`,
  because `bash-write-guard` blocks qa from scratch-copying files outside the worktree and I was not
  dispatched to provision a disposable worktree for perturbation proofs (DEC-153). All three are
  backed by direct code-trace reasoning (confirmed live/reachable) plus, for T-01 and
  `check_malformed_test_kinds`, adjacent mutation evidence already in the devs' own receipts — but
  none of that is my own measured mutation run. Flagged per O-03/O-07, not gating.
</content>
