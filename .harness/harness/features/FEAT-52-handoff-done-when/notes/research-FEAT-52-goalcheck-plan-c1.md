# Goal-check — FEAT-52 plan c1 vs stated intent

**Does this plan deliver the operator's stated intent? — Yes on mechanism: all ten settled answers are
now bound by a criterion and none of the five exclusions leaks, but one high finding stands — SC-11's
positive control is inverted (`comm -13` instead of `comm -23`), so the criterion carrying the
operator's central promise cannot detect its own broken pipeline.**

Authority: `.harness/notes/grilling-handoff-done-when-2026-09-02.md`. Graded at 13 tasks, 9 decisions,
14 criteria. `notes/research-FEAT-52-planfix-c1.md` was treated as a claim; every row below was
re-derived from BRIEF.md / plan.yaml / the tree.

## 1. Closure of the six c0 findings — 5 of 6 closed, F-01 partial

| F | Verdict | Pointer / evidence |
|---|---|---|
| F-01 | **PARTIAL** | primary clause CLOSED (BRIEF.md:121-125); positive control STILL OPEN (BRIEF.md:126-127) — see finding 1 |
| F-02 | CLOSED | D-08 plan.yaml:89-92; T-11 plan.yaml:589-648; T-07 `depends_on: [T-06, T-11]` plan.yaml:392-394; `test -n "$out"` gone, control `grep -qi 'done when' check-state.sh` at plan.yaml:401; REQ-07 base framing BRIEF.md:37-41 |
| F-03 | CLOSED | T-07 intent plan.yaml:411-419 renames `HANDOFF_HEADINGS` (verified live at check-state.sh:1059, read at :1199 and :1219 — anchors correct) to `HANDOFF_SECTIONS` with five entries + `HANDOFF_NARRATIVE_HEADINGS`; SC-08 unchanged, now meetable |
| F-04 | CLOSED | SC-09 `evidence: integration` BRIEF.md:114; `test-run-unit-tests-kinds.py` confirmed in `INTEGRATION_SCRIPTS` (run-unit-tests.sh:31); T-12 plan.yaml:649-692; no-model-call moved into T-09 verify audithook plan.yaml:497-509 |
| F-05 | CLOSED | SC-07 `verify: inspection` BRIEF.md:103; T-13 authors the experiment plan.yaml:693-741; D-09 plan.yaml:93-96 |
| F-06 | CLOSED | (b)→SC-10 BRIEF.md:115-120; (d)→SC-12 BRIEF.md:129-132; (e)→SC-13 BRIEF.md:133-137; (i)→SC-14 BRIEF.md:138-141 (second clause under-authored, finding 2) |

**F-01, re-derived from the literal command text (BRIEF.md:123).** Would a commit that rewrote the
historical notes fail SC-11? **Yes.** `git diff --name-only $BASE <review_sha> -- '.harness/harness/features/*/notes/handoff-*.md'`
lists the rewritten path (the pathspec glob works — measured: that exact pathspec over the commit that
added a note returns 1, matching a no-pathspec `grep -c`), and `comm -12` against `git ls-tree` at
`$BASE` keeps paths present in both. Measured with a baselined path injected into the diff arm, `comm -12`
printed `.../BUG-1030-stale-anchor-write-hazard/notes/handoff-build.md`. The clause is sound.

But `comm -13` shows lines unique to **FILE2** — the `ls-tree` arm — i.e. the historical notes the diff
did *not* touch, not "the notes this feature added". Measured on the current tree: diff arm 0 lines,
`comm -13` 141 lines. The control is non-empty while the diff arm read nothing at all. `comm -23` is the
arm that lists the added notes (measured: prints `.../FEAT-52.../notes/handoff-plan.md`).

## 2. Ten settled answers and five exclusions — all 15

| # | Item (grilling line) | REQ | Criterion | Verdict |
|---|---|---|---|---|
| a | fifth standalone section (:9) | REQ-01 | SC-01 | covered (T-03/04/07/08/11) |
| b | scope = immediate `## Next` action (:10) | REQ-01 | SC-10 (uat) | covered — user-gated, unmechanizable |
| c | one `Scope:` + 1–4 `Authority:`, no other prose (:11) | REQ-02 | SC-02 | covered |
| d | AND semantics (:12) | REQ-03 | SC-12 | covered (was uncovered at c0) |
| e | four bounded types; code location is not one (:13) | REQ-04 | SC-03 + SC-13 | covered (was partial) |
| f | typed pointer syntax (:14) | REQ-05 | SC-03 | covered |
| g | resolution enforced, not syntax-only (:15) | REQ-06 | SC-03, SC-06 | covered |
| h | historical valid; new/edited must comply (:16) | REQ-07 | SC-04, SC-06, SC-11 | covered; SC-11 control defective |
| i | 60-line cap kept, no per-section caps (:17) | REQ-08 | SC-05 + SC-14 | covered (was partial); SC-14 clause 2 unauthored |
| j | benchmark deterministic + rerun by hand (:18) | REQ-10 | SC-09 | covered |
| X1 | no corpus rewrite (:26) | — | SC-11 | no leak — T-11 scoped to FEAT-52 notes, forbids touching baselined (plan.yaml:639-640) |
| X2 | cap not raised (:27) | — | SC-05 | no leak — T-04:290, T-07:431, T-11:637 |
| X3 | no per-section caps (:28) | — | SC-14 | no leak — T-03(h):252-255, T-07:431-433, T-10:573 |
| X4 | no token/latency claim (:29) | — | — | no leak — BRIEF.md:12-13 disclaims; T-09 prints fact coverage only |
| X5 | benchmark not a permanent gate (:30) | — | SC-09 | no leak — D-04, `locally_run`, absent from `test_matrix` and both arrays |

Uncovered settled items: **0**. Leaked exclusions: **0**.

## 3. New scope — three tasks (not four) and four criteria

| Item | Class | Justification |
|---|---|---|
| T-11 (sweep this build's own notes) | (b) consequence | grilling:16 "every newly written or edited handoff must use the five-section contract"; D-08 |
| T-12 (assert probe registration) | (b) consequence | grilling:18 "do not add the model benchmark to every normal test run" — the assertion is what proves the absence |
| T-13 (mutation-experiment note) | **(c) plan-added** | no grilling line asks for single-implementation or for a recorded experiment; it descends from DEC-179 + SC-07, via D-09. Disclose at signature |
| SC-12 | (a) asked | grilling:12 |
| SC-13 | (a) asked | grilling:13 second sentence |
| SC-14 | (a) asked | grilling:17 / :28 |
| SC-11 | (b) consequence | grilling:16 — the falsifiable form of "untouched historical handoffs remain valid" |

Correction to the dispatch: the repair added **three** tasks (T-11, T-12, T-13) and four criteria; task
count moved 10 → 13.

## 4. Traceability and `depends_on`

REQ→task, all covered: 01→T-03,04,11 · 02→T-01..04 · 03→T-01,02 · 04→T-01,02 · 05→T-01..04 ·
06→T-01..04,13 · 07→T-05,06,07,11 · 08→T-03,04,06,07 · 09→T-08,10 · 10→T-09,12. No REQ without a task;
no task without a REQ; every `traces:` id exists in BRIEF. One mismatch: T-03 carries the gate-level
proof of REQ-04 (plan.yaml:248-251) but omits REQ-04 from `traces:` (plan.yaml:215).

`depends_on` is **acyclic**. Topological order: T-01, T-05, T-02, T-03, T-04, T-06, T-11, T-07, T-08,
T-09, T-10, T-12, T-13. No task's `verify` asserts something a predecessor deletes or rewrites: T-13 is
the only mutator and it restores byte-identically and asserts the restore (plan.yaml:714); the two
`.harness/harness.json` writers (T-05, T-09) are serialised by T-09's `depends_on: [T-05]` and T-09's
verify re-reads the baseline keys' presence indirectly via T-05's own verify.

## 5. Evidence reachability — per criterion, mechanical

`test_kinds`: `unit` cmd `run-unit-tests.sh --kind unit` (non-null), `integration` cmd
`run-unit-tests.sh --kind integration` (non-null); `functional`, `component`, `ui`, `eval`, `typecheck`
are `cmd: null`.

SC-01 integration ok · SC-02 ok · SC-03 ok · SC-04 ok · SC-05 ok · SC-06 ok · SC-09 ok · SC-12 **unit**
ok · SC-13 ok · SC-14 ok. **None rests on a null kind.** Asserting files are in the right array:
`test-check-domain.py`, `test-check-state.py`, `test-run-unit-tests-kinds.py` all in `INTEGRATION_SCRIPTS`
(run-unit-tests.sh:31); `test-handoff-done-when.py` goes to `UNIT_SCRIPTS` only (D-06, T-01) and is
matched by `unit`'s detect glob `.claude/skills/harness/bin/test-*.py`. SC-07, SC-08, SC-11 inspection;
SC-10 uat.

## 6. Surviving findings

1. **(high) SC-11's positive control cannot fail (BRIEF.md:126-127).** `comm -13` prints the 141
   baseline notes regardless of the diff arm; measured 141 lines while the diff arm printed 0.
   Consequence: any silent breakage of the diff arm — a wrong ref, a pathspec typo, the command run from
   a subdirectory — leaves `comm -12` empty, the control healthy-looking, and SC-11 graded **met** with
   nothing checked. That is the exact G-14 failure the repair cited as fixed. One-token fix: `comm -23`,
   plus a requirement that its output be non-empty and equal the notes this feature added.
2. **(medium) SC-14's state-check clause has no authoring case.** SC-14 (BRIEF.md:138-141) requires the
   25-line-`Trust`/60-line note to be "reported by no state-check line", but T-06's cases (a)–(g)
   (plan.yaml:365-379) contain no per-section-cap fixture; only T-03(h) covers the write gate.
   Consequence: a per-section cap added to check-state.sh's INV-17 ships green and SC-14 still reads met
   on half its subject.
3. **(low) T-12's anchor is rotted.** It cites the KINDCHECK block at `run-unit-tests.sh:76-83`
   (plan.yaml:666); the block is at :111-163 — lines 61-80 are the unrelated drift-detector loop.
   Consequence: the doer reads the wrong region and must re-locate the check it was told to drive.
4. **(low) T-11's `files:` names one note while its intent quantifies over all of them.** `files:` is
   `notes/handoff-plan.md` (plan.yaml:598); the intent enumerates every non-baselined
   `handoff-*.md` of the feature (plan.yaml:628-630, 642-645). Consequence: a second pre-T-04 note is in
   scope for the sweep, fails T-11's verify, and its path is in no declared file list.
5. **(low) T-11 can run before T-05.** `depends_on: [T-04]` only, yet its verify reads
   `handoff_done_when_baseline` with `.get(..., [])` (plan.yaml:602). Consequence: with T-05 unlanded the
   "a note of this build must never be baselined" assertion (plan.yaml:609-610) passes vacuously.
6. **(low) T-03 omits REQ-04 from `traces:`** (plan.yaml:215) while carrying its gate-level proof — a
   REQ-04→task query misses the task that discharges the sentence "a code location is not an authority".

## 7. If this plan executed exactly as written and nothing more

**Operator-asked and still missing:** nothing at mechanism level. Two soft gaps: the untouched-corpus
promise is graded by a criterion whose control cannot fail (finding 1 — the primary clause does hold),
and SC-10 stays `not_met` until the operator runs it. The comprehension claim remains unproven
mechanically, which the operator settled (grilling:18) and BRIEF.md:145-148 discloses.

**Present but not asked for:** the frozen `handoff_done_when_baseline` + note keys in `harness.json`
(T-05); the persisted probe and its `handoff_comprehension` kind (T-09, D-04); the three new cases in
`test-run-unit-tests-kinds.py` (T-12); the shared module itself (D-02, forced by DEC-179); and
`notes/mutation-FEAT-52-shared-module.md` (T-13) — the only one with no grilling line behind it.
