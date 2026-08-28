# Research — FEAT-37 re-plan at HEAD (`8fc87f8`), 2026-08-27

**Conclusion.** The plan is re-anchored and ready for re-signature. Every `9165162` anchor was
re-measured, not substituted; three of them were wrong at HEAD and one (B2) was wrong at every sha.
One commit, `c5e59aa` (#815), caused all of B1, B1b and the emptying of SC-07's third site.

## Measurements taken at `8fc87f8` (all re-run, none inherited)

| Claim | Result |
|---|---|
| `grep -nEi "single-flight refusal\|fires at most once\|fires ONCE" .claude/skills/harness/SKILL.md` | **exit 1** — T-03's old subject is gone |
| `.claude/skills/harness/SKILL.md` length | 288 lines (527 at `9165162`) |
| Surviving never-wait text in that file | `:60` only, "There is no waiting anywhere in this loop" — no inoculation clause |
| `^## DEC-` / `^### DEC-` in `DECISIONS.md` | **201 / 28** — entries are level TWO |
| DEC-201 entry bounds | heading `:6968`, next level-2 heading DEC-202 `:7063` |
| DEC-199 falsified sentences | `:6869`, `:6869-6871`, residual `:6872-6873` (paragraph `:6866-6873`) |
| DEC-199 index row (`:217`) | asserts **no** bound — T-06's hand-edit step was premised on a false state, now dropped |
| DEC-201 index row (`:219`) | no `lead` in the hand-written half |
| `lead` in DEC-201 body | 3 incidental hits; none co-occurs with a turn-ending phrase |
| DEC-174 am.4 library clause | `:5011` (not `:4882-4885`) |
| `inflight_registry.py` | `refusal_lines` def `:251`, #551 cite `:258`; `children_refusal_lines` def `:263`, false line `:274`; `SINGLE_FLIGHT_AGENTS` `:32` |
| `test-inflight-registry.py` `case_6b` | def `:226`, stale assertion `:246` |
| `harness-team/SKILL.md` | 240 lines; d `:97`, e `:112`, loop preamble `:81`, DEC-124 `:181` — all unmoved |
| `check-domain.sh --resolve` on both playbooks | `NOBODY` (lane pins hold) |
| `test-orchestrator-playbook.py` / `test-inflight-registry.py` / `test-validate-digest.py` | all exit **0** at HEAD |
| `check-plan-routes.py` on the re-planned file | **0 violations** |

## DEC-174 amendment 4, read at the sentence

> *a squad may write the library, and **the cutover that makes a gate use it is
> main-session-direct**, proven by showing the gate's violation set is identical before and after.*

The proof burden attaches to the **cutover**, not to the squad's write. T-04 is not a cutover —
`validate-digest.py` already imports `inflight_registry.py`. So the grant is **unconditional** and
the previous framing ("granted on a condition T-04 must discharge") was a paraphrase stronger than
the text. `test-validate-digest.py` stays in T-04's verify as evidence discipline, not obligation.
Corrected in D-08 and in BRIEF `## Constraints`.

## SC-08 — the zero-cost option was tested first, and it fails

Can this build's own leads grade it? **No.** DEC-201 records that a spawned agent loads its skills
from the **main checkout** while a rewritten playbook sits in a worktree — the reason DEC-201's own
1057.1s data point needed a dispatch-level override. Every lead spawned during this build reads the
**unedited** playbook, so a sidecar from here would grade the old text. Deferred explicitly to a
post-merge operator run (D-13); #866 is a second, weaker reason.

## Open for the operator

- **REQ-08 / T-03 / SC-09** is the operator's own scope call; my independent new-vs-covered
  judgement agrees it is new (REQ-04's subject is `harness-team/SKILL.md`; REQ-06 has no bound left
  to correct in `harness/SKILL.md`). Strike the three together if he disagrees; T-01 then drops its
  `orchestrator` group and nothing else moves.
- `inflight_registry.py:258` mis-cites #551 for what #866 measures as #628 — **disclosed residual,
  not a task**, filed in the BRIEF's backlog rows.
