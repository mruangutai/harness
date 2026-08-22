# Handoff — FEAT-33-board-lifecycle-native, plan → build — written at e3c9187, seq-3

## Next

Do NOT dispatch build. Two operator rulings gate the signature: M4 (amend DEC-186 to four
read-back purposes bounded to /harness-init, or drop REQ-02) and confirmation of the
harness-first departure for T-01. Both branches of M4 are stated at BRIEF.md:228-238 and
neither is pre-applied, so whichever the operator picks is one pm edit, not a re-plan.
Once BRIEF.md ## Approval and plan.yaml approval.status both read approved, dispatch the
build team to harness-eng-lead in dependency order, honouring execution_mode: 8 tasks are
team, 4 are main-session-direct and NOT dispatchable.

## Trust

- e3c9187 is the branch tip and df348c6 is its ancestor, so pm's re-pin to e3c9187 is CURRENT.
  main is still d065b3b — `git merge-base --is-ancestor` plus `rev-parse` — verified-at e3c9187
- Both boards are already native-correct: board 3 and board 2 each carry exactly the six Status
  options, and Item closed, Auto-close issue and Pull request merged are ENABLED on both. So
  this feature is provisioning plus migration, not repair — live GraphQL I ran — verified-at e3c9187
- Pull request linked to issue is DISABLED on board 3, ENABLED on board 2 — same query — verified-at e3c9187
- Both suites pass at e3c9187: --kind unit and --kind integration, exit 0, zero FAIL lines.
  That is SC-10's baseline — ran them myself — verified-at e3c9187
- Registering a new test file in run-unit-tests.sh UNIT_SCRIPTS is MANDATORY: the drift detector
  builds ALL_SCRIPTS as the union and flags any unregistered test-*.py, exit 2 MISCONFIGURED
  (`run-unit-tests.sh:36-41`) — read directly — verified-at e3c9187
- run-unit-tests.sh accepts `--kind` (line 23) and REJECTS a bare positional with exit 2. An
  earlier handoff of mine claimed the opposite — read directly — verified-at e3c9187
- factory_config.py:41 is a five-tuple and :134 is exact set equality; :253 product_config reads
  a served repo's config from the REMOTE at default_branch, never a checkout — verified-at e3c9187
- factory_gh.py:434-457 raises GhError for four conditions and :452-454 deliberately collapses
  "field absent" with "not single-select", so a broad except creates a DUPLICATE board —
  read directly — verified-at e3c9187
- Eight test files carry five-key station fixtures with no "plan" key (nine contain "backlog",
  21 sites). Both reviewers reported six files, so BOTH lists were incomplete — my own grep —
  verified-at e3c9187
- pm reported check-domain --post blocking on FEAT-31 feature.json "agent" keys. NOT REPRODUCIBLE:
  no FEAT-31 feature.json exists in either checkout and no feature.json anywhere carries an
  "agent" key; three commits succeeded — verified-at e3c9187

## Dead ends

- Adding an all-pending→Plan derivation branch: fires on every mirror call and overwrites a card
  promoted to Ready, a new #674-class bug — notes/research-board-lifecycle.md — verified-at e3c9187
- Adding an Abandoned Status option to any board: DEC-192 refused a seventh column and the disk
  schema already carries a column-less Abandoned — DECISIONS.md:5890-5892 — verified-at e3c9187
- Forbidding the run-unit-tests.sh registration edit: I imposed that constraint and pm correctly
  overrode it; the drift detector makes it mandatory — this session's error — verified-at e3c9187
- Mid-run course correction at any tier below the main session: no SendMessage, no wait
  primitive, so every attempt becomes a competing sibling spawn — measured twice — verified-at e3c9187

## Working set

- .harness/harness/features/FEAT-33-board-lifecycle-native/plan.yaml
- .harness/harness/features/FEAT-33-board-lifecycle-native/BRIEF.md
- .harness/harness/features/FEAT-33-board-lifecycle-native/runs/arch-eng/digest.md
- .harness/harness/features/FEAT-33-board-lifecycle-native/runs/2026-08-22-02-product/digest.md
- .claude/skills/harness/bin/factory_config.py
