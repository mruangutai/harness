# SIMPLIFY pass — EFFICIENCY angle — validate-final-simplify-c21

Scope: three remediation commits `0666c01..17106762c588b3d1c0df45efbcb6128604efb185`
(`a643e44`, `34a49c4`, `1710676`) on top of the previously-simplified tree.

## Headline

No apply warranted. The remediation's real added cost is small and correctly gated: the
hook's mean wall time for the common case (`code_grade` pass/fail/grade_2) went from a
~50ms baseline to ~75-80ms (+~25ms, one new unconditional SEC-01 binding pass, 3 git
spawns). The rare `n_a` path costs an additional ~80-110ms on top of that (9 more git
spawns) but that path only fires when a reviewer claims no Python changed — not the
common case. The two suite-level suspects named in the dispatch (`check_self_grading`'s
10-file grade, the `tokenize` joiner in `case_20`) are both immaterial by direct
measurement. One new fresh finding: `review_sha` is git-`rev-parse`-resolved five
separate times inside a single `n_a` validation, uncached — a genuine but low-frequency
waste, filed as a backlog row, not an apply.

## Measured: the hot path (`validate-digest.py` on `SubagentStop`)

All timings: `/usr/bin/time -p`, 10 repeats each, full CLI subprocess including Python
startup, from the worktree root, hook payloads built from `reviewer_digest()` in
`test-validate-digest.py` against this feature's real `feature.json`
(`review_sha=94383e67...`, artifact pointed at this feature's own `notes/`).

| case | command | mean wall (10 reps) |
|---|---|---|
| non-reviewer persona (baseline, `code_grade` logic never reached) | `validate-digest.py --hook` < `{agent_type: harness-frontend-dev}` | **0.050s** |
| `harness-code-reviewer`, `code_grade: pass`, honest `reviewed` | same, `code_grade: pass` | **0.075-0.080s** |
| `harness-code-reviewer`, `code_grade: n_a`, honest `reviewed` (real Python diff -> rejected) | same, `code_grade: n_a` | **0.16-0.17s** |

Delta over baseline: pass case **+~25-30ms**; n_a case **+~110-120ms**. This baseline
(~50ms) already carries B2's eager `from code_grade import commit_oid` — matches the
prior pass's ~42.5ms figure within normal machine variance; nothing new regressed the
baseline itself.

In-process confirmation (no process-startup noise), `timeit`, 20 reps, calling
`validate()` directly: pass **25.2ms**, n_a **104.3ms** mean — matches the CLI deltas.

### Unconditional vs conditional — traced by instrumenting `subprocess.run`

Read the branch structure directly (`validate-digest.py:1125` `code_grade_bound_to_review`
is called BEFORE the `code_grade` value is examined at all — confirmed by re-reading, not
assumed): it is genuinely unconditional for every `harness-code-reviewer` digest.

**Unconditional, every `harness-code-reviewer` digest (3 subprocess spawns, ~27ms):**
1. `git -C . rev-parse --verify --end-of-options <reviewed-head>^{commit}` (~9ms) — resolves the digest's own claimed head
2. `git -C . rev-parse --verify --end-of-options <review_sha>^{commit}` (~9ms) — resolves the pin
3. `git -C <root> rev-parse --abbrev-ref HEAD` (~8ms) — branch corroboration (wave 3)

Calls 1-2 are **B3** (`~22ms` prior estimate; measured now at ~18-20ms — update B3's
number, not a new row). Call 3 is genuinely new and NOT part of B3: the wave-3 branch
corroboration added one more unconditional subprocess spawn (~8ms) that fires on every
`harness-code-reviewer` return, not only `n_a`. Concrete cost: ~8ms × every reviewer
return. Alternative: none proposed — it is a single cheap spawn buying a real hole-close
(artifact pointed at a different shipped feature's pin), and 8ms is not worth trading
security surface for. Not a finding requiring action, recorded for completeness.

**Conditional, `n_a` only (9 more subprocess spawns, ~79ms on top of the unconditional
path):** traced call-by-call —
`rev-parse HEAD`(shape check base), `rev-parse review_sha`(shape check head),
`git diff --name-only` (shape check, digest's own range — this is the FIRST of the
"double git diff", SETTLED, measured at 9.2ms), `git symbolic-ref -q
refs/remotes/origin/HEAD` (default branch), `rev-parse review_sha` (again, for
`_derived_reviewed_python_change`'s own resolve), `git merge-base <default> <review_sha>`,
`rev-parse <merge-base-oid>`, `rev-parse review_sha` (again, third time), `git diff
--name-only` (derived range — SECOND of the double git diff, 9.3ms). All ~8-10ms each.

The double `git diff` itself costs **18.4ms measured** (9.2 + 9.3) — SETTLED, not a
finding, recorded per dispatch instruction.

## Fresh finding — `review_sha` resolved five times in one `n_a` validation

- **file/line:** `.claude/skills/harness/bin/validate-digest.py:865` (`code_grade_bound_to_review`'s `resolve_reviewed_commit(review_sha)`), `:657` and `:667` (`_derived_reviewed_python_change`'s two more resolves of the same SHA via `resolve_review_sha` -> `_read_review_sha` doesn't resolve it, but `_derived_reviewed_python_change:657` calls `resolve_reviewed_commit(review_sha)` directly, and `reviewed_python_change` at `:666` resolves it again as `head_oid`)
- **summary:** the same `review_sha` string is passed to `resolve_reviewed_commit` (a `git rev-parse` spawn) five separate times across one `n_a` validation — once in the unconditional binding, once in `_derived_reviewed_python_change`, once more inside the `reviewed_python_change` call it makes — with no memoization anywhere in `validate()`'s call graph.
- **concrete cost:** measured ~8.3ms per redundant resolve × 4 avoidable repeats ≈ **33ms** of the n_a path's ~185ms total CLI time is pure duplicate `git rev-parse` work on an identical, already-known-good OID.
- **alternative:** thread the OID resolved once in `code_grade_bound_to_review` (or a small `functools.lru_cache` on `resolve_reviewed_commit` scoped to one `validate()` call) through to `_derived_reviewed_python_change` instead of re-resolving from the string. This is a backlog row, not an apply: `n_a` is the rare branch (fires only when a reviewer claims no Python changed), the fix would touch the exact functions the double-`git-diff` decision (SETTLED, Q8) already reasoned about byte-identically, and reworking the call graph to share one resolved OID risks exactly the kind of behavior drift that decision was written to prevent. `C21-efficiency-1`.

## Suite 1 — `check_self_grading` in `test-code-grade.py` (grades 10 files, was 3)

- `test-code-grade.py` full suite: mean **0.61s** (5 reps: 0.62/0.61/0.61/0.61/0.61), exit 0, `PASS test-code-grade`.
- `check_self_grading()` alone, `timeit`, 5 reps: mean **89.3ms**.
- Share of suite: 89.3ms / 610ms ≈ **14.6%**.
- **Verdict: immaterial.** Tens of milliseconds, not seconds — closed as asked. No finding.

## Suite 2 — `tokenize`-based joiner in `test-check-plan-routes.py` `case_20`

- `test-check-plan-routes.py` full suite: mean **31.5s** (5 reps: 31.59/32.87/31.68/31.47/31.50), exit 0, `ALL PASS`.
- Per-case breakdown (timed every `case_*` function individually in one interpreter):
  the suite's cost is concentrated in **`case_23` (~18.5s)** and **`case_19` (~7.0s)** —
  both pre-existing cases, untouched by this remediation's diff (they exercise
  `check-plan-routes.py`'s budget/discovery logic, unrelated to the CR-01/SEC-01 scope).
- `case_20` (the case that gained the `tokenize` joiner) alone, `timeit`, 3 reps: mean
  **45.5ms**, and isolated it is 46.7ms on the per-case breakdown pass — consistent.
- **Verdict: immaterial.** The tokenize rewrite costs tens of milliseconds against a
  31.5s suite whose real weight lives entirely elsewhere and predates this remediation.
  No finding; the suite's total wall time is a pre-existing characteristic out of this
  pass's scope, not something these three commits added.

## Orchestrator-measured fact re-verified

`python3 .claude/skills/harness/bin/code-grade.py --base 7ccfae8d --head 17106762`:
- **exit 0**, confirmed by `echo $?` capture across 3 timed reps.
- `grep -c "^FUNCTION$"` → **178**; `grep -c "^RESULT: FAIL"` → **14**; `grep -c "SEVERITY: med"` → **14**; `grep -c "^RESULT: PASS"` → **164**. All 14 FAIL records are `grade_2`/severity `med` — zero blocking below-bar records (no `high`-severity/`fail`-class record present).
- Timing (3 reps): **0.64s / 0.61s / 0.62s** mean ≈ **0.62s** — this is the cost a future CI step invoking it once per push would pay; not a hot path (build-boundary step, not `SubagentStop`).

Secondary spot-check (not the assignment's re-verification target, done incidentally
while tracing the n_a subprocess path): the three forged-range shapes
(`review_sha..review_sha`, `review_sha~1..review_sha`, `HEAD..HEAD`) against this
feature's real `review_sha` all still produce a non-empty `errs` list (rejected) under
`validate()` at this HEAD — consistent with the dispatch's stated fact, though not run
through the exact ambient-repo test harness fixtures.

## Five focused suites — exit status and wall time

| suite | mean wall (3 reps unless noted) | exit |
|---|---|---|
| `test-code-grade.py` | 0.61s (5 reps) | 0 |
| `test-code-grade-cli.py` | 2.48s (2.58/2.44/2.43) | 0 |
| `test-gate-policy.py` | 0.02s (0.02/0.02/0.02) | 0 |
| `test-check-plan-routes.py` | 31.5s (5 reps, see breakdown above) | 0 |
| `test-validate-digest.py` | 6.40s (6.39/6.41/6.41) | 0 |

All five green. `test-check-plan-routes.py`'s 31.5s is a real, pre-existing suite cost —
not something these three commits introduced (see per-case breakdown above) — so it is
reported honestly here per B7/the dispatch's instruction, not flagged as a new problem.

## Carried findings

- **B1, B2, B4, B5, B6, B7, B8**: no fresh measurement to add; carried forward as-is.
- **B3**: updated with a real number — the unconditional binding's two `resolve_reviewed_commit` calls measured at ~9ms each (~18-20ms total) in this pass, in line with the prior ~22ms estimate.

## must_fix

`[]` — nothing here gates the pin. The hot-path delta is small (+25ms common case, on a
hook that already costs ~50ms of Python startup) and the one fresh redundancy
(`C21-efficiency-1`) is bounded to the rare `n_a` branch, correctly a backlog row per the
dispatch's own ceiling-of-one-apply and settled-decision constraints.

## Working tree

```
$ git -C <worktree> status --porcelain
 M .harness/harness/features/FEAT-43-code-risk-grading/STATE.md
 M .harness/harness/features/FEAT-43-code-risk-grading/feature.json
?? .harness/harness/features/FEAT-43-code-risk-grading/answers/Q6-cycle-20-remediation-authorization.md
?? .harness/harness/features/FEAT-43-code-risk-grading/answers/Q7-cycle-25-preemptive-authorization.md
?? .harness/harness/features/FEAT-43-code-risk-grading/answers/Q8-sec01-remedy-ruling.md
?? .harness/harness/features/FEAT-43-code-risk-grading/notes/qa-regate-c18.md
?? .harness/harness/features/FEAT-43-code-risk-grading/notes/receipt-harness-backend-dev-reuse-c21.md
?? .harness/harness/features/FEAT-43-code-risk-grading/notes/receipt-harness-backend-dev-validate-remediate-c14-eng-s1.md
?? .harness/harness/features/FEAT-43-code-risk-grading/notes/receipt-harness-backend-dev-validate-remediate-c14-eng-s1b.md
?? .harness/harness/features/FEAT-43-code-risk-grading/notes/receipt-harness-backend-dev-validate-remediate-c14-eng-s2.md
?? .harness/harness/features/FEAT-43-code-risk-grading/notes/receipt-harness-backend-dev-validate-remediate-c14-eng-s3.md
?? .harness/harness/features/FEAT-43-code-risk-grading/notes/receipt-harness-backend-dev-validate-remediate-c14-eng-s3b.md
?? .harness/harness/features/FEAT-43-code-risk-grading/notes/receipt-harness-backend-dev-validate-remediate-c14-eng-s5.md
?? .harness/harness/features/FEAT-43-code-risk-grading/notes/receipt-harness-backend-dev-validate-remediate-c18-eng.md
?? .harness/harness/features/FEAT-43-code-risk-grading/notes/receipt-harness-backend-dev-validate-sec01-c19-eng.md
?? .harness/harness/features/FEAT-43-code-risk-grading/notes/receipt-harness-dev-ops-altitude-c21.md
?? .harness/harness/features/FEAT-43-code-risk-grading/notes/receipt-harness-dev-ops-simplification-c21.md
?? .harness/harness/features/FEAT-43-code-risk-grading/notes/receipt-harness-dev-ops-validate-remediate-c14-eng-s4.md
?? .harness/harness/features/FEAT-43-code-risk-grading/notes/receipt-harness-dev-ops-validate-remediate-c14-eng-s6.md
```

All entries above pre-date this run (sibling readers' concurrent receipts and pre-existing
feature-state edits) or are this receipt's own sibling writes. **No source file (`.claude/skills/harness/bin/*.py`, `.claude/skills/harness-code-review/SKILL.md`) was touched by this run.**
