# Handoff — FEAT-1714-reject-verb, plan → build — written at 667252be6015ded083d26e13c86793447caaee07, seq-1

## Next

The plan is signed (rework 2/90) and the build entry is open (parent #1736). Build in dependency order: T-01 main-session-direct (validate-digest reject contract, judgement kind reject) — DONE at 8a83624b; then T-02 via the eng-lead build team (backend-dev: TERMINAL_STATIONS, gh-sync migration, gh-sync.py reject), T-03 direct (the INV-44 invariant — INV-43 is taken by BUG-1723), T-04 documentor, T-05 direct.

## Trust

- The intake panel's 11 findings are all marked resolved because the signed plan's text already answers each — .harness/harness/features/FEAT-1714-reject-verb/plan.yaml — UNVERIFIED (transcription by Main, not a substance ruling)
- The plan goal-check graded the declared perspectives PASS — .harness/harness/features/FEAT-1714-reject-verb/notes/research-FEAT-1714-reject-verb-goalcheck-plan.md — UNVERIFIED
- Every gate-script surface in this plan (validate-digest.py, feature-record.py, feature-schema.json, check-state.py, gh-sync.py and their tests) is main-session-direct under DEC-174 — .harness/harness/features/FEAT-1714-reject-verb/notes/answers-2026-09-15-sign.md — VERIFIED

## Dead ends

- A block-form judgement mapping is not the contract: parse_digest does not surface nested block mappings, and the reject mapping is one inline line by design — .claude/skills/harness/bin/validate-digest.py (_reject_judgement_errors) — VERIFIED
- Do not number the new invariant INV-43; BUG-1723 owns it — /Users/molchairuangutai/GitHub/harness/.harness/notes/grilling-reject-verb-2026-09-15.md — VERIFIED

## Working set

- .harness/harness/features/FEAT-1714-reject-verb/BRIEF.md
- .harness/harness/features/FEAT-1714-reject-verb/plan.yaml
- .harness/harness/features/FEAT-1714-reject-verb/feature.json
- .harness/harness/features/FEAT-1714-reject-verb/notes/receipt-main-session-T-01-fail-first.md
- .harness/harness/features/FEAT-1714-reject-verb/notes/research-FEAT-1714-reject-verb-goalcheck-plan.md

## Done when

Scope: T-01 and T-02 build segment; T-03..T-05 hand off from the build notes
Authority: brief-perspective:.harness/harness/features/FEAT-1714-reject-verb/BRIEF.md#orchestrator
Authority: plan-task:T-01.verify
Authority: plan-task:T-02.verify
