# QA ship gate — FEAT-38-decisions-current-knowledge

Diff range: `7ebfc9eb9c..8a7c75c4e5` (40 commits, 131 files, +15627/-2233).
Scope of this gate's test-first audit: T-27, T-24, T-28, T-29, T-25 (the five tasks landed in
this phase). Whole-diff test kinds enforced against the full range.

## BLUF

**PASS.** `matrix_ok: true`. Suite exit 0, 0 FAIL lines, 55/55 registered scripts ran. Contract 3
(retained anchor checker/test byte-identical, still named by both runner array and
`harness.json`) verified directly with pasted digests — all four match. Item 6 (claims files gone
from the reviewed tree) and item 7 (remaining detectors still discriminate, unmodified by this
diff) both confirmed directly. One documented, non-blocking matrix-fit finding on T-24 (see
below) — resolved without a FAIL because the standing evidence for that change is stronger, not
absent.

## 1–2. Change-type → required-kind mapping and four-state resolution

| Task | change_type | matrix `always` | Resolution | Evidence |
|---|---|---|---|---|
| T-24 | `logic` | `unit` | **satisfied** (as non-regression; see finding below) — floor also discharged by **integration**, added because the diff edits `run-unit-tests.sh`'s own registration array and deletes an integration-registered file, so integration is the kind whose tooling actually reaches this change | unit: `run-unit-tests.sh --kind unit` → 27/27 scripts, 0 FAIL, none touch this diff (confirmed: no `UNIT_SCRIPTS` entry names `run-unit-tests.sh` or the deleted checker). integration: `run-unit-tests.sh --kind integration` (part of full suite) + `--check-kinds` run standalone (exit 0, "arrays and detect agree") + `test-check-decision-anchors.py` run directly (8 named `ok -` cases, exit 0) |
| T-25 | `config` | `[]` (empty — a real pass) | **satisfied**, floor is empty; added integration as extra evidence since the edit is to `test_kinds.integration.detect` | `--check-kinds` exit 0 after the edit; full suite green |
| T-27 | `docs` | `[]` (empty — a real pass) | **satisfied** | no test kind owed; DECISIONS.md prose edit only |
| T-28 | `docs` | `[]` (empty — a real pass) | **satisfied** | task's own verify (index regeneration diff) is the evidence, not a standing kind |
| T-29 | `docs` | `[]` (empty — a real pass) | **satisfied** | audit note is the deliverable; no standing kind owed |

**Finding (non-blocking, reported not fixed):** T-24 is declared `logic`, so the matrix floor
names `unit`. No `UNIT_SCRIPTS` entry exercises this specific change — the actual change (edit
one array line in `run-unit-tests.sh`, `git rm` two files) is by this repo's own structural split
(issue #160: in-process vs forking) an **integration**-shaped edit; `run-unit-tests.sh` forks
subprocesses, so anything testing it belongs under `--kind integration` by convention, never
`--kind unit`. The unit suite's green run is real evidence of *no regression*, not of *presence
for this change*. I did not fail the gate on this because (a) the diff-warranted addition of
`integration` supplies genuine, direct, named presence evidence (`test-check-decision-anchors.py`
run standalone, `--check-kinds` run standalone, both passing), stronger than a synthetic unit test
would be; (b) T-24's verify design — cheap, `--check-kinds` plus one direct script run, explicitly
not a suite-wide sweep — was reviewed and signed three times including by an adversarial panel,
and manufacturing a unit test to satisfy the letter of the matrix would contradict that signed
design for no gain. Recorded here rather than silently marked satisfied.

## 3. Suite run (measured in Python, not shell grep)

```
$ bash .claude/skills/harness/bin/run-unit-tests.sh > /tmp/qa38_suite.out 2>&1; rc=$?
RC=0
```
- `FAIL ` lines (python `startswith('FAIL ')` over the captured file): **0**
- Script-level `PASS <name>.py` markers (regex `^PASS [\w.-]+\.py$`, deduped): **55 unique**,
  which is exactly `len(UNIT_SCRIPTS)=27 + len(INTEGRATION_SCRIPTS)=28 = 55` — every registered
  script ran and every one passed. (Raw `startswith('PASS ')` returns 1001 because several
  scripts print their own internal `PASS`-prefixed case lines; the per-script marker line is the
  correct measure — see repository Expertise G-04.)
- `--check-kinds`: `RC=0`, `"check-kinds: the script arrays and test_kinds.integration.detect
  agree."`

## 4. Contract 3 — retained anchor files byte-identical, still named both places

```
$ shasum -a 256 .claude/skills/harness/bin/check-decision-anchors.py
adb9a648cfd167e30c66b34e40e4efd0dfb89ed9958ac21f62a84282299ccb77  check-decision-anchors.py
$ git show 99bb52c:.claude/skills/harness/bin/check-decision-anchors.py | shasum -a 256
adb9a648cfd167e30c66b34e40e4efd0dfb89ed9958ac21f62a84282299ccb77  -
$ shasum -a 256 .claude/skills/harness/bin/test-check-decision-anchors.py
7a4e0ba1afcb20b4b2dad6bad297441535fe3ca96284ebad7ded941b363674fa  test-check-decision-anchors.py
$ git show 99bb52c:.claude/skills/harness/bin/test-check-decision-anchors.py | shasum -a 256
7a4e0ba1afcb20b4b2dad6bad297441535fe3ca96284ebad7ded941b363674fa  -
```
All four digests match the expected values given in the dispatch — exact match. `run-unit-tests.sh`
line 31's `INTEGRATION_SCRIPTS` array and `harness.json`'s `test_kinds.integration.detect` string
both still contain the literal substring `test-check-decision-anchors.py` (checked with Python
substring containment on the actual field values, not the grep-hazard shell), and neither contains
`test-check-decision-claims.py`. **All four sub-assertions PASS.**

## 5. Test-first audit (T-27, T-24, T-28, T-29, T-25)

Commit order over the range (`git log --name-status`, oldest first among these five):
`0a94d91` T-27 → `8c879f5` T-24 → `70690ea` T-28+T-29 → `8a7c75c` T-25. This matches the plan's
`depends_on` graph exactly (T-24 depends on T-27; T-25 and T-29 depend on T-24; T-28 depends on
T-27).

- **T-24** (`logic`): deletes `check-decision-claims.py` and `test-check-decision-claims.py`
  together in one commit; this is a deletion, not new logic — "test before code" does not apply to
  a removal. No new test was written; the retained `test-check-decision-anchors.py` predates this
  task. `unknown (record insufficient: not applicable — nothing new to precede)`.
- **T-25, T-27, T-28, T-29** (`config`/`docs`): no production logic added; each task's own verify
  block is checked at completion, not preceded by a separate test file. Test-first compliance is
  `n/a` for all four — none introduces a behavior that a unit/integration test would front-run.

No compliance violation found; none of the five tasks had an occasion where test-first discipline
was applicable and skipped.

## 6. Reviewed-tree deletion check

```
$ git ls-tree -r --name-only 8a7c75c4e59a337796c10f1bc192ea752337cbbb | python3 -c "
import sys
names = sys.stdin.read().splitlines()
print([n for n in names if 'check-decision-claims' in n])
"
[]
```
Empty — confirmed absent from the reviewed tree itself (`8a7c75c`), not merely the working tree.

## 7. Remaining guards still discriminate

- **`test-check-decision-anchors.py` run directly**: exit 0, 8 `ok -` lines counted in Python
  (`test_in_range_anchor_reports_nothing_and_exits_zero`,
  `test_missing_file_is_reported_and_exits_one`, `test_out_of_range_line_is_reported_and_exits_one`,
  `test_malformed_anchor_extension_reports_line_and_exits_one`,
  `test_zero_anchors_exits_zero_and_says_so`, `test_unreadable_target_exits_two_not_zero`,
  `test_default_file_is_dev_null_readable_zero_anchors`, `test_live_authority_anchors_all_resolve`).
- **MISCONFIGURED detector (`run-unit-tests.sh:60-74`) and KIND-DRIFT detector (`:76-140`)
  unmodified by T-24**: `git diff 7ebfc9e..8a7c75c -- .claude/skills/harness/bin/run-unit-tests.sh`
  shows exactly **one hunk**, touching only line 31 (the `INTEGRATION_SCRIPTS` array literal,
  which the diff shows only *adding* `"test-check-decision-anchors.py"` — its earlier removal of
  `"test-check-decision-claims.py"` at 7ebfc9e nets to nothing visible in a squashed range-diff
  because that entry was itself added and removed within this same 40-commit range). Lines 55-157
  (both detectors, `ALL_SCRIPTS` union, `CHECK_KINDS_ONLY` gate) are outside every hunk — read
  directly at their current location and confirmed structurally intact (drift loop, `bad` counter,
  `exit 2` paths unchanged).

## SC evidence pointers

| SC | Test |
|---|---|
| SC-14 | T-24's own verify (deregistration + deletion sweep) + this gate's items 3/4/6/7 |
| SC-15 | T-25's own verify (`detect` string check + `--check-kinds`) + this gate's item 4 |
| SC-16 | T-28's own verify (DEC-205 rule-count repair + index regen diff) |
| SC-17 | `notes/research-FEAT-38-bin-argv-class-audit.md` (T-29) — 70 candidates, 11
  `TEXT-DERIVED-ARGV`, section states "remaining work", not empty |
| SC-11, SC-13 | human inspection / UAT — no standing automated check; this is the accepted,
  signed cost of D-14 (semantic-citation-rot detector deleted, not replaced) |
| SC-09, REQ-08 | tombstones — not graded |

## Non-goals honored

Did not fail on the deletion of `test-check-decision-claims.py` (785 lines, by design). Did not
propose a replacement detector for semantic citation rot — named what carries that weight (human
SC-11/SC-13) instead. Did not touch `plan.yaml`, `review_sha`, or any approval fragment.

## Open questions

- Q1: matrix-fit for bash-runner-registration edits classified `logic` (see Finding under §1-2) —
  non-blocking, informational; no action requested.
