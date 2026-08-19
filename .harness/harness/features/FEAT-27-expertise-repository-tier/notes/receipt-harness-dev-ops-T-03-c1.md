# Receipt — harness-dev-ops — T-03 — cycle 1

**BLUF: PASS.** Both CHANGE 1 (per-tier line budget, classified on `os.path.abspath`) and
CHANGE 2 (advisory-only repository-token scan, CRAFT-tier only) are implemented in
`.claude/skills/harness/bin/check-expertise.sh`. All 6 new case groups (22 individual
assertions) added to `.claude/skills/harness/bin/test-check-expertise.py`. Verify passed
verbatim, exit 0.

## Verify — exact command run, verbatim from plan.yaml T-03

```
set -u
out=$(.claude/skills/harness/bin/run-unit-tests.sh --kind integration 2>&1)
echo "$out"
echo "$out" | grep -q '^PASS test-check-expertise.py$' || exit 1
echo "$out" | grep -q '^FAIL ' && exit 1
live=$(.claude/skills/harness/bin/check-expertise.sh .harness/expertise/ 2>&1)
rc=$?
echo "$live"
[ "$rc" = 0 ] || { echo "live craft dir no longer exits 0"; exit 1; }
echo "$live" | grep -q '^ADVISORY ' || { echo "no advisory line on the live craft dir"; exit 1; }
exit 0
```
Cross-checked byte-for-byte against `plan.yaml`'s T-03 `verify:` field before running — identical.

**Result: exit 0.** Final line of output: `OK   .harness/expertise/harness-visual-designer.md`.
No `^FAIL ` line anywhere in the integration suite. `PASS test-check-expertise.py` present.
Live craft dir (`.harness/expertise/`) exits 0 and carries multiple `^ADVISORY ` lines (e.g.
`ADVISORY .harness/expertise/harness-pm.md:4: P-01 names '.harness/' — repository-layer
candidate; rule on it (issue 340)`).

## STEP 1 — baseline

1. `git show b4659cd:...check-expertise.sh | diff - <working>` → **empty**, no drift.
2. `run-unit-tests.sh --kind integration` pre-change: exit 0, 106/106 checks in
   test-factory-integration.py, and every `PASS <name>` line present incl.
   `PASS test-check-expertise.py`; **zero `^FAIL ` lines**.
3. `check-expertise.sh .harness/expertise/` pre-change: exit 0, all 15 files `OK`, **no**
   `^ADVISORY ` line (scan didn't exist yet).
4. `git status --porcelain` baseline: T-02's dirt only (`inject-expertise.sh`,
   `run-unit-tests.sh` modified; `test-inject-expertise.py` untracked) plus unrelated
   FEAT-24/25/26 dirs and FEAT-27 STATE/feature.json/plan.yaml/notes/observations churn from
   other in-flight sessions. Not mine, left untouched.

## STEP 2 — the work

- `check-expertise.sh:36-64` — `CRAFT_LINE_BUDGET=150`, `REPO_LINE_BUDGET=40`,
  `CRAFT_TIER_RE`/`REPO_TIER_RE`, `classify_tier()` on `os.path.abspath(path)`.
- `check-expertise.sh:74-75` — over-budget message now names the applied budget.
- `check-expertise.sh:146-153` — advisory scan, CRAFT-tier only, `REPO_TOKEN_RE` verbatim
  from issue 340's token set, appended to a separate `advisories` list — never `problems`.
- `check-expertise.sh:155-163` — advisories print after the `OK`/`FAIL` line, for both
  outcomes (not special-cased on pass/fail, per intent's "must not be special-cased" for
  the FEAT-\d+ dual-hit case).
- `test-check-expertise.py:87-235` — new `run_extra()` harness (own tempdir/subprocess
  helpers, since the existing `case()` helper can't build `.harness/expertise/...` and
  `.harness/<seg>/expertise/...` directory shapes) implementing cases 1–6 exactly as
  specified, `__main__` now runs both `run()` and `run_extra()` and fails on either.

## STEP 3 — pre-change RED proof (pinned `b4659cd` via `CHECK_EXPERTISE_BIN`)

Overall: 9/22 extra cases passed pre-change, 13 failed. Split against the pre-decided list:

**Genuine reds (matched prediction):**
- case1 first half (ADVISORY / DEC-042 assertions) — 2 assertions failed as predicted.
- case2 — 9 of 10 token sub-cases failed as predicted (see delta below).
- case5 first sub-case (41-line repo-form over budget, names 40) — failed as predicted.
- case6 (bare-path invocation, abspath discriminator) — failed as predicted.

**Vacuous passes (matched prediction, reason labelled):**
- case1 second half (token-removed, no ADVISORY) — passed because no scan exists pre-change,
  not because the logic is right.
- case4 (repository-tier exemption) — passed for the same reason: no scan exists pre-change.
- case3 exit-1 half (token + real violation) — passed because the word-cap violation already
  exits 1 pre-change, independent of the advisory scan.

**Observed delta from the pre-decided split (reported, not corrected):**
- case2's `FEAT-\d+` sub-case was a **vacuous pass**, not a genuine red. `FEAT-12` already
  trips the pre-existing hard `FEATURE_TOKEN_RE` violation, so the assertion (`'FEAT-12'`
  appears in output) is satisfied by that old violation message alone, not by the new scan.
  Logged in the observations file.
- case3 exit-0 half (token + no violation, expect exit 0) and case5's second/third sub-cases
  (41-line craft not reported; 151-line craft reported naming 150) also passed pre-change —
  unsurprising and not contradicting anything, since the old checker already used a flat
  150-line budget and did no scanning, so these were never expected to redden.

## STEP 4 — post-change state

- `run-unit-tests.sh --kind integration`: exit 0, all `PASS`, zero `FAIL`, including
  `PASS test-check-expertise.py` (32/32: 10 base + 22 extra, all `ok`).
- Verify command: exit 0 as reported above.
- `git status --porcelain` after minus baseline: exactly
  `.claude/skills/harness/bin/check-expertise.sh` and
  `.claude/skills/harness/bin/test-check-expertise.py` newly modified by me. Everything else
  unchanged from baseline (T-02's dirt, other in-flight feature dirs). **Confirmed: nothing
  under `.harness/expertise/` or `.harness/harness/expertise/` was created, edited, or
  touched.**

## Counting convention

**22 new cases** by the convention that case 2's ten token files count as ten individual
cases (each is asserted individually per the task's own instruction — "Assert them one at a
time"). Case-group breakdown: case1=5, case2=10, case3=2, case4=1, case5=3, case6=1 → 22.
