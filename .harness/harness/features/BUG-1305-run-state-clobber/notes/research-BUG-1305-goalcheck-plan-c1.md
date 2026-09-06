# Goal-check — BUG-1305 plan vs stated intent (panel-1, cycle 1)

## BLUF

**No — not as written.** The plan delivers Mode B and the detection half of Mode A end to end, but its
Mode-A *prevention* (REQ-01) closes only routes that were already closed or were never named as the
live mechanism, and leaves the diagnosis's **leading** clobber route (two different runs sharing a
slug, hence a string-equal `run_id`) open by construction — a residual disclosed only inside T-04's
task body, not where the operator signs. The Advisor, whom the operator delegated these questions to,
ruled that a plan leaving that route open "is not deliverable as written" (`notes/review-harness-code-reviewer-advisor-c1.md:21-23`).
**Fit for the adversarial panel; NOT fit for signature until F-01 and F-02 are resolved.**

Verified independently: every code anchor and prose gloss the plan asserts is correct
(check-domain.sh `RE_STATE_YAML` :1439 / `_no_parser` :1475 / #1124 branch :1567 / `RE_RUN_DIGEST`
comment :1237-1238 / Edit reconstruction :1905; check-state.sh loop :1426 with INV-16 :1443 before
INV-15 :1476; validate-digest.py `check_artifact_file` :1486 and its single-candidate `cands` :1535;
harness_yaml `_resolve_identity` :511; inflight_registry :255-258; SKILL.md:272-274;
harness-team/SKILL.md:45; DECISIONS.md:3243). Lane rows spot-checked with
`check-domain.sh --resolve`: both SKILL.md files answer `NOBODY`, the four bin/test surfaces answer
as the plan records. Highest live invariant is INV-35, so T-03's "next unused number" instruction is
sound. `feature.json max_total_cycles: 8` matches the stated cap.

## Findings

**F-01 · high · Mode-A prevention does not reach the mechanism the diagnosis leads with.**
`run_identity.conflict()` (T-01, plan.yaml:136-143) denies on `run_id`, then `feature`, `squad`,
`host`. In the diagnosis's route 8 — the "leading Mode-A candidate"
(`notes/receipt-harness-dev-ops-diag-c1.md:52`) — two runs of the *same feature* choose the same
`<purpose>-<squad>` slug, so all four fields are equal and `conflict()` returns None. T-02 therefore
denies nothing that check-domain.sh:1567 does not already deny, except the narrow new case of a run
directory whose prior `state.yaml` was **deleted**. The signal that would discriminate (`session_id`)
is recorded by D-01 and explicitly barred from being a denial input; T-04 measures it and is forbidden
to write a follow-through task (plan.yaml:359-360), so even a `discriminates: yes` answer lands
nowhere. Scenario: after this feature ships, two lead squads in one feature reuse `plan-product`; the
second `state.yaml` Write is accepted as an upsert exactly as in BUG-1286, the operator is told Mode A
is prevented, and the only thing that fires is T-03's post-hoc report *after* the record is destroyed.
The grilling artifact puts "risk acceptance, scope reduction" out of scope
(`grilling-six-residual-bugs-2026-09-05.md:28`), which is what deferring this to a post-ship operator
call amounts to.

**F-02 · med · The residual is invisible where the operator signs.** The disclosure lives only in
T-04's `intent` prose (plan.yaml:356-360). BRIEF.md — the document the human reads — asserts REQ-01 as
an outcome (:53-56) and SC-01 as met by the marker test (:140-145), and names no residual anywhere;
`plan.yaml` has no `open_questions` slot (the template carries none). Scenario: the operator signs a
BRIEF that reads as "Mode A prevented", the goal-check later marks SC-01 `met` because its test
fixture uses *differing* run_ids, and the open route is discovered by the next clobber.

**F-03 · med · T-07 is scope leakage with an inflated trace.** T-07 traces `REQ-01`, but D-07
(plan.yaml:76-79) states no mechanism in the plan reads a slug and T-07's own body forbids any
mechanism change (:540-542) — so it cannot move REQ-01's outcome, and no SC covers it. What it does do
is rewrite `.claude/skills/harness/SKILL.md` doctrine and supersede part of signed DEC-145
(DECISIONS.md:3243). BRIEF.md names DEC-145 nowhere, in Constraints or elsewhere. Scenario: the
operator approves a plan whose visible framing is "fix #1305" and thereby supersedes an unrelated
clause of a signed decision, with the change graded by no criterion.

**F-04 · med · SC-07 is graded on an artifact no task produces.** SC-07 (BRIEF.md:176-181) requires
every altered assertion to be "justified **in the plan**"; T-08's deliverable is
`notes/regression-delta-BUG-1305.md` (plan.yaml:553), and pm may not add justifications to an approved
plan without resetting approval. "Pass unchanged in substance" is also reader-dependent. Two readers
grading SC-07 — one opening plan.yaml, one opening the note — reach opposite verdicts.

**F-05 · med · SC-01's route set is under-specified against REQ-01's.** REQ-01 says "any write route
the harness governs"; SC-01 says "both governed tool write routes". Bash is a governed, refusing route
(`bash-write-guard.sh:745-767`) and NotebookEdit's coverage rests on an unverified host-matcher
assumption the diagnosis raised as its own open Q1 (`receipt-...-diag-c1.md:47`, :209-212). A reader
taking "both" as {Write, Edit} passes SC-01; a reader taking REQ-01's wording fails it.

**F-06 · low · D-04 decides an operator question instead of asking it.** DEC-208 ruling 3's scope
sentence is measured false; D-04 (plan.yaml:64-67) records that this feature will *not* amend it. The
observation reaches BRIEF Constraints (:104-108), but nothing puts a ruling in front of the operator —
it is framed as settled. Scenario: the plan is signed, the false clause survives in the decision
record, and the next reader of DEC-208 is misled exactly as REQ-06's comment-reader was.

**F-07 · low · T-03's un-droppability is real but not structural.** `depends_on` makes T-03 depend on
T-01 only; nothing depends on T-03 except T-08. There *is* an execution order in which T-03 is the one
task that does not land (T-01, T-02, T-05, T-06, T-07 then budget exhaustion). What actually holds the
line is SC-02 being its own criterion plus T-08's `depends_on: [T-02, T-03, T-05, T-06]` — i.e. the
ship gate, not the graph. The claim survives in effect; the plan's phrasing overstates its mechanism.

**F-08 · info · The clobber-vs-malformed discriminator lives in the task, not the criterion.** SC-03
(BRIEF.md:151-157) says an operator "can tell" the two apart; the falsifiable rule — must not reuse
INV-16's "non-checkpoint top-level key" wording — is only in T-03's intent (plan.yaml:299-303). A
grader holding the criterion alone is judging tone.

## Answers to the seven questions

1. **Intent coverage — partial.** Eight-cycle cap present (`feature.json max_total_cycles: 8`);
   material questions were delegated and answered (advisor note, five questions). Ship/merge/close are
   lifecycle stations, correctly not tasks. **Not delivered by any task:** the Advisor's Q2 remedy —
   consuming an identity signal as prevention. F-01.
2. **Mode separation — holds.** Mode A: REQ-01/02/03 → T-01,T-02,T-03,T-04 → SC-01,02,03. Mode B:
   REQ-04/05/06 → T-05,T-06 → SC-04,05,06. No task and no criterion conflates them; either mode can be
   declared done while the other is open. One coupling, benign: T-06 `depends_on: [T-02]`, an
   edit-collision ordering on check-domain.sh, not a conflation. SC-07 spans both by design.
3. **Determinism — SC-02, SC-04, SC-05 are clean; SC-01 (F-05), SC-03 (F-08) and SC-07 (F-04) admit
   opposite verdicts.** No criterion anchors on a line number or a population count — checked
   explicitly against the two disagreeing counts in the evidence base
   (`ship-review-2026-09-05-ship-final.md:44-49`; diagnosis :189-195 records 612/38 against a claimed
   608/37). SC-03 and SC-06 correctly pin `git show REVIEW_SHA:`.
4. **Unbudgetable detection — the claim does NOT survive as stated.** See F-07: no `depends_on` edge
   forces T-03 to land, and an order exists where it is the one that does not. It is held by SC-02 and
   by T-08's dependency instead.
5. **The admitted residual — stated, but not where it counts.** T-04 is honest that a `no` or
   `inconclusive` leaves a Mode-A route open and that the call is the operator's. It appears in no
   BRIEF clause, no decision text and no SC. F-02. It is also worse than the plan admits: per F-01 the
   route is open regardless of T-04's answer, because no task can act on a `yes`.
6. **Scope leakage — one instance.** T-05 is correctly confined to `check_artifact_file`'s root
   resolution and fail-open branch; #1303's `code_grade`/`review_sha` surface is untouched and D-05
   records the merge serialisation. No task touches #1302, #1304, #1306 or #1308. T-07 leaks — F-03.
7. **Signature-blocking residue — half surfaced.** The DEC-145 supersession is loud in the plan (D-06,
   T-07:509-510) but absent from the BRIEF (F-03). The DEC-208 falsity is in the BRIEF but framed as
   already-decided rather than as an operator ruling (F-06). Neither is buried inside a task body, but
   neither is presented as a live choice the operator must make.

## Verdict on readiness

Fit to go to the adversarial panel now. **Not fit for signature:** F-01 and F-02 must change first —
either a task that turns the measured identity signal into a denial input (the Advisor's Q2/Q5
answer), or an explicit, operator-facing statement in BRIEF.md that the slug-reuse route stays open,
which is a scope reduction the grilling artifact puts out of scope and therefore an operator ruling,
not a plan decision. F-03..F-05 are cheap edits at plan time and expensive after.

## git status (verbatim, run at end of this run)

```
?? .harness/harness/features/BUG-1305-run-state-clobber/
```

No tracked file is modified; this note is untracked inside that directory. I edited no plan.yaml, no
BRIEF.md and no code.
