# Plan amendment c13 — BUG-1309 — panel c7 rulings R-1/R-2/R-3 landed in plan.yaml

**All four amendments applied through `plan-merge.py`, compare-and-swap on every field, `approval:`
byte-identical.** The signed plan now specifies the three panel remedies as behaviour, and three
decisions record the operator's ruling. **Two blocking questions remain for the operator** — the
amended spec is under-covered by the re-signed BRIEF (below), and neither is fixable by an edit here.

## What changed (new line ranges, post-amendment)

| field | new range | change |
|---|---|---|
| `tasks` T-04 `intent` | 781–952 (value 782–952) | non-era `recovery-required` notice: command **derived** at emission from `feature_schema.recovery_command_for(feat_dir)`, names exactly what it returns, ` --yes` only for `recover-terminal`, **no `open` token in any form** on that horn; the shipped sentence retained verbatim on the `open` horn; **no second hardcoded string** (that is the R-3 defect). Era-exempt half and the six `T-04 …` case names untouched. |
| `tasks` T-05 `intent` step 2 DETECT | block 996–1020 (changed 1000–1020) | flag-aware **ordered walk** consuming value-taking git globals before testing the subcommand; the globals named as a **class with examples** (`-C`, `-c`, `--work-tree`, `--git-dir`, `--namespace`, `--exec-path`, `--config-env`, attached or next-token); shell-variable indirection and depth past `nested_merge`'s cap recorded **out of scope** per R-2. |
| `tasks` T-05 `intent` step 4 LOCATE | 1032–1056 | zero / one / **two-or-more owners**: ambiguity **DENIES** naming every claiming feature id, sorted; attribution bound restated (unreadable, non-object or non-matching records are **skipped and can never refuse**; one owner + noise is **not** ambiguity), citing `894adc0f` after panel c5 failed `473d82cb`; decided before the era gate, since the era rule presupposes one identified feature. |
| `tasks` T-05 `verify` | 973–982 (value 974–982) | **19 case names** — the 14 originals in order, plus the 5 named in the dispatch. `|` literal block; the `test-omp-hooks.py`, `merge-settings.py --check` and `all 9 prerequisites present (8 hooks` lines byte-identical. |
| `decisions` | D-13 203–224, D-14 225–243, D-15 244–262 | one per finding: D-13 PANEL-1/R-1 (`dec: DEC-174`), D-14 PANEL-2/R-2 (`dec: DEC-174`), D-15 PANEL-3/R-3 (`dec: none`). D-01..D-12 undisturbed. |

Compare-and-swap: T-04 `intent` on `a80a7dfd…b75aa`, T-05 `intent` on `5a1b77e8…5de4a9`, T-05 `verify`
on `cf25387c…a7b723`. All three `AMENDED`, exit 0, first try; `--show` after each returned bytes
identical to the value file. `plan-merge.py apply` added D-13/D-14/D-15 (union, no existing entry
touched). T-05 `verify` at dispatch time matched the dispatch's verbatim block exactly.

## Acceptance evidence

- `harness_yaml.load_file(plan.yaml)` exits 0; `decisions` = D-01..D-15; `T-05.verify` still a
  9-newline literal block starting `out=$(python3 tests/integration/test-merge-gate.py)`.
- **`approval:` untouched.** `git diff -U0 -- plan.yaml` hunk headers: `@@ -202,0 +203,60 @@`,
  `@@ -776,6 +836,29 @@`, `@@ -790,2 +873,3 @@`, `@@ -892 +976 @@`, `@@ -916 +1000,21 @@`,
  `@@ -928,3 +1032,25 @@`. The `approval:` mapping is lines 3–23; the earliest changed line is 203.
  Post-amend read-back: `date: 2026-09-04`, `status: approved`, 4 `rulings` entries — unchanged.
  (The plan signature therefore does **not** yet cover this amended text; `sign-approval` is the main
  session's act, not pm's.)
- `check-plan-routes.py <this plan>` → `0 violation(s)`, exit 0. The 6 `DEVIATION` lines are the
  expected DEC-174 carve-out output and do not gate.

## BRIEF success criteria vs the amended spec — stated explicitly

Read `BRIEF.md:84-151` (SC-01..SC-10, re-signed `ea0bdd6b`, 2026-09-08). Verdicts:

- **SC-01, SC-02, SC-05..SC-10: unaffected.** No amended clause touches their subjects. SC-10's UAT
  ("normal merge command … refused … then allowed") stays true under both amended rules.
- **SC-04 covers R-2 by its own words** — `git -C <d> merge X` *is* "a merge command issued for a
  feature", so the three new detection cases sit inside SC-04's existing quantifier. No SC change
  needed for PANEL-2.
- **SC-04 UNDER-COVERS R-1 (blocking, Q1).** SC-04 enumerates deny only for a *single* feature whose
  outcome is `recovery-required` or absent, and pins the reason shape as "naming the feature and the
  re-run command". The new ambiguity DENY names **several** features and **no** re-run command (none
  clears a duplicated branch claim). No criterion covers a two-or-more-owner deny, so
  `T-05 duplicate valid records claiming the branch deny naming both` and
  `T-05 single owner plus unrelated malformed record still allows` trace to no SC. Not a
  contradiction — SC-04's clauses each presuppose one owner — but the outcome would ship ungraded.
- **SC-03 UNDER-COVERS R-3 (blocking, Q2).** SC-03's station-choice clause governs the *refusal* line
  on an absent receipt, not the `recovery-required` **continue** line that R-3 amends; and this batch
  was scoped to four amendments, so **T-04's `verify` case list is unchanged and names no case for the
  recover-terminal horn**. As it stands the R-3 remedy has zero automated evidence: the exact PANEL-3
  harm (the notice naming `open` where the classifier says `recover-terminal`) would be asserted by
  nothing. Fixing this needs a new `T-04 …` case name plus a `verify` extension — a further plan
  amendment, or an explicit `## Verification gaps` disclosure. Operator's call, not an edit here.

## Open questions

- **Q1 (blocking)** — SC-04 does not cover the ambiguity DENY and its reason shape assumes one owner.
  Widen SC-04, add an SC, or accept it as a disclosed gap? BRIEF was re-signed today; pm does not edit it.
- **Q2 (blocking)** — R-3's remedy has no named test case. Authorise a fifth amendment adding a
  `T-04 recovery-required non-era names the derived command` case to T-04's `intent` + `verify`, or
  record the gap in BRIEF `## Verification gaps`?
- **Q3 (non-blocking, per dispatch)** — the non-era `MERGE is refused` clause is now **conditional**
  on the `open` horn. The existing case that asserts that substring stays valid: its fixture's
  `plan.yaml` records no task status, so `recovery_command_for` returns `open`. The amended intent
  states this and instructs the implementer to keep that fixture on that horn; the case itself was
  **not** edited.
- **Q4 (non-blocking)** — the plan signature (`2026-09-04`) predates this amended text. `amend`
  leaves it byte-identical by design; `plan-merge.py sign-approval` before ship is the main session's.
