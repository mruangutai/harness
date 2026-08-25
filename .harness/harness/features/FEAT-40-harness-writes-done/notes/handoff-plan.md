# Handoff — FEAT-40 plan phase → signature

## Next

**No plan edit remains. The operator signs, once one scope call is made.** All five carried questions
are ruled and folded in. Two changed the plan: the board audit is scheduled inside `ship` (T-04 step
7c, SC-17), and `close-task` is deleted (T-11, REQ-12, SC-16). A wrong premise about the read-back
bound was then caught by engineering and corrected across five sites.

The plan is 11 tasks, 13 decisions, REQ-01..REQ-12 all traced, `approval.status: pending` — correct,
because the task set changed. The one open decision is a **scope call**: fold the three unplanned
`Item-closed` comment sites into T-04 and T-08, or backlog them.

## Trust

- **Suite GREEN at `a60bc49`**, measured by me one kind at a time, nothing else running, NO env var
  set: `--kind unit` 355 PASS / 0 FAIL / exit 0; `--kind integration` 26/26, zero `^FAIL`, exit 0.
- **The red's cause:** `test-validate-digest.py`'s `[hook]` cases call the real hook via
  `subprocess.run` with **no `env=`**, reading the live `.harness/.inflight-claims.json` — untracked
  and gitignored, which is why the main checkout and CI were green. The refusal fires ONCE per claim,
  so re-running drained six and the fourth run passed 14/14 with ZERO code changes. Filed as #843.
- **DEC-203 needs SEVEN read-back purposes, not six** — eng-lead's ruling, and I verified its three
  premises myself at HEAD: `DECISIONS.md:5731` bounds the workflow read to `/harness-init` with
  "no other surface makes this read"; `board_lifecycle.py:867` is that read; `plan.yaml:470-473` had
  instructed the executor not to add a seventh. Five sites corrected, **including D-07 in the
  approval-gated `decisions:` block** — the one the operator signs.
- **`plan.yaml:503` still says "enumerates six purposes" and that is CORRECT.** It is the
  prohibition in T-09's guard ("This task writes nothing... asserting that DEC-203 enumerates six
  purposes"). I read it in full before accepting it. Do not "fix" it — that deletes the guard.
- **`#818`-`#830`: I re-derived BOTH halves live this run.** All thirteen read CLOSED and sit at
  `Review` today. T-03 writes this into DEC-138 amendment 8 as a permanent record; it is true.
- **T-04 correctly stays `depends_on: [T-01]`.** Corrected step 7c only makes a negative assertion
  and its `verify:` greps no decision id, so it does not transcribe DEC-203 the way T-09 does.
- `check-plan-routes.py` 0 violations; `check-state.sh` leaves ONE FEAT-40 violation, BRIEF.md
  unapproved — both run by me after the edits.
- **`cycles_used` is 5 and I chose the higher reading each time** rather than the flattering one.
  Budget is 10, so nothing turns on it. Named so the judgement is visible.

## Dead ends

- **Do not re-derive a red baseline from a stale worktree.** `ps` for a competing run first, and
  account for `.harness/.inflight-claims.json`. The registry is PER-ROOT: `release-all` on the main
  checkout does not touch this one. It self-clears at `CLAIM_TTL_SECONDS = 3600`.
- **Do not argue the read-back bound by component** ("this read belongs to `board_lifecycle`").
  DEC-186 amendments 2 and 3 each already rejected that move; a caller inherits the bound and is
  named in it (`DECISIONS.md:5761-5763`).
- **Do not strike DEC-168** — it is a measurement, and a blunt DEC-188 strike destroys a live one.
- **`Edit` is disabled this session**, subagents too; the write guard blocks bash redirects outside
  your domain and parses a literal `>` in heredoc prose as a redirect.
- **No `SendMessage` at this tier** — a lead cannot be corrected mid-flight. This killed run
  `2026-08-25-03-product`, which never wrote a digest; the three `Item-closed` sites are that loss.

## Working set

- `.harness/harness/features/FEAT-40-harness-writes-done/plan.yaml` (`approval:` at `:6`)
- `.harness/harness/features/FEAT-40-harness-writes-done/BRIEF.md` (`## Approval` at the tail)
- `.harness/harness/features/FEAT-40-harness-writes-done/runs/2026-08-25-05-eng/digest.md`
- `.harness/harness/features/FEAT-40-harness-writes-done/runs/2026-08-25-06-product/digest.md`
- `.harness/harness/features/FEAT-40-harness-writes-done/notes/answers-2026-08-25-02.md`
