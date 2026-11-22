# Handoff — FEAT-2229-decision-dispositions, validate c4 (ESCALATE) → operator decision after the ruling's last round — written at c4 close, seq-9

## Next

Validate c4 `r-20261121-validate-c4-validator` returned ESCALATE at pin 46d0c4bc (station commit, code-identical to fix-c3 ef269da2). F3-I is CLOSED in production: qa reproduced the three new cases red 108/113 at d1fd4aa1 and green 113/113 at the pin, a 40-case actual-CLI probe over every CommonMark boundary the ruling names behaves correctly, security and code PASS, goal-check grades all seven SCs and DEC-188 met by pinned inspection. The gate did not clear because the ruling requires "each rule written test-first with its own actual-CLI case" and two rule legs have none: M6 (a ``` closer closing a ~~~ fence and vice versa) and M8 (the no-backtick-in-info rule wrongly applied to tilde openers) survive the suite 113/113. Orchestrator confirmed the premise: `tests/integration/test-plan-decision-dispositions.py` contains no `~~~` anywhere. Both are test-only on T-01 (main-session-direct) / SC-02; production code needs no change.

The rework ruling is spent (3/3 rounds, 53/90 min at c4 close), so the orchestrator recorded `continue:stop` and returns. **The operator decides** (one question): (a) authorize one test-only main-session-direct addition — two actual-CLI cases in `tests/integration/test-plan-decision-dispositions.py` on top of ef269da2 (a backtick fence holding `~~~` then a spoof `## DEC-10`, a tilde fence holding ``` then a spoof, and a `~~~ a`b` fence holding a spoof; all must reject the spoof and select the genuine section), each red by mutation (M6/M8 per `notes/review-harness-qa-c4.md`) then green — followed by one qa-only re-validation over a new pin; or (b) waive both gaps to backlog and proceed to the ship briefing. Recommendation: (a) — bounded, test-only, the ruling's own text demands it, and the station stays `review`.

On (a): fix lands as `[harness:fix-c4]`, then re-pin, `gh-sync.py status review` is already in force (station review, no building/review flip needed unless the operator wants the board to show it), ONE validate dispatch (`run-start --regate "validate cycle 5"`) scoped to qa plus goal-check SC-02. On (b): briefing per `briefing.md` with the backlog below. Either way the new-class advisories go to backlog, never into F3-I.

## Trust

- Pin `review_sha` = 46d0c4bce7cec18e0aabec56a490981496970cc0; `git diff --stat ef269da2 46d0c4bc -- . ':!.harness'` empty — orchestrator-measured — verified-at ee924c96
- c4 readers: qa ESCALATE (matrix_ok true; unit 62 files, integration 89 files rc 0; T-01 verify rc 0; code-grade --base dfa52536 PASSING 97; red 108/113 at d1fd4aa1, green 113/113 at pin; M6/M8 survive), code PASS, security PASS (F3-I closed by reasoning; SEC-C4-01 advisory), ui PASS (50 paths, no UI), pm goalcheck PASS (all SCs met; lead consolidates SC-02 partial) — `runs/r-20261121-validate-c4-validator/digest.md`, `notes/review-harness-*-c4.md`, `notes/research-FEAT-2229-decision-dispositions-goalcheck-validate-c4.md` — verified-at 46d0c4bc
- c4 lead `cycles_used: 1` (one qa receipt send-back correcting PASS-with-must_fix to ESCALATE); feature `cycles_used` 2/10 — close-run output — verified-at c4 close
- c3 FAIL run stays `cycles_used: 0`: `run-end --cycles-used 1` refused "disagrees with authentic digest evidence" — orchestrator probe — verified-at ef269da2
- Spend at c4 close: 9 runs, 105 min wall, 524332 tokens, rework 53 min / 3 rounds of 90 / 3 — close-run spend output — verified-at c4 close
- Succession seq-8 recorded as a standalone `judgement --kind succession` at 04:00:13, before run-start at 04:00:15 (run-start refused `--succession`: "owes no succession") — feature.json judgements — verified-at c4 open

## Backlog candidates (new classes, c4, for the briefing)

- QA: Unicode line-break/whitespace mismatch between the scanner and CommonMark (CLI-reproduced spoof; absent in live corpus) — `notes/review-harness-qa-c4.md`
- QA: fences inside list containers create phantom fence state (CLI-reproduced; absent in live corpus) — same note
- Security SEC-C4-01 (med, static): `_heading_level` dec match uses `(?!\d)`, so `## DEC-10x` can impersonate `DEC-10` — `check.py:277-283`, `notes/review-harness-security-reviewer-c4.md`
- QA contract: its validator refuses FAIL for mandatory coverage gaps when suite and matrix are green (harness defect, lead's C4-QA-CONTRACT)
- Carried from simplify: B-1, B-2; `create: true` plan-check item on landed plans (handoff-validate-c3.md)

## Dead ends

- No `fix` dispatch to harness-validator-lead for M6/M8: T-01 is main-session-direct by the signed plan — plan.yaml T-01 `execution_reason` — verified-at dfa52536
- Do not re-run readers over 46d0c4bc, ab1e4246, a8b8df61 or 1ef1edbf (SC-13); a c5 needs a new pin containing the test additions — build-phase.md step 5 — source
- Do not renumber or touch DEC-254 — DECISIONS.md:8253 — source

## Working set

- .harness/harness/features/FEAT-2229-decision-dispositions/runs/r-20261121-validate-c4-validator/digest.md
- .harness/harness/features/FEAT-2229-decision-dispositions/notes/review-harness-qa-c4.md (M6/M8 mutations, 40-case probe, new-class advisories)
- .harness/harness/features/FEAT-2229-decision-dispositions/notes/review-harness-security-reviewer-c4.md (SEC-C4-01)
- .claude/skills/harness/bin/plan_merge/check.py (:203-204, :275-325)
- tests/integration/test-plan-decision-dispositions.py

## Done when

Scope: operator answer recorded; on (a) two actual-CLI cases landed test-first, qa + SC-02 re-validated over a new pin, then briefing; on (b) backlog rows for M6/M8 and the new classes, then ship briefing per briefing.md
Authority: brief-perspective:.harness/harness/features/FEAT-2229-decision-dispositions/BRIEF.md#reader
Authority: plan-task:T-01.verify
