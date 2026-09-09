# Receipt — harness-dev-ops — deccite-eng

## Task
Fix stale DEC citations in two test files (comments/docstrings only), per FEAT-56 integration
correction. Only two files may be written:
- tests/unit/test-no-distribution.py
- tests/integration/test-onboarding-split.py

## Pre-edit git status (baseline, unfiltered)
```
 M .harness/README.md
 M .harness/harness/docs/BUILD.md
 M .harness/harness/docs/DECISIONS-INDEX.md
 M .harness/harness/docs/DECISIONS.md
 M .harness/harness/docs/SPEC.md
 M .harness/harness/docs/org.html
 M .harness/harness/features/FEAT-56-central-onboarding-model/observations/harness-documentor.md
 M .harness/harness/features/FEAT-56-central-onboarding-model/observations/harness-pm.md
 M .harness/harness/features/FEAT-56-central-onboarding-model/plan.yaml
 M README.md
 M tests/integration/test-check-state-records.py
?? .harness/harness/features/FEAT-56-central-onboarding-model/notes/receipt-harness-dev-ops-rehome-eng.md
?? .harness/harness/features/FEAT-56-central-onboarding-model/notes/receipt-harness-documentor-renumber-product.md
?? .harness/harness/features/FEAT-56-central-onboarding-model/notes/receipt-harness-pm-renumber-product.md
```
(Note: test-check-state-records.py already re-homed under tests/integration/ per sibling's landed work — untouched by me.)

## Grep results (own, re-derived — pattern `DEC-2[0-9][0-9]`)
- `tests/unit/test-no-distribution.py:84` — `# split (DEC-221) the four canonical doors live under .omp/commands, and`
- `tests/integration/test-onboarding-split.py:5` — `` (fresh-checkout configuration only) and `harness-add-repo` (fleet-member registration only, DEC-221). ``
Also present, correctly untouched: `test-no-distribution.py:83` cites DEC-149 (codebase map tier retirement) — different decision, out of scope.

Exactly one DEC-2xx hit per file matching the lead's prior read; no additional hits found.

## Classification table

| File | Line | Citation as found | Subject (my words) | Changed? | Why |
|---|---|---|---|---|---|
| tests/unit/test-no-distribution.py | 84 | `DEC-221` in "After the onboarding split (DEC-221) the four canonical doors live under .omp/commands" | The sentence is explaining that the onboarding skill was split into two artifacts (implying `.omp/commands` reorganization followed the two-skill split), i.e. the subject is the split of the one onboarding skill into two skills/doors, not the fleet-registration model (harness.json/fleet.yaml/product-resident file). | Yes | Subject is the two-skill split (harness-init vs harness-add-repo), which is DEC-222 per contract; DEC-221 (fleet-registration model) does not describe a "split" and would be a wrong citation left in place. |
| tests/integration/test-onboarding-split.py | 5 | `DEC-221` in "`harness-add-repo` (fleet-member registration only, DEC-221)" | The whole docstring paragraph (lines 4-8) states: "FEAT-56 cut the one combined onboarding skill into two: harness-init ... and harness-add-repo ... The two must stay disjoint." The DEC-221 citation sits inside this two-skill-split sentence, attached to describing harness-add-repo's half of the split. | Yes | Subject of the paragraph and the specific clause is the two-skill split (cutting one skill into two disjoint skills), which is DEC-222 per contract, not the fleet-registration model. |

## Test runs (both exit 0)

`env -u HARNESS_AGENT_TYPE python3 tests/unit/test-no-distribution.py` — 35 cases collected, all PASS,
tail: `ALL PASS`, exit 0.

`env -u HARNESS_AGENT_TYPE python3 tests/integration/test-onboarding-split.py` — 24 cases collected,
all PASS, tail: `EXIT=0`, exit 0.

## Diff (comment/docstring-only, full)
```
--- a/tests/integration/test-onboarding-split.py
+++ b/tests/integration/test-onboarding-split.py
@@ -2,7 +2,7 @@
-(fresh-checkout configuration only) and `harness-add-repo` (fleet-member registration only, DEC-221).
+(fresh-checkout configuration only) and `harness-add-repo` (fleet-member registration only, DEC-222).

--- a/tests/unit/test-no-distribution.py
+++ b/tests/unit/test-no-distribution.py
@@ -81,7 +81,7 @@ def case1():
-    # split (DEC-221) the four canonical doors live under .omp/commands, and
+    # split (DEC-222) the four canonical doors live under .omp/commands, and
```
Both hunks touch only a comment line and a docstring line respectively — no assertion, fixture,
`check(...)` call, case registration, or case-name string was altered.

## Post-edit `git status --porcelain` (unfiltered)
```
 M .harness/README.md
 M .harness/harness/docs/BUILD.md
 M .harness/harness/docs/DECISIONS-INDEX.md
 M .harness/harness/docs/DECISIONS.md
 M .harness/harness/docs/SPEC.md
 M .harness/harness/docs/org.html
 M .harness/harness/features/FEAT-56-central-onboarding-model/observations/harness-documentor.md
 M .harness/harness/features/FEAT-56-central-onboarding-model/observations/harness-pm.md
 M .harness/harness/features/FEAT-56-central-onboarding-model/plan.yaml
 M README.md
 M tests/integration/test-check-state-records.py
 M tests/integration/test-onboarding-split.py
 M tests/unit/test-no-distribution.py
?? .harness/harness/features/FEAT-56-central-onboarding-model/notes/receipt-harness-dev-ops-deccite-eng.md
?? .harness/harness/features/FEAT-56-central-onboarding-model/notes/receipt-harness-dev-ops-rehome-eng.md
?? .harness/harness/features/FEAT-56-central-onboarding-model/notes/receipt-harness-documentor-renumber-product.md
?? .harness/harness/features/FEAT-56-central-onboarding-model/notes/receipt-harness-pm-renumber-product.md
```

Sibling entries I did not touch (confirmed unchanged by me — pre-existing on entry, per baseline
snapshot above): `.harness/README.md`, `.harness/harness/docs/BUILD.md`,
`.harness/harness/docs/DECISIONS-INDEX.md`, `.harness/harness/docs/DECISIONS.md`,
`.harness/harness/docs/SPEC.md`, `.harness/harness/docs/org.html`, `README.md` (documentor's docs
work), `.harness/harness/features/FEAT-56-central-onboarding-model/plan.yaml` (SIGNED plan, untouched),
the two `observations/*.md` files, `tests/integration/test-check-state-records.py` (the re-homed unit
test, landed by a sibling), and the three pre-existing receipt files
(`receipt-harness-dev-ops-rehome-eng.md`, `receipt-harness-documentor-renumber-product.md`,
`receipt-harness-pm-renumber-product.md`). My own diff adds exactly two modified files
(`tests/unit/test-no-distribution.py`, `tests/integration/test-onboarding-split.py`) plus this one new
receipt — nothing beyond that.

No `git add`, no `git commit`, no `git checkout`/`reset`/`rebase`/`merge` run at any point. HEAD
unmoved (still merge commit bb39d5c4, per dispatch).

## Conclusion
Both stale DEC-221 citations (subject in both cases: the two-skill split of onboarding into
`harness-init` + `harness-add-repo`) corrected to DEC-222. No other DEC-2xx citation found in either
file. No fleet-registration-model citation existed in either file to leave alone. VERDICT: PASS.
