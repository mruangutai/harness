# Goal-check — does this plan deliver the operator's stated intent? — BUG-1286, plan phase, cycle 2

**Yes, with one surviving gap** — the amended plan reaches the Destination, settles all four blocking
questions decisively, drifts into none of the four out-of-scope areas, begins no implementation, and
closes four of c1's five gaps outright; but SC-06's leading "produces no violations" clause is graded
over a fixture that deliberately plants a rogue, so it is ungradable as written and AC-05 stays
partially delivered.

Graded from the CURRENT text at HEAD `1977ebd68d34cc0308968b03ad2d24399c0b5335`; every c1 citation
re-resolved, none carried forward. Standard: `.harness/notes/grilling-test-tree-enforcement-2026-09-04.md`.
Floor: issue #1286 (11 AC, 4 blocking questions). Subject: `plan.yaml` (D-01..D-06, T-01..T-05),
`BRIEF.md` (8 REQ, 17 SC). Prior context cited, not redone: `research-…-goalcheck-plan-c1.md`,
`research-BUG-1286-plan-gap-closure-c2.md`, `review-harness-eng-lead-plan-c0.md`.

## 1. The Destination — delivered

Positive: tree enforced over the tracked repository — `BRIEF.md:18-21`, clause spec `plan.yaml:157-171`.

Negative 1, product-checkout discovery unchanged — **delivered.** Four locks: the clause is inert
unless the scanned root's own index carries the predicate at that exact path (`plan.yaml:61-81`,
`plan.yaml:162-164`), asserted by T-01 case 9 (`plan.yaml:217-221`); `harness.json` frozen (SC-14,
`BRIEF.md:118-119`) and forbidden to T-01 (`plan.yaml:222`); the single-caller half pinned by the live
`runner delegates layout once` check (`tests/unit/test-suite-layout.py:136-139`, re-read); SC-16
(`BRIEF.md:125-131`).

Negative 2, no implementation begun — **delivered, verified.** `git diff --stat 1977ebd6 -- .` in the
worktree is empty; `git status --porcelain` shows exactly two untracked planning paths (the feature
directory and the grilling note). `approval.status: pending` (`plan.yaml:4-5`), `BRIEF.md:180-183`
likewise. `check-plan-routes.py` on this plan: `OK T-01`..`OK T-05`, 0 violations, exit 0.

## 2. The four blocking questions — all four delivered

| # | Question | Settled at | Decisive? |
|---|---|---|---|
| 1 | authoritative vocabulary | D-01 `plan.yaml:34-50`, constants `plan.yaml:133-147` | **yes** — now scoped per clause; see Gap 1 |
| 2 | exception contract | D-02 `plan.yaml:51-60`, D-05 `plan.yaml:90-102`, self-policing `plan.yaml:172-179` | yes — one in-module tuple, exact paths, four named staleness failures each with its own message |
| 3 | tracked authority + failure semantics | D-03 `plan.yaml:61-81` | yes — `git ls-files` in the root, staged add scanned / staged delete not, three activation conditions with the toplevel test ordered first and the reason why, no-index root usable, unreadable index in a claimed checkout is a violation |
| 4 | DEC-213 amendment | D-06 `plan.yaml:103-111`, T-05 `plan.yaml:340-397` | yes — amendment prose dictated, hand-written index tail rewritten, regeneration + anchor check in `verify:` |

## 3. The eleven acceptance criteria — 10 delivered, 1 partially delivered, 0 not delivered

| AC | SC (current numbering) | Task work | Grade |
|---|---|---|---|
| AC-01 rogue tracked file rejected | SC-01 `BRIEF.md:58-60`, SC-02 `BRIEF.md:61-66` | T-01 case 1 `plan.yaml:185-195` | delivered |
| AC-02 all paths, deterministic | SC-03 `BRIEF.md:67-69` | T-01 case 3 `plan.yaml:198-200`, T-02 case 3 `plan.yaml:252-253` | delivered |
| AC-03 refusal before any sentinel | SC-04 `BRIEF.md:70-72` | T-02 case 2, third assertion `PASS test-unit.py` absent `plan.yaml:246-251` | delivered |
| AC-04 enumeration failure fails closed | SC-05 `BRIEF.md:73-76`, SC-17 `BRIEF.md:132-135` | T-01 cases 4-5 `plan.yaml:201-204`, T-02 case 4 `plan.yaml:254-256` | delivered |
| AC-05 valid unit/integration/manual accepted; manual outside discovery | SC-06 `BRIEF.md:77-84`, SC-07 `BRIEF.md:85-89` | T-01 case 1 now plants `tests/manual/probe-fixture.py` `plan.yaml:186-195`; live `manual tests are not actively detected` `tests/unit/test-suite-layout.py:104-105` | **partially** → surviving gap 1 |
| AC-06 support modules incl. `bin/` | SC-08 `BRIEF.md:90-91`, SC-09 `BRIEF.md:92-97` | T-01 case 7 `plan.yaml:210-214`; `import layout_fixtures as lf` `tests/integration/test-layout-migration.py:62` | delivered |
| AC-07 exact exceptions, stale/broadened/duplicated/unnecessary refused | SC-10 `BRIEF.md:98-102` | registry clauses `plan.yaml:172-179`, case 6 incl. positive accept `plan.yaml:205-209` | delivered |
| AC-08 tracked-vs-untracked coverage | SC-11 `BRIEF.md:103-105` | T-01 case 2 `plan.yaml:196-197`, T-02 case 5 `plan.yaml:257-258` | delivered |
| AC-09 audit at `review_sha`, complete, explained | SC-12 `BRIEF.md:106-112` | T-03 `plan.yaml:261-308`, T-04 `plan.yaml:309-339` | delivered |
| AC-10 DEC-213 + index state the invariant | SC-13 `BRIEF.md:113-117` | T-05 `plan.yaml:340-397` | delivered |
| AC-11 product discovery + mutation scope unchanged | SC-14/15/16 `BRIEF.md:118-131` | T-01 case 9 + `plan.yaml:222`; `run-unit-tests.sh` in no task's `files:` | delivered |

`run-unit-tests.sh:47` re-verified as the sole `run_pool.py --mutation-check "$BIN_DIR"` line, so
SC-15's pin is live rather than rotted.

## 4. The FEAT-44 `.ts` classification — delivered, carried through every touching site

`.ts` in `SOURCE_EXTENSIONS` (`plan.yaml:37-38`, `plan.yaml:135`); D-05 allows it at its exact path
and forbids relocation with the archival consequence stated (`plan.yaml:90-102`); T-01 seeds exactly
that path and reason (`plan.yaml:136-141`); T-03 orders `documented-exception` above
`out-of-vocabulary` (`plan.yaml:288-291`) and its `verify:` greps for the row (`plan.yaml:272`);
T-04 requires `suite_layout.DOCUMENTED_EXCEPTIONS` cited as the authority (`plan.yaml:331-335`);
T-05 bullet 5 records it (`plan.yaml:380-383`); SC-10's last sentence makes the live entry
load-bearing (`BRIEF.md:100-101`); the un-typechecked residual is disclosed (`BRIEF.md:168-170`).
The consumer at `tests/manual/probe-omp-session-accessor.py:54-55` is in no task's `files:`.

## 5. The four out-of-scope entries — no drift

No task redesigns product-checkout discovery (`plan.yaml:222`, SC-14); nothing touches the mutation
snapshot — `run-unit-tests.sh` appears in no `lanes:` row (`plan.yaml:8-31`) and no task's `files:`,
and SC-15 freezes its scope; no support module is renamed — `layout_fixtures.py` explicitly stays and
needs no exception (`plan.yaml:384-385`, D-04 `plan.yaml:82-89`); implementation not begun (§1).

## 6. Delivered but never asked for — one finding, unchanged from c1

T-03's `--against` note-comparison mode (`plan.yaml:296-304`) is a comparator #1286 does not request.
It is load-bearing — it is T-04's `verify:` (`plan.yaml:320`) — and now carries the explicit
do-not-call-`baseline()` warning. Recorded for the panel to accept or strike. SC-02 is new scope the
operator did not state either, but it is harness doctrine (test-first), not product surface.

## c1 gap closure

| c1 gap | Closed? | Proof | Residual? |
|---|---|---|---|
| 1 D-01 "everywhere" false | **closed** | see enumeration below | none — divergence now stated as deliberate |
| 2 SC-01 clause ungradable by its method | **closed** | split: SC-01 behavioural `BRIEF.md:58-60`; SC-02 `verify: inspection` names the grader (qa's test-first audit), the evidence (red run against `suite_layout.py` at the base commit) and that a passing review-time run cannot discharge it `BRIEF.md:61-66` | none — the red proof is recordable on disk |
| 3 AC-05's manual half unasserted | **partially closed** | assertion added: T-01 case 1 creates `tests/manual/probe-fixture.py` and asserts separately that no finding names it, with the shape reason `plan.yaml:186-195`; criterion names the shape `BRIEF.md:77-84` | **yes** — the "produces no violations" clause is left ungradable; surviving gap 1 |
| 4 SC-13 named no grading target | **closed** | split into SC-14 (`harness.json`, no byte) `BRIEF.md:118-119` and SC-15 (file, line 47 at the named HEAD, `--mutation-check "$BIN_DIR"`) `BRIEF.md:120-124`; two independently failable claims | none — line 47 re-verified as the `run_pool.py` invocation |
| 5 BRIEF did not record SC-06/SC-08's pre-existing discharge | **closed** | SC-07 names `manual tests are not actively detected` at `tests/unit/test-suite-layout.py:104-105` `BRIEF.md:85-89`; SC-09 names `import layout_fixtures as lf` at `tests/integration/test-layout-migration.py:62` `BRIEF.md:92-97`; both anchors re-read at HEAD and both resolve | none |

**Gap 1, site by site.** Does the site still claim the extension restriction reaches the bin clause?
- **D-01** (`plan.yaml:36-45`) — **no.** Scopes the restriction "to that clause alone", states the bin
  clause "deliberately keeps its own unrestricted probe-* glob".
- **D-04** (`plan.yaml:82-89`) — **no**, and never did; unchanged, and it now agrees rather than
  contradicts.
- **T-01 intent** (`plan.yaml:144-147`) — **no.** "govern the NEW repository-wide clause ONLY", both
  other clauses byte-identical, bin's `probe-*` named "deliberately unrestricted".
- **T-05 bullet 1** (`plan.yaml:360-366`) — **no.** "FOR THAT CLAUSE", "out of scope OF THE
  REPOSITORY-WIDE CLAUSE", plus an explicit instruction not to write that the restriction holds
  everywhere; bullet 2 (`plan.yaml:367-370`) supersedes the bin-only enumeration "as a statement of
  the predicate's reach, not as a rule".

Judgement: the three vocabularies now read **as deliberate, not as oversight.** Each divergence is
stated with its load-bearing reason at the site that could mislead — bin reads the filesystem and is
the untracked-plant net, the index clause cannot see untracked plants — and D-01 closes on "three
clauses, three deliberately different vocabularies, none of them widened by this feature"
(`plan.yaml:44-45`). The live vocabularies were re-confirmed at source (`suite_layout.py:20-33`).

**c1 open question:** unchanged and not re-litigated — `unit.detect`'s extension-agnostic residual
stays a disclosed residual with no SC added (`BRIEF.md:171-179`), measured by T-03's unfiltered
selection; accepting it remains the operator's call at approval.

## Surviving gaps

1. **SC-06 is ungradable as written — its two clauses have different subjects**
   (`BRIEF.md:77-84`). Clause A, "a fixture holding valid `tests/unit/**`, `tests/integration/**` and
   `tests/manual/**` files produces no violations", is graded over the only fixture in the plan that
   holds a manual file — T-01 case 1 — which deliberately plants `.harness/tools/test_rogue.py` and
   must therefore report exactly one violation (`plan.yaml:185-195`). No other fixture can host the
   subject: `legal_tree()` creates only the two kind directories
   (`tests/unit/test-suite-layout.py:53-60`) and case 7 grades the real `ROOT`, which contains no
   `tests/manual/probe-fixture.py` (`plan.yaml:210-214`). So clause A is false by construction on its
   own fixture while clause B ("no finding names it") passes, and a grader must silently pick one.
   The amending run's advisory is upheld: this is a real gap, and it is why AC-05 stays partial.
   Remedy, either half suffices — add a violation-free variant of case 1's fixture holding all three
   kinds and assert `violations(root) == []` on it, or narrow clause A to the manual file so SC-06
   asserts only that no finding names `tests/manual/probe-fixture.py` and let SC-08 carry
   clean-tree-produces-nothing.

---

## Later addition — 2026-09-04, fix cycle 3: surviving gap 1 is closed

Appended after the fact; nothing above this line is rewritten. The verdict, the AC table and the
"Surviving gaps" section stand as the c2 re-run found them.

**The single surviving gap — SC-06 clause A has no grader — is now closed**, by the first of the two
remedies that section offered, applied in place rather than as a new fixture.

Proof, three amendments:

1. **T-01 case 1 now carries an exact-equality assertion** (`plan.yaml:196-216`, case 1 now spanning
   `plan.yaml:185-216`). It requires `violations(fixture)` to be EQUAL to the one-element list
   `["tracked test-shaped file outside tests/: .harness/tools/test_rogue.py"]`, explicitly forbidding
   `in`, containment, substring and length-plus-membership forms (`plan.yaml:201-205`) — membership is
   precisely what left clause A ungraded. Equality is what proves the valid `tests/unit`,
   `tests/integration` and `tests/manual` files and the copied `bin/` module each contributed nothing,
   so clause A is graded without needing a fixture that produces no violations at all.
2. **The assertion is satisfiable, and the plan says how** (`plan.yaml:206-216`). Unrebound, that call
   returns TWO findings: the rogue line and `documented exception is no longer tracked:` for the
   seeded FEAT-44 path, which case 1's fixture does not track. The case now rebinds
   `suite_layout.DOCUMENTED_EXCEPTIONS` to `()` in a try/finally — case 6's own mechanism — for the
   duration, and forbids the alternative of tracking that path in the fixture, which would couple
   case 1 to the live registry that case 7 exists to isolate. Both counts were measured, not reasoned:
   a throwaway prototype of the specified clauses over case 1's exact fixture returned 2 findings
   unrebound and exactly the 1 expected finding rebound, and the pre-existing clauses
   (`suite_layout.py:6-33`, re-read at HEAD `1977ebd6`) returned none — the under-`tests/` clause
   rglobs only `root/tests`, both kind directories are non-empty, and the fixture's `bin/` holds only
   the copied module.
3. **SC-06 now states the observable that assertion produces** (`BRIEF.md:77-92`): no finding
   attributable to any of the three valid kinds, graded by that assertion, with the failure mode
   written down — any second element in the returned list, and specifically a membership test in
   equality's place, leaves the criterion ungraded. `verify: automated  evidence: unit` unchanged.

**Not split.** Under exact equality the former clause B ("no finding names
`tests/manual/probe-fixture.py`") is strictly subsumed — a list equal to the one-element rogue list
cannot contain a finding naming it — so there is no second independently failable claim and no
`SC-18`. `SC-07`..`SC-17` are unrenumbered and every citation in this note still resolves. The
traceability table is unchanged: SC-06 → AC-05.

**Consequence for §3.** AC-05's grade of *partially delivered* was correct when taken and is left as
written; on the amended text its cause no longer exists. Re-grading is the next goal-check's to do,
not this append's.
