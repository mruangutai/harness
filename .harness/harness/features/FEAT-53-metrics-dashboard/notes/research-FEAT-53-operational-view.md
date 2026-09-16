# FEAT-53 operational-view research — 2026-09-15

## Sources read

- `.harness/notes/grilling-work-dashboard-2026-09-15.md` in the control-plane main checkout.
- FEAT-53 `BRIEF.md`, `plan.yaml`, `STATE.md`, `DESIGN.md`, `.harness/team-config.yaml` and `.harness/harness.json` in the FEAT-53 worktree.
- `.claude/skills/harness/bin/harness-observe.py` in the dirty FEAT-61 worktree.
- Existing fleet/config seams: `factory_config.py`, `factory_workspace.py`, `worktree_terminal.py`, `upgrade-config.py`, the grilling skill, plan/patch commands and `check-state.sh`.

## Verified constraints

- Fleet feature state is segmented under the control plane, while live feature copies can exist only in linked worktrees. The collector therefore needs both central enumeration and every `git worktree list --porcelain` entry for the control plane and each configured workspace repository; primary checkouts remain visible rows but never override their own main copy.
- `worktree_terminal.py` already owns fleet worktree enumeration/classification. The operational collector should reuse it rather than introduce a competing scanner.
- FEAT-53 already chose Flask, loopback-only serving, request-time recomputation, a committed React/TanStack/Astryx shell and explicit unavailable reasons in D-03 through D-07, D-17 and D-19 through D-20. None needs amendment.
- The active and template `harness.json` files are schema version 2 and `upgrade-config.py` merges new template keys. Adding a required `dashboard` block therefore needs one schema-version advance so existing installations receive it.
- Grilling notes have no lifecycle front-matter today. Creation is owned by the grilling skill; conversion begins in the plan or patch intake commands; `check-state.sh` is the invariant gate. Those surfaces and the 46-note migration corpus have no single team-member grant, so they require one main-session-direct cutover.
- The FEAT-61 prototype has useful disk parsing and restartable-collection ideas, but its single-root assumptions, fixed-width rendering, hard-coded rank data and Herdr plugin conflict with the settled destination. Its dirty worktree must remain input-only until the adopted collector is verified, then be force-removed without merging its branch.
- FEAT-53's current DESIGN and prototype describe KPI routes only. The operational route therefore needs a visual-designer answer covering shell placement, responsive rows, attention tokens, source-path disclosure and malformed-source presentation before the amended bundle can be signed.

## Specification consequences

- New decisions are limited to fleet scope, attention derivation, grilling lifecycle metadata, worktree precedence and disk-only operation. Existing KPI and technology decisions remain unchanged.
- Seven operational tasks form their own lane: collector, attention/config, grilling lifecycle/backfill, worktree rows, Flask API, client view and FEAT-61 disposition. The API depends on T-12; the client depends on T-04, T-13 and the API; T-16 must wait for the client task so the committed bundle contains `/work`.
- The API surface is `GET /api/work`, schema `harness-work/1`. It returns effective thresholds, ranked items and explicit source errors, recomputed for every request.
- Attention order is exactly needs-you, blocked, stalled, over-budget, running, stale. The configured boundaries are 45 minutes, seven days and one remaining cycle. `running` is only a recent persisted-run label; no process-liveness claim is made.
- Source precedence is whole-record worktree-wins with main-checkout fallback. `main_path`, nullable `worktree_path` and `source_path` are always distinct contract fields; fields are never merged.
