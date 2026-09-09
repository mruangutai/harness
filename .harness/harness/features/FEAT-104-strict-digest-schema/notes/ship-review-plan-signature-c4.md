# FEAT-104 — final plan signature packet (c4)

**Ready to sign.** All six rulings executed, Q2 closed, and `check-state.sh` is down to a single
FEAT-104 violation: "BRIEF.md is NOT approved" — the signature gate itself. Nothing is implemented
and nothing is signed.

Supersedes `c3`, which is kept on disk with `c2` because each carries a statement of mine that was
later found wrong, and a correction is only legible beside what it corrects.

## Rulings — all six executed and verified on disk

| Ruling | State |
|---|---|
| OD-1 — hermetic inert fixture remedy | APPLIED — `plan.yaml:108,120,255,563,577`, `BRIEF.md:74-88` |
| OD-2 — drop `failures`/`suite`/`kinds` | APPLIED — 5 passthrough rows, D-02's bar repaired |
| OD-3 — T-01 PART 1 precision correction | APPLIED — `plan.yaml:141-147` |
| OD-4 — SC-11 precision correction | APPLIED — `BRIEF.md:105-108` |
| OD-5 — strike T-02 | **EXECUTED — T-02 REMOVED** by `delete-items`; nine tasks remain |
| OD-6 — correct DEC-126 | VERIFIED, already carried by T-09's WRITE 2, one clause |
| B-1..B-6 | ALL STRUCK — none appears as task, decision, issue or note |

## Q2 closed

`T-01.intent`'s opening sentence read "the former T-02, which is abandoned". It now reads **"the
former T-02, which the operator struck under ruling OD-5 on 2026-09-09 and removed from this
plan"**. The field went 10432 → 10498 characters; the diff is one hunk, and two assertions passed
*before* the write — exactly one occurrence replaced, and a length delta equal to the replacement's
own 66. Every other T-01 field is byte-identical against `git show HEAD:`. The word `abandon` now
occurs nowhere in `plan.yaml`.

**Correction to c3:** that packet gave you `plan-merge.py amend --task T-01 --field intent --value
"..."` as the command to close this. **That interface does not exist.** The real one, which I have
now checked against `amend --help` myself, is:

```
plan-merge.py amend --file <plan.yaml> --key tasks --id T-01 --field intent \
  --show                                   # prints the field and its sha256
plan-merge.py amend --file <plan.yaml> --key tasks --id T-01 --field intent \
  --expect-sha256 <that sha> --value-file <path>
```

pm caught it at source rather than following my dispatch literally. This is the **second** premise
I asserted from this worktree's stale copy of `plan-merge.py` — the same root cause as the
delete-verb error one cycle earlier, and the reason I now check the control-plane copy first.

## What you are signing

`BRIEF.md` — 9 requirements, 15 success criteria, each with a verification method: **13 `automated`**
on the `integration` runner, **1 `inspection`** (SC-12's sha256 run-artifact manifest), **1 `uat`**
(SC-13 — you read the DEC-174 carve-out diff; no automated gate substitutes).

`plan.yaml` — 12 decisions, **9 tasks** (T-01, T-03..T-10), the `lanes:` routing table resolving
every literal path through `check-domain.sh --resolve`, and `panel:` with three readers recorded
`ran` and all four `PF-` findings at `disposition: resolved`, ids, severities, readers and evidence
unchanged.

Traceability closed both ways: every REQ has at least one SC and at least one task, every task
traces at least one REQ, no task cites a REQ that does not exist. Nothing dangles after the removal.

The substance is unchanged from the plan you reviewed: unknown keys on a new digest return get
rejected instead of ignored, the same inside a run `state.yaml` `steps[]` entry where nothing
governs them today, a declared free-form-inside `evidence:` container so per-step evidence keeps a
legal home, and **issue #37 resolved in-feature** — `adequacy_notes` becomes a required lead field.

## Gate state

- `check-state.sh` — **one** FEAT-104 violation: BRIEF not approved. The gate working.
- `check-plan-routes.py` — exit 1, `1 violation(s)`, the pre-existing manifest deviation (this
  worktree's `.harness/team-config.yaml` is behind the owner root by `4d81e460`). No task
  violation. You struck B-2, so it stays.
- `validate-digest.py lead` — `digest ok` on every run digest in this feature.

## The record's own corrections, in one place

Four statements of mine were wrong during this signature cycle and each is corrected in place with
the original left readable:

1. "The FEAT-57 claim had cleared" — it had not; I read a per-ROOT registry from the wrong root.
2. "The PID is alive, so the claim is live" — that proves the supervisor lives, not the run; the
   discriminating read showed the live run backs FEAT-57's *validator* claim, not the product-lead
   one that blocked me.
3. "`plan-merge.py` has no delete verb" — true at this worktree's HEAD, false at the control plane,
   where a human landed `delete-items` the same day. pm refused to write on the false premise,
   which is why OD-5 was executed rather than approximated.
4. The `amend` interface above.

Three of the four share one root cause: **I read something true of the checkout I was standing in
as true of the system.** It is logged as a rule rather than as an incident.

## The cross-worktree claim

`FEAT-57-review-latency` held live `harness-product-lead` and `harness-pm` claims through this
cycle and refused a lead's `runs/**` write twice more. Each time the lead returned its digest inline
with the fenced contract block and I landed it from my tier; `plan.yaml` and `notes/` writes were
never refused. Blast radius is run bookkeeping only, now confirmed four times across two features.
FEAT-56 owns the escalation to you and carries it as three separate defects. I am citing, not
re-filing. Only the type-scoped single-flight bears on this signature: it will shape the build phase
while another flow holds a lead persona.

## Budget

`cycles_used: 4` of 10. `runs: 10` of an informational 20. Both healthy; every run resolved
findings and advanced the criteria.

## Artifacts

Under
`/Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-104-strict-digest-schema/.harness/harness/features/FEAT-104-strict-digest-schema/`:

- `BRIEF.md` and `plan.yaml` — both `pending`
- `notes/research-FEAT-104-triage-c0.md` — the measurement and per-key triage
- `notes/research-FEAT-104-goalcheck-plan-c0.md`, `notes/research-FEAT-104-planfix-c1.md`,
  `notes/research-FEAT-104-sigfix-c2.md`, `notes/research-FEAT-104-od5-t02-strike.md`,
  `notes/research-t01-intent-amend.md`
- `notes/review-harness-code-reviewer-planpanel-c1.md` — the panel's `scope` reader
- `runs/*/digest.md` — ten runs, every one validating
- `notes/ship-review-plan-signature-c2.md` and `c3` — superseded, kept legible
