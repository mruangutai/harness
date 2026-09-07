# Receipt — harness-backend-dev — BUG-1290 T-01-followup

**BLUF:** Both operator directives closed in `tests/unit/test-factory-claim.py` only. Suite green
125/125 intact; arm 2 (B-27 raising mutant) now REDS on the `5g` check itself, closing the fail-open
gap; arms 3 (B-16) and 4 (5b's own fragment) still RED; case `5b` itself is the check that fails
under the issue-map-cache mutation, captured (not printed) so it never leaks into `5c`-`5f`.
Production byte-identical to `c488218e`. Working tree restored.

## Structure

Extracted `_emit_5b(record)` (new helper, ~line 1226): runs `_run_5b_scenario()` and reports the
verdict to `record` under `name_5b`. The intact `5b` case calls `_emit_5b(check)` — unchanged
printing/counting behavior. Case `5g`'s self-defence arm now calls `_emit_5b(_capture)` — a
non-printing shim, never `check` — under the mutant `_BlockerCache`, in the same `try/finally` that
restores `claim._BlockerCache`. It then asserts on the **captured `name_5b` verdict**: `not
mutant_cond` (case 5b itself failed) AND the specific observable (`mutant_code == 1`, `mutant_out ==
""`, `"952"` and `"unresolvable blocker"` in stderr, `"no plan could be read"` absent).

**Decision — kept the name `5g`.** It is still structurally the B-16 self-defence arm (mutant
cache, restore in `finally`); renaming it would only relabel the same responsibility. What changed
is what it now measures: `not _5b_property_holds(...)` (bare negation, B-27's fail-open gap) became
an assertion on 5b's own captured verdict plus its measured specific observable.

## Measured mutant observable

Ran the mutant scenario directly (temporary debug print, removed before final edit): under the
feature-only-key mutant, `_run_5b_scenario()` returns `code=1`, `out=''`,
`err="factory: claim: skip #951 — ... unresolvable blocker)\nfactory: claim: skip #952 — issue #952
depends_on T-99, which has no recorded issue in feature.json (unresolvable blocker)\nfactory: claim:
no claimable work\n"`. **Matches the orchestrator's stated expectation exactly**: exit 1, empty
stdout, stderr names `952` and `unresolvable blocker`, and does not contain `no plan could be read`
(it additionally names `951`, which the assertion does not exclude).

## Four verification arms (env cleared: `env -u HARNESS_AGENT_TYPE python3 tests/unit/test-factory-claim.py`)

1. **Intact** — exit `0`. Final line: `125/125 checks passed.` Check count unchanged from baseline
   (125); the refactor added no new checks, only tightened `5g`'s assertion body.
2. **B-27 discharged** (mutant `issue_number` replaced with bare `raise`, delegating call restored
   after) — exit `1`. Final line: `1 of 125 FAILING.` Failing check: `FAIL  BUG-1290 5g:
   issue-map-cache mutation fails case 5b itself on its own specific observable`. Confirms the
   raising mutant — previously green at 125/125 under the old bare-negation form — is now caught.
3. **B-16 preserved** (harness segment fixture's `depends_on=["T-99"]` removed, restored after) —
   exit `1`. Final line: `1 of 125 FAILING.` Failing check: `5g` (mutation produces no observable
   difference once the dependency is gone, so `not mutant_cond` fails). Suite RED as required.
4. **5b's own fragment preserved** (harness segment `feature.json` issue map emptied, restored
   after) — exit `1`. Final line: `1 of 125 FAILING.` Failing check: `FAIL  BUG-1290 5b: same
   feature id on two repositories resolves per-segment, no cache bleed` (the intact, non-mutated
   run of `5b` itself reds, since `T-99` no longer resolves). Suite RED as required.

Grep on the intact run (arm 1's output): exactly one `^ok    BUG-1290 5b` line, zero `^FAIL  BUG-1290
5b` lines.

## Restoration proof

`git status --porcelain` (final, post all four arms):
```
 M .harness/harness/features/BUG-1290-factory-claim-repo-root/feature.json
 M tests/unit/test-factory-claim.py
?? .harness/harness/features/BUG-1290-factory-claim-repo-root/notes/answers-2026-09-06-b27.md
```
Only the orchestrator's `feature.json` (M), the orchestrator's untracked answers file, and my own
`tests/unit/test-factory-claim.py` (M) — plus this receipt once written. No lingering fixture edits.

## Production untouched

`git diff --stat c488218e -- .agents/ .claude/skills/ bin/` → **empty** (no output).

`git diff --stat c488218e` → names exactly one source file, `tests/unit/test-factory-claim.py | 45
+++++--`, alongside pre-existing feature-directory notes/STATE.md/feature.json churn from earlier
cycles between `c488218e` and current HEAD (not touched by me). No other `bin/`, `.agents/`, or
`.claude/skills/` file appears.

## Non-goals honored

No edit to cases `5a`, `5c`-`5f`, or any case before `5a`. No edit to `BRIEF.md`, `plan.yaml`,
`STATE.md`, `feature.json`, `test-factory-claim-mutation.py`, or any other test file. No commit,
stage, PR, merge, or push — change sits in the working tree only.
