# FEAT-104 — corrected plan signature packet (c3)

**Supersedes `ship-review-plan-signature-c2.md`, which is left on disk because it asserts a premise
that turned out to be false and the correction is only legible beside it.** All six of your rulings
are now executed, OD-5 included. Nothing is implemented and nothing is signed. **The signature is
the only thing outstanding.**

## Your rulings — all six executed

| Ruling | State | Where |
|---|---|---|
| OD-1 — hermetic inert fixture remedy | **APPLIED** | `plan.yaml:108,120,255,563,577`; `BRIEF.md:74-88` |
| OD-2 — drop `failures`/`suite`/`kinds` | **APPLIED** | `plan.yaml:132-134` (5 rows); D-02's bar repaired |
| OD-3 — T-01 PART 1 precision correction | **APPLIED** | `plan.yaml:141-147` |
| OD-4 — SC-11 precision correction | **APPLIED** | `BRIEF.md:105-108` |
| **OD-5 — strike T-02** | **EXECUTED — T-02 REMOVED** | `delete-items`; nine tasks remain |
| OD-6 — correct DEC-126 | **VERIFIED, already carried** | `plan.yaml:645-653`, WRITE 2, one clause |
| B-1..B-6 backlog | **ALL STRUCK** | none appears as task, decision, issue or note |

## How the T-02 strike was legally represented — and why the answer changed twice

**It is a removal.** T-02 is gone from the plan. The verb:

```
python3 <control-plane>/.agents/skills/harness/bin/plan-merge.py delete-items \
  --file <this plan.yaml> --task T-02 \
  --reason "operator ruling OD-5 at the plan signature review, 2026-09-09: struck; work already subsumed by T-01 PART 3 and PART 4"
```

Receipt: `DELETED tasks:T-02` / `DELETED-ITEMS 1 ... APPLIED`, exit 0. The plan now carries
**nine** tasks — T-01, T-03..T-10 — and I verified on disk that `approval:` is still
`{status: pending}`, all twelve decisions survive, and `panel:` still holds three readers, four
findings and two dismissals.

**The honest history, because two of my earlier statements to you were wrong.** In the c2 packet I
told you the entry survived only because `plan-merge.py` had no delete verb, and I recommended
recording the strike in place. When you asked how the strike had been represented, I dispatched
that in-place amend and told the squad the no-delete premise was settled and not to re-investigate
it. **pm checked anyway and refused to write on a false premise.** `delete-items` exists at the
control plane — landed by human commit `11541475` the same day. My premise was true at this
worktree's HEAD `25918bd2` and false at the tooling as such; I had generalised from the checkout I
was standing in, which is the second time this feature I have read a root-scoped fact as a global
one. pm's refusal is why the ruling was executed properly instead of approximated, and I would
rather record that than have it read as a clean run.

I then ruled removal rather than asking you a third time: your packet had been told the entry
survived *only* for want of that verb, and a human closed exactly that gap the same day.

**Removal also clears a red gate.** B-1's INV-26 false positive was tripped by T-02's `abandoned`
value alone. With T-02 gone, `check-state.sh` reports exactly **one** FEAT-104 violation — "BRIEF.md
is NOT approved", which is the signature gate itself working.

## One residual, and the one-line command that closes it

`plan.yaml:125`, inside T-01's `intent:`, still reads "This task subsumes the former T-02, which is
abandoned". Historical prose, accurate about the merge and now stale about the disposition — T-02
was struck and removed, not left abandoned. Amending T-01 was outside that dispatch's scope and pm
correctly left it. It misleads nobody about what T-01 does, so I did not spend a cycle on it. If
you want it gone before signing:

```
python3 <control-plane>/.agents/skills/harness/bin/plan-merge.py amend \
  --file <this plan.yaml> --task T-01 --field intent --value "<corrected text>"
```

## What signing gets you

`BRIEF.md` — 9 requirements, 15 success criteria, every one with a verification method: 13
`automated` on the `integration` runner, 1 `inspection` (SC-12's sha256 manifest), 1 `uat`
(SC-13, you read the DEC-174 carve-out diff). `plan.yaml` — 12 decisions, 9 tasks, the `lanes:`
routing table, and `panel:` with all four `PF-` findings at `disposition: resolved`, ids,
severities, readers and evidence unchanged.

Traceability closed both ways over the nine tasks: every REQ has at least one SC and at least one
task, every task traces at least one REQ, no task cites a REQ that does not exist. REQ-07 is
carried by T-01, which absorbed T-02's work as PART 3 and PART 4, and by T-09.

Nothing dangles after the removal: no `depends_on`, panel finding, SC or REQ references T-02.

## Gate state at signature

- `check-state.sh`: **one** FEAT-104 violation — BRIEF not approved. The gate working.
- `check-plan-routes.py`: exit 1 on the pre-existing manifest deviation (this worktree's
  `.harness/team-config.yaml` is behind the owner root by `4d81e460`). No task violation. You
  struck B-2, so it stays.
- `validate-digest.py lead` on both of this cycle's run digests: `digest ok`.

## The cross-worktree claim, third confirmation

`FEAT-57-review-latency` held live `harness-product-lead` and `harness-pm` claims through this
cycle. It refused one lead's `runs/**` write again; that lead returned its digest inline with the
fenced contract block and I landed it from my tier. **pm's `plan.yaml` and `notes/` writes were
never refused** — the blast radius is run bookkeeping only, now confirmed three times across two
features. FEAT-56 owns the escalation to you and carries it as three separate defects: the
type-scoped single-flight, the per-ROOT registry resolution, and claim retention bound to a
long-lived supervisor PID. I am citing, not re-filing. Only the first bears on this signature: it
will shape the build phase while another flow holds a lead persona.

## Budget

`cycles_used: 4` of 10 — the fourth is the OD-5 re-dispatch after the false-premise escalation.
`runs: 9` of an informational 20. Both healthy.

## Artifacts

All under
`/Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-104-strict-digest-schema/.harness/harness/features/FEAT-104-strict-digest-schema/`:

- `BRIEF.md` — approval `pending`
- `plan.yaml` — approval `pending`, station `plan`, nine tasks, panel resolved
- `notes/research-FEAT-104-od5-t02-strike.md` and `notes/research-FEAT-104-sigfix-c2.md` — both
  carry the delete-verb correction legibly, neither overwritten
- `notes/research-FEAT-104-triage-c0.md`, `notes/research-FEAT-104-goalcheck-plan-c0.md`,
  `notes/research-FEAT-104-planfix-c1.md`, `notes/review-harness-code-reviewer-planpanel-c1.md`
- `runs/od5-c3-product/digest.md` and `runs/od5b-c3-product/digest.md` — this cycle's record
- `notes/ship-review-plan-signature-c2.md` — superseded, kept so the correction is legible
