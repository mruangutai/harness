# QA re-gate — FEAT-43 code risk grading, validate-regate-c18

```yaml
VERDICT: FAIL
DIGEST:
  headline: "unit+integration matrix holds at baseline (29/29, 28/28) and CR-01/CR-02/UI-01 close under live discrimination and mutation, but SEC-01 does NOT close — the literal security-reviewer bypass digest (review_sha..review_sha, code_grade: n_a) still validates at exit 0 today, contradicting Q6's explicit 'a self-named no-op range must not buy n_a'"
  suite: pass
  failures: 0
  matrix_ok: true
  kinds:
    - { kind: unit, state: satisfied, cmd: ".agents/skills/harness/bin/run-unit-tests.sh --kind unit", named_tests: 29 }
    - { kind: integration, state: satisfied, cmd: ".agents/skills/harness/bin/run-unit-tests.sh --kind integration", named_tests: 28 }
  coverage_gaps:
    - "SEC-01: no test in test-validate-digest.py exercises a self-consistent no-op range AT review_sha itself (base=head=review_sha). Every existing SEC-01 case (check_review_sha_binding, check_review_sha_binding_unconditional) forges a no-op whose head is NOT review_sha ('HEAD..HEAD' against the fixture's distinct REVIEW_SHA). That is why the residual bypass ships green."
  sc_evidence:
    - { id: SC-14, test: "test-code-grade-cli.py:test_bars_follow_test_kinds (REASON REQUIRED presence/absence pair)" }
    - { id: SC-17, test: "test-code-grade-cli.py:test_bars_follow_test_kinds (four boundary discriminators, now each with a severity assertion)" }
  open_questions:
    - { id: Q1, question: "SEC-01 residual: a digest with reviewed: \"<review_sha>..<review_sha>\" (base=head=review_sha, code_grade: n_a) is ACCEPTED at exit 0 today — reproduced live, see 'SEC-01 discrimination' below. This is the EXACT shape the security reviewer used at the panel (review-harness-security-reviewer-validate-final-panel.md). code_grade_bound_to_review only asserts head_oid==pin_oid; it never constrains base to the feature's true predecessor, so a reviewer who always knows review_sha (it's in feature.json, not secret) can always construct this no-op and skip grading — exactly Q6's forbidden case ('a self-named no-op range must not buy n_a'). Is this accepted as a scoped limitation (the docstring says so: 'base has no independent system-of-record value today (batch contract)'), or does it need a fifth remediation wave binding base to the true predecessor (or requiring base != head)?", blocking: true }
  files_touched: []
  expertise_update: []
artifact: .harness/harness/features/FEAT-43-code-risk-grading/notes/qa-regate-c18.md
```

## Change type and matrix

`cross_module` — ten `.py`/`.md` files under `.claude/skills/` changed by two commits
(`a643e44`, `34a49c4b`) touching three production seams (`code_grade.py`, `code-grade.py`,
`gate_policy.py`, `check-plan-routes.py`, `validate-digest.py`) and their tests plus shipped
guidance. Matrix requires `unit` + `integration`, both configured active; neither added beyond the
floor.

| kind | required | command | state | count | vs baseline |
|---|---|---|---|---|---|
| unit | matrix: cross_module.always | `.agents/skills/harness/bin/run-unit-tests.sh --kind unit` | satisfied | 29/29 scripts, 0 fail, exit 0 | matches (29/29) |
| integration | matrix: cross_module.always | `.agents/skills/harness/bin/run-unit-tests.sh --kind integration` | satisfied | 28/28 scripts, 0 fail, exit 0 | matches (28/28) |
| functional | excluded (DEC-187) | n/a | soft skip | n/a | n/a |

Raw logs: `/tmp/qa_unit_c18.log` (1444 lines), `/tmp/qa_integration_c18.log` (1909 lines),
re-confirmed after both mutation excursions at `/tmp/qa_unit_final.log`,
`/tmp/qa_integration_final.log` — all four runs exit 0, all counts identical. Dedup method: some
scripts print an internal case whose name is a prefix of the script's own `PASS test-<file>` line
(`test-code-grade`/`test-code-grade-cli`) and some integration scripts print `PASS <name>` twice
(`test-feature-worktree.py`, `test-expertise-merge.py`, `test-plan-merge.py`,
`test-observations-merge.py`); unique `.py` script names give 29 and 28 respectively, both zero
`^FAIL test-`.

## Ten-file binding table

| file | kind | named case | what reverting breaks |
|---|---|---|---|
| `code_grade.py` | unit (test-code-grade.py) | `check_self_grading`: `code_grade.py:_records.collect grade >= 4`, `code_grade.py:_changed_python_files grade >= 4`; behaviourally also `check_nested_qualnames` (exercises `_child_qualname`) and the NUL-safe-rename case at `test-code-grade.py:418-422` (exercises `_next_paths`) | reverting the `_records.collect`/`_child_qualname` and `_changed_python_files`/`_next_paths` splits regrades both back below the production bar of 4; `check_self_grading` fails by qualname |
| `code-grade.py` | integration (test-code-grade-cli.py) | `test_diff_paths_complexity` (asserts `_diff_paths`, `_run_name_status_diff`, `_name_status_entries`, `_is_changed_python`, `_record`, `_status`, `_severity`, `_blocks` all present and grade >= 4); `test_bars_follow_test_kinds` (severity present/absent, exact value, text+JSON) | reverting `_diff_paths`'s split regrades it below 4, failing `test_diff_paths_complexity` by qualname; reverting `_severity`/`_blocks` back to `{1: "high", 2: "med"}.get(grade)` drops `SEVERITY:`/`"severity"` for a blocking grade-3 record, failing `test_bars_follow_test_kinds`'s new severity assertions |
| `gate_policy.py` | unit (test-code-grade.py + test-gate-policy.py) | `check_self_grading`: `gate_policy.py:load_policy grade >= 4`, `gate_policy.py:evaluate_qa grade >= 4` — **proven live by my own mutation** (below) | reverting `load_policy`/`evaluate_qa`'s split back to the monolithic pre-fix shape regrades both to grade 3, below bar; `check_self_grading` fails naming `gate_policy.py:load_policy` |
| `check-plan-routes.py` | integration (test-check-plan-routes.py + test-code-grade.py) | `check_self_grading`: `check-plan-routes.py:resolution_manifest grade >= 4`; behaviourally `case_27`/`case_14_15`/`case_27c_unreadable_owner_manifest_refuses` exercise `resolution_manifest`/`_owner_root`/`_manifest_deviation` end-to-end | reverting the `_owner_root`/`_manifest_deviation` split regrades `resolution_manifest` below 4; `check_self_grading` fails by qualname |
| `validate-digest.py` | integration (test-validate-digest.py) | `check_review_sha_binding`, `check_review_sha_binding_unconditional` — **proven live by my own mutation** (below) | disabling the `head_oid != pin_oid` comparison reproduces the exact live bypass; `check_review_sha_binding_unconditional`'s `code_grade='fail'` case fails by name |
| `test-code-grade.py` | unit (is the test) | self: `check_self_grading` (`test-code-grade.py:main grade >= 3`) — this is literally the CR-01 class-fix regression the c18 receipt reproduced RED before GREEN | reverting `main`'s decomposition into `check_fixtures`/`check_nested_qualnames`/`check_direction_pairs` drops `main` back to ABC 45.7/grade 1; `check_self_grading` fails naming `test-code-grade.py:main` |
| `test-code-grade-cli.py` | integration (is the test) | self: `test_diff_paths_complexity`, `test_bars_follow_test_kinds`, `test_review_skill_states_severity_vocabulary` are new in this diff | reverting this file removes these three checks outright — CR-01's CLI half, CR-02/UI-01's severity, and the SKILL.md vocabulary cross-check all lose their only test |
| `test-check-plan-routes.py` | integration (is the test) | self: `case_20_logical_lines_is_string_and_comment_aware` (direct fixture proof: bracket-in-string, bracket-in-comment, multi-line join) | reverting `logical_lines`'s tokenize dispatch back to the naive bracket counter reproduces the 48,393-character false-positive merge on `validate-digest.py`; the fixture assertion fails directly, and `case_20_validate_digest_py_probes_the_manifest`-equivalent (`_report_scan_result` for that file) fails again |
| `test-validate-digest.py` | integration (is the test) | self: `check_review_sha_binding`, `check_review_sha_binding_unconditional`, `check_branch_corroboration`, `check_resolve_review_sha_artifact_path`, `check_resolve_review_sha_feature_json` are all new in this diff; `reviewer_digest()`'s default `reviewed` no longer defaults to the bypass shape | reverting this file removes every SEC-01 test and restores the bypass-shaped fixture default — the exact regression this feature exists to prevent |
| `harness-code-review/SKILL.md` | integration (test-code-grade-cli.py) | `test_review_skill_states_severity_vocabulary` reads the shipped file and asserts `"SEVERITY: high"`, `"code_grade: fail"`, `"not grade 2"`, `"code_grade: grade_2"` are all present | reverting the guidance text to the pre-fix wording (grade-1/grade-2-only language) fails this check by name |

No file lacks binding coverage under the matrix's own suites.

## Test-first audit (receipts vs. what landed)

| item | receipt | claims test-first | landed test matches claim |
|---|---|---|---|
| s1 (core complexity, 5 fns) | `receipt-...-s1.md` | Yes — "Test-first record": 13 pre-fix failures (`grade >= 4` / `exists`), 0 post-fix | Yes — `check_self_grading`'s per-qualname assertions for `_records.collect`, `_changed_python_files`, `load_policy`, `evaluate_qa`, `resolution_manifest` are exactly what's in the current file |
| s1b (allowlist honesty, test-only) | `receipt-...-s1b.md` | N/A framing (test-shape correction, not new production code) but ships 3 mutation proofs | Yes — `SELF_GRADING_ALLOWLIST`'s 8-then-37-entry growth and staleness assertion match |
| s2 (severity + CLI CR-01) | `receipt-...-s2.md` | Yes — "Fix, test-first:" | Yes — `_severity`/`_blocks` and `_diff_paths` split, `test_bars_follow_test_kinds`/`test_diff_paths_complexity` present as claimed |
| s3 (SEC-01 wave 2) | `receipt-...-s3.md` | Yes — "Test-first (RED confirmed before the GREEN fix)", quotes the exact pre-fix `digest ok`/exit 0 reproduction | Yes — `resolve_review_sha`/`code_grade_bound_to_review` and `check_review_sha_binding`/`_unconditional`/`_other_personas` all present and match the quoted shapes |
| s3b (SEC-01 wave 3, branch corroboration) | `receipt-...-s3b.md` | Yes — "Test-first (RED confirmed before implementing, and again independently after)" | Yes — `_branch_corroboration_error`, `check_branch_corroboration` present, additive-only as claimed |
| s4 (dev-ops consolidated verification) | `receipt-...-s4.md` | N/A (verification-only run; correctly returned FAIL naming `case_20`) | Yes — the FAIL it reported is the same defect s5 then fixed |
| s5 (case_20 joiner) | `receipt-...-s5.md` | Section A is literally "RED — reproduce before fixing", quotes the pre-fix failure | Yes — `logical_lines`/`_logical_lines_python`/`_assert_logical_lines_fixture` all present and match |
| s6 (dev-ops final confirmation) | `receipt-...-s6.md` | N/A (verification-only, independently re-ran everything) | Yes — five suites + adapter check, case_20 stable across two runs, as claimed |
| c18 backend-dev (main decomposition) | `receipt-harness-backend-dev-validate-remediate-c18-eng.md` | Yes — "Step 1 — guard extended (RED before fix)", quotes `FAIL test-code-grade.py:main grade >= 3` then `PASS test-code-grade` | Yes — `main`'s tuple-of-callables decomposition and grade 5 (CYCLOMATIC 3/COGNITIVE 2/ABC 5.1) match exactly |

No item's claim disagrees with the tree. All nine receipts checked are honest.

## Closure 1 — SEC-01: FAILS discrimination (this is why VERDICT is FAIL)

Reconstructed the exact literal digest the security reviewer used at the panel
(`review-harness-security-reviewer-validate-final-panel.md`): `code_grade: n_a`,
`reviewed: "94383e671e51f95d142f3220f97c8e453721d516..94383e671e51f95d142f3220f97c8e453721d516"`
(review_sha named as both base and head), `artifact:` pointing at this feature's own
`notes/qa-regate-c18.md`.

```
$ python3 .claude/skills/harness/bin/validate-digest.py harness-code-reviewer /tmp/sec01probe/forged_pin_pin.txt
digest ok
EXIT=0
```

**Still accepted, exit 0 — NOT rejected.** This is because `code_grade_bound_to_review` only
asserts `head_oid == pin_oid` (`validate-digest.py:792`); it places no constraint on `base`. Since
`review_sha` is a public, non-secret value (it's read straight out of `feature.json`), any reviewer
can always construct `reviewed: "<review_sha>..<review_sha>"` — a self-consistent no-op whose head
legitimately resolves to `review_sha` — and buy `code_grade: n_a` without ever running the grader.
This is functionally identical to the original bypass; the fix narrowed the forgeable set from "any
resolvable commit" to "review_sha specifically," but a reviewer always knows `review_sha`, so the
narrowing does not close the practical hole.

Confirmed this is NOT what the shipped test suite exercises — `check_review_sha_binding`'s forged
case is `reviewed="HEAD..HEAD"` against a fixture `HEAD` constant that is deliberately **distinct**
from the fixture's `REVIEW_SHA` (test-validate-digest.py:1899, comment: "a resolvable,
self-consistent no-op range whose head is simply not review_sha"). No case anywhere in
`test-validate-digest.py` forges a no-op **at** `review_sha` itself — which is exactly the value an
attacker would pick, since it's the only value guaranteed to pass the SHA check.

Two more probes for contrast:

```
$ python3 .claude/skills/harness/bin/validate-digest.py harness-code-reviewer /tmp/sec01probe/forged_offpin_pin.txt
VERDICT: BLOCKED (contract violation)
  - reviewed head '7ccfae8dd7644bc3aaea612dabf4317c0d804f99' does not resolve to this feature's pinned review_sha (94383e671e51f95d142f3220f97c8e453721d516) — write the range that ends at review_sha (feature.json), not a convenient no-op.
EXIT=1
```
(a no-op at a DIFFERENT pin, not review_sha — correctly rejected)

```
$ python3 .claude/skills/harness/bin/validate-digest.py harness-code-reviewer /tmp/sec01probe/honest.txt
digest ok
EXIT=0
```
(base=df63193 the true predecessor, head=review_sha, code_grade: fail — correctly accepted)

`reviewer_digest()`'s shared fixture no longer defaults to the bypass shape — confirmed by reading
`test-validate-digest.py:1756-1765`: the default is now `f"HEAD..{REVIEW_SHA}"`, an honest,
non-self-consistent range, with an explicit comment naming the old default
(`PRE_FEATURE_REVISION..PRE_FEATURE_REVISION`) as "the exact bypass this feature closes." That part
of SEC-01 is genuinely fixed. The gap is narrower than the original defect but real: a self-named
no-op **at the pin** still buys `n_a`, contradicting Q6's explicit "a self-named no-op range must
not buy n_a."

### Mutation proof (SEC-01 binding, performed by me)

- md5 of `validate-digest.py` before: `26ae05f5ec7834810352e105e8f8de5b`.
- Mutation: `if head_oid != pin_oid:` → `if False and head_oid != pin_oid:` (disables the binding
  unconditionally).
- Ran `python3 .claude/skills/harness/bin/test-validate-digest.py` against the mutant: `REAL_EXIT=1`.
- Exact failing assertion, quoted verbatim:
  ```
  FAIL  code-grade and review-policy gates
        code_grade='fail' with a forged no-op range must still reject — the binding runs before the code_grade branch, not only inside it
  1 FAILING.
  ```
- Restored via `cp` from a pre-mutation backup (never `git checkout`/`git restore`). md5 after
  restore: `26ae05f5ec7834810352e105e8f8de5b` — matches exactly.
- `git status --porcelain -- .claude/skills/harness/bin/validate-digest.py` after restore: empty.
- Re-ran green: `ALL PASSED`, exit 0.

## Closure 2 — CR-02 + UI-01: holds

Built a scratch fixture (`/tmp/cr02check`, outside the repo, deleted after) with a five-level-nested
production function graded 3 against bar 4:

```
$ python3 .../code-grade.py src/grade_three.py
...
GRADE: 3
BAR: 4
RESULT: FAIL
SEVERITY: high
PASSING: 0
EXIT=1

$ python3 .../code-grade.py --json src/grade_three.py
{"...": ..., "grade": 3, "bar": 4, "result": "FAIL", "severity": "high"}
EXIT=1
```

Non-null severity present in both text (`SEVERITY: high`) and JSON (`"severity": "high"`) for a
blocking, non-grade-2 record. `harness-code-review/SKILL.md:63-71` uses the identical spellings —
`SEVERITY: high`, `"severity": "high"`, `code_grade: fail`, `not grade 2` (explicitly distinguishing
this from grade-1-only), `code_grade: grade_2` — and `validate-digest.py`'s schema
(`{"pass", "fail", "grade_2", "n_a"}`) accepts exactly those two spellings. Three surfaces agree.

SC-14 and SC-17 both still hold, unchanged in substance, in `test-code-grade-cli.py:187`
`test_bars_follow_test_kinds`: the four boundary discriminators (`src/grade-four.py` 4/4 PASS,
`src/grade-three.py` 3/4 FAIL, `checks/grade-three.py` 3/3 PASS, `checks/grade-two.py` 2/3 FAIL) are
present verbatim, each now additionally carrying a severity assertion (`None`, `"high"`, `None`,
`"med"` respectively) in both text and JSON.

## Closure 3 — CR-01: holds, including the allowlist question

Re-ran the authoritative range command:

```
$ python3 .claude/skills/harness/bin/code-grade.py --base 7ccfae8d --head 34a49c4b
...
EXIT=0
```

All five orchestrator-measured numbers reproduced exactly: **exit 0**, **161 records**
(`grep -c '^FUNCTION$'`), **`PASSING: 147`** clean (161-147=14 below-bar, zero of them blocking),
**0** `SEVERITY: high` lines, **14** `SEVERITY: med` lines, all 14 at `GRADE: 2`.

### The allowlist/gated-set intersection (the highest-value check)

Enumerated `SELF_GRADING_ALLOWLIST`'s 37 `(filename, qualname)` keys by AST-parsing
`test-code-grade.py` (never trusting the dict literal by eye), and the gated set's 161
`(filename, qualname)` pairs from `code-grade.py --base 7ccfae8d --head 34a49c4b --json`. Intersected
them:

```
Gated set size: 161
Allowlist size: 37
Intersection size: 14
Intersection: {
  ('test-code-grade.py', 'check_changed_function_resolution'),
  ('test-code-grade.py', 'check_commit_resolution'),
  ('test-code-grade-cli.py', 'test_bars_follow_test_kinds'),
  ('validate-digest.py', 'reviewed_python_change'),
  ('code_grade.py', '_body_hashes.collect'),
  ('check-plan-routes.py', 'main'),
  ('test-gate-policy.py', 'check_policy_loading'),
  ('test-check-plan-routes.py', '_case_27_owner_manifest'),
  ('code_grade.py', 'gated_set'),
  ('test-code-grade-cli.py', 'test_paths'),
  ('test-code-grade-cli.py', 'test_rejected_revisions'),
  ('code-grade.py', 'main'),
  ('test-code-grade-cli.py', 'test_control_paths'),
  ('test-code-grade-cli.py', 'test_diff_and_determinism'),
}
```

**Non-empty (14), but not the failure mode the check exists to catch.** Every one of these 14 is
exactly the SC-15-reviewed grade-2 set (items 1-12,14,15 — 14 items, since item 13
`test-code-grade.py:main` was deliberately dropped and fixed, not re-cited): grade 2 is a named,
non-blocking carve-out (`RESULT: FAIL` prints but the run exits clean once reasoned; `SEVERITY: med`,
never `high`), reviewed and reasoned at commit 94383e6 (`notes/review-harness-code-reviewer-validate-final-panel.md`,
SC-15 section), and legitimately part of the gated set by REQ-06/D-06's design — grade 2 was never
required to reach the production/test bar, only to carry a reason.

Directly checked the concern the dispatch names — **not** "is the allowlist non-empty against the
gated set" (it always will be, by design, for reviewed grade-2 records) but "does it exempt a
function this feature introduced/worsened that should have been fixed": none of the six
terminal-panel-blocking grade-3 production functions (`resolution_manifest`, `_diff_paths`,
`_records.collect`, `_changed_python_files`, `load_policy`, `evaluate_qa`) or the grade-1 regression
(`test-code-grade.py:main`) appear anywhere in `SELF_GRADING_ALLOWLIST` — confirmed by direct
membership check, all seven print "not in allowlist". No grade-1 record and no production grade-3
record is intersected. **Verdict: the allowlist does not launder this feature's own regressions.**

### Mutation proof (CR-01 guard, performed by me)

- md5 of `gate_policy.py` before: `ec90d0a3b498911cd28d8b0b3f76aec0`.
- Mutation: reverted `load_policy`'s three-function split (`_load_config`/`_require_gates`/
  `_resolve_gate`) back to the pre-fix monolithic body (behaviour-preserving, grade-regressing).
- Ran `python3 .claude/skills/harness/bin/test-code-grade.py` against the mutant: `REAL_EXIT=1`.
- Exact failing assertion, quoted verbatim:
  ```
  FAIL gate_policy.py:load_policy grade >= 4: expected True, got False
  1 failures
  ```
- Restored via `cp` from a pre-mutation backup. md5 after restore: `ec90d0a3b498911cd28d8b0b3f76aec0`
  — matches exactly.
- `git status --porcelain -- .claude/skills/harness/bin/gate_policy.py` after restore: empty.
- Re-ran green: `PASS test-code-grade`, exit 0; `test-gate-policy.py` also green (28/28 ok).

## Tree state at the end

```
$ git -C <worktree> rev-parse HEAD
34a49c4b78c74cac6676ec91d7cb7f262abf19e7
$ git -C <worktree> status --porcelain -- .claude/skills/harness/bin/code_grade.py .claude/skills/harness/bin/code-grade.py .claude/skills/harness/bin/gate_policy.py .claude/skills/harness/bin/check-plan-routes.py .claude/skills/harness/bin/validate-digest.py .claude/skills/harness/bin/test-code-grade.py .claude/skills/harness/bin/test-code-grade-cli.py .claude/skills/harness/bin/test-check-plan-routes.py .claude/skills/harness/bin/test-validate-digest.py .claude/skills/harness-code-review/SKILL.md
(empty)
```
All ten changed files byte-identical to `34a49c4b`. Full `git status --porcelain` still shows only
the pre-existing untracked feature-bookkeeping (`STATE.md`/`feature.json` modified by earlier runs,
receipts/answers written by prior squad members) — none of it mine, none of it in the ten source
files. `qa-regate-c18.md` itself is the only new file this run adds.

## Why this is FAIL, not PASS-with-advisory

The matrix itself (unit 29/29, integration 28/28) is fully satisfied and holds at baseline — that
part alone would be `PASS`. But this dispatch's explicit acceptance line for SEC-01 (Q6: "a
self-named no-op range must not buy `n_a`") is demonstrably violated today, reproduced live with the
exact digest the security reviewer used, at exit 0. A green suite is not evidence the mechanism
works; the discriminating run is, and it shows a real, exploitable residual: any reviewer who reads
`feature.json`'s `review_sha` (not secret) can still write `reviewed: "<review_sha>..<review_sha>"`
and skip grading entirely, on this feature or any other. This is not softened to an advisory note —
it is the loop-back finding for a fifth remediation pass, most likely binding `base` to the feature's
recorded true-predecessor commit (mirroring `PRE_FEATURE_REVISION`/`df63193` in this repo) or simply
rejecting `base == head` outright for `harness-code-reviewer` digests.
