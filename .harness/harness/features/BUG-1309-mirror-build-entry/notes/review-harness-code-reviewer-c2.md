# Code review — BUG-1309-mirror-build-entry — cycle 2 — review_sha 358ac561

## BLUF

**PASS**, both stages. The tip carries no code change: `git diff d80a7b12..358ac561` touches only
`feature.json`'s `review_sha` pin field and a 4-line `GRADE-2 REASON` comment added above
`_run_merge_and_check` in `tests/integration/test-hooks-install.py` — confirmed myself via
`git diff --stat` and full patch, not taken on the lead's word. That comment closes cycle 1's F2
(the one open, non-gating finding this panel carried forward) and disturbs nothing else. The bulk
of this review's effort went to the files no prior code-review cycle examined in depth — c0/c1 both
concentrated on `merge-gate.py`. I found nothing new there either.

## Stage 1 — spec compliance: PASS

- (a) **The comment-only commit, verified.** `_run_merge_and_check` (`test-hooks-install.py:392`)
  really does interleave clone/setup/commit/worktree-add/real-merge/hook-observation/retention
  assertions in one routine (read the body at this pin: `test-hooks-install.py:392-448`) — the
  comment's claim is true of the function as written, not aspirational. `code-grade.py --base
  $(git merge-base origin/main 358ac561) --head 358ac561` still reports it `GRADE: 2, CYCLOMATIC:
  5, COGNITIVE: 6, ABC: 27.0` — **identical to c0/c1's numbers** — because `REASON REQUIRED` lines
  are computed purely from AST-derived cyclomatic/cognitive/ABC metrics
  (`code-grade.py:118-119`); the tool never reads or parses the comment text. The comment satisfies
  the review protocol's human-facing "reason on file" requirement and changes no grade. All four
  gated grade-2 records at this pin now carry a `GRADE-2 REASON` comment
  (`merge-gate.py:29,118`, `test-check-state.py:4619`, `test-hooks-install.py:392`,
  `test-post-merge-sweep.py:883`) — cycle 1's Q1/F2 is now closed, not merely restated.
- (b) **Widened to files no prior code-review cycle covered.** c0/c1 read `merge-gate.py`,
  `feature_schema.py`'s era set, and `gh-sync.py`'s skip/refuse table closely; both left
  `post-merge-sweep.sh`'s SC-06 branch, `feature-schema.json`'s schema declaration, `gh-sync.py`'s
  `cmd_recover_terminal`/`cmd_open`/`record_build_entry` bodies, `plan-merge.py`'s regex change,
  `check-state.sh` INV-37, the hook-registration surfaces, and the doc surfaces largely
  unexamined. I read and traced each (not merely grepped) and additionally **ran** the beds that
  exercise them, rather than trusting a prior green claim:
  - `plan-merge.py:1120` narrowed `_replace_signature_fields`'s regex from `^(\s+)` to `^(  )`.
    Traced the reason myself: a `rulings:` entry's own `date:` key sits at 6-space indent inside
    the approval block's line range, so the old `\s+` regex matched and would silently clobber a
    historical ruling's date with the new signature date — a real defect, not a style change. The
    fix is exactly the correct narrowing (the tool's own writers, `_new_approval_block` and the
    `missing`-field insert, always emit exactly two spaces). A dedicated regression test,
    `case_sign_approval_preserves_existing_rulings` (`test-plan-merge.py:902`), asserts the
    ruling's untouched date via a parsed-YAML equality check, not a substring. Ran
    `tests/integration/test-plan-merge.py` directly: full suite green.
  - `gh-sync.py`'s `cmd_recover_terminal`/`_recover_terminal_apply`/`_recover_terminal_report`
    (`:1261-1325`) satisfy REQ-08/SC-05: `_recover_terminal_apply` never calls
    `_open_sync_task` (the only site that creates a task sub-issue), and
    `record_build_entry(feat_dir, "recovered-terminal")` is the function's last statement.
    `test-gh-sync.py`'s `"T-03 FEAT-55 shape adopts and creates nothing"` asserts
    `len(create_calls(...)) == 0` against the exact FEAT-55 shape (milestone 52, parent 1289,
    twelve task issues, no build_entry) — an exact count via a payload-scoped helper
    (`create_calls`, `test-gh-sync.py:714`, explicitly scoped to POST/`issue create` payloads, not
    path substrings), not a substring search, matching SC-05's own wording. Ran
    `tests/integration/test-gh-sync.py`: full suite green (T-02/T-03/T-04/T-12 sections all `ok`).
  - `post-merge-sweep.sh`'s SC-06 branch (era-absent print-then-fall-through vs.
    not-in-allow-set `elif`-return) matches D-08/D-12's text: era+absent prints and continues to
    normal removal (swept); anything outside `{opened, not-applicable, recovered-terminal}`
    (including era `recovery-required`) returns before removal (retained).
  - `check-state.sh`'s new INV-37 (`:1983-2019`) skips a feature whose `factory.issues` is
    non-empty. This looked, on first read, like an unplanned fail-open — a second, undocumented
    exemption alongside the era set. Traced it to source: `factory.issues` is a *different*
    mirroring mechanism (`factory_decompose.py`/`factory_claim.py`, a separate fleet-decompose
    path, `feature-schema.json:103-127`), a feature published that way legitimately never runs
    `gh-sync.py open`. This is planned and named explicitly in `plan.yaml:1208,1321-1322` (T-06)
    with its own case, `"T-06 INV-37 silent on a feature with factory.issues"`
    (`test-check-state.py:4668`) — ran `tests/integration/test-check-state.py`: full suite green,
    including that case and its era/build_entry siblings.
  - `feature-schema.json`'s `build_entry` enum declaration (SC-08) — ran
    `tests/integration/test-validate-feature-json.py` directly: all four legal values accepted,
    an illegal value (`'opened '`, `'reopened'`) and a hyphen misspelling both rejected, full suite
    green.
  - SC-09 (inspection): `git show 358ac561:.claude/skills/harness/references/github-mirror.md`
    and `:.claude/skills/harness/SKILL.md` both name the act "Build entry", tied to signed
    approval (`github-mirror.md:41,51-54`, `SKILL.md:141-143`); the orchestrator's own build-phase
    sequence names it as step 1 (`SKILL.md:141`). Grepped both files for "ship"-as-mirror-trigger
    wording: none found.
  - Hook registration (`settings.json`, `settings.snippet.json`, `merge-settings.py`,
    `.omp/extensions/harness-hooks.ts`): `merge-gate.sh` is registered once in each surface,
    consistent with the other three. The `should-not-exist` reader's plan-time position finding
    (PF-f1684…) is recorded resolved by T-05 and is a placement question, not a behavioral one —
    not re-litigated here.
  - Ran `tests/integration/test-merge-gate.py` and `tests/integration/test-hooks-install.py`
    directly at this pin: both full suites green, including the two era-boundary cases
    (`"T-05 era-exempt absent build_entry allows"`, `"T-05 era-exempt recovery-required allows"`)
    that cycle 0's F1 originally broke and cycle 1 confirmed closed.

No REQ/D found unimplemented, no undeclared scope creep found in the newly-examined surfaces, no
SC-verify-inspection claim found false.

## Stage 2 — code quality: PASS

Grader run against `merge-base(origin/main, 358ac561)..358ac561`: same 54 gated functions as c0/c1,
same 4 grade-2 records, all now carrying written reasons, zero grade-1 or below-bar production-grade
records — `code_grade: grade_2`.

**Fail-open hunt on the newly-examined surfaces** (per this cycle's standing charge): `skip()`
(`gh-sync.py:166`) only records a Build-entry outcome when `_BUILD_ENTRY["remote_written"]` is
still `False`, so a partial remote write never gets papered over as `recovery-required` (D-04) —
traced the flag's only two writers and confirmed neither sets it before `open`'s first successful
create. `record_build_entry` (`:940`) re-reads `load_recorded` fresh rather than trusting a
possibly-stale caller-held `rec`, and refuses to downgrade an already-`"opened"` record — matches
the `"T-02 opened never downgrades"` test, which is green. `save_recorded` refuses (does not
silently no-op) on an absent `feature.json` rather than starting from `{}` — verified by the
"contract error records nothing" test. Nothing found that exits 0 while claiming a write it did not
perform.

## What I looked for and did not find

- No re-derivation of `BUILD_ENTRY_ERA_EXEMPT` outside `feature_schema.py` (checked `check-state.sh`,
  `merge-gate.py`, `gh-sync.py`, `post-merge-sweep.sh` — all import the one module-level set).
- No consumer of `github.build_entry` that defaults absence to a permissive value (re-confirmed for
  `check-state.sh` INV-37 and `post-merge-sweep.sh`'s SC-06 branch, both newly read this cycle;
  `merge-gate.py`/`gh-sync.py` sides were c0's own finding, not re-derived here).
- No place where the `GRADE-2 REASON` comment text is consumed by tooling, and no discrepancy
  between the comment's claim and the function it sits above.
- No scope creep beyond what c0 already traced (the `plan-merge.py` regex fix); re-derived that
  trace myself this cycle rather than accepting it, and found it correct with its own dedicated
  regression test.

## Findings summary

None new. Cycle 0's two highs remain settled-closed (not re-derived here, per the dispatch's
instruction). Cycle 1's F2 (unruled grade-2 `_run_merge_and_check`) is now closed by this commit.
F3 (`gh-sync.py:278,282`, low, informational) remains open/unchanged and non-gating; not re-raised
as anything new.

## Open questions

None blocking.
