# Confirmation review — PR #385, pinned 6296149 (was a714bd0), base 3c75aa6

**BLUF: PASS.** All three must-fix findings (M-1, M-2, M-3) verified fixed by execution, not by
reading. No must-fix candidates this round; two low/info notes, one repeated-not-new advisory.

## 1. DEC-194 verbatim restoration — PROVEN, byte-identical

`git show 3c75aa6:docs/harness/DECISIONS.md` and `git show 6296149:...` at lines 5834-5897 (the
base entry body, before `### DEC-194 amendment 1` at 5898 in both): `diff` exit 0, and both blobs
hash to the same SHA-256 (`4621b6f3...f8312a6`). Byte-identical, not eyeballed.

## 2. Amendment 2 vs the post-M-1 code

- **Every cause appends blame(), matching code.** `check-state.sh:1295-1319`'s `_cv_wording` now
  computes `_named = ...blame(_srep)` and appends it unconditionally for every cause reached (the
  `unrecognised cause` branch at :1314-1316 returns first and correctly skips it — a defensive
  path, not a regression). `layout_migration.py:318-320`'s `render()` already called `blame()`
  unconditionally. Confirmed by **execution**, not inspection: constructed a tree with an
  `undeclared-segment` on `features` plus a `check-state.sh`-reader forced to the `migrated`
  pattern. Both surfaces now agree —
  `render()`: `"...undeclared segment: ...; .claude/skills/harness/bin/check-state.sh [migrated]"`
  `check-state.sh` live run: `"...UNDECLARED segment: ... — .claude/skills/harness/bin/check-state.sh [migrated]"`
  — the exact divergence c1 reproduced with a synthetic `SurfaceReport` no longer reproduces on a
  real tree through the real script.
- **The "reader-less causes" label is imprecise — flag, not block.** Amendment 2 calls
  `no-evidence, no-rows, undeclared-segment` "the three reader-less causes" and says `blame() may
  return an empty list` for them. Checked against `scan()`'s branch order
  (`layout_migration.py:233,236,246`): only `no-rows` passes `readers=[]` and is **structurally**
  always empty. `undeclared-segment` (:236) and `no-evidence` (:246) pass the real reader list and
  — as the probe above and the prior M-1 finding both show — **can** carry a non-empty blame list.
  The hedge "may return an empty list" is literally true and not flatly false (it never claims
  "always empty"), so this does **not** repeat c1's error outright, but the label "reader-less"
  applied to all three uniformly undersells that two of the three can name a reader. A future
  maintainer skimming the label alone could reintroduce per-cause filtering on exactly the
  mistaken belief M-1 disproved. Low severity: doc-precision risk, not a code defect — the code is
  correct and unconditional at both sites regardless of what the label implies.
- **Ruling framed as a ruling, not backdated design.** "ruled by the operator after validator
  finding M-1 (2026-08-14)" — correct, matches the dispatch's ordering constraint.
- **Format matches siblings exactly.** `### DEC-194 amendment 2 (2026-08-14) — blame is one
  exported policy, rendered whole at both call sites` — same shape as `### DEC-193 amendment 1
  (2026-08-12) — "preserved" was too wide by one column` and `### DEC-194 amendment 1 (2026-08-14)
  — the applicability marker is the fleet declaration...`.

## 3. Index and plan alignment — clean

`docs/harness/DECISIONS-INDEX.md:212` reads `am.1-am.2`. Not hand-verified by eye: ran
`gen-decisions-index.py --stdout | diff - docs/harness/DECISIONS-INDEX.md` at HEAD (=6296149,
working tree clean) — exit 0, the committed index is exactly the generator's output, including the
tag reorder (`[docs,plan,state,dispatch]` → `[docs,state,plan,dispatch]`), which is the generator's
own frequency-scored tag ordering, not tampering. `@5834` anchor still points at the DEC-194
heading (confirmed at that line). `plan.yaml:660-670` now cites "DEC-194 am.2", restates the same
"reader-less causes yield an empty list" phrasing (same imprecision as §2, not a new instance —
consistent with the authority text) and does not contradict the restored (byte-identical) base
sentence.

## 4. `_cv_wording` as code — no defects found

- `callable(_fmt)` is safe: the closed 5-entry table holds only plain `str` or `lambda` values;
  `callable(str_instance)` is always `False`. No third type ever reaches this line.
- The `unrecognised cause` early return (:1314-1316) correctly precedes and skips the
  `blame()`/`_named` computation — confirmed intentional and correct, not merely accidental: an
  unrecognised cause means the two modules' cause tables disagree, and naming readers under an
  undefined semantics would be worse than the loud fallback.
- Em-dash join: verified no dangling separator in any of the 5 causes (when `_named` is empty,
  `" — " + _named` is skipped entirely, not emitted empty). One info-level style note:
  `undeclared-segment`'s base text already ends in its own em-dash clause ("...or move this out of
  `.harness/`"), so a non-empty blame list produces two dashes in one rendered sentence (reproduced
  above). Not wrong, not gating — just mildly informal.

## 5. No regression outside the claimed surface

`a714bd0..6296149 --stat` touches exactly: `check-state.sh` (M-1), `test-check-state.py` (M-2, pure
deletion, -1148/+0), `DECISIONS.md`/`DECISIONS-INDEX.md` (M-3), `plan.yaml` (am.2 citation),
`.harness/members/backend-dev/{FEAT-02-t01,t02}.md` (now actually **committed** deletions — resolves
the prior FAIL digest's Q1), `.harness/logs/2026-08-14.md` (bookkeeping), and four review
artifacts + observations. `6296149` itself is log-only (`git diff a094dac..6296149 --stat` = 1 file,
`.harness/logs/2026-08-14.md`, +4/-0). No `[harness:human]` commits in `3c75aa6..6296149`
(`git log --format='%H %ci %an'`, no `human` marker). `3c75aa6..6296149` net stat matches PR #385's
scope: `check-state.sh`, `layout_fixtures.py` (new), `layout_migration.py`, `test-check-state.py`,
`test-layout-migration.py`, the two decision files, `plan.yaml`, log, member deletions, review
artifacts.

**M-2 acceptance, verified exhaustively, not just on `case_*` names.** Exactly one `def case_x`
(`test-check-state.py:1585`), imports `layout_fixtures` (`:1595`). An AST walk of every top-level
`FunctionDef`, `ClassDef` and simple `Assign` target name in the file (not just names matching
`^def case_`) finds **zero** duplicates — the 17 doubled names qa measured pre-fix are now unique
across the whole top-level namespace, not merely the ones named `case_*`. Both `test-check-state.py`
and `test-layout-migration.py` run clean: exit 0, 0 `FAIL` lines in either.

## 6. Residual, repeated not new — unpinned against regression

`grep -n "blame\|379" test-check-state.py test-layout-migration.py` still returns **zero** after the
fix. The M-1 fix landed correct (proven above by execution) but with no test asserting CI/session-entry
parity on any cause, so a future re-filtering regression (the same defect, twice already) would not
be caught by the suite. This is the prior panel's A-2, still true post-fix — not re-filed as new,
surfaced because the fix commit was the natural place to close it and didn't.

## Rejected candidates

- Treating the "reader-less causes" imprecision (§2) as a repeat of c1's must-fix-grade error —
  rejected as stated: the hedge ("may return an empty list") never asserts the false claim outright,
  and the code itself is correct and empirically verified in both directions. Kept as a low
  precision note, not promoted.
- Treating the double-dash rendering on `undeclared-segment` (§4) as a UI/wording defect — rejected,
  ui's domain and cosmetic; noted at info only.
- Trusting a `case_*`-only duplicate-name grep as proof of M-2's acceptance — rejected as
  insufficient on its own: 17 doubled names (qa's measured count) exceeds the 14 `case_*` names
  c1 enumerated, so a name-pattern-scoped sweep could have missed a surviving duplicate outside the
  `case_` family. Replaced with the exhaustive AST walk in §5 before shipping the claim.

```yaml
VERDICT: PASS
DIGEST:
  headline: "All three must-fix findings from the FAIL round are verified fixed by execution at 6296149: DEC-194's base body is byte-identical (SHA-256) to pre-#385, amendment 2 correctly describes the settled blame-on-every-cause behaviour and is empirically reproduced live (render() and check-state.sh now name the same reader on a constructed undeclared-segment+disagreeing-reader tree), and test-check-state.py's shadowed duplicate region is gone with zero top-level name collisions by exhaustive AST check and both unit suites green; one low-severity doc-precision note and one repeated (not new) coverage advisory remain."
  severity_max: low
  findings: 3
  must_fix: []
  spec_violations: []
  reviewed: "3c75aa6..6296149"
  human_commits_in_scope: []
  open_questions:
    - { id: Q1, question: "DEC-194 amendment 2 labels no-evidence/no-rows/undeclared-segment uniformly as 'the three reader-less causes' while hedging blame() 'may return an empty list' for them — only no-rows is structurally always-empty (readers=[] at layout_migration.py:233); undeclared-segment and no-evidence can carry a non-empty blame list, as reproduced live. The hedge keeps the sentence technically true, but the label risks a future maintainer reintroducing per-cause filtering on the same false premise M-1 disproved. Worth a follow-up wording pass, not a blocker.", blocking: false }
    - { id: Q2, question: "Neither test-check-state.py nor test-layout-migration.py asserts blame()/#379 CI-vs-session-entry parity for any cause (grep for 'blame' or '379' returns zero in both, pre- and post-fix). The fix is correct but unpinned against a third regression. Carried forward from the prior panel's A-2, not re-filed as new.", blocking: false }
  files_touched: [.harness/features/FEAT-20-migration-detector/notes/review-harness-code-reviewer-hygiene-c2.md]
  expertise_update: []
artifact: .harness/features/FEAT-20-migration-detector/notes/review-harness-code-reviewer-hygiene-c2.md
```
