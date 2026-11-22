# Handoff — FEAT-2229-decision-dispositions, validate c5 (BLOCKED on security execution capability) → operator ship decision — written at c5 close, seq-10

## Next

Validate c5 `r-20261122-validate-c5-validator` returned BLOCKED at pin c163d5ea: qa, code, ui and goal-check PASS, every SC and DEC-188 met, no must_fix; security BLOCKED because its `git diff`-only Bash grant let the guard refuse its actual-CLI fixture command before any observation ran (SEC-C5-EXEC). The orchestrator executed the reader's planned classes itself — 325 actual-CLI observations, no bypass — and wrote the ship briefing `notes/ship-review-r-20261122-validate-c5-validator.md`. **The operator decides Q1**: (a) accept qa's red-first spoof evidence plus the orchestrator probe as security runtime closure and ship (recommended), or (b) grant the security reviewer an execution path and re-run over a NEW pin (SC-13 forbids a second reader run over c163d5ea). On (a): terminus — merge, PR, ship are the main session's; a successor only distills after the merge. On (b): main session changes the grant (harness change outside this feature), successor re-pins to the then tip, `gh-sync.py status review`, one validate dispatch scoped to security + goal-check SC-02, run-start plain (c5 is BLOCKED, not FAIL, so no regate is owed). No further dev round exists under any ruling — plan.yaml T-01 and `notes/answers-2026-11-22-c4-ruling.md`.

## Trust

- Pin `review_sha` = c163d5ea0fb17da27b3455559f317d67852981c7; `git diff --stat c163d5ea e220cde8 -- . ':!.harness'` empty — orchestrator-measured — verified-at e220cde8
- c5 readers: qa PASS (M6 both 128/130, each 129/130; M8 129/130; identifier mutant 122/130; pin 130/130; verify + runners rc 0), code PASS (code-grade --base dfa52536 --head c163d5ea rc 0, 101 passing), security BLOCKED (static closure, 0/107 CLI observations), ui PASS (declined, 57 paths no UI), goalcheck PASS (all SCs + DEC-188 met) — `runs/r-20261122-validate-c5-validator/digest.md`, `notes/review-harness-*-c5.md`, `notes/research-FEAT-2229-decision-dispositions-goalcheck-validate-c5.md` — verified-at c163d5ea
- Orchestrator probe: 319 ok / 6 design-conformant mislabels / 325 observations — `notes/sec-c5-orchestrator-probe.md`, `.py`, `.out.txt` — verified-at e220cde8
- c5 lead `cycles_used: 2` (two same-run receipt corrections); feature `cycles_used` 4/10 — close-run output — verified-at c5 close
- Spend at c5 close: 10 runs, 126 min wall, 596244 tokens, rework 74 min / 3 rounds, plus the one round the c4 ruling authorized beyond the ruling (`rework` record unchanged: set-rework is main-session-only) — close-run spend output — verified-at c5 close
- Succession seq-9 recorded as a standalone `judgement --kind succession` at 13:39:08, 16 s AFTER run-start at 13:38:52: run-start refused `--succession` ("owes no succession") and `--regate` ("owes no regate"), and the first standalone attempt was refused for reason length; check-state reports no INV-43 finding — feature.json judgements — verified-at c5 open

## Dead ends

- No second reader run over c163d5ea, 46d0c4bc, ab1e4246, a8b8df61 or 1ef1edbf (SC-13); option (b) needs a new pin — build-phase.md step 5 — source
- No `fix` dispatch: no reader raised must_fix at c5; B-7/B-8/B-10 are backlog by the c4 ruling's scope — `runs/r-20261122-validate-c5-validator/digest.md` must_fix [] — verified-at c163d5ea
- Do not renumber or touch DEC-254 — DECISIONS.md:8253 — source
- Do not write the security reviewer's grant or run its probes as a stand-in for its verdict: the probe note is orchestrator-tier evidence for the operator, never a reader receipt — DEC-177, harness-handoff — source

## Working set

- .harness/harness/features/FEAT-2229-decision-dispositions/notes/ship-review-r-20261122-validate-c5-validator.md
- .harness/harness/features/FEAT-2229-decision-dispositions/runs/r-20261122-validate-c5-validator/digest.md
- .harness/harness/features/FEAT-2229-decision-dispositions/notes/review-harness-security-reviewer-c5.md
- .harness/harness/features/FEAT-2229-decision-dispositions/notes/sec-c5-orchestrator-probe.md
- .claude/skills/harness/bin/plan_merge/check.py (:203-212, :275-290)

## Done when

Scope: operator answer to Q1 recorded; on (a) the main session ships (merge/PR are its); on (b) one security-scoped re-validation over a new pin returns PASS, then the briefing is refreshed
Authority: brief-perspective:.harness/harness/features/FEAT-2229-decision-dispositions/BRIEF.md#reader
Authority: plan-task:T-01.verify
