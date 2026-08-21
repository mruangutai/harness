# Handoff — FEAT-31, plan → plan (second half) — written at b8ba798, seq-2

## Next

Fix the three plan defects below, get rulings on Q1-Q3 in this feature's return, then dispatch
`harness-product-lead` for the RELAY half — SC-07, SC-09, SC-13, SC-14, SC-15, that is REQ-04,
REQ-08, REQ-09, REQ-10. Its design is already in `plan.yaml` D-13, D-14, D-15; only tasks are
missing, and D-02 declares the half-written scope. Do not re-plan the tool half.
Three defects, all found after the commit, none fixed:
1. T-01 and T-08 `verify:` cannot fail — the command exits 0 whatever it prints and the expected
   value sits in a comment. Assert the value in the command.
2. Both new test files classify as `unit` and neither as `integration`, so SC-01 and SC-06 would be
   evidenced by the wrong kind. `integration.detect` must gain them; no task's `files:` names
   `.harness/harness.json` for that purpose.
3. SC-15 cannot be met as written — see Q3.

## Trust

- plan.yaml parses at the committed blob, 9 tasks, 15 decisions, 14 lane rows, approval pending
  — `harness_yaml.load_file` on `git show b8ba798:...` — verified-at b8ba798
- check-plan-routes.py returns 0 violations across 4 plans, examined 30 feature dirs, exit 0; every
  DEVIATION names a FEAT-29 path — verified-at b8ba798
- The only ungranted `files:` path is `.claude/skills/harness/templates/harness.json` on T-04,
  correctly declared main-session-direct — `check-domain.sh --resolve` per path — verified-at b8ba798
- Both suites pass at baseline; check-state.sh exits 1 with 9 violations, all foreign to FEAT-31
  — `run-unit-tests.sh` both kinds, `check-state.sh` — verified-at b8ba798
- Neither new test file matches `integration.detect`, which names four files explicitly, and both
  match `unit.detect`'s `test-*.py` glob — `.harness/harness.json` test_kinds — verified-at b8ba798
- The warning channel is PostToolUse plus exit 2, which reaches the agent and blocks nothing
  — `check-domain.sh:571-573` and `:648-653` — verified-at b8ba798
- Feature attribution reads the first FEAT-NN in a transcript's first four entries, 89 of 89;
  gitBranch and cwd name the SPAWN checkout — `notes/probe-hook-delivery-channel.md` — verified-at b8ba798
- SC-07's rule must diff against git HEAD, not disk: check-domain POST already sees the new content
  — pm's `notes/research-FEAT-31-plan-tensions.md` — UNVERIFIED

## Dead ends

- Dispatching pm to write plan.yaml without naming the Write tool. 36 Bash calls, zero Write calls,
  refused twice with `redirect targets 60:` — pm transcript agent-ae34374df4026b54c — verified-at b8ba798
- Trusting a lead to collect its own member's return. Three runs closed with pm unreturned; two
  leads returned after I had recorded their runs — `runs/*/state.yaml` — verified-at b8ba798
- Two writers on plan.yaml. A complete 1002-line plan was overwritten to 190 lines; plan.yaml is
  DELIBERATELY absent from check-domain's SHAPE_PATTERNS, so nothing gates it
  — `check-domain.sh:670` — verified-at b8ba798
- Asserting SC-14's second half. It is green at BOTH gates: check-state.sh:593 builds paths only for
  SEAM_NOTES stems, and check-domain.sh:665 RE_HANDOFF accepts any lowercase stem with no whitelist
  — verified-at b8ba798

## Working set

- .harness/harness/features/FEAT-31-orchestrator-context-watch/plan.yaml
- .harness/harness/features/FEAT-31-orchestrator-context-watch/notes/probe-hook-delivery-channel.md
- .harness/harness/features/FEAT-31-orchestrator-context-watch/notes/research-FEAT-31-plan-tensions.md
- .harness/harness/features/FEAT-31-orchestrator-context-watch/BRIEF.md
- .claude/skills/harness/bin/check-state.sh lines 462 to 628, INV-17's seam table
