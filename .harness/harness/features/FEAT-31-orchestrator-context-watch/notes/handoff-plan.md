# Handoff — FEAT-31, plan → plan (second half) — written at 59b493f, seq-3

## Next

Get rulings on Q1-Q4 in this feature's return, then dispatch `harness-product-lead` to write the
RELAY half — SC-07, SC-09, SC-13, SC-14 — MINING the recovered draft named below rather than
starting cold. Do not restore that draft: it does not parse. Do not re-plan the tool half.
Three defects in the live plan, all verified, none fixed:
1. T-01 and T-08 `verify:` cannot fail — the command exits 0 whatever it prints and the expected
   value sits in a comment. Assert the value in the command.
2. Both new test files classify as `unit` and neither as `integration`, so SC-01 and SC-06 would be
   evidenced by the wrong kind. `integration.detect` must gain them; no task's `files:` names
   `.harness/harness.json` for that.
3. SC-15's live half — see Q3. T-10 already covers its automatable half.

## Trust

- The live plan.yaml parses at the committed blob: 10 tasks, 16 decisions, 14 lane rows, approval
  pending — `harness_yaml.load_file` — verified-at 59b493f
- check-plan-routes.py reports 0 violations across 4 plans, examined 30 feature dirs; the recovered
  draft in notes/ is NOT picked up as a plan — verified-at 59b493f
- A 14-task draft was recovered from agent transcripts and preserved at
  `notes/recovered-draft-14task-does-not-parse.yaml`. It carries T-10 widen INV-17, T-11 its red
  proof, T-12 the mid-phase relay rule, T-13 integration tests, T-14 correct DEC-159 in place
  — verified-at 59b493f
- THAT DRAFT DOES NOT PARSE — safe_load fails at line 85 column 37 — so it was never a valid plan
  and reverting to it is not available. Mine it; do not restore it — verified-at 59b493f
- Its T-10/T-11 independently arrive at the same INV-17 remedy Q2 proposes, which is corroboration
  from a second author, not agreement with me — verified-at 59b493f
- Both suites pass; check-state.sh exits 1 with 9 violations, all foreign to FEAT-31 — verified-at 59b493f
- The warning channel is PostToolUse plus exit 2, and matcher Write|Edit|Bash fires for 89 of 89
  orchestrators, Bash alone 5770 calls — `notes/research-FEAT-31-plan2b-three-gaps.md` — verified-at 59b493f

## Dead ends

- Reverting to the 14-task draft. It does not load, so it cannot pass the route gate that already
  reported exit 2 on it — `safe_load` at line 85 — verified-at 59b493f
- Writing any file through Bash. The guard resolves the UNEXPANDED token, so `cp $F/notes/x` is
  refused while the same literal path succeeds; heredoc prose containing a `>` is read as a redirect
  — both reproduced here — verified-at 59b493f
- Trusting a lead to collect its member's return. Three runs closed with pm unreturned; all three
  leads returned after I had recorded their runs from disk — `runs/*/state.yaml` — verified-at 59b493f
- Two writers on plan.yaml. 14 tasks became 1 in 63 seconds, 13:05:17Z to 13:06:20Z; plan.yaml is
  DELIBERATELY absent from check-domain's SHAPE_PATTERNS — `check-domain.sh:670` — verified-at 59b493f
- Asserting SC-14's second half. Green at BOTH gates: check-state.sh:593 builds paths only for
  SEAM_NOTES stems, check-domain.sh:665 accepts any lowercase stem — verified-at 59b493f

## Working set

- .harness/harness/features/FEAT-31-orchestrator-context-watch/plan.yaml
- .harness/harness/features/FEAT-31-orchestrator-context-watch/notes/recovered-draft-14task-does-not-parse.yaml
- .harness/harness/features/FEAT-31-orchestrator-context-watch/notes/probe-hook-delivery-channel.md
- .harness/harness/features/FEAT-31-orchestrator-context-watch/notes/research-FEAT-31-plan2b-three-gaps.md
- .claude/skills/harness/bin/check-state.sh lines 462 to 628, INV-17's seam table
