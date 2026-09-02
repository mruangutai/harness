# Re-anchor of FEAT-51's plan artifacts — 6ddcac3 to ad93d43e (cycle plan-fix-c1)

**Both artifacts now measure against `ad93d43e1f232ec1ab87e08ccf70a01a08c206b7`, and
`check-plan-routes.py` returns 0 violations (exit 0).** The design was not touched. Nine
`intent:` claims were false at the new base and are corrected. Two blocking questions came
out of the re-measurement — one a harness defect that stops this plan being signed at all,
one a coverage hole FEAT-41 opened in REQ-04.

The plan was created through `plan-merge.py apply` from the proposal at
`/tmp/feat51-plan-proposal-c1.yaml` (the dispatch's `notes/plan-proposal-c1.yaml` is
ungranted to pm — `--resolve` answers `harness-orchestrator` only — so the proposal stayed
outside the tree; `plan.yaml` itself is the durable record).

## Blocking questions

**Q1 — a plan created by `plan-merge.py apply` can never be signed.** `apply` refuses a
proposal carrying `approval:` when the destination is absent (`plan-merge.py:468`, exit 8),
no verb writes the mapping, and `sign-approval` refuses a plan that carries none
(`plan-merge.py:879`, exit 5). So `plan.yaml` has no `approval:` block and cannot acquire
one. Candidate remedies, both in the harness and neither in this feature's scope: let
`sign-approval` insert the block when absent, or let `apply` write a status-only unsigned
block on the create path. FEAT-51's user signature currently rests on `BRIEF.md`'s own
Approval section, which is unsigned.

**Q2 — REQ-04 and REQ-05 are no longer fully reachable for `plan.yaml`.** At the old base
`plan.yaml` was written with `Write`, so the `check-domain.sh` Write gate covered it. FEAT-41
made that route non-existent for every author (`check-domain.sh:1529-1678`) and moved the
real write to `plan-merge.py`, a **Bash** route the PreToolUse Write gate never sees. An
orphaned child can therefore still land canonical `plan.yaml` content via
`plan-merge.py apply` with no adoption. The union merge means it cannot *delete* tasks
(D-07's protection now lives in the tool), so the measured #551 loss is prevented — but
REQ-05's "only by explicit adoption" is not enforced there. The two candidate answers are a
quarantine check inside `plan-merge.py`'s verbs (new work), or accepting a Write-route-only
boundary. **Requirements left standing, unedited, per dispatch.**

## `intent:` claims that were false at the new base

| Task | Was | Is at `ad93d43e` |
|---|---|---|
| T-01 | cases go through `case()` | `case()` (`:239`) is the CLI schema harness and carries no registry; the fixture builders are `_t09_root` `:1241`, `_reg_module` `:1231`, `_t09_fire` `:1249`, recorder `t09` `:1227`, runner `main` `:3036` |
| T-01 | comment `STEP TWO - THE D-09 RETURN CONTRACT` | em dash, `:1549`; refusal `:1574`, `hook_mode` `:1453` |
| T-01 | "step one releases on every return" | true, at `STEP ONE` `:1527` — but the text is only read at `:1602`, *after* the block, so the suspension branch must read it itself |
| T-02 | cases 29-33 free | still free (`case_28...` is the highest); **`main()` calls every case by name** — registration added to the intent |
| T-03 | cases through `case()` + `_env` | `case()` `:41` carries no `session_id`; `_env` `:22` is right for env only |
| T-03 | branch after `domain_check()`, before the shape phase | that position now sits **ahead** of FEAT-41's plan.yaml route denial. Moved to immediately after `:1678`, before the mode split at `:1680` — recorded as **D-11** |
| T-03 | grade the canonical case on `plan.yaml` | non-discriminating: already exit 2 for every author. Regraded on `BRIEF.md`, plus a case pinning the route-denial text for `plan.yaml` |
| T-04 | `.claude/...test-quarantine.py` into `integration.detect` | the cross-check (`run-unit-tests.sh:98-131`) uses the `.agents` spelling as its prefix, so the `.claude` spelling fails it |
| T-05 | add `case9_claude_code_suspension` | `case9_plan_yaml_write_is_a_verb_not_an_edit` is **taken** (FEAT-41, `:129`) → `case10_...`; and the override is `PLAYBOOK_PATH` / `TEAM_PLAYBOOK_PATH`, not `TEAM_PLAYBOOK_DEFAULT` (`:34` is the default) |
| T-05 | "add a passage beside the dispatch step" | `harness-team/SKILL.md:126-130` already tells a lead to *expect the refusal to recur*. This feature supersedes that clause; it must be rewritten, not doubled |
| T-06 | `DEC-208` | taken; `DEC-209` is free (0 tokens in `DECISIONS.md` at `ad93d43e`) |

## Re-verified and unchanged

The premise holds: `validate-digest.py` still calls `live_children` (`:1563`) and
`children_refusal_lines` (`:1575`); `inflight_registry` still exposes `_update_registry`
`_expire_where` `_matches` `_visible`, `CLAIM_TTL_SECONDS = 1200`,
`OMP_UNVERIFIED_TTL_SECONDS`; `team-config.yaml` still has a `shared:` list (`:77`);
`test_kinds` `component`/`ui`/`eval`/`typecheck` are still `cmd: null`, `functional`
excluded; 16 `.omp/agents/harness-*.md` files, every non-orchestrator one still
`blocking: true`; `check-omp-port.py`, `gen-decisions-index.py` and
`test-gen-decisions-index.py` all present. The four `--resolve` NOBODY answers in the BRIEF
still hold; `check-domain.sh` itself resolves to **both** `harness-backend-dev` and
`harness-dev-ops` (the batch context named only the first), which changes nothing because
DEC-174 holds it back either way.

## Lanes

All 17 surfaces re-resolved with the main checkout's `check-domain.sh --resolve` and written
into `lanes.rows`. `.claude/settings.json` is not a plan surface and has no row (it is still
NOBODY, and the BRIEF's constraint still cites it correctly).
