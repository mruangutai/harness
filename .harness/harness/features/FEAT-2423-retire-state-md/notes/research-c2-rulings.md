# Research — FEAT-2423 c2 revision per operator rulings (2026-11-28)

**BLUF:** Every ruling in `notes/answers-2026-11-28-plan-c1.md` is applied to BRIEF.md and plan.yaml. Tasks changed: T-01, T-02, T-04, T-07. T-03, T-05 and T-06 are untouched. `plan-merge.py check --root <main checkout>` exits 0: 7 tasks, 78 anchors, 0 failures. No APPROVAL-RESET was emitted (the plan is pending).

## Probes
- org.html linkers: `git grep -n 'org\.html' -- ':(exclude).harness/*/features/**'` at main `ca0c1a6e` exits 1. Only shipped feature records (BUG-2565) mention it, and they stay historical. Nothing live links to it, so no new question.
- Quoted bare-token probe: `git grep -n -I -E "[\"']STATE[\"']" -- tests ':(exclude)tests/integration/fixtures/prior-*'` exits 1 at main `ca0c1a6e`. It can join SC-03 and T-07 as the split-literal guard. A plain `-w STATE` over tests would not work: `tests/integration/test-check-state-plans.py` holds an unrelated comment, "FORGED STATE LOUDER".
- Surviving routing: after `_rule_state_md` goes, `deny()` (which appends ROUTING) is called only by `_rule_feature_json`'s budget branch in `check-domain.py`. That makes the feature.json budget denial the positive control for the new ROUTING sentence.
- Generic feature-directory reads: INV-7, INV-15, INV-37 and INV-46 list `.harness/*/features/*/**` in `check-state.py --list`. SC-05's removal proof does not cover them. The gap is recorded under the BRIEF's Verification gaps.

## Q-06 choice (SC-05 / SC-06)
- SC-05 is now **inspection, with removal as the proof**. No test may write the file, so no behavioural assertion about a stray copy is possible without naming it. The proof is the deleted rules (`RE_STATE_MD`, `_rule_state_md`, INV-2, INV-5, INV-23's third source), checked by SC-03's grep and a pinned read of the pattern tables. T-01 and T-02 trace it.
- SC-06 is now an **automated live-behaviour case**, `run_budget_denials_route_to_live_records`. The surviving budgets (feature.json, handoff, CLAUDE.md) exit 2, and the feature.json denial carries the new ROUTING sentence exactly. It is genuinely red at base, because the base denial carries the old sentence. It never names the file. Fail-first wording is kept only for the clause that can be red.
- The T-01 INV-23 assertion is now a set equality over the two read sources, so the test never spells a third name.

## c1 high remedies — what changed
- T-01: `rows[-8]`, the rename witness and the INV-2/5 grep are unchanged. The python verify block lost only the span check (`case_stray_status_file_is_inert`). Its exit now requires git grep exit 0, no live hits and exactly 2 retired hits. `test-check-state-table.py` joined the status-file grep.
- T-05: unchanged.
- T-06/T-07 `set -e -o pipefail` sweep: T-06 is unchanged. T-07 drops the two test-file exclusions, adds the quoted bare-token grep and drops the kaya conditional.
