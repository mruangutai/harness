# QA gate — BUG-1304-worktree-relative-path-guard — cycle 2, pinned `c5869301`

**Verdict: PASS.** All required test_matrix kinds ran green at the pin, no discovered-file
drop, and the panel's load-bearing claim — the 10/12 pre-change-assertion count survived the
ABC-driven splits — is CONFIRMED by runtime measurement at both pins, not the textual grep
the panel warned against.

## 1. Change type / matrix

Diff `af5ddd7a..c5869301` touches `bash-write-guard.sh`, `harness_boundary.py`, and three
`tests/{integration,unit}/*.py` files. Every live plan task is `change_type: logic`
(plan.yaml:692,831,944,1106,1160,1333,1503,1542 — one `docs` at :1397, one `scaffolding` at
:1652, neither touched by this diff). `logic` → `always: [unit]` (harness.json:157-161) — the
matrix floor is unit only.

I add **integration** above the floor: the diff's own changed files are
`tests/integration/test-bash-write-guard.py` and `tests/integration/test-check-domain.py`,
squarely inside `test_kinds.integration.detect` (`tests/integration/**`). A diff that rewrites
integration tests cannot be graded without running integration.

`matrix_ok: true` — both required kinds ran and passed; no kind was null/misconfigured.

| kind | required by | cmd | exit |
|---|---|---|---|
| unit | matrix floor (`logic`→always) | `run-unit-tests.sh --kind unit` | 0 |
| integration | added (diff touches `tests/integration/**`) | `run-unit-tests.sh --kind integration` | 0 |

## 2. Six suites at the pin (env -u HARNESS_AGENT_TYPE)

| suite | cmd | exit | detail |
|---|---|---|---|
| check-domain | `python3 tests/integration/test-check-domain.py` | 0 | all `[bug1304]` cases PASS |
| bash-write-guard | `python3 tests/integration/test-bash-write-guard.py` | 0 | all `[bug1304]` cases PASS |
| harness-boundary | `python3 tests/unit/test-harness-boundary.py` | 0 | ALL PASS |
| inflight-registry | `python3 tests/integration/test-inflight-registry.py` | 0 | **147/147** checks passed |
| dispatch-guard | `python3 tests/integration/test-dispatch-guard.py` | 0 | **48/48** cases passed |
| `run-unit-tests.sh --kind all` | (wraps all suites) | 0 | **0** `^FAIL ` lines; **73 files** discovered |

Discovered-file count: unit pool reported 27 files, integration pool 46 files, `--kind all`
pool 73 files (27+46). Matches the pre-build baseline of 73 exactly — **no drop**.

## 3. The adequacy question — runtime assertion count, both pins

Measured by running each suite directly and counting the PASS/FAIL lines the shared helper
itself prints (`"<name> is allowed by the frozen pre-change {hook,guard}"`), i.e. counting
executions, not call-site text:

```
grep -c "is allowed by the frozen pre-change hook"  <check-domain output>
grep -c "is allowed by the frozen pre-change guard" <bash-write-guard output>
```

| pin | test-check-domain.py | test-bash-write-guard.py |
|---|---|---|
| `af5ddd7a` (measured in a disposable detached worktree at `.claude/worktrees/qa-bug1304-af5ddd7a`, removed clean after) | 10 | 12 |
| `c5869301` (this worktree, HEAD unmoved) | 10 | 12 |

**CONFIRMED**: the runtime count of pre-change assertions executed by
`bug1304_assert_pre_change_allows` is unchanged at 10 and 12 across the ABC-driven split. The
split hoisted call sites into shared helpers invoked more than once, which is exactly why the
textual grep dropped (10→8, 12→9) while the runtime count did not move. I did not use the
textual call-site grep for this measurement, per the dispatch's instruction.

Both `af5ddd7a` and `c5869301` runs exited 0 with no `FAIL` lines in either file at either pin —
the helper's body (harness_boundary.py's split `claim_worktrees`, plus the split test
mega-functions) still runs the full 10/12 case sets; nothing was dropped or weakened by the
split.

## 4. Advisory — T-03/T-05 `verify:` blocks now read red on a *textual* grep

T-03's and T-05's `verify:` clauses grep source text for `bug1304_assert_pre_change_allows(`
call sites and assert `-ge 10` / `-ge 12`. Post-split the textual counts are 8 and 9
respectively (call sites hoisted into shared helpers invoked multiple times), so those verify
commands would now read red. This is **advisory only, not gating** — the runtime evidence in
§3 shows the actual assertion counts executed are unchanged at 10/12 in both files at both
pins. If this panel wants T-03/T-05's `verify:` text kept meaningful going forward, the fix is
to point the grep at the runtime output convention (`is allowed by the frozen pre-change
{hook,guard}` line count) rather than the call-site literal — but that is a plan/verify-text
edit, out of scope for a gate-only, author-nothing dispatch.

## Gate-only discipline

No source, test, fixture, or plan file was written or edited. One disposable git worktree was
created under `.claude/worktrees/` (guard-compliant path) to measure the `af5ddd7a` baseline
without moving this worktree's HEAD, and was removed cleanly (non-forced; tree was clean) before
this note was written. HEAD of `.claude/worktrees/harness/BUG-1304-worktree-relative-path-guard`
was never touched.
