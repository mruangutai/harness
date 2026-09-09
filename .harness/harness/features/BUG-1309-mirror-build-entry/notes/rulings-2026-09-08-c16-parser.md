# Operator rulings — c15 escalation (VF-01..VF-04) — BUG-1309-mirror-build-entry — 2026-09-08

**Both open questions are answered FIX, and the cycle budget is raised 14 → 16.** The ship is not
blocked on a decision any more; it is blocked on one main-session-direct implementation round
(DEC-174) and the re-validation that follows it, then the operator's own SC-10 UAT.

## Provenance — read this before trusting the rulings below

These were relayed **inline by the main session** in the dispatch that opened this orchestrator run.
There is no `notes/answers-<runid>.md` on disk for this round and this file is **not** that channel:
the orchestrator may not author an answers file (issue #671), so this note is an
orchestrator-authored TRANSCRIPTION of a main-session relay. It is evidence of the relay, never a
substitute for it. The measurements it cites are the orchestrator's own, taken at
`review_sha` `e374c9a29e4321968e4c2a6bbae045da9203440c` and recorded in `STATE.md` before the relay.

## R-4 — the parser is FIXED comprehensively, not form by form (answers Q1 and Q2)

The c15 evidence stands: at `e374c9a2` `git_merge` splits option handling into two closed
enumerations of option NAMES (`merge-gate.py:46-75`), and the CLASS signed T-05 step 2 requires
survives its instances. Measured against real git 2.50.1 and the real hook
(`/tmp/bug1309-c15-verify.py`, orchestrator, at the pin):

| form | real git | gate today | required after R-4 |
|---|---|---|---|
| `git merge -F <file> <ref>` | MERGED | none — silent allow | **DENY** |
| `git merge --cleanup <mode> <ref>` | MERGED | none — silent allow | **DENY** |
| `git --attr-source <tree> merge --no-ff <ref>` | MERGED | none — silent allow | **DENY** |
| `git merge --abort` / `--continue` / `--quit` | not a merge | **deny** (regression of `e374c9a2`) | **ALLOW, exit 0** |

Four clauses, all ruled FIX:

1. **Value-taking options are handled as a CLASS in BOTH positions** — pre-subcommand git globals
   and post-`merge` options, in the attached (`--opt=value`) and the detached (`--opt value`)
   spelling. A closed set of names that must be extended per option is the defect, not the fix.
2. **The gate FAILS CLOSED when a merge is identified and its ref is not.** Where the walk cannot
   name the ref, the head branch resolves through the existing local fallback and the receipt rule
   decides — a merge command whose ref the gate cannot read is never a silent allow.
3. **Merge CONTROL operations are not merges.** `git merge --abort`, `--continue` and `--quit`
   ALLOW at exit 0 with no permission decision, on an owing branch as much as on any other. They
   move no branch and the operator needs them precisely while a merge is in trouble.
4. **`git_merge` grades 4 or better** on `code-grade.py`. At the pin it is GRADE 3 / BAR 4 / FAIL
   (CYCLOMATIC 8, COGNITIVE 15, ABC 16.1) — the grade-4 figure carried into the c15 dispatch was
   falsified by the tool at the tip. A comprehensive parser that grades 3 is not accepted; the fix
   is decomposition, not a suppression.

**The bounds R-4 must not break** — each is a case that is green today and stays green unmodified:
the two malformed-record fences (`tests/integration/test-merge-gate.py:128-150`), the no-record
branch, `git merge-base`, `git commit -m 'merge …'`, and every allow case in the existing bed. A
fail-closed posture that widens into "deny anything unparseable" resurrects cycle 11's `473d82cb`,
which panel c5 failed and `894adc0f` scoped back.

**Tests are DISCRIMINATING or they are not evidence.** Each of the four rows above gets a case in
the reserved bed, and each must be shown red against `e374c9a2` before it is shown green — the
same present-tense discrimination requirement SC-03 and SC-07 carry, applied here by ruling.

## R-5 — the cycle budget is raised 14 → 16

`max_total_cycles` moves to 16 in `feature.json` on the operator's say-so (DEC-157: per-feature
raises are user decisions recorded there). It funds exactly two rework cycles: **c16**, this
remediation round, and **c17**, the re-validation that grades it. It is not a licence for a third
attempt at the same parser — an exhausted budget is a hard stop and returns `BLOCKED`.

## What each ruling binds, and to whom

| ruling | surface | lane |
|---|---|---|
| R-4 clauses 1-4 | `.claude/skills/harness/bin/merge-gate.py` `git_merge` and its helpers | **main-session-direct** (DEC-174; `plan.yaml` lanes rows 47-49) |
| R-4 tests | `tests/integration/test-merge-gate.py` | **main-session-direct** (lanes rows 73-75 — each gate's own test is inside the carve-out) |
| R-5 | `feature.json` `max_total_cycles` | orchestrator, on the operator's decision |

No squad may execute any of R-4. The harness specifies it and hands it to the operator to run:
`notes/direct-packet-2026-09-08-c16-parser.md`.

## Consequences the operator has not yet been asked about

1. **The plan signature must move again.** The T-05 amendment R-4 forces (see
   `notes/research-BUG-1309-planamend-c16.md`) leaves `approval:` byte-identical by design, so the
   plan will read `approved 2026-09-08` over text amended after that signature until the main
   session runs `plan-merge.py sign-approval`. **Required before ship.**
2. **SC-04 does not mention merge control operations.** R-4 clause 3 is gated by T-05's `verify`
   and traces to no success criterion as written; pm's amendment note records whether that is
   coverage inside SC-04's existing subject or a disclosed verification gap. Either answer is the
   operator's to accept.
3. **SC-10 still blocks the ship** (`notes/uat-BUG-1309-mirror-build-entry.md`), and its Step 3b
   must be extended with the three silent-allow forms once they deny.
4. **After R-5 the budget is 15 of 16 used** once this remediation cycle is recorded. One cycle
   remains for the re-validation round. A second failed implementation attempt exhausts it.
