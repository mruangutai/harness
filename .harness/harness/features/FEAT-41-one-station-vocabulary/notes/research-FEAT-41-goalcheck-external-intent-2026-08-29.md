# Goal-check FEAT-41 against EXTERNAL intent — 2026-08-29, pin `0dbd284` (signature `49638bf`)

Intent reconstructed from #845 + #867 bodies, `.harness/notes/grilling-845-one-vocabulary-2026-08-25.md`,
`notes/answers-2026-08-29-01.md`, `docs/PRINCIPLES.md` and DEC-188/174/157/120/203/191/182 — never from
BRIEF.md or plan.yaml. Every citation opened at the pin.

## BLUF

**Zero of the 13 tasks are self-assigned.** Every task traces to a named sentence in #845's seven
numbered items, #845's Constraints, the grilling's Settled list, or #867. The prosecution's expected
defect — planning-invented work — is not present.

Three real findings instead, ranked:

1. **CHANGE BEFORE BUILD — one grilling Settled item is silently dropped.** The grilling, which #845's
   `## Input` section incorporates by reference ("carries ten settled decisions … so pm does not
   re-derive them"), settles at lines 27-28: *"The task-to-issue map moves into `plan.yaml`. Today the
   key and the value live in different files."* No task moves it. T-06's own signature is the proof the
   split survives — `project(plan_doc, rec)` (`plan.yaml:499-504`) needs **two files** to answer one
   question, `rec["issues"]` still coming from `feature.json github.issues` via `gh-sync.load_recorded`.
   This is exactly the two-files-one-record shape the feature exists to end. A prior panel
   (`notes/receipt-harness-backend-dev-2026-08-25-01-eng-scope.md:41-49`) ruled it "not one of the
   seven" and therefore not a defect; **I disagree** — the ticket delegates its own detail to the
   grilling, so a Settled grilling bullet is ticket-grade intent. It is not in the BRIEF's residuals and
   not in PB-01..PB-04. Minimum fix: an explicit disclosure (a fifth PB row), or a task. Not a
   silent drop.
2. **CHANGE BEFORE BUILD — SC-02 has no verify anywhere, and six of its 27 lines have no owner.**
   Dumped all 13 `verify:` blocks: none runs SC-02's own grep. Declared `verify: automated evidence:
   unit`; its observation is a tree-wide grep no task executes. Worse, six of the 27 lines are
   `check-state.sh:539-552` `SEAM_NOTES`, a **second** capitalised station table, keyed by the six
   capitalised names. T-07 names only `STATUS_ORDER` (`:538` def, `:629` use). D-04's `because` and
   `notes/research-FEAT-41-vocabulary-surface.md:39` both know the table exists; no task instruction
   touches it. Rekeying `STATUS_ORDER` lowercase without `SEAM_NOTES` makes `SEAM_NOTES[_status]`
   (`:636`, outside the try at `:622-627`) a **KeyError** on every feature. Caught — `test-check-state.py`
   drives it via `_handoff_fixture(tmp, "Building", …)` (`:2034`) — so it reds T-07's verify rather than
   shipping. Fix is one sentence in T-07's intent plus SC-02's grep in a verify block.
3. **CHANGE BEFORE BUILD — SC-05 hardcodes the post-rename name; T-09 forbids it.** SC-05 requires the
   denial message name `plan-write.py`. T-09 instructs the opposite in capitals: the basename is the one
   on disk when T-09 runs, `plan-merge.py`, "and, if T-13 is struck, never will" exist. SC-12 is
   explicitly struck-with-T-13; SC-05 is not. As written SC-05 cannot be met at T-09 and is met only
   after T-13.

## Per-issue verdict

| Issue | Verdict | Task(s) |
|---|---|---|
| **#845** | **DELIVERED** on all seven numbered items | 1→T-01+T-11 · 2→T-01+T-02 · 3→T-04 · 4→T-06 · 5→T-03+T-05+T-08+T-09+T-13 · 6→T-07 · 7→T-10 |
| **#845** grilling line 27-28 | **MISSED** (finding 1) | none |
| **#867** | **ADJACENT by ruling** | T-14 |

#867 asks a three-step check with a stated precondition: *"For any feature whose `feature.json` records
a validator run."* T-14 ships a different precondition on the operator's Q7 — validator-run dropped
(wider), non-terminal added on Q6 (narrower). The byte comparison is delivered exactly as asked; the
scope is not the one the ticket states. Both deltas are operator-sanctioned, so this is not a defect —
but after ship #867's body reads as the spec for something else. Recommend a comment on #867 at ship
acceptance, not a plan change. (#867's own "T-07 and T-10 already touch check-state.sh" is now stale:
T-10's file list is gh-sync.py and two tests.)

## Scope: what grew, what was asked for

Asked for **verbatim**, contrary to the framing: the verb expansion 1→5 (grilling line 32 names
`add-tasks`, `set-task-station`, `set-feature-station`, `sign-approval` by name), the signature-denial
gate (grilling 36-38, "a PreToolUse Bash gate refuses sign-approval when `agent_type` is present"), the
`feature.json.status` deletion (grilling 25-26), INV-32 (#867).

Grew in planning: **D-11's removal of the ready→backlog exception and T-10's one-time live-board pass.**
No external ask. The grilling settles the near-opposite at line 46 — *"`Backlog` does not participate in
the sync"* — and under D-11 a task at `backlog` projects to `Backlog`, i.e. it does. Measured cost is
zero writes over 656 cards, so the observable outcome of the pass is one printed skip (issue 223,
carried as PB-03). Note-level given the measurement; the grilling reversal is unrecorded.

Also grew: SC-08's reader count 4→11 (#845 and grilling both say four; eleven is a re-measurement,
legitimate) — but SC-08 now quantifies over eleven readers while T-07 gives **five** a
demonstrated-failing case. Per one-assertion-per-item, six readers are graded by nobody.

**What left with T-12, and does D-09 hold it?** Partly. D-09 preserves all three clause corrections
verbatim (`DEC-203 §6` casing/location, `DEC-191` closed-key membership, `DEC-182` shape-gate exclusion),
each with what holds instead. It does **not** carry the new station-vocabulary entry's content — only its
existence. BRIEF PB-04 claims D-09 preserves "the new entry's four content points"; it does not, so
PB-04's "recording job, not a fresh derivation" is false for the new entry.

## SC-NN: proves or observes a proxy

| SC | Ruling |
|---|---|
| SC-01, 03, 06, 07, 10, 12 | **PROVES.** Observation is in a task verify; positive and negative sides both asserted |
| SC-04 | **PROVES.** Count asserted (`= "4"`), not a discarded grep |
| SC-02 | **PROXY, unpinned.** No verify runs it; `evidence: unit` for a tree grep; 6 of 27 lines unowned |
| SC-05 | **PROVES the wrong thing** — names `plan-write.py`, T-09 forbids it (finding 3) |
| SC-08 | **PARTIAL PROXY.** Eleven readers claimed, five given a failing-first case |
| SC-09 | **METHOD MISMATCH.** Clause 1 (`git show <review_sha>:…`) is properly inspection at a pinned ref. Clause 2, "a full run of `check-state.sh` reports no INV-26 line" — the load-bearing regression bound — is a **command result** graded as inspection, discharged by a receipt paste |
| SC-11 | **PROXY at plan level.** No task verify runs `run-unit-tests.sh` in full; rests entirely on the qa gate |
| SC-13 | **PROVES, but weaker than its task.** SC-13's stated grep is `_EXPECT` alone — precisely the blind grep T-06's own intent warns leaves `_st26` at `:1526` live. Met by T-06's stronger two-name verify, not by the criterion as written |

REQ coverage: all seven REQs have ≥1 tracing task; no orphan REQ, no orphan task. The revision's claim
that nothing is orphaned holds for REQ/SC↔task **existence**; it does not hold for SC-02's *method*.

## PB-04: can the record stay honest?

**No.** But DEC-188 does not say what the BRIEF and the dispatch both assume.

DEC-188 (`DECISIONS.md:5945-5947`): the strike rule "applies to a **flat** contradiction with no room
for interpretation. Anything softer than that — a decision that is merely dated, narrowed, or partly
overtaken — is **amended**, and striking it needs the operator's word first." Three one-clause
contradictions are partial, so the instrument is **amendment**, not a strike. That materially shrinks the
"external dependency" the operator declined on Q1: PB-04 and D-09 frame the open question as *strike vs
subsume*, and DEC-188's own last two paragraphs already answer it for a clause-level contradiction.

The sharper point is `:5942-5943`: "This holds **only while the striking actually happens every time**,
and nothing mechanical now checks that it did. The enforcement is a human reading a diff." Deferring the
recording out of this feature removes the sole enforcement DEC-188 has, at the one moment it would have
fired — the diff a human is reading right now. Shipping unchanged spends that moment.

**Minimum honest record**, all inside `.harness/harness/docs/`:
- one amendment line each on DEC-203 §6, DEC-191, DEC-182, naming the struck clause and what holds
  instead (D-09 already holds all three, verbatim);
- one new entry for the station vocabulary — this content is **not** in D-09 and must be written;
- regenerate `DECISIONS-INDEX.md` with `gen-decisions-index.py`: the index stores a per-row source line,
  so lengthening three entries shifts every later anchor and the regeneration test reds. The
  `integration` CI job is a required check on `main` (DEC-183), so this is not optional cleanup.

That is a documentor-lane edit to `.harness/harness/docs/**` — the one `team` lane the lanes block still
declares (`plan.yaml:50-52`), now with no task using it. It has no dependency on the strike-vs-subsume
question if DEC-188's amendment path is taken.

## Open questions for the operator

- **Q1.** The grilling's task-to-issue map bullet is dropped with no record. Disclose as a PB row, or add
  a task? (Blocking — a Settled item leaving the plan unrecorded is the honest-record rule.)
- **Q2.** SC-02 has no verify and `SEAM_NOTES` has no owner. Add the grep to T-07's verify and the table
  to its intent? (Blocking — SC-02 is otherwise ungradeable.)
- **Q3.** SC-05 names `plan-write.py` against T-09's explicit instruction. Struck-with-T-13 like SC-12,
  or reworded to "the writer's basename on disk"? (Blocking.)
- **Q4.** DEC-188 already prescribes amendment for a clause-level contradiction. Does that dissolve
  PB-04's external dependency and let the recording land in this feature on the documentor lane?
- **Q5.** D-11 reverses grilling line 46 ("Backlog does not participate in the sync") without recording
  it. Note-level; record in D-11?
- **Q6.** #867's body states a precondition T-14 does not implement. Comment on the issue at ship?

## Feasibility, against DEC-157

8 of 10 cycles used, 2 of headroom for build + validate + ship. Thirteen tasks, all hand-built by the
operator under DEC-174 with no delegable lane. Four of them (T-02, T-04, T-06, T-07) co-edit
`check-state.sh` and `test-check-state.py`, and `test-gh-sync.py` at 149 s runs in three verifies
(~447 s). One routed-back FAIL on any of those four consumes a cycle. Surface **L**, risk **med**.
Recommend: **proceed**, after the three change-before-build items land as one consolidated edit
(DEC-176) — none of them is a re-plan, all three are one-sentence corrections.
