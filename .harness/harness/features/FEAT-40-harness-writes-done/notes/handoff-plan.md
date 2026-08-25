# Handoff — FEAT-40 plan phase → signature

## Next

**The plan is finished. It needs a signature, nothing else.** Every operator ruling is folded in:
the audit runs inside `ship` (T-04 step 7c, SC-17), `close-task` is deleted (T-11, REQ-12, SC-16),
DEC-203 enumerates SEVEN read-back purposes, and the falsified `Item-closed` premise is owned at
five code sites across T-04 and T-08. 11 tasks, 13 decisions, REQ-01..REQ-12 all traced.

`approval.status` is `pending` and correct. Two non-blocking questions remain for the operator: the
sweep's boundary, and the T-04-to-T-11 window on `gh-sync.py:851`. Neither blocks the signature.

## Trust

- **Suite GREEN at `a60bc49`**, measured by me one kind at a time, nothing else running, NO env var
  set: `--kind unit` 355 PASS / 0 FAIL / exit 0; `--kind integration` 26/26, zero `^FAIL`, exit 0.
- **Its red was stale runtime state, proven causally:** `test-validate-digest.py`'s `[hook]` cases
  call the real hook with **no `env=`**, reading the live `.harness/.inflight-claims.json` —
  untracked and gitignored, which is why the main checkout and CI were green. The refusal fires ONCE
  per claim, so re-running drained six and the fourth run passed 14/14 with ZERO code changes. #843.
- **DEC-203 needs SEVEN purposes, not six.** I verified the three premises myself: `DECISIONS.md:5731`
  bounds the workflow read to `/harness-init` with "no other surface makes this read";
  `board_lifecycle.py:867` is that read; the plan had told the executor not to add a seventh.
  Corrected at five sites including **D-07, inside the `decisions:` block the operator signs**.
- **`plan.yaml:503` still says "six purposes" and that is CORRECT** — it is T-09's prohibition.
  The operator has ruled on this. Do not "fix" it; that deletes the guard.
- **The `Item-closed` class has FIVE live sites, not three** — T-04 steps 8b, 8d, 8e and T-08
  (a)/(b). `gh-sync.py:851` is deliberately left to T-11's deletion.
- **T-04 is `depends_on: [T-01, T-03]`** — I chose the edge because the corrected comment cites
  DEC-203 by name, and confirmed it acyclic (`T-03` is `depends_on: []`).
- **`#818`-`#830`: I re-derived BOTH halves live.** All thirteen read CLOSED and sit at `Review`.
- `check-plan-routes.py` 0 violations; `check-state.sh` leaves ONE FEAT-40 violation, BRIEF
  unapproved — both run by me after every edit.
- **`cycles_used` is 6, and I took the higher reading each time** rather than the flattering one.

## Dead ends

- **An enumerated list of sites is a HYPOTHESIS, not a set.** Three consecutive cycles produced a
  list short by at least one — the last miss was found only after pm returned PASS. Sweep the class
  by its claim shape, not by the names you were handed.
- **Do not re-derive a red baseline from a stale worktree.** `ps` for a competing run first, and
  account for `.harness/.inflight-claims.json`. The registry is PER-ROOT: `release-all` on the main
  checkout does not touch this one. It self-clears at `CLAIM_TTL_SECONDS = 3600`.
- **Do not argue the read-back bound by component.** DEC-186 amendments 2 and 3 each rejected that
  move; a caller inherits the bound and is named in it (`DECISIONS.md:5761-5763`).
- **Do not "correct" `DECISIONS.md:6614`** — same false causality, but inside DEC-196, which T-03
  strikes. Editing it would falsify the record. Likewise do not repoint the ~15 other live DEC-192
  citations: DEC-188 keeps a struck entry's row, so they still resolve.
- **No `SendMessage` at lead or orchestrator tier.** A running child cannot be corrected mid-flight.
  This killed run `2026-08-25-03-product`, which never wrote a digest.
- **`Edit` is disabled this session**, subagents too; the write guard blocks bash redirects outside
  your domain and parses a literal `>` in heredoc prose as a redirect.

## Working set

- `.harness/harness/features/FEAT-40-harness-writes-done/plan.yaml` (`approval:` at `:6`)
- `.harness/harness/features/FEAT-40-harness-writes-done/BRIEF.md` (`## Approval` at the tail)
- `.harness/harness/features/FEAT-40-harness-writes-done/runs/2026-08-25-05-eng/digest.md`
- `.harness/harness/features/FEAT-40-harness-writes-done/runs/2026-08-25-07-product/digest.md`
- `.harness/harness/features/FEAT-40-harness-writes-done/notes/answers-2026-08-25-02.md`
