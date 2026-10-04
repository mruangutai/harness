# QA gate — validate c3 — pin ef9cbce243444628d4ca74931be94a576e493dd5

**PASS.** R2 closed. Matrix floor met, T-01 124/0, T-02 clean, R2 red with old adapter and green restored, all independently measured.

## Range / pin
- merge-base(main, pin) = af2a958ab06c0d6fc026b363b59fc3147e3982f1; canonical range af2a958a..ef9cbce2.
- `git diff a6a1e9c8 ef9cbce2 -- .omp tests` empty: code pin == a6a1e9c8 over .omp/tests. a6a1e9c8 touches only `.omp/extensions/harness-hooks.ts`, `tests/unit/omp-hooks.test.ts`. 65f5e563/ef9cbce2 are record-only.
- Assigned worktree HEAD at run time was 8c370f7c (later than pin; not used for pin claims). Tests/mutation ran in disposable pin `.pins/BUG-1016-worktree-relative-paths--validate-c3--harness-qa` (HEAD verified = pin); removed on return.

## Matrix (harness.json test_matrix)
- T-01 bugfix: always [], when unit if touches_runtime_code (adapter is runtime) -> **unit required, satisfied**. integration clause (fix confined to tests/docs) not triggered. `__bug_class__` placeholder unresolvable (repo G-08).
- T-02 docs: always [] -> nothing required; verify ran.
- unit kind cmd `run-unit-tests.py --kind unit` (env -u HARNESS_AGENT_TYPE): exit 0, 44 files discovered (nonzero), 11.3s wall, test-omp-hooks.py included (exit 0, 5.53s). Run in worktree HEAD 8c370f7c (code identical to pin).

## Verify literals (pin)
- `python3 tests/unit/test-omp-hooks.py`: exit 0, **124 pass / 0 fail**, 552 expects, 4.77s (<60s).
- `gen-decisions-index.py --stdout | diff - DECISIONS-INDEX.md`: exit 0, no diff.

## R2 falsification (pin only)
- Adapter reverted to a6a1e9c8^ (`git checkout a6a1e9c8^ -- .omp/extensions/harness-hooks.ts`), new tests kept: exit 1, **123 pass / 1 fail**; sole red = `BUG-1016: a quoted target is rooted inside its quotes, even one made of quotes (R2)` at omp-hooks.test.ts:1356; received `/wt/FEAT-43-long-run/""""` vs expected `"/wt/.../""` (root inserted before wrapper).
- Adapter restored from pin: clean `git status`, 124/0 green again.
- G1 mutant (classify ~/absolute/scheme on trimmed instead of unquoted target): 122/2 — R2 test and the edit quoted-MV test redden. Restored, 124/0.

## c2 G1 re-grade: RESOLVED
Rows at :1359 feed quoted `"~/notes.md"`, `"/abs/a.ts"`, `"agent://LeadTwo"` and assert untouched; padded `' "x" '` and quoted-space rows pinned. Scope: asserted via the `read` path field only (rootTarget is shared by all path tools, edit MV covered separately); not per-tool. Advisory only.

## fail_first (test failed before fix)
SC-01..SC-06: notes/t01-receipts-main-session.md red-first list (14 new cases failed vs unmodified adapter, 109/14, commit 10f38a42; two controls pass-before by design). SC-06 dedicated red-first: c1 F1 dismissed in c2 (control-labelled). R2 (amended SC-03 predicate/quote leg): my own reproduction above, 123/1.
Tier: SC-01..05 natural RED (receipt); SC-06 control + mutation; R2 constructed old-adapter RED (own run).

## sc_status
SC-01 omp-hooks.test.ts "a relative path on every path tool..." automated pass; SC-02 "edit sections and MV destinations..." pass; SC-03 "omitted or null..." + "blank strings..." + R2 :1347 pass; SC-04 "resolver asked once..." / "no worktree..." / "unusable..." / "prose..." pass; SC-05 "each list entry..." / "BUG-2003's URI rule..." / "write and edit gates..." pass; SC-06 "held run..." + silent/main/Bash controls pass; SC-07 inspection (DEC-251, index diff clean) — not QA-automated.

## Advisories / out of range
- Q1 agent://, xd:// host guard refusals: harness-owner advisory, unchanged.
- Pre-existing ast_edit not in mutation set (receipt note): not this diff.
- Simplify F1 duplicate rootedHooks fixture: operator backlog.
- Receipt counts (123 at 10f38a42) predate R2 test; current 124 independently measured.

## Receipt contract (form-only correction; no new execution)
Measurements above are unchanged. Scope note: the 44-file `run-unit-tests.py --kind unit` run is a supplemental run at later HEAD 8c370f7c (code identical to pin over .omp/tests); it was NOT executed at the pin. The pinned unit evidence is the T-01 runner `python3 tests/unit/test-omp-hooks.py` at pin ef9cbce2: 124 pass / 0 fail. G1's original advisory gap is resolved by the quoted exclusion rows (:1359); the residual bound (asserted via the `read` path field, not per tool) is a qualification, not an unclassified finding.

```yaml
VERDICT: PASS
DIGEST:
  headline: "c3 PASS: R2 fixed; pinned T-01 124/0 and T-02 diff clean; old adapter reddens only the R2 test (123/1), restored green"
  suite: pass
  failures: 0
  matrix_ok: true
  kinds:
    - { kind: unit, state: satisfied, cmd: "python3 tests/unit/test-omp-hooks.py (pin ef9cbce2; supplemental 44-file run-unit-tests.py --kind unit at later HEAD 8c370f7c, not at pin)", named_tests: 124 }
  coverage_gaps:
    - "Qualification: G1 quoted ~/absolute/scheme exclusions asserted via read path field only, not per tool (shared rootTarget; edit MV covered separately); original G1 gap resolved"
    - "SC-07 is inspection (DEC-251, index diff clean), not automated"
  sc_evidence:
    - { id: SC-01, test: "tests/unit/omp-hooks.test.ts: a relative path on every path tool..." }
    - { id: SC-02, test: "tests/unit/omp-hooks.test.ts: edit sections and MV destinations..." }
    - { id: SC-03, test: "tests/unit/omp-hooks.test.ts:1347 (R2) plus omitted/null and blank-string cases" }
    - { id: SC-04, test: "tests/unit/omp-hooks.test.ts: resolver asked once / no worktree / unusable / prose cases" }
    - { id: SC-05, test: "tests/unit/omp-hooks.test.ts:1359 and BUG-2003 URI rule, write and edit gates" }
    - { id: SC-06, test: "tests/unit/omp-hooks.test.ts: held run refused before rewrite; silent/main/Bash controls" }
  fail_first:
    - { sc: SC-01, evidence: "notes/t01-receipts-main-session.md red-first list (109 pass/14 fail vs unmodified adapter, commit 10f38a42)" }
    - { sc: SC-02, evidence: "notes/t01-receipts-main-session.md red-first: edit sections and MV case" }
    - { sc: SC-03, evidence: "receipt omitted/null and blank cases; R2 own reproduction: adapter a6a1e9c8^ + new tests = 123 pass/1 fail at omp-hooks.test.ts:1356" }
    - { sc: SC-04, evidence: "notes/t01-receipts-main-session.md red-first: resolver cases" }
    - { sc: SC-05, evidence: "notes/t01-receipts-main-session.md red-first: URI beside rooted sibling, write/edit gates cases" }
    - { sc: SC-06, evidence: "notes/t01-receipts-main-session.md: held-run case; silent-success control passes pre-fix by design (c1 F1 dismissed in c2)" }
  open_questions:
    - { id: Q1, question: "agent:// and xd:// host guard refusals: out-of-range harness-owner advisory, unchanged, not attributed to this diff", blocking: false }
  files_touched: []
  expertise_update: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-1016-worktree-relative-paths/.harness/harness/features/BUG-1016-worktree-relative-paths/notes/review-harness-qa-c3.md
```
