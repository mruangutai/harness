# Handoff — FEAT-2229-decision-dispositions, validate c2 (FAIL) → fix round 2 (main-session-direct segment) — written at bf0ef996, seq-7

## Next

The validate c2 run `r-20261121-validate-c2-validator` returned FAIL at pin a8b8df61 with ONE `must_fix` finding, F3 = SEC-C2-01, citing T-01 (`execution_mode: main-session-direct`, DEC-174): no squad dev owns it, so the fix is one main-session segment inside the rework ruling (round 2 of 3; 27 of 90 rework minutes spent at close; cycles 1/10). Fix it test-first on top of bf0ef996 in one `[harness:fix-c2]` commit; re-run T-01's signed verify verbatim plus the full unit and integration runners; then re-delegate the orchestrator, which re-pins `review_sha` to a commit containing the fix, runs `gh-sync.py status review`, and dispatches validate c3 over the new pin (`run-start --regate`).

RULE: a closing fence is a run of the fence character at least as long as the opener followed by whitespace only (CommonMark 4.5); a same-character run carrying an info string (` ```python `) inside an open fence is CONTENT and keeps the fence open. LEAVE everything else: the F1/F2 fixes (3bff5623), F-01 (c8a8e174), D-01/DEC-254 content, `_is_draft` reading `FINISHED_STATIONS`, pm Mode 2's `<repo-relative DECISIONS.md path>` placeholder, the `## The gate` placement, simplify leaves L-1..L-4 and briefing rows B-1/B-2, the `create: true` plan-check behaviour on landed plans, and the 34 s vs 30 s integration duration (advisory only).

1. **F3 — T-01 / SC-02 / substance / med.** `.claude/skills/harness/bin/plan_merge/check.py` `_fence_after` (pinned :279-287) closes an open fence on ANY same-character run at least as long as the opener, so a literal ` ```python ` content line inside an open ` ``` ` text fence closes it in the scanner while Markdown keeps the block open; a following fenced `## DEC-10` example plus spoof clause is then selected as DEC-10's section (`_real_headings` :290-298, `_Authority.section` :312-320) before the genuine DEC-10. Fix: `FENCE_RE` (:203) or `_fence_after` must distinguish opener from closer — a closer is the run followed by optional whitespace to end of line, nothing else; an opener may carry an info string. Fixture, in `tests/integration/test-plan-decision-dispositions.py` beside `case_fenced_heading_is_not_a_section` (:281-290, setup `_fenced_docs` :277): a DECISIONS.md where DEC-11's fence contains a ` ```python ` content line, then `## DEC-10` and a spoof clause, the real fence closes later, and the genuine DEC-10 follows → `plan-merge.py check` fails the DEC-10 row for the spoof clause; a genuine-section positive control passes. Record red-then-green in `notes/red-first-T-01.md` (append a F3 section; same style). Reader evidence: notes/review-harness-code-reviewer-c2.md F3 (REASONED, not executed — the red fixture is the first execution); notes/review-harness-security-reviewer-c2.md SEC-C2-01.

Verify verbatim after the fix (T-01 signed `verify:`, also re-run T-02's for the shared runner):

```
set -eu
python3 tests/unit/test-decision-disposition-schema.py
python3 tests/integration/test-plan-decision-dispositions.py
python3 tests/integration/test-plan-team.py
```

plus the full unit and integration runners, `python3 tests/integration/test-plan-merge.py`, and `code-grade.py --base dfa52536 --head HEAD`, all with `HARNESS_AGENT_TYPE` unset (`env -u HARNESS_AGENT_TYPE`).

## Trust

- Pin `review_sha` = a8b8df6196c6107b76cbd941bf2266b3e71476d6 (station commit; code-identical to fix seam c8a8e174, `git diff --stat c8a8e174 a8b8df61 -- . ':!.harness'` empty); HEAD bf0ef996 differs only in `feature.json` — `git -C <worktree> log --oneline -4` — verified-at bf0ef996
- F3 premise: `_fence_after` returns `None` for any same-char run `>= len(fence)` with no end-of-line check — check.py:279-287 — verified-at bf0ef996
- Validate c2 readers: qa PASS (matrix_ok true; unit 62 files, integration 89 files, rc 0; signed verifies rc 0; fail-first reproduced for SC-01/02/03/07 and the F1/F2/F-01 fixes), code PASS-advisory with F3, security PASS-advisory with SEC-C2-01 (same defect), ui PASS (38-object census, no UI), pm goalcheck FAIL (SC-02 not_met; SC-01/03/04/05/06/07 and DEC-188 met; perspectives operator pass, reader partial, maintainer pass) — `runs/r-20261121-validate-c2-validator/digest.md`, `notes/review-harness-*-c2.md`, `notes/research-FEAT-2229-decision-dispositions-goalcheck-validate-c2.md` — verified-at a8b8df61
- c2 lead reported `cycles_used: 1` (one same-run pm evidence-completion send-back), closed as 1; feature `cycles_used` 1/10 — feature.json runs[6], close-run spend output — verified-at bf0ef996
- F1/F2 (3bff5623) and F-01 (c8a8e174) closed by c2: SC-01 and SC-07 met at the pin — c2 digest `sc_status` — verified-at a8b8df61
- Station: tasks T-01..T-03 `done`; feature station `building` again (`gh-sync.py status building` after c2 close wrote #2229/#2277/#2278/#2279/#2280 → building) — plan.yaml:7 — verified-at bf0ef996 (uncommitted at write; committed with this note)
- Spend at close of c2: 7 runs, 79 min wall, 425808 tokens, rework 27 min / 1 round, cycles 1/10 — close-run spend output — verified-at bf0ef996

## Dead ends

- No `fix` dispatch to harness-validator-lead for F3: T-01's `files:` are main-session-direct by the signed plan and `check-domain.py --resolve` on check.py gives no squad dev — plan.yaml T-01 `execution_reason` — verified-at dfa52536
- Do not re-run the validate panel over a8b8df61 or 1ef1edbf (SC-13); validate c3 needs a new pin containing the F3 fix — build-phase.md step 5 — source
- The c1 FAIL run's `cycles_used` stays 0: `run-end --cycles-used 1` is refused because its authentic digest says 0 (P-11 is superseded by the evidence-bound attribution check); check-state reports no FEAT-2229 violation at 0 — feature-record.py run-end output "cycles_used disagrees with authentic digest evidence" — verified-at c8a8e174
- Do not renumber or touch DEC-254 — DECISIONS.md:8253 — verified-at 6c4da464
- `plan-merge.py check` on this plan reports T-01's `create: true` rows as existing files: pre-existing post-landing tool behaviour, backlog candidate, not a finding — notes/receipt-main-session-T-01-T-02.md §Known — source

## Working set

- .harness/harness/features/FEAT-2229-decision-dispositions/runs/r-20261121-validate-c2-validator/digest.md
- .harness/harness/features/FEAT-2229-decision-dispositions/notes/review-harness-code-reviewer-c2.md (F3)
- .claude/skills/harness/bin/plan_merge/check.py (:203, :279-320)
- tests/integration/test-plan-decision-dispositions.py (:249-290)
- /Users/molchairuangutai/GitHub/harness/.agents/skills/harness/references/build-phase.md (step 6)

## Done when

Scope: F3 fixed test-first on top of bf0ef996 and committed, T-01's signed verify and the full runners green, orchestrator re-delegated for re-pin, status review and validate c3
Authority: brief-perspective:.harness/harness/features/FEAT-2229-decision-dispositions/BRIEF.md#reader
Authority: brief-perspective:.harness/harness/features/FEAT-2229-decision-dispositions/BRIEF.md#code maintainer
Authority: plan-task:T-01.verify
