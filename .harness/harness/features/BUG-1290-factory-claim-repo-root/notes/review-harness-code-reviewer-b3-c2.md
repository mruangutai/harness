## Code review — BUG-1290 B-3 fix cycle, pinned `7104aa43` (panel/code, run b3-c2)

**Verdict: PASS.** Test-only delta (`tests/unit/test-factory-claim.py`, +14/-9). Production code
byte-identical to `76e26386` (confirmed: `git diff --stat 76e26386 7104aa43 -- .agents/ .claude/skills/`
is empty). No must_fix. `code_grade: grade_2` (two pre-existing test-harness functions, unaffected
by this delta — see below), severity_max `med`.

### Stage 1 — spec compliance

**REQ-02 ("neither reads the other's ... from cache") / SC-02 ("second candidate does not receive
the first's cached task").** I did not accept the orchestrator's mutant numbers; I re-ran all four
mutant combinations myself, in-process, by monkeypatching `_BlockerCache._plan` /
`_BlockerCache.issue_number` to key on `feature` alone (discarding `repo`) and executing the real
test file (old content fetched via `git show <sha>:...` and `exec`'d with `__file__` pointed at the
real path so the anchor-relative `sys.path` setup still resolves; production code untouched):

| mutant | @ 76e26386 (before) | @ 7104aa43 (after) |
|---|---|---|
| `issue_number` keyed on `feature` | 5b **ok** (blind — matches "B-3 reported this") | 5b **FAIL** (caught) |
| `_plan` keyed on `feature` | 5b **FAIL** (caught) | 5b **FAIL** (caught — unweakened) |
| none | 124/124 | 124/124 |

**Q1 (does the new coverage hold): yes**, independently reproduced. The mechanism: pre-fix,
`harness_seg`'s `T-77` task had no `depends_on` at all (`plan_dict(SEG_FEATURE, [task_dict("T-77")])`
at `76e26386`), so `_blocker_gate` returned clear before ever calling `issue_number` for the harness
segment — the issue-map cache was never exercised on that side, hence "blind." The fix gives
harness's `T-77` a real dependency (`depends_on=["T-99"]`, `tests/unit/test-factory-claim.py:382`)
resolved via harness's own map (`"T-99": 954`, line 383) to a closed issue, forcing a real
cross-segment `issue_number` call that a feature-keyed cache would corrupt.

**Q2 (did strengthening issue-map half weaken plan half): no.** The plan-cache mutant is still red
at `7104aa43`, confirmed by direct execution above (`_plan` keyed on `feature` → 5b FAIL, same as
`76e26386`). Both segments' plans stay distinguishing tasks (`T-77 depends_on T-88` vs `T-77
depends_on T-99`), untouched by this diff.

**Q3 (does anything else now assert less): enumerated, answer is no, with one caveat.**
Grepped the full 1278-line file for `REPO_KAYA`, `REPO_HARNESS_SEG`, `SEG_FEATURE` — every hit is
inside the constant declarations (lines 69-71), `build_features_root()` itself (349-386), or cases
5a/5b (1160-1210). Zero hits in 5c-5f, M/C/R/B/X/P. Those series use `FEAT-01-demo`/`FEAT-02-block`
under the untouched `widget` segment (`build_features_root` lines ~349-373, not touched by this
diff) or fixtures unrelated to `build_features_root` entirely (5c uses a synthetic missing path).
No case outside 5a/5b depends on the two changed segment roots or their issue maps.

**Caveat — one piece of the new fixture data is inert.** The docstring (lines 335-340) and the
kaya `feature.json` edit (`{"T-77": 850}`, line 378) present kaya's map as deliberately
"non-empty, differing" to strengthen the proof. I tested this directly: reverting kaya's map back
to `{}` while keeping harness's `T-99` dependency intact still yields 124/124 unmutated **and**
still catches the `issue_number` mutant identically (5b FAILs the same way). The `"T-77": 850` entry
is never read by any code path 5a/5b exercise — `_blocker_gate` only calls `issue_number` for a
task's `depends_on` entries, and kaya's `T-77` depends on `T-88`, never on itself. The actual
discriminating change is entirely on the harness side (`depends_on=["T-99"]` + `"T-99": 954`); the
kaya-side "non-empty map" detail is decorative, not a second point of proof, despite the docstring's
phrasing implying it carries weight. Not a defect — nothing is weakened — but the docstring
overstates what this specific literal buys. Reported as a low finding (F-1) below.

**Feature-directory bookkeeping.** `plan.yaml`'s diff is empty (zero bytes changed) — no tasks,
decisions, or approval touched. `feature.json` only updates `review_sha`/`cycles_used` and appends
two run-history entries (`validator`/`product`, both `PASS`). `STATE.md` is narrative only. No
scope leakage.

### Stage 2 — code quality

- **F-1** (low): `test-factory-claim.py:335-340,378` — the `build_features_root` docstring frames
  kaya's `"T-77": 850` issue-map entry as part of the cache-separation proof ("DIFFERENT
  non-empty issue maps ... kaya-ai's ... own map holds only T-77, never T-88"); verified by mutation
  (see Q3 caveat) that this entry is never consumed by any exercised code path and contributes zero
  discriminating power. Advisory only — the claim is literally true, just not load-bearing.
- No correctness bugs, silent-failure paths, or copy-paste divergence introduced by the diff itself.
  `factory_claim.py`/`factory_config.py` untouched (confirmed via `git diff --stat` above); not
  re-reviewed on the merits per the dispatch's non-goals.

**code_grade.** Ran `code-grade.py --base $(git merge-base origin/main 7104aa43) --head 7104aa43`
(merge-base `6e95435a`, per DEC-209 — never the B-3-only range). Result: 13 PASS, 2 FAIL-but-med
(`grade_2`), 0 grade-1, 0 production functions below bar. Re-ran the SAME tool at `base=76e26386
head=7104aa43` (the B-3-only range): 0 records — neither flagged function's grade moved during
B-3, confirming both are pre-existing debt from the earlier T-01/T-03 build, not introduced or
worsened by this test-only fix.

- `tests/unit/test-factory-claim.py:324 build_features_root` — ABC 33.5 (bar 3), driver=abc,
  cyclomatic 1, cognitive 0. **Reason:** pure sequential fixture assembly (four segments'
  `write_yaml`/`write_json` calls, no branches, no loops) — ABC is high because each fixture write
  is its own call/assignment, not because the function is hard to follow top-to-bottom. Accepted.
- `tests/unit/test-factory-claim.py:403 run_main` — ABC 26.7 (bar 3), cyclomatic 6, cognitive 9.
  **Reason:** the single shared test-harness driver every one of the file's ~124 checks calls
  through (patches `gh`, builds argv, captures stdout/stderr, restores four monkeypatched
  globals in `finally`) — legitimately touches many collaborators once, in one place, rather than
  duplicating that wiring per case. Splitting it would fragment the one per-invocation contract the
  whole suite relies on. Accepted, pre-existing.

### Findings summary

| id | severity | one-line |
|---|---|---|
| F-1 | low | kaya's `"T-77": 850` issue-map fixture entry is inert (verified by mutation); docstring overstates its role |
| CG-1 | med | `build_features_root` grade 2 (ABC 33.5), pre-existing, reasoned above |
| CG-2 | med | `run_main` grade 2 (ABC 26.7), pre-existing, reasoned above |

No must_fix. Nothing gates.
