# FEAT-43 · validate-delta-c25 — code review of T-01's self-bar closure — PASS

**BLUF:** The delta does exactly what T-01/Q9 demanded and nothing more — six named helpers pull
`_body_hashes.collect` and `gated_set` from grade 2 to grade 4, both `SELF_GRADING_ALLOWLIST`
carve-outs are deleted with no replacement anywhere in `code_grade.py`, and the pre-image
resolution order and sole gating comparison are byte-identical to before. I reproduced every load-
bearing claim myself — the mutation, the allowlist staleness guard, and the 12-demand SC-15 set —
rather than trusting the receipt or the eng digest. One low-severity, non-blocking comment-drift
finding. `must_fix: []`, `severity_max: low`.

**Reviewed:** `d2e3b5eb47c84fdfac5371b924b7ce1bb8fc37ba..e12d53b16e49e7c4d9332c5e290e6bdbc806251f`
(commit `e12d53b` is the sole content-bearing commit in this range; `ea61b5e` and `f3b31d8` inside
it touch only `feature.json`/`STATE.md`/notes — confirmed by `git show --stat` on each — so the
code delta reviewed is exactly the two named files). No `[harness:human]` commit in range. No
send-back was spent in this run — solo review, no team members to send back to.

## Stage 1 — spec compliance

T-01 (`plan.yaml:113-140`, traces `REQ-03`) states unconditionally: "The tool must pass its own
bar." The operator's Q9 ruling refused the two-function exemption outright: "no exemption, fix it."
Every line in the diff traces to this:

- `_qualname`, `_strip_docstring`, `_hash_body` — extracted from `_body_hashes.collect`, the exact
  function named in the refusal.
- `_resolve_base_source`, `_resolve_pre_image`, `_gate_file_records` — extracted from `gated_set`,
  the other named function, and the seam D-01/D-02/D-03 specify.
- Two `SELF_GRADING_ALLOWLIST` lines deleted, no replacement lines added.
- Two new characterization tests (`check_pre_image_resolution_priority`,
  `check_base_source_rename_fallback`) registered in `main()`'s runner tuple.

Nothing here serves a requirement other than T-01/Q9 — no scope creep. Nothing named by T-01/D-01
through D-03 is left unaddressed — no omission. Stage 1 passes.

## Item 1 — behaviour proven, not asserted (my own mutation)

Read at the pin (`code_grade.py:353-430`): `_resolve_pre_image` does `before_names.get(qualname)`
first, returns early if not `None`, then falls to `before_hashes.get(head_hashes[qualname], [])` —
qualname first, hash second, unchanged order. `_resolve_base_source` reads `path` then falls back
to `old_path` only when the first is `None` — rename-aware fallback unchanged. `_gate_file_records`'s
sole gating test is `before is None or record.grade < before.grade` — the same comparison, unmoved.

I performed my own mutation (not merely reviewed the receipt's):

```
$ md5sum code_grade.py test-code-grade.py
c5db829f96b3b8dc8d144a1466392e4d  code_grade.py
a25e2fcd0733aca406b358653d1fa416  test-code-grade.py
$ python3 test-code-grade.py            # baseline
PASS test-code-grade
EXIT:0
```
Edited `_resolve_pre_image` to check `before_hashes` before `before_names` (hash-first instead of
qualname-first):
```python
def _resolve_pre_image(record, before_names, before_hashes, head_hashes):
    matches = before_hashes.get(head_hashes[record.qualname], [])
    if matches:
        return matches[0]
    return before_names.get(record.qualname)
```
```
$ python3 test-code-grade.py
FAIL gated set: expected {'worsened', 'newly_added'}, got {'newly_added'}
FAIL qualname match wins over hash match: expected True, got False
2 failures
EXIT:1
```
Both the new unit-level characterization (`qualname match wins over hash match`, inside
`check_pre_image_resolution_priority`) and the pre-existing integration-level fixture
(`check_changed_function_resolution`'s `gated set` case, driven through the real `gated_set()` API)
fail by name under the reorder — the priority rule is covered at both the helper seam and the
public-API seam, not just one.

Restored:
```
$ git checkout -- code_grade.py
$ md5sum code_grade.py
c5db829f96b3b8dc8d144a1466392e4d          # identical to pre-mutation
$ git status --porcelain -- .claude/skills/harness/bin/code_grade.py .claude/skills/harness/bin/test-code-grade.py
                                            # (empty)
$ python3 test-code-grade.py
PASS test-code-grade
EXIT:0
```

## Item 2 — the carve-out is deleted, not moved

```
$ python3 -c "text=open('test-code-grade.py').read(); \
  s=text.index('SELF_GRADING_ALLOWLIST = {'); e=text.index('\n}\n', s)+3; \
  block=text[s:e]; print(block.count('code_grade.py'))"
0
```
Zero occurrences of the string `code_grade.py` anywhere inside the `SELF_GRADING_ALLOWLIST` block —
not as a key, not in a comment. That settles (a) no entry keys on `code_grade.py` and (b) no
replacement entry for any of the six new helpers, since an entry for a helper in this file would
require the same `"code_grade.py"` filename key. `code_grade.py` is still listed in
`SELF_GRADED_FILES` (line 191), so the file stays covered by `check_self_grading`, not opted out.

To rule out "a guard that simply stopped looking" (the exact trap the assignment names): I
reintroduced a stale entry — `("code_grade.py", "gated_set"): 2` — while leaving the fixed source
untouched, and re-ran:
```
$ python3 test-code-grade.py
FAIL code_grade.py:gated_set allowlisted grade is stale: expected 2, got 4
1 failures
EXIT:1
```
The staleness check (`check_self_grading`, `test-code-grade.py:282-300`) is live: it re-grades
`code_grade.py` on every run and would have caught a reintroduced or silently-repointed entry. This
also independently reconfirms `gated_set`'s actual grade is 4, not 2. Restored:
```
$ git checkout -- test-code-grade.py
$ md5sum test-code-grade.py
a25e2fcd0733aca406b358653d1fa416          # identical to pre-experiment
$ python3 test-code-grade.py
PASS test-code-grade
EXIT:0
```

## Item 3 — SC-15 at the new pin, all 12 demands named and answered

```
$ python3 code-grade.py --base 7ccfae8d --head e12d53b1 > /tmp/gated_output.txt
EXIT:0
$ grep -c '^FUNCTION$' /tmp/gated_output.txt
195
$ grep -c 'REASON REQUIRED' /tmp/gated_output.txt
12
$ grep -c '^RESULT: FAIL' /tmp/gated_output.txt   # 183 PASSING + 12 FAIL(grade_2) = 195
12
```
**Confirms the orchestrator's measurement exactly**: 195 gated records, 12 `REASON REQUIRED`
demands (down from the 14 the prior pin's note answered — the c21 note names 15 originally, but
item 13 (`test-code-grade.py:main`) was already fixed in code before this cycle's pin, per the
comment at `test-code-grade.py:210-212`, leaving 14 live at the prior pin). The two that vanished
between the prior pin and this one are, individually confirmed by extracting `PATH`/`QUALNAME` from
every `REASON REQUIRED` block: **exactly** `_body_hashes.collect` and `gated_set` — no other item's
path/qualname pair disappeared and none appeared new. Every one of the 12 surviving demands is
untouched by this delta's diff (the diff touches only `code_grade.py`'s target functions/helpers and
`test-code-grade.py`'s allowlist/new tests — none of the 12 files-and-qualnames below are in that
diff), so the reasons the prior review recorded remain valid; I restate each here rather than point
at the stale-pin note, per SC-15's own text ("the code reviewer's finding note answers every reason
demand... naming each function").

All 12, current pin, current line numbers:

1. **`check-plan-routes.py:786 main`** (cyc 10, cog 13, abc 30.9, driver abc). The one CLI lifecycle
   joining mode/root selection, owner-manifest resolution (D-11), per-plan processing, deviation and
   invariant-collision accumulation, and the four-way exit status — splitting it scatters the one
   place that owns those exit codes.
2. **`code-grade.py:169 main`** (cyc 9, cog 13, abc 30.4, driver abc). The single CLI entry point
   joining argument validation (`--base`/`--head` XOR `paths`), revision resolution through
   `commit_oid`, path-vs-diff report selection, sort, and text/JSON emission — one coordinated
   decision behind T-03's determinism/exit-status requirement.
3. **`test-check-plan-routes.py:1549 _case_27_owner_manifest`** (cyc 5, cog 2, abc 27.0, driver abc).
   One fixture builder plus assertion couples owner/branch manifest divergence, the `DEVIATION`
   line, the `OK` grant line, and the prior-revision false-`OK` proof SC-16 requires live beside it.
4. **`test-code-grade-cli.py:64 test_paths`** (cyc 5, cog 2, abc 29.8, driver abc). SC-05's
   one-assertion-per-field requirement, in both text and JSON, against the same fixture record — the
   per-field loops belong together so both modes are proven against identical input.
5. **`test-code-grade-cli.py:118 test_rejected_revisions`** (cyc 7, cog 15, abc 43.9, driver abc).
   Proves option-like and blob revisions are rejected identically at `--base` and `--head`, Git is
   never invoked with the raw option, and no file is written as a side effect — one integration
   transaction over `commit_oid`'s full contract.
6. **`test-code-grade-cli.py:165 test_control_paths`** (cyc 6, cog 0, abc 29.1, driver abc). NUL/
   control-byte path handling proven to stay single-line across text, parse-error, and ungraded
   rendering — three renderings of one deliberately shared fixture.
7. **`test-code-grade-cli.py:187 test_bars_follow_test_kinds`** (cyc 6, cog 9, abc 33.3, driver abc).
   SC-17's four-boundary-discriminator fixture; splitting it risks the four cases drifting out of
   the shared `test_kinds` config they must all read from.
8. **`test-code-grade-cli.py:238 test_diff_and_determinism`** (cyc 5, cog 7, abc 40.5, driver abc).
   One repository fixture deliberately coupling deletion handling, odd-path rename resolution,
   CWD-independent determinism, and the injected-order proof against one committed base/head pair.
9. **`test-code-grade.py:121 check_commit_resolution`** (cyc 4, cog 24, abc 24.4, driver cognitive).
   Exercises `commit_oid`'s full contract (valid ref, option-like rejection, blob rejection,
   `^{commit}` peeling) against one synthetic repository built once.
10. **`test-code-grade.py:333 check_changed_function_resolution`** (cyc 5, cog 0, abc 33.3, driver
    abc). The SC-07/SC-08 seven-way fixture — the D-01/D-02/D-03 non-gating proof (this review's
    Item 1 mutation included) depends on all seven cases living in one commit, not fixtures that
    could drift apart.
11. **`test-gate-policy.py:55 check_policy_loading`** (cyc 1, cog 0, abc 36.1, driver abc). SC-13
    requires each of the four gate keys resolved individually plus loud failure on
    missing/invalid/unreadable/unparseable config — one shared temp-config lifecycle keeps all eight
    named cases from paying for their own fixture setup.
12. **`validate-digest.py:549 reviewed_python_change`** (cyc 11, cog 10, abc 18.6, driver
    cyclomatic). The sole gate on `code_grade: n_a`'s legitimacy — REQ-04's drift-detection charter
    exercised as one real code path rather than a decomposed stand-in.

## `code_grade.py`'s own self-grade — independently reconfirmed

```
$ python3 code-grade.py code_grade.py
EXIT:0
$ grep -c '^FUNCTION$' /tmp/self_grade.txt   → 53
$ grep -oE '^GRADE: [0-9]' /tmp/self_grade.txt | sort | uniq -c
     11 GRADE: 4
     42 GRADE: 5
$ grep -c '^RESULT: FAIL'                    → 0
```
53 functions, zero below grade 4 (11 at grade 4 + 42 at grade 5 = 53). Target/new-helper triples,
read from the same run: `_body_hashes.collect` cyc4/cog5/abc8.8 → grade 4; `gated_set`
cyc2/cog1/abc10.0 → grade 4; `_qualname` grade 5; `_strip_docstring` grade 4 (cyclomatic-driven);
`_hash_body` grade 5; `_resolve_base_source` grade 5; `_resolve_pre_image` grade 5;
`_gate_file_records` grade 4 — all match the receipt exactly.

**Before-state, independently re-derived** (not taken from the receipt): checked out
`code_grade.py` at the base pin `d2e3b5eb`, copied it into the bin directory under a scratch name
(outside the repo the tool refuses to grade — `code-grade.py` rejects paths outside the repo, exit
2, confirmed), graded it, then deleted the scratch file (`git status --porcelain` clean
afterward):
```
_body_hashes.collect: cyc=9 cog=18 abc=17.3 grade=2
gated_set: cyc=8 cog=25 abc=24.9 grade=2
```
Both match the orchestrator's and the receipt's "before" figures exactly.

## Stage 2 — code quality

- **[positive]** The extraction earns its keep by the deletion test: inlining any of the six
  helpers back into their caller restores the exact nesting that drove the grade down. None is a
  pass-through.
- **[positive, fail-open hunt]** Every miss in the new/touched code degrades safely: `_resolve_base_source`
  returns `None` on a double miss (path and old_path both absent), which `_gate_file_records`
  turns into `({}, {})` pre-images, which makes every head record's `before` resolve to `None` via
  `_resolve_pre_image`, which the sole gating test (`before is None or ...`) correctly treats as
  "gate it" — a missing pre-image blocks, it does not sail through. Confirmed by reading the branch,
  not inferred.
- **[low, advisory, does not gate]** The range-comment above `SELF_GRADING_ALLOWLIST`
  (`test-code-grade.py:210`) still reads "SC-15 section, items 1-12,14,15", but items 3 and 4
  (the two entries this delta deleted) are no longer represented below it — the aggregate range
  comment is now stale even though every individual `# SC-15 item N` inline comment beside a
  surviving entry is still accurate. This is comment drift introduced by this delta (the two lines
  were removed without touching the summary comment above them). It does not affect behaviour or
  gating — `check_self_grading`'s staleness assertion reads the dict, never the comment — and is
  advisory only.

No other quality issues found. Copy-paste divergence: none — `_qualname` is called identically from
both the function and `ClassDef` branches, `_strip_docstring`'s logic is lifted verbatim (not
reimplemented). No dead code left behind.

## What this delta review did NOT cover

Per the non-goals: the five blockers closed in `runs/validate-final-panel-c21-validator/digest.md`
and `runs/validate-delta-c23-validator/digest.md` were not re-examined (T-02 through T-10, D-11,
SC-05/07/08/09/12/13/14/16/17/19/20, the CLI, `gate_policy.py`, `validate-digest.py`'s wiring, the
glossary, and the skill's worked examples) — I relied on their prior `met` verdicts, since this
delta's diff does not touch any of those files. I did not re-run the canonical/project-wide test
suite or `check-state.sh` (excluded by the assignment; the orchestrator runs those). SC-11's UAT is
untouched (`verify: uat`, explicitly out of scope, and the operator's Q9 ruling records it as not
yet judged). I did not review the two housekeeping commits (`ea61b5e`, `f3b31d8`) beyond confirming
via `git show --stat` that they touch no source — their content (feature bookkeeping, STATE.md,
glossary research notes) is outside a code reviewer's domain.

```yaml
VERDICT: PASS
DIGEST:
  headline: Both grade-2 functions in code_grade.py now grade 4, both allowlist carve-outs are deleted with no replacement anywhere in the file, and the pre-image resolution order/gating comparison are proven unchanged by my own mutation — one low-severity comment-drift finding, non-blocking
  severity_max: low
  findings: 3
  must_fix: []
  spec_violations: []
  reviewed: "d2e3b5eb47c84fdfac5371b924b7ce1bb8fc37ba..e12d53b16e49e7c4d9332c5e290e6bdbc806251f"
  human_commits_in_scope: []
  open_questions: []
  files_touched: []
  expertise_update: []
  code_grade: pass
artifact: .harness/harness/features/FEAT-43-code-risk-grading/notes/review-harness-code-reviewer-validate-delta-c25.md
```
