# Operator ruling — SC-04 remaining evidence gap — BUG-1309-mirror-build-entry — 2026-09-08

**The operator ACCEPTS the remaining SC-04 automated-evidence gap at
`9fe5cf3112aed6782dfe3f1833b5e7077b31d953`, on inspected-correct behaviour, at an exhausted budget
(`cycles_used` 16 of 16). SC-04 therefore reads MET by recorded ruling — not by re-measurement.**
Nothing was re-run to produce this note; every figure below is cited from evidence already on disk.
I am the scribe here, not the decider.

**Filename note (read first).** This dispatch asked for `notes/rulings-2026-09-08-c18-sc04.md`.
`check-domain.sh` denies that path to `harness-pm`: `notes/rulings-*.md` falls under the
orchestrator's `.harness/*/features/**` grant (`.harness/team-config.yaml:45`), which is why the
c16 ruling note is orchestrator-authored. Per #216 the guard is right and is not worked around, so
the content lives here, at a pm-owned path. Renaming or re-homing it is the orchestrator's write.

## The naming discrepancy — said out loud, once

The operator's dispatch spelled the accepted item **"clause (g)"**; that is the letter the c18
validator panel uses for "ambiguity decided before the era gate"
(`runs/c18-validator/digest.md`, per-gap table). The c18 goal-check letters the same clause **(h)**
and reserves **(f)** for the reason-wording clause
(`notes/research-BUG-1309-goalcheck-c18.md` §1). **The ruling accepts BOTH open evidence items**,
which is what makes it unambiguous under either lettering.

## What is accepted

**Clause (f) — the ambiguity deny's reason wording carries NO automated assertion.**
The carrying case `tests/integration/test-merge-gate.py:159-163` asserts the two claimant ids, the
absence of `gh-sync.py`, and run-to-run equality of the reason — and nothing about the wording.
Production is inspected-correct: it emits `Correct the duplicated top-level "branch" field` at
`merge-gate.py:174` (`notes/research-BUG-1309-goalcheck-c18.md` §1 row f;
`notes/handoff-validate.md` Trust).

**Clause (h) — the era-ordering case is a behaviour witness, not a defence.**
`T-05 duplicate era-exempt claimant still denies before era gate`
(`tests/integration/test-merge-gate.py:165-174`) PASSES and does construct a genuinely era-exempt
second claimant, but it does not redden against an `owners[0]`-keyed era-check hoist, because
`glob.glob` returns `FEAT-9001-fixture-non-era` before `BUG-1030-stale-anchor-write-hazard` on this
host (`notes/research-BUG-1309-goalcheck-c18.md` §2; `notes/qa-c18.md` §2). The source is
order-independent by construction: the guard is `if len(owners) > 1:` at `merge-gate.py:172`, it
never keys on `owners[0]`'s identity, and the message uses `sorted(...)`.

## Both are evidence-kind, NOT production defects

Neither item describes wrong behaviour. Clause (f)'s wording is correct in source at
`merge-gate.py:174`; clause (h)'s ordering is correct in source at `merge-gate.py:172`. What is
missing in each is the `automated` evidence SC-04 declares, not the behaviour it declares it over.
Neither is a regression: c17's clause table had no row for (f) at all
(`notes/handoff-validate.md` Trust, citing `notes/research-BUG-1309-goalcheck-c17.md:44-56`).

## Follow-up — backlog only, no cycle

1. one added conjunct on the existing case at `tests/integration/test-merge-gate.py:159-163`
   (e.g. `"branch" in reason`);
2. one fixture ordering change so the era-exempt claimant sorts first into `owners[0]`.

**No cycle exists to spend and none is being requested.** The budget is 16 of 16 used; both are
backlog items for a future effort, not work scheduled by this ruling.

## Resulting SC record

| SC | Verdict | Basis |
|---|---|---|
| SC-04 | **MET by ruling** | evidence gap (clauses f and h) accepted by the operator; behaviour inspected-correct at `merge-gate.py:172` and `:174`. Not re-measured |
| SC-11 | **MET** | at the pin, on evidence, unchanged by this cycle — `notes/research-BUG-1309-goalcheck-c18.md` §3 |
| SC-10 | **NOT MET / NOT EXECUTED** | the operator's hand test is still owed and still blocks the ship decision — `notes/uat-BUG-1309-mirror-build-entry.md` |

This ruling changes no approval and moves no station.

## Non-modification

The only files written in this dispatch are this note and
`notes/uat-BUG-1309-mirror-build-entry.md` (Step 3b only). `BRIEF.md`, `plan.yaml` including every
approval field, `feature.json`, `STATE.md`, every production source file, every test file and every
hook are **untouched**. Nothing was shipped, merged or pushed; no formatter, linter or
project-wide suite was run.
