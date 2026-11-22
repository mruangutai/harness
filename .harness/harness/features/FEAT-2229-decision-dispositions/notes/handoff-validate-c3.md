# Handoff — FEAT-2229-decision-dispositions, validate c3 (FAIL) → operator decision on the rework ruling — written at 9712ec62 + c3 close, seq-8

## Next

Validate c3 `r-20261121-validate-c3-validator` returned FAIL at pin ab1e4246 (code-identical to fix-c2 8cf1d93f) with ONE `must_fix`, F3-I = SEC-C2-01 residual = GC-C3-01, citing T-01 (`execution_mode: main-session-direct`) and SC-02: `plan_merge/check.py` `FENCE_RE` (:203, `^\s*`) admits unlimited leading whitespace, so a closer indented four or more spaces closes the scanner's fence while CommonMark 4.5 keeps it inside the open fence (a fence line may be indented at most three spaces); a fenced `## DEC-10` example plus spoof clause is then selected before the genuine DEC-10. F3 (info-string suffix) is CLOSED: qa reproduced its regression red 99/100 at 48cc5b6a → green 100/100 at the pin. Every other SC and DEC-188 met; qa matrix green; cycles 1/10.

The orchestrator was ordered to stop after c3 and NOT start another round. Closed the run FAIL with a `continue:stop` judgement and moved the station back to `building` (cards #2229/#2277-#2280). **The operator decides** (one question, in the orchestrator's return): (a) take one more main-session-direct fix round — the record's own measurement leaves room: spend prints `rework_rounds: 2` of 3 and `rework_minutes: 38` of 90 — or (b) accept the residual as backlog and ship. Recommendation: (a). The fix is bounded: cap fence indentation to 0–3 spaces (CommonMark 4.5) in `FENCE_RE`/`_fence_after`, test-first with an actual-CLI case (over-indented closer → spoof rejected, genuine DEC-10 selected), on top of 8cf1d93f in one `[harness:fix-c3]` commit, then re-delegate the orchestrator for re-pin, `status review`, validate c4 (`run-start --regate "validate cycle 4"`).

RULE for that fix: a fence opener or closer is indented at most three spaces; a run with four or more spaces of indentation (or a tab) inside an open fence is CONTENT. LEAVE: the F3 fix (8cf1d93f, `not line[m.end():].strip()`), F1/F2 (3bff5623), F-01 (c8a8e174), D-01/DEC-254 content, `_is_draft`/`FINISHED_STATIONS`, pm Mode 2 placeholder, `## The gate` placement, simplify L-1..L-4, briefing rows B-1/B-2, `create: true` plan-check behaviour on landed plans, integration duration (36.9 s, advisory). Verify verbatim after the fix: T-01's signed `verify:` (unit schema test, integration decision-dispositions test, plan-team test), full unit and integration runners, `code-grade.py --base dfa52536 --head HEAD`, all with `env -u HARNESS_AGENT_TYPE`.

## Trust

- Pin `review_sha` = ab1e42460b5310a9473724edfb574454d39f6ca8 (station commit; `git diff --stat 8cf1d93f ab1e4246 -- . ':!.harness'` empty); HEAD 9712ec62 differs only in feature.json — `git -C <worktree> log --oneline -4` — verified-at 9712ec62
- F3-I premise: `FENCE_RE = ^\s*(`{3,}|~{3,})` and `_fence_after` apply no indentation cap — check.py:203, :282-292 — verified-at ab1e4246 (orchestrator read)
- c3 readers: qa PASS (matrix_ok true; unit 62 files, integration 89 files rc 0; signed verifies rc 0; code-grade PASSING 90; F3 regression red at 48cc5b6a/green at pin; low advisory on indented closer, folded into F3-I), code PASS-advisory (med, indentation residual), security FAIL (same residual), ui PASS (43 objects, no UI), pm goalcheck FAIL (SC-02 not_met; SC-01/03/04/05/06/07 and DEC-188 met; operator pass, reader partial, maintainer pass) — `runs/r-20261121-validate-c3-validator/digest.md`, `notes/review-harness-*-c3.md`, `notes/research-FEAT-2229-decision-dispositions-goalcheck-validate-c3.md` — verified-at ab1e4246
- c3 lead `cycles_used: 0` (no send-back); feature `cycles_used` 1/10 — close-run output — verified-at c3 close
- Spend at c3 close: 8 runs, 90 min wall, 478183 tokens, rework window 38 min / 2 regate rounds (c2, c3) of ruling 90 min / 3 rounds — close-run spend output — verified-at c3 close
- Succession for seq-7 recorded as a standalone `judgement --kind succession` at 03:xx (run-start refused `--succession`: ledger already held 3 successions for 3 handoffs; the 02:46 entry pre-dated seq-7) — feature.json judgements — verified-at c3 open

## Dead ends

- No `fix` dispatch to harness-validator-lead for F3-I: T-01 is main-session-direct by the signed plan (same as F3) — plan.yaml T-01 `execution_reason` — verified-at dfa52536
- Do not re-run readers over ab1e4246, a8b8df61 or 1ef1edbf (SC-13); validate c4 needs a new pin containing the F3-I fix — build-phase.md step 5 — source
- The c1 FAIL run stays at `cycles_used` 0 (evidence-bound attribution refuses 1) — handoff-fix.md seq-7 — source
- Do not renumber or touch DEC-254 — DECISIONS.md:8253 — source

## Working set

- .harness/harness/features/FEAT-2229-decision-dispositions/runs/r-20261121-validate-c3-validator/digest.md
- .harness/harness/features/FEAT-2229-decision-dispositions/notes/review-harness-security-reviewer-c3.md (F3-I, concrete input)
- .harness/harness/features/FEAT-2229-decision-dispositions/notes/review-harness-qa-c3.md (synthetic probe, Q-C3-01)
- .claude/skills/harness/bin/plan_merge/check.py (:203, :279-325)
- tests/integration/test-plan-decision-dispositions.py (:295-323, :587-604)

## Done when

Scope: operator answer recorded; on (a) F3-I fixed test-first and committed, orchestrator re-delegated for re-pin, status review, validate c4; on (b) backlog row for F3-I and ship briefing per briefing.md
Authority: brief-perspective:.harness/harness/features/FEAT-2229-decision-dispositions/BRIEF.md#reader
Authority: plan-task:T-01.verify
