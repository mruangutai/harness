# QA gate — BUG-1303 review-c5 (pinned e2c800f1, GATE-ONLY confirmation of the two panel must_fix)

## VERDICT: PASS — both remedies confirmed closed at the new pin; matrix still holds

`<base>` resolved: `git -C <worktree> merge-base main e2c800f1` = **`63404ef06cd798c6d933b52336bf73de7b248028`**
— **unchanged** from cycle 4's `63404ef0`. Confirms the accumulated diff window did not shift.

## MF-1 (DECISIONS-INDEX.md DEC-217 row) — CONFIRMED closed

`e2c800f1`'s own diff changes exactly one line: the DEC-217 row's tag bracket
`[tests,qa,state]` → `[tests,docs,digest,plan]`, ruling text after ` :: ` byte-identical (matches
dispatch claim). Ran the idempotence check myself:

```
env -u HARNESS_AGENT_TYPE python3 .agents/skills/harness/bin/gen-decisions-index.py --stdout \
  | diff -q - .harness/harness/docs/DECISIONS-INDEX.md
```
→ **silent, exit 0**. The cycle-4 FAIL (`test_committed_index_matches_a_fresh_regeneration`) is closed.

## MF-2 (`_derive_plan_mode_code_grade`) — CONFIRMED closed, and mutation-proven at this pin

Read the new function (`test-validate-digest.py` diff in `e2c800f1`): it probes
`validator._pending_plan_review_error` across every member of `sorted(validator.CODE_GRADE_VALUES)`,
keeps the single member not rejected with a `"code_grade must be"` error, and fails loud
(`derive_error`, a named `(False, ...)` result line) on zero or >1 qualifying members or a raised
exception — never a silent default. `_reviewer_plan_mode_results` now builds its regex from that
derived member; the literal `n_a` is gone from the check (grepped the diff, confirmed).

**Perturbation proof** (disposable worktree, DEC-153): `git worktree add
.claude/worktrees/qa-c5-perturb-1303 e2c800f1` (absolute path, main-worktree guard requires it).
Mutated line 418 `if not any("code_grade must be" in error for error in errors)` → `if any(...)`
(inverts the selection: keeps the *rejected* members instead of the accepted one). Ran
`tests/integration/test-validate-digest.py` in the perturbed worktree:
`1 FAILING`, exit 1, named line `FAIL [documented contract] plan-mode code_grade derivation from
CODE_GRADE_VALUES failed: expected exactly one qualifying member of CODE_GRADE_VALUES, found
['fail', 'grade_2', 'pass']`. Restored (`git checkout --`), confirmed clean, worktree removed
(`git worktree remove`, no `--force` needed — confirms nothing left dirty by the mutation).
**This answers the adequacy question directly: yes, a test — this same
`_reviewer_plan_mode_results`/`_derive_plan_mode_code_grade` path inside
`tests/integration/test-validate-digest.py` — goes RED if the derivation silently produces the
wrong member (or fails to converge on exactly one).** The DEC-217 index-row regression class is
separately covered by the standing `test-gen-decisions-index.py::test_committed_index_matches_a_fresh_regeneration`
(part of the 46-file integration run below, green at this pin, and independently confirmed via the
direct `--stdout | diff` above).

## Change_type and DEC-217 predicates — evaluated over `<base>..e2c800f1`'s full diff (40 files)

`change_type` resolution (read `plan.yaml` directly): T-01/T-02/T-03 = `bugfix`; T-04 = `docs`
(`docs.always: []`, contributes nothing). Floor = bugfix's `when` legs from the worktree's actual
`.harness/harness.json` (confirmed by direct read of the **worktree** copy — the main-repo copy at
`/Users/molchairuangutai/GitHub/harness/.harness/harness.json` is a **different, stale** commit and
must never be substituted for the worktree's; caught this on a first pass and re-read the correct
path):

```
"bugfix": { "always": [], "when": [
  {"kind":"unit","if":"touches_runtime_code"},
  {"kind":"integration","if":"fix_confined_to_tests_and_contract_docs"},
  {"kind":"__bug_class__","if":"match_bug_class"} ]}
```

Non-`.harness/` files in the full 40-file diff (everything else is `.md` or under `.harness/` or
`tests/**`, all excluded by the predicates' own text): `.claude/agents/harness-code-reviewer.md`
(*.md), `.omp/agents/harness-code-reviewer.md` (*.md), `.claude/skills/harness-code-review/SKILL.md`
(*.md), `tests/integration/test-validate-digest.py` (tests/**), `tests/unit/test-config-shape-matrix.py`
(tests/**), **`.claude/skills/harness/templates/harness.json`** — not `*.md`, not `tests/**`, not
under `.harness/`.

- **`touches_runtime_code`** — verbatim: "the bugfix diff modifies at least one file that is not
  under `tests/**`, is not a `*.md` documentation or contract file, and is not under `.harness/`":
  **TRUE**, solely because of `.claude/skills/harness/templates/harness.json` (a JSON *template*
  file, not "runtime code" in a colloquial sense — this is the formal-vs-colloquial trap the
  dispatch warns about, and the literal path-based text fires TRUE regardless). → requires **unit**.
- **`fix_confined_to_tests_and_contract_docs`** — verbatim: "every non-`.harness` change is either
  a `*.md` documentation or contract file or lives under `tests/**`": **FALSE** — same file breaks it.
- **`match_bug_class`**: unresolvable placeholder, no bug-class taxonomy entry fires for any diff
  today (repo Expertise G-08 already records this) — not applicable, unchanged by this feature.

**Required kind: `unit`.** Identical to cycle 4's finding — this diff window has not changed on this
axis, base and predicate evaluation both hold. The prior cycle's untraced-commit open question
(`e014ede3`, the mechanism that installs DEC-217 itself, bundled by the merge-base window rather
than any T-01..T-04 task) still applies unchanged; not re-litigated here since e2c800f1 does not
touch that file.

## Required-kind resolution and evidence (re-run at e2c800f1, `env -u HARNESS_AGENT_TYPE` before each)

| kind | state | cmd | result |
|---|---|---|---|
| unit | satisfied | `python3 tests/unit/test-config-shape-matrix.py` | rc=0, `19/19 cases passed` |
| unit | satisfied | `.agents/skills/harness/bin/run-unit-tests.sh --kind unit` | rc=0, 0 `^FAIL ` lines, 27 files, 2.12s wall |
| integration | satisfied | `python3 tests/integration/test-validate-digest.py` | rc=0, 0 `^FAIL ` lines, `ALL PASSED.`, 24s |
| integration (SC-06 regression class) | satisfied | `.agents/skills/harness/bin/run-unit-tests.sh --kind integration` | rc=0, 0 `^FAIL ` lines, 46 files, 80.44s wall |

## Contract figures — agreement / DISAGREEMENT with orchestrator's cited measurements

- `test-validate-digest.py`: orchestrator cited exit 0, zero `^FAIL `, `ALL PASSED.`, ~19s. **I got
  exit 0, zero `^FAIL `, `ALL PASSED.`, but 24s** (rc captured via `rc=$?` immediately, never read
  off a trailing line) — **AGREEMENT on verdict, mild DISAGREEMENT on wall time** (24s vs ~19s;
  within plausible machine-load variance, not a correctness signal, but flagged per instruction to
  report any disagreement loudly rather than silently rounding).
- `test-config-shape-matrix.py`: orchestrator cited 19/19. **I got 19/19.** AGREEMENT.
- `run-unit-tests.sh --kind integration`: orchestrator cited exit 0, zero `^FAIL `, 46 files, 60.9s.
  **I got exit 0 (captured via `rc=$?` immediately), zero `^FAIL `, 46 files — AGREEMENT on verdict
  and file count, DISAGREEMENT on wall time (80.44s vs 60.9s cited)**. Slowest scripts this run:
  `test-check-state.py` 78.14s, `test-gh-sync.py` 59.00s, `test-check-domain.py` 58.78s — consistent
  with a loaded pool run, not evidence of a regression (no new `^FAIL`, no file-count drift).
- `gen-decisions-index.py --stdout | diff -q` (not in the three named commands but load-bearing for
  MF-1): silent, exit 0 — matches contract.
- `check-state.sh`: ran it (rc=0) — matches contract; output is advisory `note` lines only (INV-17,
  INV-23, INV-28 across unrelated features), no error-level lines, consistent with a healthy state.

## Adequacy statement

Both remedies are covered by tests that would go RED on the defect they close:
- **MF-1**: `test-gen-decisions-index.py::test_committed_index_matches_a_fresh_regeneration`
  (standing, part of the 46-file integration bucket, confirmed green) — this is the exact test that
  caught the original staleness at cycle 4 and would catch any future regression of any
  DECISIONS-INDEX.md row, including DEC-217's.
- **MF-2**: the same-file mutation proof above demonstrates `_reviewer_plan_mode_results` /
  `_derive_plan_mode_code_grade` goes RED (`1 FAILING`, named line) when the derivation logic is
  broken to select a wrong/ambiguous member. **A green matrix over an untested remedy is not what
  shipped here** — both remedies now carry a red-capable guard, MF-1 via a pre-existing standing
  test and MF-2 via new code proven red-capable at this pin by direct mutation.

No coverage gap found in the two remedies specifically. The two carried-forward findings from
cycle 4 — the untraced `e014ede3` commit (Q1) and the DEC-212 `touches_config_shape`/`config`
change_type never being applied to `test_matrix.bugfix`'s own structural-nesting edit (a config-shape
change with no `change_type: config` task routing it to `integration`) — are unchanged by this
commit and are re-flagged, not re-litigated, below.

## DIGEST

```yaml
VERDICT: PASS
DIGEST:
  headline: Both panel must_fix remedies (MF-1 DECISIONS-INDEX.md regen, MF-2 CODE_GRADE_VALUES-derived code_grade) are confirmed closed at e2c800f1 with red-capable coverage — MF-1 via the standing test-gen-decisions-index.py idempotence guard, MF-2 via a fresh mutation proof in a disposable worktree — and the test_matrix gate still holds over the whole base..e2c800f1 range.
  suite: pass
  failures: 0
  matrix_ok: true
  base_resolved: 63404ef06cd798c6d933b52336bf73de7b248028
  change_type: bugfix (T-01/T-02/T-03); docs (T-04, contributes nothing)
  predicates:
    - { name: touches_runtime_code, result: true, deciding_path: ".claude/skills/harness/templates/harness.json", note: "formal path-based text fires TRUE though the file is a JSON template, not colloquial runtime code" }
    - { name: fix_confined_to_tests_and_contract_docs, result: false, deciding_path: ".claude/skills/harness/templates/harness.json" }
    - { name: match_bug_class, result: "n/a (unresolvable placeholder)", deciding_path: none }
  coverage_gaps: []
  kinds:
    - { kind: unit, state: satisfied, cmd: "python3 tests/unit/test-config-shape-matrix.py", named_tests: 19 }
    - { kind: integration, state: satisfied, cmd: "python3 tests/integration/test-validate-digest.py", named_tests: 1 }
    - { kind: integration, state: satisfied, cmd: ".agents/skills/harness/bin/run-unit-tests.sh --kind integration", named_tests: 46 }
  exit_statuses:
    - { cmd: "python3 tests/integration/test-validate-digest.py", rc: 0, fail_lines: 0, wall_s: 24, verdict_agreement: true, timing_agreement: false }
    - { cmd: "python3 tests/unit/test-config-shape-matrix.py", rc: 0, cases: "19/19", agreement: true }
    - { cmd: "run-unit-tests.sh --kind integration", rc: 0, fail_lines: 0, files: 46, wall_s: 80.44, verdict_agreement: true, timing_agreement: false }
  sc_evidence:
    - { id: SC-03, test: "tests/integration/test-validate-digest.py::_derive_plan_mode_code_grade — no longer hardcodes n_a; mutation-proven red-capable this cycle" }
    - { id: SC-06, test: "tests/integration/test-gen-decisions-index.py::test_committed_index_matches_a_fresh_regeneration — green, DEC-217 row now idempotent" }
  adequacy:
    mf1_red_capable_test: "tests/integration/test-gen-decisions-index.py::test_committed_index_matches_a_fresh_regeneration (standing, confirmed green + independently re-derived)"
    mf2_red_capable_test: "tests/integration/test-validate-digest.py::_reviewer_plan_mode_results (via _derive_plan_mode_code_grade) — mutation-proven RED in disposable worktree qa-c5-perturb-1303 (removed after restore)"
  open_questions:
    - { id: Q1, question: "Carried from c4, unchanged: e014ede3 (harness.json/templates/harness.json bugfix+config predicate edit, DEC-217's own DECISIONS.md entry, test-config-shape-matrix.py) is untraced to any BUG-1303 task. Should it be attributed to a task, or is bundling infrastructure commits into a feature's reviewed diff via the merge-base/review_sha window intentional and out of scope for this feature's own gate?", blocking: false }
    - { id: Q2, question: "Carried from c4, unchanged: test_matrix.bugfix's own container-shape edit (always:[unit] -> always:[],when:[...]) is squarely DEC-212's touches_config_shape example (structural nesting change to a config a gate script reads), yet no task declares change_type: config, so DEC-212's integration-requiring leg never fires via plan.yaml's mechanical routing for this specific edit. Only the unit-kind test-config-shape-matrix.py covers it. Is this an accepted gap or should a config-typed task be retrofitted?", blocking: false }
  files_touched: ["/Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-1303-plan-code-review-digest/.harness/harness/features/BUG-1303-plan-code-review-digest/notes/review-harness-qa-c5.md"]
  expertise_update: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-1303-plan-code-review-digest/.harness/harness/features/BUG-1303-plan-code-review-digest/notes/review-harness-qa-c5.md
```
