HEAD: 0f12f14c166d231ddf648cc00ff4d12029ce0122

## PRE-MOVE

The FEATURES surface must read CLEAN — evidence migrated at EVERY boundary of this
feature; if it ever does not, the move touched the wrong surface and the work stops.
The feature-dir count reads 22 (21 at pin 0f12f14): this feature's own feature.json
was created after the pin. Recorded, not compared — below 21 is the drift signal.

### layout_migration.py
```
features: CLEAN — evidence migrated
docs: CLEAN — evidence legacy
examined 22 feature dir(s), 1 doc root(s), 7 reader file(s)
layout: 2 surface(s) clean, 0 mixed, 0 cannot-verify
exit: 0
```

### check-state.sh
```
  note       .harness/harness/features/FEAT-19-central-product-config/plan.yaml approval is pending — awaiting the user.
  note       .harness/harness/features/FEAT-08-remove-cost-tracking/PLAN.md approval is pending — awaiting the user.
  note       FEAT-21-features-layout-migration: run dir 2026-08-15-1-validator exists on disk but feature.json does not record it — orphaned work (interrupted flow?). A resume must reconcile it, not rediscover it by luck.
  note       FEAT-13-single-issue-board-lookup: run t01-eng is referenced but its dir is absent (pruned, or never created).
  note       FEAT-13-single-issue-board-lookup: run qa-validator is referenced but its dir is absent (pruned, or never created).
  note       FEAT-13-single-issue-board-lookup: run t02-eng is referenced but its dir is absent (pruned, or never created).
  note       FEAT-13-single-issue-board-lookup: run panel-validator is referenced but its dir is absent (pruned, or never created).
  note       FEAT-13-single-issue-board-lookup: run goalcheck-product is referenced but its dir is absent (pruned, or never created).
  note       FEAT-13-single-issue-board-lookup: run fix01-eng is referenced but its dir is absent (pruned, or never created).
  note       FEAT-13-single-issue-board-lookup: run sc05recheck-product is referenced but its dir is absent (pruned, or never created).
  note       FEAT-13-single-issue-board-lookup: run distill-eng is referenced but its dir is absent (pruned, or never created).
  note       FEAT-13-single-issue-board-lookup: run distill-validator is referenced but its dir is absent (pruned, or never created).
  note       FEAT-13-single-issue-board-lookup: run distill-product is referenced but its dir is absent (pruned, or never created).
  note       INV-22 FEAT-10-software-factory: 32 runs recorded against a 20-run budget (cycles_used=12 counts REWORK only, DEC-157, so it does not see this). Not a defect by itself — check each run is efficient, is resolving issues, and is advancing the SCs. The count is a FLOOR: main-session-direct segments are not runs.
  note       FEAT-09-plan-time-route-check: run plan-product is referenced but its dir is absent (pruned, or never created).
  note       FEAT-09-plan-time-route-check: run seg1-main-session is referenced but its dir is absent (pruned, or never created).
  note       FEAT-09-plan-time-route-check: run t02-eng is referenced but its dir is absent (pruned, or never created).
  note       FEAT-09-plan-time-route-check: run dec179-product is referenced but its dir is absent (pruned, or never created).
  note       FEAT-09-plan-time-route-check: run panel-validator is referenced but its dir is absent (pruned, or never created).
  note       FEAT-09-plan-time-route-check: run goalcheck-product is referenced but its dir is absent (pruned, or never created).
  note       FEAT-09-plan-time-route-check: run distill-eng is referenced but its dir is absent (pruned, or never created).
  note       FEAT-09-plan-time-route-check: run distill-validator is referenced but its dir is absent (pruned, or never created).
  note       FEAT-09-plan-time-route-check: run distill-product is referenced but its dir is absent (pruned, or never created).
  note       INV-22 FEAT-14-feature-json-schema: 21 runs recorded against a 20-run budget (cycles_used=6 counts REWORK only, DEC-157, so it does not see this). Not a defect by itself — check each run is efficient, is resolving issues, and is advancing the SCs. The count is a FLOOR: main-session-direct segments are not runs.
  note       FEAT-05-pyyaml-file-parsers: run 2026-08-02-01-product is referenced but its dir is absent (pruned, or never created).
  note       FEAT-05-pyyaml-file-parsers: run 2026-08-02-02-eng is referenced but its dir is absent (pruned, or never created).
  note       FEAT-05-pyyaml-file-parsers: run 2026-08-02-03-product is referenced but its dir is absent (pruned, or never created).
  note       FEAT-05-pyyaml-file-parsers: run 2026-08-03-01-validator is referenced but its dir is absent (pruned, or never created).
  note       FEAT-05-pyyaml-file-parsers: run 2026-08-03-04-eng is referenced but its dir is absent (pruned, or never created).
  note       FEAT-05-pyyaml-file-parsers: run 2026-08-03-05-validator is referenced but its dir is absent (pruned, or never created).
  note       FEAT-06-team-layer-inv6: run inter-gate-q1q2 is referenced but its dir is absent (pruned, or never created).
  note       FEAT-15-domain-product-base: run dir 2026-08-11-01-validator exists on disk but feature.json does not record it — orphaned work (interrupted flow?). A resume must reconcile it, not rediscover it by luck.
  note       FEAT-20-migration-detector: run dir 2026-08-14-5-validator exists on disk but feature.json does not record it — orphaned work (interrupted flow?). A resume must reconcile it, not rediscover it by luck.
  note       FEAT-20-migration-detector: run dir 2026-08-14-4-validator exists on disk but feature.json does not record it — orphaned work (interrupted flow?). A resume must reconcile it, not rediscover it by luck.
  note       FEAT-20-migration-detector: run dir 2026-08-14-7-validator exists on disk but feature.json does not record it — orphaned work (interrupted flow?). A resume must reconcile it, not rediscover it by luck.
  note       FEAT-20-migration-detector: run dir 2026-08-14-6-validator exists on disk but feature.json does not record it — orphaned work (interrupted flow?). A resume must reconcile it, not rediscover it by luck.
  note       INV-17 FEAT-21-features-layout-migration: exempt from handoff notes — every task in its plan.yaml is execution_mode main-session-direct (DEC-174), so no squad ran and no seam was crossed. Suppressed handoff-build, handoff-validate.
  note       INV-17 FEAT-22-docs-layout-migration: exempt from handoff notes — every task in its plan.yaml is execution_mode main-session-direct (DEC-174), so no squad ran and no seam was crossed. Suppressed handoff-plan.
  note       INV-17 FEAT-15-domain-product-base: exempt from handoff notes — every task in its plan.yaml is execution_mode main-session-direct (DEC-174), so no squad ran and no seam was crossed. Suppressed handoff-plan, handoff-build, handoff-validate.
  note       INV-23 .harness/harness/features/FEAT-02/STATE.md has illegal section(s) ['## Feature', '## Mission', '## Success criteria (binding; pm may refine wording, not weaken)', '## Constraints', '## Log'] — STATE.md is `## Current` + `## Open Questions` and nothing else (SPEC §2).
  note       INV-23 .harness/harness/features/FEAT-05-pyyaml-file-parsers/STATE.md is 165 lines — budget is 120. It holds no history: ## Current is replaced, never appended (DEC-150).
  note       INV-23 .harness/harness/features/FEAT-05-pyyaml-file-parsers/STATE.md has illegal section(s) ['## Landed', '## Two rulings LANDED, 2026-08-03 — both were mine to raise, neither mine to decide', '## Carried forward', '## Backlog nit — not fixed here', '## Cost'] — STATE.md is `## Current` + `## Open Questions` and nothing else (SPEC §2).
exit: 0
```

SUITES

### unit
```
PASS test-harness-yaml-corpus.py
PASS test-render-brief.py
PASS test-team-catalog.py
PASS test-factory-cli.py
PASS test-factory-gh.py
PASS test-factory-config.py
PASS test-factory-workspace.py
PASS test-factory-decompose.py
PASS test-factory-claim.py
PASS test-factory-land.py
PASS test-no-distribution.py
PASS test-validate-feature-json.py
PASS test-gh-board.py
PASS test-branch-create-gate.py
PASS test-layout-migration.py
exit: 0
```

### integration
```
PASS test-validate-digest.py
PASS test-gh-sync.py
PASS test-check-state.py
PASS test-check-expertise.py
PASS test-gen-decisions-index.py
PASS test-bash-write-guard.py
PASS test-check-domain.py
PASS test-harness-yaml.py
PASS test-upgrade-config.py
PASS test-check-plan-routes.py
PASS test-merge-settings.py
PASS test-factory-integration.py
exit: 0
```

## RED STATES

Expected reds between boundaries, per T-01's intent (table form per the binding
simplify note). Any red NOT in this table is collateral and a stop:

| Interval | Suite | Expected FAILs | Cleared by |
|---|---|---|---|
| after T-02, before T-04 | integration | test-harness-yaml (COLLECT_FIXTURE ninth grant) | T-04 |
| after T-02, before T-03 | unit | test-layout-migration (team-config carries migrated docs grant on legacy evidence) | T-03 |
| after T-03, before T-09 | integration | test-gen-decisions-index (readers migrated, docs/ not yet moved — clears when T-09 lands the move) | T-09 |
| after T-04, before T-05 | integration | exactly ONE FAIL total (T-05's verify pins it) | T-05 |
| all other intervals | both | none — any FAIL is collateral, STOP | — |

DEPTH SWEEP

Method: RESOLVER sweep, not a grep — for each of the 51 Python files under
.claude/skills/harness/bin/, every site that RESOLVES the design-docs location was read and
asked whether it still resolves post-move. The four shapes hunted (plan.yaml:1205-1209):
counted relative climbs, empty-glob-equals-clean, module-scope open() of a joined path, and
hard-coded depth. FEAT-21's worked example applies: its three worst defects carried no legacy
literal at all.

Resolver findings, all verified live:
- factory_config._PROBE — joins ".harness/harness/docs/SPEC.md"; resolves (T-03).
- gen-decisions-index DOCS_DIR/DECISIONS_PATH/INDEX_PATH — runtime opens inside main(), not
  module scope; regenerated in place at T-09, byte-identical on re-run.
- harness_boundary HARNESS_CONTROL_PLANE — carries ".harness/*/docs/**"; both consumers
  short-circuit earlier, redundancy recorded in DEC-189 am.1.
- layout_migration / layout_fixtures — the detector's own patterns; segment-aware by design.
- check-plan-routes.py and factory_config.py ".." climbs — BIN_DIR-anchored root derivation,
  four levels from bin/, unaffected by the docs depth change; test files' climbs likewise.
- .harness/notes/audit-decisions.py — module-scope read_text, repointed at T-06, runs exit 0.
- render-map.py — its `docs` variable walks the CODEBASE map (.harness/codebase/), not the
  design docs; unrelated, no action.
Zero unresolved resolver-class sites remain.

Literal cross-check, partitioned — these are knowing survivors, NOT swept:

survivors: 174

- 158 under .harness/harness/features/ — shipped feature records (briefs, plans, notes,
  receipts, observations): historical prose recording what was true when written. Rule: a
  record is never rewritten to agree with the present (FEAT-21's partition rule).
- 6 under .harness/notes/ + 3 under .harness/logs/ — session and grilling records, same rule.
- 2 under .harness/harness/docs/ — DECISIONS.md's own history plus DEC-189 am.1, which QUOTES
  the pre-move spelling it corrects; an amendment that cannot name the old text cannot correct it.
- 5 under .claude/skills/harness/bin/ — the detector's legacy patterns (layout_migration,
  layout_fixtures: detection requires naming what it detects), the refused-direction case and
  FEAT-21's deliberate legacy sandbox (test-check-domain, test-check-state), and
  test-layout-migration's fixture stubs.

Reviewer note (plan.yaml:1262-1265): the detector proves per-file FORM AGREEMENT and never
per-site completeness — this sweep is the only control over sites the patterns are too narrow
to name.

## POST-MOVE

POST-MOVE HEAD: 1246b06c5eb96ac17cedfe4220668fedfdb67ecb
Cluster commit: e6e74c8 — the logs commit (1246b06) landed on top of the cluster
afterwards under the main session's own pen, so HEAD and the cluster commit differ.

### layout_migration.py
```
features: CLEAN — evidence migrated
docs: CLEAN — evidence migrated
examined 22 feature dir(s), 1 doc root(s), 7 reader file(s)
layout: 2 surface(s) clean, 0 mixed, 0 cannot-verify
exit: 0
```

### check-state.sh
```
  note       .harness/harness/features/FEAT-19-central-product-config/plan.yaml approval is pending — awaiting the user.
  note       .harness/harness/features/FEAT-08-remove-cost-tracking/PLAN.md approval is pending — awaiting the user.
  note       FEAT-21-features-layout-migration: run dir 2026-08-15-1-validator exists on disk but feature.json does not record it — orphaned work (interrupted flow?). A resume must reconcile it, not rediscover it by luck.
  note       FEAT-13-single-issue-board-lookup: run t01-eng is referenced but its dir is absent (pruned, or never created).
  note       FEAT-13-single-issue-board-lookup: run qa-validator is referenced but its dir is absent (pruned, or never created).
  note       FEAT-13-single-issue-board-lookup: run t02-eng is referenced but its dir is absent (pruned, or never created).
  note       FEAT-13-single-issue-board-lookup: run panel-validator is referenced but its dir is absent (pruned, or never created).
  note       FEAT-13-single-issue-board-lookup: run goalcheck-product is referenced but its dir is absent (pruned, or never created).
  note       FEAT-13-single-issue-board-lookup: run fix01-eng is referenced but its dir is absent (pruned, or never created).
  note       FEAT-13-single-issue-board-lookup: run sc05recheck-product is referenced but its dir is absent (pruned, or never created).
  note       FEAT-13-single-issue-board-lookup: run distill-eng is referenced but its dir is absent (pruned, or never created).
  note       FEAT-13-single-issue-board-lookup: run distill-validator is referenced but its dir is absent (pruned, or never created).
  note       FEAT-13-single-issue-board-lookup: run distill-product is referenced but its dir is absent (pruned, or never created).
  note       INV-22 FEAT-10-software-factory: 32 runs recorded against a 20-run budget (cycles_used=12 counts REWORK only, DEC-157, so it does not see this). Not a defect by itself — check each run is efficient, is resolving issues, and is advancing the SCs. The count is a FLOOR: main-session-direct segments are not runs.
  note       FEAT-09-plan-time-route-check: run plan-product is referenced but its dir is absent (pruned, or never created).
  note       FEAT-09-plan-time-route-check: run seg1-main-session is referenced but its dir is absent (pruned, or never created).
  note       FEAT-09-plan-time-route-check: run t02-eng is referenced but its dir is absent (pruned, or never created).
  note       FEAT-09-plan-time-route-check: run dec179-product is referenced but its dir is absent (pruned, or never created).
  note       FEAT-09-plan-time-route-check: run panel-validator is referenced but its dir is absent (pruned, or never created).
  note       FEAT-09-plan-time-route-check: run goalcheck-product is referenced but its dir is absent (pruned, or never created).
  note       FEAT-09-plan-time-route-check: run distill-eng is referenced but its dir is absent (pruned, or never created).
  note       FEAT-09-plan-time-route-check: run distill-validator is referenced but its dir is absent (pruned, or never created).
  note       FEAT-09-plan-time-route-check: run distill-product is referenced but its dir is absent (pruned, or never created).
  note       INV-22 FEAT-14-feature-json-schema: 21 runs recorded against a 20-run budget (cycles_used=6 counts REWORK only, DEC-157, so it does not see this). Not a defect by itself — check each run is efficient, is resolving issues, and is advancing the SCs. The count is a FLOOR: main-session-direct segments are not runs.
  note       FEAT-05-pyyaml-file-parsers: run 2026-08-02-01-product is referenced but its dir is absent (pruned, or never created).
  note       FEAT-05-pyyaml-file-parsers: run 2026-08-02-02-eng is referenced but its dir is absent (pruned, or never created).
  note       FEAT-05-pyyaml-file-parsers: run 2026-08-02-03-product is referenced but its dir is absent (pruned, or never created).
  note       FEAT-05-pyyaml-file-parsers: run 2026-08-03-01-validator is referenced but its dir is absent (pruned, or never created).
  note       FEAT-05-pyyaml-file-parsers: run 2026-08-03-04-eng is referenced but its dir is absent (pruned, or never created).
  note       FEAT-05-pyyaml-file-parsers: run 2026-08-03-05-validator is referenced but its dir is absent (pruned, or never created).
  note       FEAT-06-team-layer-inv6: run inter-gate-q1q2 is referenced but its dir is absent (pruned, or never created).
  note       FEAT-15-domain-product-base: run dir 2026-08-11-01-validator exists on disk but feature.json does not record it — orphaned work (interrupted flow?). A resume must reconcile it, not rediscover it by luck.
  note       FEAT-20-migration-detector: run dir 2026-08-14-5-validator exists on disk but feature.json does not record it — orphaned work (interrupted flow?). A resume must reconcile it, not rediscover it by luck.
  note       FEAT-20-migration-detector: run dir 2026-08-14-4-validator exists on disk but feature.json does not record it — orphaned work (interrupted flow?). A resume must reconcile it, not rediscover it by luck.
  note       FEAT-20-migration-detector: run dir 2026-08-14-7-validator exists on disk but feature.json does not record it — orphaned work (interrupted flow?). A resume must reconcile it, not rediscover it by luck.
  note       FEAT-20-migration-detector: run dir 2026-08-14-6-validator exists on disk but feature.json does not record it — orphaned work (interrupted flow?). A resume must reconcile it, not rediscover it by luck.
  note       INV-17 FEAT-21-features-layout-migration: exempt from handoff notes — every task in its plan.yaml is execution_mode main-session-direct (DEC-174), so no squad ran and no seam was crossed. Suppressed handoff-build, handoff-validate.
  note       INV-17 FEAT-22-docs-layout-migration: exempt from handoff notes — every task in its plan.yaml is execution_mode main-session-direct (DEC-174), so no squad ran and no seam was crossed. Suppressed handoff-plan.
  note       INV-17 FEAT-15-domain-product-base: exempt from handoff notes — every task in its plan.yaml is execution_mode main-session-direct (DEC-174), so no squad ran and no seam was crossed. Suppressed handoff-plan, handoff-build, handoff-validate.
  note       INV-23 .harness/harness/features/FEAT-02/STATE.md has illegal section(s) ['## Feature', '## Mission', '## Success criteria (binding; pm may refine wording, not weaken)', '## Constraints', '## Log'] — STATE.md is `## Current` + `## Open Questions` and nothing else (SPEC §2).
  note       INV-23 .harness/harness/features/FEAT-05-pyyaml-file-parsers/STATE.md is 165 lines — budget is 120. It holds no history: ## Current is replaced, never appended (DEC-150).
  note       INV-23 .harness/harness/features/FEAT-05-pyyaml-file-parsers/STATE.md has illegal section(s) ['## Landed', '## Two rulings LANDED, 2026-08-03 — both were mine to raise, neither mine to decide', '## Carried forward', '## Backlog nit — not fixed here', '## Cost'] — STATE.md is `## Current` + `## Open Questions` and nothing else (SPEC §2).
exit: 0
```

RECONCILIATION

1. Did the docs surface go legacy -> migrated with features CLEAN at both captures?
   Yes. PRE-MOVE recorded docs: CLEAN — evidence legacy; this capture records
   docs: CLEAN — evidence migrated, and features: CLEAN — evidence migrated appears
   in both. Command: python3 .claude/skills/harness/bin/layout_migration.py (above).
2. Tracked legacy files 0, destination files 5 including org.html?
   Yes. `git ls-files docs/harness/` returns 0 paths; `git ls-files .harness/harness/docs/`
   returns 5: BUILD.md, DECISIONS-INDEX.md, DECISIONS.md, SPEC.md, org.html.
3. Did check-state's note count move for any reason other than this feature?
   No. 42 note lines at this capture vs 42 in the PRE-MOVE capture — unchanged.
   Command: bash .claude/skills/harness/bin/check-state.sh | grep -c '^  note'.
Close-out commit: 5faa832449529554361c23bd3efebb14ca2e7d1c

## CORRECTION — the SC-10 fix, appended 2026-08-16

Pre-fix SHA: e26e628. This section and the fix it describes land in the same commit.

WHAT THE DEPTH SWEEP GOT WRONG. The docs partition above reads "2 under
.harness/harness/docs/ — DECISIONS.md's own history plus DEC-189 am.1". That names one file
twice: am.1 lives INSIDE DECISIONS.md. The genuine second file was SPEC.md, never named — and
it was the one carrying a DEFECT rather than a survivor. SPEC.md:1721 read
`decisions: # pointers; reasoning lives in docs/harness/DECISIONS.md`: a present-tense claim in
live instruction, naming the dead path. By the partition rule that is not historical prose, so it
was misclassified. It is now repointed to `.harness/harness/docs/DECISIONS.md`, matching the
template it specifies (templates/plan.yaml:44), which had already been corrected — spec and
template had disagreed since the cluster landed.

WHY T-10'S OWN VERIFY COULD NOT CATCH IT. The live-surface control is an exact per-file table
over .claude, CLAUDE.md and .harness/expertise. The moved docs are in none of those three, so no
clause of the sweep ever examined .harness/harness/docs/ for present-tense claims. The sweep's
positive control and its survivor arithmetic were both green while the defect sat inside a class
the table does not reach. The goal-check's inspection of SC-10 is what found it.

RE-DERIVED AT THE FIXED TREE, with plan.yaml's own two-spelling command, not carried:

  git grep -lE 'docs/harness|"docs", ?"harness"' -- . ':!<this feature dir>' | wc -l

survivors (post-fix): 173 — and the classes reconcile exactly, 158 + 6 + 3 + 1 + 5 = 173:
- 158 shipped feature records · 6 under .harness/notes/ · 3 under .harness/logs/ (unchanged)
- 1 under .harness/harness/docs/ — DECISIONS.md alone, was 2 before SPEC.md was fixed out
- 5 under .claude/skills/harness/bin/ (unchanged; the live-surface table is undisturbed)

THE `survivors: 174` LINE ABOVE IS LEFT STANDING AND IS NOT AN ERROR. It was true at e26e628,
when it was measured. Consequently `feat22-verify-T10.sh` reds if re-run at or after this commit,
comparing its recorded 174 against a tree that now holds 173. That red is the tree changing, not
a regression: a task verify binds its own tree at acceptance and is not a standing gate.
