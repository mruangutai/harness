# Receipt — harness-data-engineer — distill — FEAT-23 — run 2026-08-17-13-distill-eng

## What happened

`.harness/expertise/harness-data-engineer.md` did not exist. Created it. Two entries accepted,
one candidate rejected. Checker green.

## Counts

- Before: `0/0/0/0` (Patterns/Gotchas/Outcomes/Open) — file absent.
- After: `1/1/0/0`.

## Checker output (verbatim)

```
$ bash .claude/skills/harness/bin/check-expertise.sh .harness/expertise/harness-data-engineer.md
OK   .harness/expertise/harness-data-engineer.md
EXIT:0
```

## Accepted entries, by source

- **(a) from an observations log:** zero, by construction — this agent's `observations/` file
  does not exist for FEAT-23; this run produced no observations entries (`files_touched: []` on
  the segment digest's `angle-efficiency` row).
- **(b) surfaced by the lead's skim relay:** both accepted entries — C2 and C3 in the dispatch.
  I re-derived C2 at source (`gh_board.py:180-189`, confirmed the read-before-write ordering
  independently) before accepting it; per the dispatch, a lead-surfaced candidate I then verified
  still counts as (b), noted here as lead-relayed with my own derivation behind it. C3 I accepted
  directly from the dispatch's framing without an independent source check beyond the digest's
  own numbers.
- **(c) self-derived from the segment digest, absent from the lead's relay:** none.

## Accepted

**Pattern P-01** (from C3 — "measuring a cost you are about to declare negligible"):

> WHEN judging whether a measured cost is negligible DO state it in the unit matching its
> frequency — per-call, per-session, or share of the surrounding budget — not a bare number. A
> reader cannot check "negligible" against a figure with no scale attached.

Why: the segment digest shows the discriminating factor between the two findings that got flagged
(1.163s / 5.589s bucket — a real share) and the ones that didn't (0.043ms per call on a
once-per-feature command) was never the raw number, it was which unit it was expressed in. The
skill states the policy (judge minutes/hot-path-ms) but not how to report the number so a reader
can check it — this closes that gap. Generalizes past this repo: any efficiency judgment needs a
scale, not a bare figure.

**Gotcha G-01** (from C2 — the self-disclosed bounds breach):

> WHEN timing-probing a CLI that shells out to an external service (e.g. `gh`) DO wire the
> fake-binary env vars first, or run from a directory outside any real target — probing from a
> real project root can reach production and issue live network calls.

Why: this is the mechanism, not the disclosure. The disclosure itself was correct behavior but is
situational, not durable craft — the durable fact is that an un-isolated timing probe of a
CLI wrapper reaches the real backing service. True in any repository with a CLI that shells out.

## Rejected

**C1 — the empty return itself.** Rejected as written. An entry saying "an empty return can be a
real result" restates `.claude/skills/harness-simplify/SKILL.md:31-32` and `:67` verbatim — it is
the shipped procedure read back, not new craft. The durable residual — what makes an empty return
*defensible* rather than merely asserted — is what P-01 captures instead. No separate entry for
C1's literal form.

## Layer check

Both accepted entries are **craft**, not repository-tier. Neither turns on a path, file, decision
or invariant unique to this repository — "state costs in a comparable unit" and "isolate before
timing a network-calling CLI" hold in any codebase. No repository-tier file was written or
considered for a repository-tier path (there is no such tier wired in this repo per the dispatch's
correction).

## `suite:` truthfulness — verbatim

```
$ bash .claude/skills/harness/bin/run-unit-tests.sh > <scratchpad>/feat23-de-suite.log 2>&1
EXIT: 0
$ grep -c "^PASS" <scratchpad>/feat23-de-suite.log
197
$ grep -c "^FAIL" <scratchpad>/feat23-de-suite.log
0
```

No source touched this cycle — Expertise-file-only edit plus this receipt. `validate-digest.py`
rejects `suite: n/a` alongside `VERDICT: PASS` for the `dev`-aliased schema (confirmed empirically:
piping a `suite: n/a`/`task: none`/`PASS` block through the validator returns `BLOCKED (contract
violation)` — the `task: none` release in `harness-tdd-enforcement` names `task_verify` only, not
`suite`). This re-run establishes `suite: pass` truthfully, same mechanism as the sibling
(`receipt-harness-backend-dev-2026-08-17-13-distill-eng.md`, itself citing FEAT-12's precedent),
nothing more — it is not a claim that this distillation added or exercised any test.

## `expertise_update` (the ops, verbatim)

```yaml
expertise_update:
  - op: add
    section: Patterns
    entry: "WHEN judging whether a measured cost is negligible DO state it in the unit matching its frequency — per-call, per-session, or share of the surrounding budget — not a bare number."
    why: "digest's two findings turned on unit, not magnitude; skill states the policy but not how to report the number"
  - op: add
    section: Gotchas
    entry: "WHEN timing-probing a CLI that shells out to an external service (e.g. gh) DO wire the fake-binary env vars first, or run from a directory outside any real target."
    why: "self-disclosed bounds breach this run — an un-isolated probe reached the real gh and issued one live GraphQL call"
```
