# FAIL — BUG-1016 code review c2

**R1 is closed by the pinned operator amendment; one new quoted-relative-entry mismatch remains (R2, T-01).** Review range: `af2a958ab06c0d6fc026b363b59fc3147e3982f1..55c99a856321ef9d059b144b6ee2ac2bf1f75096`. Feature pin agrees with dispatch. Complete 39-path census and commit list contain no changed Python paths or `[harness:human]` commits; tracked worktree status was clean. The four implementation/test/decision subjects are unchanged since c1 pin `8211687fd442258a4ae1a50d8e5375228a51b540` (empty pinned diff).

## Stage 1 — amended specification compliance: FAIL

- **R1 closure (inspection, not runtime):** pinned BRIEF Constraints now classifies after trimming and removing one surrounding double-quote pair. `rootTarget` (`.omp/extensions/harness-hooks.ts:354-362`) does exactly that for classification, matching DEC-251 (`.harness/harness/docs/DECISIONS.md:8029-8041`). Former counterexample `path: '"~/notes.md"'` becomes target `~/notes.md`, is explicitly excluded, and correctly returns the original bytes without a rewrite lookup. No code change was required or made.
- SC-01..06 otherwise map to the revised-input helpers, omitted/null defaults, independent list entries, shared edit matcher, readiness/authorization ordering, resolver refusal/cache lifecycle, downstream URI checks, and registered-handler tests (`harness-hooks.ts:75-88,354-405,975-1014,1135-1187,1453-1459`; `tests/unit/omp-hooks.test.ts:1279-1550`). D-01 and T-02 serve these criteria; no unrelated executable changes were found.
- **SC-07 inspection:** read all four subjects using `git show 55c99a85:<path>`: `.harness/harness/docs/DECISIONS.md:8013-8089`, `.harness/harness/docs/DECISIONS-INDEX.md:237`, `.omp/extensions/harness-hooks.ts:354-405,975-1014,1174-1187,1453-1459`, and `tests/unit/omp-hooks.test.ts:1279-1550`. Seven tools, authority, exclusions, defaults, URI policy and silence agree; quoted-entry preservation has the exception below.

**R2 — med / substance / owning task T-01 / SC-01, SC-02, SC-07.** `harness-hooks.ts:355,359-360` locates the unquoted target with `raw.indexOf(target)`. For a relative filename consisting of one double-quote character, represented as three consecutive double quotes (`raw = '"""'`), classification removes the outer pair and produces the nonblank relative target `'"'`. `indexOf` returns 0, the opening wrapper, instead of 1, the target position. With root `/wt`, the revision is `/wt/"""`; the contract requires `"/wt/""` (opening quote, root prefix, target quote, closing quote). The root is inserted outside the surrounding pair, contrary to the amended preservation constraint. The same `rootTarget` is used for an edit's quoted `MV` destination. This is a concrete lexical-output mismatch for an unusual but valid filesystem filename, not a demonstrated authorization bypass. **Reasoned from pinned expressions; no probe executed.** Locate insertion from the trimmed entry's known quote boundary rather than the first matching substring, and add a literal revised-input regression. Enforcement/test remediation belongs to **T-01, main-session-direct under DEC-174**, never a hosted fix. T-02 already states the intended preservation rule and needs no contract weakening.

## Stage 2 — code quality: not entered

Specification did not pass, so no code-quality verdict is asserted. `code_grade: n_a` is supported by the complete changed-path census (no Python edits), not by inheriting c1's quality grade.

## Evidence and preserved dispositions

Historical execution only: `notes/t01-receipts-main-session.md` records 14 named red-first cases, 123/0 final adapter cases, seven mutation checks and real-resolver smoke; `runs/validate-validator/digest.md` records c1 QA's independent T-01/T-02 success. No runtime suites, builds, linters, formatters or mutants ran here. QA alone runs final T-01 `python3 tests/unit/test-omp-hooks.py` and T-02 `python3 .claude/skills/harness/bin/gen-decisions-index.py --stdout | diff - .harness/harness/docs/DECISIONS-INDEX.md`.

SC-06 dedicated-red-first and receipt-shape candidates remain assessed-and-dismissed. The duplicate `rootedHooks` fixture remains operator backlog only. The pre-existing ast_edit mutation-set omission remains out of scope; actual `paths: string[]` handling remains the accepted interface correction. No open questions; source/tests/docs unchanged.

```yaml
VERDICT: FAIL
DIGEST:
  headline: "R1 conforms to the amended predicate; T-01 still misplaces rooting for a quoted quote-only filename."
  severity_max: med
  findings:
    - kind: substance
      scope: task
      severity: med
      reader: code-reviewer
      summary: "R2 (T-01): rootTarget inserts outside the surrounding quotes for a three-double-quote relative entry."
      why: "After unquoting, the target is one double quote; raw.indexOf(target) selects the opening wrapper, yielding /wt/ followed by three quotes instead of a quoted rooted target. SC-01/SC-02/SC-07 preservation fails."
  must_fix:
    - "R2: T-01 main-session-direct under DEC-174 must anchor insertion to the surrounding-quote boundary and add a literal regression; do not host a governed fix."
  spec_violations:
    - {kind: mismatch, path: .omp/extensions/harness-hooks.ts, ref: SC-01}
    - {kind: mismatch, path: .omp/extensions/harness-hooks.ts, ref: SC-02}
    - {kind: mismatch, path: .omp/extensions/harness-hooks.ts, ref: SC-07}
  code_grade: n_a
  reviewed: "af2a958ab06c0d6fc026b363b59fc3147e3982f1..55c99a856321ef9d059b144b6ee2ac2bf1f75096"
  human_commits_in_scope: []
  open_questions: []
  files_touched: []
  expertise_update: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-1016-worktree-relative-paths/.harness/harness/features/BUG-1016-worktree-relative-paths/notes/review-harness-code-reviewer-c2.md
```
