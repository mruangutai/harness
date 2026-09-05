# Goal-check — does this plan deliver the operator's stated intent? — BUG-1286, plan phase, cycle 1

**Yes, with five named gaps** — the plan reaches the Destination, settles all four blocking
questions decisively, drifts into none of the four out-of-scope areas and begins no implementation;
but one of the eleven acceptance criteria (AC-05) is only half discharged, SC-01's own "demonstrated
failing before the fix" clause is unreachable by the method it declares, and D-01's vocabulary
answer contradicts what T-01 tells the doer to leave alone.

Graded against the grilling artifact (`.harness/notes/grilling-test-tree-enforcement-2026-09-04.md`)
as the standard and issue #1286 as the acceptance floor. Subject: `plan.yaml` (6 D, 5 T) and
`BRIEF.md` (8 REQ, 15 SC) at HEAD `1977ebd68d34cc0308968b03ad2d24399c0b5335`. Prior context cited,
not redone: `notes/review-harness-eng-lead-plan-c0.md`,
`notes/research-BUG-1286-plan-review-application-c1.md`.

## 1. The Destination — **delivered**

Positive: the brief and plan together make the `tests/**` tree enforced over the tracked repository
(`BRIEF.md:18-21`, `plan.yaml:147-161`).

Negative 1, product-checkout discovery unchanged — **delivered.** Three independent locks: the
repository-wide clause is inert unless the scanned root's own index carries the predicate at that
exact path (`plan.yaml:57-63`, `plan.yaml:152-154`); `harness.json` is frozen (`BRIEF.md:103-105`);
the single-caller half is pinned by the live `runner delegates layout once` check
(`tests/unit/test-suite-layout.py:136-139`).

Negative 2, no implementation begun — **delivered, verified.** `git diff --stat 1977ebd6 -- .` in the
worktree is empty; `git status --porcelain` shows exactly two untracked planning paths
(`.harness/harness/features/BUG-1286-test-tree-enforcement/`, the grilling note). No test,
predicate, `DECISIONS.md` or `harness.json` byte has moved. `approval.status: pending`
(`plan.yaml:4-5`), `BRIEF.md:159-163` likewise. `check-plan-routes.py` on this plan: `OK T-01..T-05`,
0 violations, exit 0.

## 2. The four blocking questions — **three delivered, one partially delivered**

| # | Question | Settled at | Decisive? |
|---|---|---|---|
| 1 | authoritative test-shaped vocabulary | `plan.yaml:36-39` (D-01), constants in `plan.yaml:128-137` | **partially** — see Gap 1 |
| 2 | exception contract | `plan.yaml:47-50` (D-02) + `plan.yaml:86-88` (D-05) | yes — location, exact-path-only, and four named staleness failures, each with its own message string (`plan.yaml:164-169`) |
| 3 | tracked authority + failure semantics | `plan.yaml:57-63` (D-03) | yes — `git ls-files` in the root, staged add scanned / staged delete not, three activation conditions, no-index root stays usable for the synthetic fixtures, unreadable index in a claimed checkout is a violation |
| 4 | DEC-213 amendment | `plan.yaml:99-101` (D-06) + T-05 `plan.yaml:338-379` | yes — amendment prose dictated, index row's hand-written tail rewritten, regeneration and anchor check in `verify:` |

D-01 is decisive about the new clause but its own trailing claim — probe-shaped names "carry the
same extension restriction everywhere" (`plan.yaml:39`) — is contradicted by the retained bin clause,
which globs `probe-*` with no extension filter (`suite_layout.py:30`) and which T-01 orders kept
byte-identical (`plan.yaml:124-125`, D-04 at `plan.yaml:78-79`). A `probe-notes.md` planted under
`bin/` is still refused, so "everywhere" is false as shipped. → **Gap 1.**

## 3. The eleven acceptance criteria — 10 delivered, 1 partially delivered, 0 not delivered

| AC | SC | Task work that would make it true | Grade |
|---|---|---|---|
| AC-01 tracked file outside `tests/**` rejected | SC-01 (`BRIEF.md:58-61`) | T-01 case 1 (`plan.yaml:177-180`) | delivered (see Gap 2 on SC-01's second clause) |
| AC-02 all paths, deterministic order | SC-02 (`BRIEF.md:62-64`) | T-01 case 3 (`plan.yaml:183-185`), T-02 case 3 (`plan.yaml:237-238`) | delivered |
| AC-03 runner refuses before any sentinel | SC-03 (`BRIEF.md:65-67`) | T-02 case 2, whose third assertion is `PASS test-unit.py` **absent** (`plan.yaml:231-236`) | delivered |
| AC-04 enumeration failure fails closed | SC-04, SC-15 (`BRIEF.md:68-71`, `113-116`) | T-01 cases 4 and 5 (`plan.yaml:186-189`), T-02 case 4 (`plan.yaml:239-241`) | delivered |
| AC-05 valid unit/integration/manual accepted; manual outside active discovery | SC-05, SC-06 (`BRIEF.md:72-77`) | second half: live check `manual tests are not actively detected` (`tests/unit/test-suite-layout.py:104-105`). First half: **no case builds a `tests/manual/**` file** — `legal_tree()` creates only unit and integration (`tests/unit/test-suite-layout.py:53-60`) and T-01 case 1's fixture the same (`plan.yaml:178-179`) | **partially** → Gap 3 |
| AC-06 ordinary support modules, incl. the `bin/` case | SC-07, SC-08 (`BRIEF.md:78-82`) | T-01 case 7 asserts `violations(ROOT) == []` (`plan.yaml:195-199`); `layout_fixtures.py` is load-bearing via `import layout_fixtures` (`tests/integration/test-layout-migration.py:62`) | delivered |
| AC-07 exact documented exceptions; stale/broadened/duplicated/unnecessary refused | SC-09 (`BRIEF.md:83-87`) | T-01 registry clauses (`plan.yaml:162-169`) and case 6, which includes the positive accept case (`plan.yaml:190-194`) | delivered |
| AC-08 coverage shows the tracked distinction | SC-10 (`BRIEF.md:88-90`) | T-01 case 2 (`plan.yaml:181-182`), T-02 case 5 (`plan.yaml:242-243`) | delivered |
| AC-09 audit re-run at `review_sha`, complete set, no unexplained match | SC-11 (`BRIEF.md:91-97`) | T-03 instrument (`plan.yaml:258-293`), T-04 record (`plan.yaml:306-324`); SC-11's ancestor-of-`review_sha` clause closes the build-time/review-time gap | delivered |
| AC-10 DEC-213 + index state the shipped invariant | SC-12 (`BRIEF.md:98-102`) | T-05 (`plan.yaml:336-379`); the index grep was measured non-vacuous and positive-controlled (`research-BUG-1286-plan-review-application-c1.md:38-42`) | delivered |
| AC-11 product discovery and mutation-snapshot scope unchanged | SC-13, SC-14 (`BRIEF.md:103-112`) | SC-13 inspection over the diff; SC-14 via T-01 case 9 (`plan.yaml:202-206`) plus the single-caller check | delivered, with Gap 4 on SC-13's grading target |

No criterion maps to a task whose `verify:` would pass without the criterion holding, with one
qualification: T-01's `verify:` (`plan.yaml:119-120`) is the whole unit file, so it is only as
discriminating as the nine cases the intent dictates — which is why Gap 3 matters.

## 4. The FEAT-44 classification — **delivered**

Explicit and consistent across every touch point: D-05 classifies it an allowed exception at its
current path and forbids relocation (`plan.yaml:86-88`), with the archival consequence stated
(`plan.yaml:92-95`); T-01 seeds exactly that path with that reason (`plan.yaml:130-135`); T-03
disposition ordering puts `documented-exception` ahead of `out-of-vocabulary`, so the `.ts` file
lands in the right row (`plan.yaml:273-276`) and the `verify:` greps for it (`plan.yaml:257`); T-04
requires the note to cite `suite_layout.DOCUMENTED_EXCEPTIONS` as the authority
(`plan.yaml:316-320`); T-05 bullet 5 records it in DEC-213 (`plan.yaml:362-365`); SC-09's last
sentence makes the live entry load-bearing (`BRIEF.md:85-86`). The consumer reference at
`tests/manual/probe-omp-session-accessor.py:54-55` stays untouched — no task lists that file.

## 5. The four out-of-scope entries — **no drift**

No task redesigns product-checkout discovery (`harness.json` is frozen by SC-13 and T-01 forbids
editing it, `plan.yaml:207`); nothing touches the runtime mutation snapshot, whose scope is
`run-unit-tests.sh:47`'s `--mutation-check "$BIN_DIR"`, named in no task's `files:`; nothing renames
a support module — `layout_fixtures.py` is explicitly left in place (`plan.yaml:366-367`); and no
task edits `suite_layout.py`'s behaviour before approval (§1, negative 2).

## 6. Delivered but never asked for — one finding

T-03's `--against` note-comparison mode (`plan.yaml:281-289`) is a diffing instrument the ticket does
not ask for; #1286 asks for an audit that is re-run at the review revision, not for a note-versus-
measurement comparator. It is *used* — it is T-04's `verify:` (`plan.yaml:305`) — so it is
load-bearing rather than speculative, and the eng-lead review's R1/R2 shaped it. Recorded as scope
the operator did not state, for the panel to accept or strike. Everything else in the plan traces to
an AC or to a blocking question. The `tree-audit` subcommand itself is not a finding: AC-09's "rerun
against `review_sha`" requires an instrument.

## Gaps — every one actionable, none applied

1. **D-01's "everywhere" is false as planned.** D-01 (`plan.yaml:39`) says probe-shaped names carry
   the extension restriction everywhere, while D-04 and T-01 keep the bin clause's unrestricted
   `probe-*` glob (`suite_layout.py:30`, `plan.yaml:78-79`, `plan.yaml:124-125`). Either narrow
   D-01's claim to the repository-wide clause, or make the bin clause share `SOURCE_EXTENSIONS` and
   say so in T-01. T-05 bullet 1 inherits the ambiguity (`plan.yaml:345-349`).
2. **SC-01's second clause is unreachable by its declared method.** "the same assertion is
   demonstrated failing against the predicate as it stands today" (`BRIEF.md:59-60`) cannot be graded
   from a passing unit run; `evidence: unit` sees only green. Either name the recorded red proof —
   running the new cases against the pre-change copy of `suite_layout.py` from the base commit — or
   split the clause out and grade it by qa's test-first audit.
3. **AC-05's first half has no assertion.** SC-05 quantifies over `tests/manual/**`
   (`BRIEF.md:72-74`) and no fixture in the plan or in the live file contains a manual file
   (`tests/unit/test-suite-layout.py:53-60`, `plan.yaml:178-179`). Add a `tests/manual/probe-x.py`
   to T-01's git fixture and assert no finding names it. Note while doing so: a
   `tests/manual/test-*.py` IS refused today by the unchanged `tests/` clause
   (`suite_layout.py:26-28`), so the criterion must say which manual shape it means.
4. **SC-13 names no grading target.** "the mutation snapshot's scope" (`BRIEF.md:103-104`) leaves an
   inspection reader to find it; the surface is `run-unit-tests.sh:47`. Name the file and the
   argument in the criterion.
5. **The BRIEF does not record that SC-06 and SC-08 are discharged by pre-existing checks.** Only
   the predecessor note does (`research-BUG-1286-plan-review-application-c1.md:69-74`). A goal-check
   reading only the BRIEF sees two automated criteria that no task traces to and reads it as missing
   work. State the discharging assertion inside each criterion.

## Open question

- Is the residual recorded at `BRIEF.md:150-157` — `unit.detect`'s extension-agnostic globs
  permitting a `*_test.md` outside `tests/**` that the guard allows and no runner executes —
  acceptable to ship as a measured residual, given SC-13 freezes `harness.json`? The class is empty
  at the pinned SHA and T-03 measures it, so it is disclosed rather than hidden; but whether to
  accept it is the operator's, not mine.
