# Handoff — FEAT-31, plan → plan (second half) — written at 6f651f1, seq-1

## Next

Answer the two blocking operator questions in this feature's return, then dispatch
`harness-product-lead` for plan segment C: the RELAY half of `plan.yaml` — SC-07, SC-09, SC-13,
SC-14, SC-15, that is REQ-04, REQ-08, REQ-09, REQ-10. Its design is already recorded in
`plan.yaml` decisions D-13, D-14 and D-15; the tasks are what is missing. `plan.yaml` D-02 states
the half-written scope explicitly. Do not re-plan the tool half — it is gate-clean.

## Trust

- plan.yaml parses under safe_load, 6 top keys, 9 tasks, 15 decisions, 14 lane rows, approval
  pending — `harness_yaml.load_file` run by me — verified-at 6f651f1
- check-plan-routes.py returns 0 violations across 4 plans, examined 30 feature dirs, exit 0; every
  DEVIATION line names a FEAT-29 path, none a FEAT-31 path — verified-at 6f651f1
- Every literal files path in plan.yaml resolves; the only NOBODY is
  `.claude/skills/harness/templates/harness.json` on T-04, correctly declared main-session-direct
  — `check-domain.sh --resolve` per path — verified-at 6f651f1
- Both suites pass at baseline: unit 39/39 final script, integration 106/106 final script
  — `run-unit-tests.sh --kind unit` and `--kind integration` — verified-at 6f651f1
- check-state.sh exits 1 with 9 violations, ALL foreign: FEAT-26 and FEAT-28 unapproved BRIEFs, 7
  INV-26 FEAT-29 board-drift rows. Zero FEAT-31 violations — verified-at 6f651f1
- The in-context warning channel is PostToolUse plus exit 2, which delivers stderr to the agent and
  blocks nothing — `check-domain.sh:571-573` and `:648-653`, and settings.json already registers
  that route — `notes/probe-hook-delivery-channel.md` finding 1 — verified-at 6f651f1
- Feature attribution comes from the first FEAT-NN in an agent transcript's first four entries, 89
  of 89 orchestrator transcripts; gitBranch and cwd both name the SPAWN checkout and would report
  this orchestrator as FEAT-30 — same note, finding 2 — verified-at 6f651f1
- feature-schema.json runs.items is additionalProperties false, required id, squad, verdict; read
  from INSIDE this worktree, not the main checkout — verified-at 6f651f1

## Dead ends

- Dispatching pm to write plan.yaml without naming the Write tool. pm made 36 Bash calls and zero
  Write calls, hitting `bash-write-guard: BLOCKED — harness-pm: redirect targets 60:` twice; there
  is no file `60:` — pm transcript agent-ae34374df4026b54c — verified-at 6f651f1
- Trusting a lead to collect its own member's return. Three product-lead runs closed with pm
  unreturned; one pm kept writing four minutes after its lead stopped. Check the ARTIFACT on disk
  — `runs/plan-product`, `plan2a-product`, `plan2b-product` state.yaml — verified-at 6f651f1
- Running two pm spawns against plan.yaml concurrently. A complete 1002-line plan was overwritten
  by a second pm's fresh Write-1 down to 190 lines — mtime sequence on plan.yaml — verified-at
  6f651f1
- Asserting SC-14's second half as written. check-state.sh:593 is the only place a handoff path is
  built and it draws stems from SEAM_NOTES, so a mid-phase stem is accepted by silence and the
  assertion is green before and after — verified-at 6f651f1

## Working set

- .harness/harness/features/FEAT-31-orchestrator-context-watch/plan.yaml
- .harness/harness/features/FEAT-31-orchestrator-context-watch/notes/probe-hook-delivery-channel.md
- .harness/harness/features/FEAT-31-orchestrator-context-watch/BRIEF.md
- .harness/harness/features/FEAT-31-orchestrator-context-watch/runs/plan2b-product/digest.md
- .claude/skills/harness/bin/check-state.sh lines 462 to 628, INV-17's seam table
