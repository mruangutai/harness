# SC-04 evidence gaps — operator ruling: ACCEPT BOTH — BUG-1309-mirror-build-entry — 2026-09-08

**BLUF: the operator, re-asked the correctly-scoped question, answered "Accept both gaps". SC-04 is
therefore MET — by operator ruling accepting both evidence gaps on inspected-correct source, NOT by
new automated evidence.** SC-11 stays MET on its existing citation. SC-10 stays NOT MET, pending the
operator's own execution of the hand test. Because SC-04 and SC-11 are both met, the UAT Step 3b
amendment's own stated precondition is satisfied, and the amendment has been applied in this
dispatch. Nothing was re-measured to produce this note; every figure is cited from evidence already
on disk, and no cycle is requested at 16 of 16 used.

## What was accepted — both items, in their own terms

**Gap B — SC-04 clause (g) in panel lettering, clause (h) in goal-check lettering: "ambiguity
decided BEFORE the era gate" ORDERING evidence.** The carrying case `T-05 duplicate era-exempt
claimant still denies before era gate` (`tests/integration/test-merge-gate.py:165-174`) **passes**
and does construct a genuinely era-exempt second claimant, so the clause's literal text is
satisfied. It is **not discriminating** evidence: it survives the natural regression — an era check
hoisted above `len(owners) > 1` and keyed on `owners[0]` — because `glob.glob` returns
`FEAT-9001-fixture-non-era` before `BUG-1030-stale-anchor-write-hazard` on this host, so the
era-exempt claimant never occupies the position an era gate reads. Measured two ways: qa across both
directory-creation orders and security by instrumenting `feature_for()`
(`runs/c18-validator/digest.md` Gap B section; `notes/research-BUG-1309-goalcheck-c18.md` §2;
`notes/qa-c18.md` §2). This was the validator panel's one BLOCKING item, escalated as E1.

**Clause (f) — the ambiguity deny's REASON WORDING.** No automated assertion covers it. The carrying
case `tests/integration/test-merge-gate.py:159-163` asserts the two claimant ids, the absence of
`gh-sync.py`, and run-to-run equality of the reason — and nothing about the wording. There is no
`duplicated top-level branch` assertion anywhere in the suite. This was the clause the c18
goal-check blocked SC-04 on (`notes/research-BUG-1309-goalcheck-c18.md` §1 row f, Q1 of §5).

The two graders blocked on different clauses — the goal-check on (f), the panel on Gap B. The
ruling accepts **both**, which is what closes SC-04; accepting either alone would not have.

## Both are evidence-kind gaps, NOT production defects

Neither item describes wrong behaviour.

- **Ordering is correct in source at `merge-gate.py:172`**: `main()`'s ambiguity guard fires on
  `len(owners)` alone and never on `owners[0]`'s identity, so no era-exempt claimant can slip past
  it whatever the glob order. The cause of Gap B's non-discrimination is this host's glob order, not
  the code under test.
- **Wording is emitted correctly at `merge-gate.py:174`**: it emits
  `Correct the duplicated top-level "branch" field`.

What was missing in each case is the `automated` evidence SC-04 declares, not the behaviour it
declares it over. The ruling accepts the missing evidence kind on inspected-correct source. **It is
not, and must not be read as, a claim that automated evidence now exists.**

## The record of how this ruling came to be (PRINCIPLES rule 15)

Preserved in sequence, not erased:

1. **Commit `d74bdcc8` — acceptance recorded, but INVALID.** It asserted the operator had accepted
   the remaining SC-04 evidence gap for both open clauses, and amended UAT Step 3b from three merge
   invocations to six on that basis. The Main-session question the operator answered **misdescribed
   the c18 blocker**: it presented the denial-reason-wording clause as the accepted item, whereas the
   panel's single blocking item was the ambiguity-before-era-gate ordering evidence. An answer to a
   misdescribed question is not a ruling on the actual gap.
2. **The correction commit — withdrawal.** The acceptance was recorded as superseded, SC-04 was
   returned to NOT MET pending a clarified ruling, and `## Step 3b` was restored byte-identical to
   `d74bdcc8^` (three invocations).
3. **This ruling — VALID.** The operator was re-asked with both items named and distinguished (Gap B
   as the ordering evidence, clause (f) as the reason wording), and answered **"Accept both gaps"**.
   The premise the first acceptance got wrong — which item was the blocker — is the premise this
   question stated correctly, which is why this one stands and the first did not.

## Filename note (still true, still escalated)

The originating dispatch asked for `notes/rulings-2026-09-08-c18-sc04.md`. `check-domain.sh` denies
that path to `harness-pm`: `notes/rulings-*.md` falls under the orchestrator's
`.harness/*/features/**` grant (`.harness/team-config.yaml:45`), which is why the c16 ruling note is
orchestrator-authored. Per #216 the guard is right and is not worked around, so the content lives
here at a pm-owned path. Renaming or re-homing it is the orchestrator's write.

## Resulting SC record

| SC | Verdict | Basis |
|---|---|---|
| SC-04 | **MET — by operator ruling accepting both evidence gaps on inspected-correct source** | operator answered "Accept both gaps" to the corrected question: Gap B / clause (g)-(h) ordering evidence and clause (f) reason wording. NOT met by new automated evidence; nothing re-measured. Source inspected correct at `merge-gate.py:172` and `:174` |
| SC-11 | **MET** | at the pin, on evidence, unchanged by this dispatch — `notes/research-BUG-1309-goalcheck-c18.md` §3 |
| SC-10 | **NOT MET — pending operator execution** | the hand test is still owed and still blocks the ship decision — `notes/uat-BUG-1309-mirror-build-entry.md` |

This note changes no approval and moves no station.

## Backlog remedies — still open, still unscheduled

Accepting an evidence gap does not close the gap and does not schedule its fix. Both remain
follow-up items for a future effort:

1. add `"branch" in reason` as one conjunct on the existing case at
   `tests/integration/test-merge-gate.py:159-163` — clause (f);
2. reorder the fixture so the era-exempt claimant sorts into `owners[0]` — Gap B.

**The budget is 16 of 16 used. No cycle is opened by this note and none is requested.**

## The three measured merge-flag denial forms — retained, and now applied

They remain valid, measured evidence:

- `git merge -F /tmp/message <branch>` → deny
- `git merge --cleanup strip <branch>` → deny
- `git --attr-source HEAD merge --no-ff <branch>` → deny

All three deny at the pin, `rc=0`, `decision=deny`, naming `FEAT-9001-fixture-non-era` and the
`gh-sync.py open <dir>` re-run command, exercised at `tests/integration/test-merge-gate.py:219-221`
(loop `:218-226`) per `notes/qa-c18.md` §5 and `runs/c18-validator/digest.md`. **They were not
re-measured in this dispatch.**

**The amendment's precondition — "SC-04 and SC-11 met" — is now satisfied, and the amendment has
been applied.** `## Step 3b` of `notes/uat-BUG-1309-mirror-build-entry.md` now carries six
invocations: the three already-approved forms (`--no-ff`, `--squash`, `-m message`) untouched and
first, then these three. Its observe line reads SIX JSON lines, PASS requires all six to print a
`deny`, and FAIL keeps its "a silent allow here is the whole defect" reasoning extended to six.

**The amendment's only deviation from the measured strings — the branch argument.** The three forms
were measured against the integration fixture's branch `feature/test`. The UAT fixture's branch is
`feature/uat-scratch` (`feature.json`, and every other UAT step). `feature/test` owns nothing in the
UAT fixture, so a Step 3b line using it would ALLOW and the operator would read a correct gate as a
failure. Every added invocation therefore substitutes `feature/uat-scratch`, in the same
`printf … | HARNESS_PROJECT_DIR=$UAT_ROOT bash …/merge-gate.sh` shape as the existing three. That
substitution is the sole difference between the measured strings and the Step 3b lines.

## Non-modification

The only files written in this dispatch are:

1. this note (rewritten to record the clarified operator acceptance);
2. `notes/uat-BUG-1309-mirror-build-entry.md`, `## Step 3b` and its observe/PASS/FAIL lines only —
   no step renumbered, no step added, Steps 1-3 and 4-9, the preamble, the safety and
   verification-gap paragraphs and `## Your verdict` untouched;
3. one appended bullet in `observations/harness-pm.md`, via `observations-merge.py`.

`BRIEF.md`, `plan.yaml` including every approval field, `feature.json`, `STATE.md`, every production
source file, every test file, every hook and every other agent's notes are **untouched**. Nothing
was shipped, merged or pushed; no formatter, linter, project-wide suite or integration re-run was
executed; no cycle was opened.
