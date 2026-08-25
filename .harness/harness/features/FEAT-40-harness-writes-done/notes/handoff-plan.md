# Handoff — FEAT-40 plan phase → signature

## Next

**No plan edit remains. The operator signs, once three questions are ruled.** All five carried
questions are answered. Two changed the plan: the board audit is scheduled inside `ship` (new T-04
step 7c, SC-17), and `close-task` is deleted (new task T-11, REQ-12, SC-16). Three did not.

The plan is 11 tasks, 13 decisions, REQ-01..REQ-12 all traced, `approval.status: pending` — correct,
because the task set changed. What is left is a signature plus three rulings: the three unplanned
Item-closed sites, the T-04 read-back reading (routed to eng-lead, not to the operator), and the
T-11/D-12 id reuse.

## Trust

- **Suite GREEN at `a60bc49`**, measured by me one kind at a time, nothing else running, NO env var
  set: `--kind unit` 355 PASS / 0 FAIL / exit 0; `--kind integration` 26/26, zero `^FAIL` lines,
  exit 0. The predecessor's eight-script red does NOT reproduce.
- **Its cause, proven causally:** `test-validate-digest.py`'s `[hook]` cases call the real hook via
  `subprocess.run` with **no `env=`**, so it reads the live `.harness/.inflight-claims.json` —
  untracked and gitignored, which is why the main checkout and CI were green. The refusal fires ONCE
  per claim, so re-running drained six claims and the fourth run passed 14/14 with ZERO code
  changes. Filed as #843.
- **The registry is PER-ROOT.** `release-all` was run against the main checkout (`{}`), while this
  worktree still held the stale claim — the same gitignored-file trap, recurring inside its own fix.
  It cleared itself: `CLAIM_TTL_SECONDS = 3600` and the claim was 5153s old. Verified, not assumed.
- **pm's work verified at source by me, not taken on report:** 11 tasks, 13 decisions, no dangling
  `depends_on`, REQ-01..REQ-12 each traced at least once, `approval: {status: pending}`.
- `check-plan-routes.py` 0 violations; `check-state.sh` leaves ONE FEAT-40 violation, BRIEF.md
  unapproved, which is the pending signature — both run by me after the edits.
- **ID REUSE:** `answers-2026-08-25-01.md:36` ruled "delete T-11 and D-12" — the QUARANTINE task and
  decision, and they are gone. pm reused both freed ids for the `close-task` deletion. Internally
  consistent; the hazard is only cross-document.
- **cycles_used is 3, and the lead reads it as 1.** I kept the higher, conservative count rather than
  the flattering one; the budget is 10, so nothing turns on it. Named so the disagreement is visible.

## Dead ends

- **Do not re-derive a red baseline from a stale worktree.** Any suite measurement here is worthless
  unless you first `ps` for a competing run and account for `.harness/.inflight-claims.json`.
- **`HARNESS_PROJECT_DIR` will not isolate those hook cases** — tried against an empty root, the
  failures persisted. Only draining or releasing the claims works. It IS read
  (`validate-digest.py:780`), just not for the children-in-flight lookup.
- **The orchestrator cannot clear the registry** — `bash-write-guard.sh` denies it, correctly.
- **`Edit` is disabled this session**, subagents too; the write guard blocks bash redirects outside
  your domain, and parses a literal `>` in heredoc prose as a redirect. In-domain writes are fine.
- **No `SendMessage` at this tier** — a running lead cannot be corrected mid-flight. This killed run
  `2026-08-25-03-product`, which never wrote a digest and lost its findings; the three Item-closed
  sites are that loss, recovered.
- **Do not strike DEC-168** — it is a measurement, and a blunt DEC-188 strike destroys a live one.

## Working set

- `.harness/harness/features/FEAT-40-harness-writes-done/plan.yaml` (`approval:` at `:6`)
- `.harness/harness/features/FEAT-40-harness-writes-done/BRIEF.md` (`## Approval` at the tail)
- `.harness/harness/features/FEAT-40-harness-writes-done/runs/2026-08-25-04-product/digest.md`
- `.harness/harness/features/FEAT-40-harness-writes-done/notes/research-2026-08-25-q6q8-fold.md`
- `.harness/harness/features/FEAT-40-harness-writes-done/notes/answers-2026-08-25-02.md`
