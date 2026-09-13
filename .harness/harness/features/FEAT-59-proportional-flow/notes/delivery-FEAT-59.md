# Delivery — FEAT-59 Proportional flow — branch `feat/FEAT-59-proportional-flow`

Built as DEC-174 main-session-direct work: the main session owned decomposition, the
interfaces between slices, integration and the final read; eight generic OMP subagents each
owned one file-bounded slice, test-first, and never ran a harness gate as a gate. No harness
persona, lead or orchestrator ran. 14 commits, 75 files, +7,132 / −1,459.

## How each SC is discharged

| SC | Evidence |
|---|---|
| SC-01 mission judgement in grilling | `harness-grilling/SKILL.md` "Judge the mission"; `harness-plan.md` / `harness-patch.md` refuse without `## Mission` — inspection |
| SC-02 patch lane, one intake run, one-task plan | `harness-brief/SKILL.md` §7, `harness-patch.md`, playbook plan phase; INV-32 exempts `mission: patch` (`test-check-state-records.py::case_inv32_patch_mission_has_no_panel`). **Live evidence pending SC-23** |
| SC-03 proportionality downgrade | playbook "The plan phase" (`set-mission patch` + `mission` judgement); `plan.yaml` team digest `recommend: downgrade patch` — inspection. Live evidence pending SC-24 |
| SC-04 one plan run | `teams/plan.yaml` (draft → readers in one turn → apply → goalcheck); `test-plan-team.py` 137/137. **Live evidence pending SC-24** |
| SC-05 `record-panel` verb | `plan-merge.py record-panel`; `test-plan-merge.py` `case_f59_record_panel_*` (3 cases) |
| SC-06 finding `kind` | `validate-digest.py` `FINDING_KINDS`; `test-validate-digest.py` 8 FEAT-59 kind cases |
| SC-07 symbol anchors, `check`, line numbers refused | `plan_anchors.py`, `plan-merge.py check`; `case_f59_check_*`, `case_f59_line_number_anchor_is_refused_at_write` |
| SC-08 approval auto-reset, `apply` replaces, `lanes`, `set-panel` identity | `case_f59_approval_auto_reset_*` (2), `case_conflict`, `case_f59_set_lanes_*`, `case_f59_set_panel_keeps_*` |
| SC-09 goal-check twice, never per cycle | playbook step 7 and plan/validate teams — inspection |
| SC-10 BRIEF shape + INV-38 | `templates/BRIEF.md`; `check-state.sh` INV-38; `test-check-state-feat59.py::case_inv38` (8 cases) |
| SC-11 handoff cites `brief-perspective:` | `handoff_done_when.py`; `test-handoff-done-when.py` 13 new cases; `templates/HANDOFF.md` |
| SC-12 scope reader hunts orphan SCs | `teams/plan.yaml` scope prompt; `harness-brief/SKILL.md` §3 — inspection |
| SC-13 batched validate | `teams/validate.yaml` (qa, code, security, ui, goalcheck in one turn); `test-plan-team.py`. **Live evidence pending SC-24** |
| SC-14 single-run fix loop | `teams/fix.yaml`; validator-lead `spawns:` gains the five devs; grants probed live (TeamsConfig digest). **Live evidence pending SC-24** |
| SC-15 one rework ruling; cycles enforced; raise needs decision | `sign-approval --rework`, `feature-record.py set-rework/raise-cycles`; INV-39 (`case_inv39`, 8 cases); playbook cycle budget |
| SC-16 repo-wide SC refused | INV-41 (`case_inv41`, 8 cases); `harness-brief/SKILL.md` §4 |
| SC-17 qa fail-first | `validate-digest.py` `fail_first`; 7 qa cases in `test-validate-digest.py`; `harness-qa-gate`, `harness-verification-rules` |
| SC-18 per-run spend, measured | `feature-schema.json` runs keys; `feature-record.py run-start/run-end`; `test-feature-record.py` 27 cases; header: tokens measured or null. Child figure reachable at `details.results[i].tokens` on a blocking wake — playbook "The ledger" |
| SC-19 SPEND advisory | `harness-hooks.ts` `spendAdvisoryFor`; `omp-hooks.test.ts` 6 injection cases; `budgets.plan_phase_warn_minutes` in both harness.json |
| SC-20 succession decides, does not ask | playbook "Succession"; INV-40 (c) requires the `succession` entry — inspection. Live evidence pending a real handoff |
| SC-21 judgement ledger | `feature.json` `judgements[]`; `feature-record.py judgement`; INV-40 (`case_inv40`, 13 cases); DEC-230 |
| SC-22 uncertainty asks once | playbook "Uncertainty"; grilling and brief red flags — inspection; ledgers of the first two features graded at SC-23/24 |
| SC-23 live bug through patch lane | **OPEN** — the next real bug |
| SC-24 live feature through plan lane | **OPEN** — the next real feature |

Suites at `a1c3a683`: unit 37 files exit 0; integration 71 files exit 0; `check-omp-port.py`,
`sync-agent-adapters.py --check`, `sync-command-adapters.py --check` exit 0; `check-state.sh`
on the branch: 0 violations, 69 legacy notes (one per pre-ledger feature.json, as INV-39/40 intend).

## Judgements made outside the ledger

This feature has no `feature.json`: a main-session-direct segment is not a run, and a signed
`plan.yaml` with no panel would trip INV-32 — the record below is the honest substitute, in the
`judgements[]` shape, so the first two real ledgers (SC-23/24) have a baseline to compare against.

```yaml
- at: 2026-09-11  by: main-session  kind: mission
  decision: plan lane, executed DEC-174-direct
  reason: new interfaces and gate scripts; /harness-plan would spend the loop this feature removes
- at: 2026-09-11  by: main-session  kind: continue
  decision: amend SC-02 — patch lane writes a one-task plan.yaml
  reason: stations, gh-sync, review_sha and the build team all key on plan tasks; one generated task keeps one lane
- at: 2026-09-11  by: main-session  kind: finding_kind
  decision: substance — INV-32 exempts mission: patch
  reason: TeamsConfig found INV-32 would fail every signed patch plan; fixed test-first, not deferred
- at: 2026-09-11  by: main-session  kind: finding_kind
  decision: form — DigestKind findings int→list; PlanMerge bare-path rule; SPEC/agent doc-line edits
  reason: contract-adjacent shape changes, approved in-flight, no re-read
- at: 2026-09-11  by: main-session  kind: continue
  decision: no feature.json/plan.yaml for FEAT-59 itself
  reason: a synthetic ledger for a direct build would be a record of runs that never happened
```

## Independent review, and what it changed

Two read-only reviewers (generic `reviewer` and `security-reviewer`, outside the harness path per
DEC-174) read the enforcement-layer diff at `312cad9e`. Eleven findings; ten fixed test-first in
the commits that follow it: the rework window keyed on `startswith("validate-")` and never opened
on the corpus's date-prefixed run ids (SC-19 would never have fired); INV-40 was presence-only, so
a second `set-mission` passed unrecorded (`set-mission` now writes the judgement atomically and
INV-40 matches the last one); the approval reset was reported without being verified; the
signature was written before the ruling; a `patch` exemption keyed on the string alone; the two
budget verbs had no principal gate and a free-text `--decision`; `apply` could roll a station
back; `record-panel` accepted a pre-resolved finding; INV-39 skipped an inherited bound; a panel
comment migrated. The eleventh is below.

## Known limits, stated

- **The overrule KPI has no ledger shape yet.** `judgements[]` has no `overrule` kind and `by` is
  free text, so the rate is countable only from `approval.rulings` and the operator's returns, not
  mechanically from `feature.json`. Deliberately left until the first two real ledgers exist
  (SC-23/24) so the shape follows observed overrules rather than a guess; it is FEAT-60-adjacent.

- SC-23 and SC-24 are the acceptance and are open by design; the brief says it is not done until
  both ship. Everything above is the mechanism; those two are the proof.
- `tokens` on a run is null unless the orchestrator passes the measured child figure; the
  playbook tells it where the figure is. Nothing estimates.
- INV-39/40 note, never fail, on the 69 pre-ledger features. A retrofit is out of scope.
- The `integration` test kind is a replayed-fixture runner here; the four SCs the brief flags as
  needing a live flow rest on SC-23/24, as `## Verification gaps` says.
