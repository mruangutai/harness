# SC-04 evidence gap — NO valid operator ruling exists — BUG-1309-mirror-build-entry — 2026-09-08

**BLUF: there is currently NO valid operator ruling on the SC-04 automated-evidence gap, and
SC-04 therefore reads NOT MET, pending a clarified operator ruling.** The acceptance recorded in
commit `d74bdcc8` — which asserted that the operator accepted the remaining SC-04 evidence gap for
both open clauses, and which amended UAT Step 3b on the strength of it — is **SUPERSEDED**. The
Main-session question the operator answered **misdescribed the c18 blocker**: it presented the
denial-reason-wording clause as the accepted item, whereas the panel's single blocking item is the
ambiguity-before-era-gate ordering evidence. An answer to a misdescribed question is not a ruling
on the actual gap. Nothing was re-measured to produce this note; every figure is cited from
evidence already on disk, and no cycle is requested.

**History, not deleted (PRINCIPLES rule 15).** The earlier note at this path stated that the
operator had granted acceptance of the remaining SC-04 automated-evidence gap for both open
clauses, and that SC-04 was consequently met by that recorded ruling; on that basis it amended UAT
Step 3b from three merge invocations to six. Both acts are recorded here as superseded and
withdrawn — the earlier statement existed, was wrong in its premise, and is retracted rather than
erased. The commit that carried it is `d74bdcc8`; the pre-amendment UAT text is `d74bdcc8^`.

**Filename note (still true, still escalated).** The originating dispatch asked for
`notes/rulings-2026-09-08-c18-sc04.md`. `check-domain.sh` denies that path to `harness-pm`:
`notes/rulings-*.md` falls under the orchestrator's `.harness/*/features/**` grant
(`.harness/team-config.yaml:45`), which is why the c16 ruling note is orchestrator-authored. Per
#216 the guard is right and is not worked around, so the content lives here at a pm-owned path.
Renaming or re-homing it is the orchestrator's write.

## The actual blocking gap — Gap B, as the panel names it

**Gap B — SC-04 clause (g) in panel lettering, clause (h) in goal-check lettering: "ambiguity
decided BEFORE the era gate".** This is the panel's one BLOCKING item (`runs/c18-validator/digest.md`
Gap B row of the per-gap table, plus Q1 and escalation E1).

The carrying case `T-05 duplicate era-exempt claimant still denies before era gate`
(`tests/integration/test-merge-gate.py:165-174`) **passes** and does construct a genuinely
era-exempt second claimant, so the clause's literal text is satisfied. It is **not discriminating
evidence** for the ordering: it survives the natural regression — an era check hoisted above
`len(owners) > 1` and keyed on `owners[0]` — because `glob.glob` returns `FEAT-9001-fixture-non-era`
before `BUG-1030-stale-anchor-write-hazard` on this host, so the era-exempt claimant never occupies
the position an era gate reads. Measured two ways: qa across both directory-creation orders and
security by instrumenting `feature_for()` (`runs/c18-validator/digest.md` Gap B section;
`notes/research-BUG-1309-goalcheck-c18.md` §2; `notes/qa-c18.md` §2).

Note the tier disagreement, unresolved and carried by name: the c18 goal-check §2 **ruled clause (h)
MET** on the clause's literal subject, while the validator panel rates the same gap **NOT CLOSED**
as automated evidence and escalated it as E1. Neither has a valid operator ruling.

## Second open, unruled evidence item — clause (f)

**Clause (f) — the ambiguity deny's reason wording carries NO automated assertion.** The carrying
case `tests/integration/test-merge-gate.py:159-163` asserts the two claimant ids, the absence of
`gh-sync.py`, and run-to-run equality of the reason — and nothing about the wording. Source is
inspected-correct: it emits `Correct the duplicated top-level "branch" field` at `merge-gate.py:174`
(`notes/research-BUG-1309-goalcheck-c18.md` §1 row f).

**The two graders block on different clauses.** The c18 goal-check graded SC-04 **UNMET solely on
clause (f)** (`notes/research-BUG-1309-goalcheck-c18.md` §1 and Q1 of §5); the validator panel
blocks on **Gap B** (clause (g)/(h)). **Neither item carries a valid ruling**, so both stay open.

## Both are evidence-kind, NOT production defects

Neither item describes wrong behaviour. `main()`'s ambiguity guard fires on `len(owners)` alone and
never on `owners[0]`'s identity (`merge-gate.py:172`), so the ordering is correct in source and the
message uses `sorted(...)`; the duplicated-`branch` wording is emitted correctly at
`merge-gate.py:174`. What is missing in each case is the `automated` evidence SC-04 declares, not the
behaviour it declares it over. The cause of Gap B's non-discrimination is this host's glob order, not
the code under test.

**Backlog remedies (no cycle):**

1. one added conjunct on the existing case at `tests/integration/test-merge-gate.py:159-163`
   (e.g. `"branch" in reason`) — clause (f);
2. one fixture ordering change so the era-exempt claimant sorts first into `owners[0]` — Gap B.

**No cycle exists to spend and none is requested.** The budget is 16 of 16 used; both are backlog
items for a future effort, not work scheduled by this note.

## Resulting SC record

| SC | Verdict | Basis |
|---|---|---|
| SC-04 | **NOT MET — pending clarified operator ruling** | two open, unruled evidence items: Gap B / clause (g)-(h) (panel's blocking item, `runs/c18-validator/digest.md` Q1/E1) and clause (f) (`notes/research-BUG-1309-goalcheck-c18.md` §1). Behaviour inspected-correct at `merge-gate.py:172` and `:174`. Not re-measured |
| SC-11 | **MET** | at the pin, on evidence, unchanged by this cycle — `notes/research-BUG-1309-goalcheck-c18.md` §3 |
| SC-10 | **NOT MET / NOT EXECUTED** | the operator's hand test is still owed and still blocks the ship decision — `notes/uat-BUG-1309-mirror-build-entry.md` |

This note changes no approval and moves no station.

## The EXACT remaining operator decision — stated once, here

Phrased so it cannot be answered by accident. There are **two separate questions**, and an answer
must name which one it answers:

1. **Gap B — the ambiguity-before-era-gate ORDERING evidence** (SC-04 clause (g) panel lettering,
   clause (h) goal-check lettering). Its case passes but does not discriminate against an
   `owners[0]`-keyed era-gate hoist, because of this host's glob order. Either **accept this
   evidence gap on inspected-correct source with a recorded ruling**, or **carry it as a follow-up
   bug**.
2. **Clause (f) — the ambiguity deny's REASON WORDING evidence.** No case asserts the wording;
   source is correct at `merge-gate.py:174`. Either **accept this evidence gap on inspected-correct
   source with a recorded ruling**, or **carry it as a follow-up bug**.

At 16/16 cycles **no work is offered either way**: accepting does not schedule a fix and carrying
does not open a cycle. Accepting item 1 alone does not make SC-04 met while item 2 is open, and vice
versa. Until both are ruled, SC-04 stays NOT MET.

## The three measured merge-flag denial forms are RETAINED, not discarded

They remain valid, measured evidence and are **not** withdrawn by this correction:

- `git merge -F /tmp/message feature/test` → deny
- `git merge --cleanup strip feature/test` → deny
- `git --attr-source HEAD merge --no-ff feature/test` → deny

All three deny at the pin, `rc=0`, `decision=deny`, naming `FEAT-9001-fixture-non-era` and the
`gh-sync.py open <dir>` re-run command, exercised at `tests/integration/test-merge-gate.py:219-221`
(loop `:218-226`) per `notes/qa-c18.md` §5 and `runs/c18-validator/digest.md`. **Do not re-measure
them.**

They become available for a UAT Step 3b amendment **only once a valid operator ruling makes SC-04
met** — the amendment's own precondition is "SC-04 and SC-11 met". SC-04 is not met, so **Step 3b
stays exactly as approved**: three invocations, and it has been restored to that state in this
dispatch.

## Non-modification

The only files written in this dispatch are:

1. this note (rewritten to record no operator acceptance);
2. `notes/uat-BUG-1309-mirror-build-entry.md`, restored so `## Step 3b` is byte-identical to
   `d74bdcc8^` — `git diff d74bdcc8^ -- <that path>` is empty;
3. one appended bullet in `observations/harness-pm.md`, via `observations-merge.py`.

`BRIEF.md`, `plan.yaml` including every approval field, `feature.json`, `STATE.md`, every production
source file, every test file, every hook and every other agent's notes are **untouched**. Nothing
was shipped, merged or pushed; no formatter, linter, project-wide suite or integration re-run was
executed; no cycle was opened.
