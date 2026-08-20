# REUSE angle — FEAT-26 plan surface — 2026-08-18

## Read
- `plan.yaml` (full, 686 lines) — all decisions D-01..D-08, all tasks T-01..T-08 verify+intent.
- `BRIEF.md`.
- `.claude/skills/harness/bin/gh-sync.py` — grepped every top-level `def`, read
  `_opt_int` (315), `load_recorded` (330), `_atomic_write` (418), `_record_status` (445),
  `save_recorded` (469), `cmd_open` (518), `cmd_ship` (707) in full or near-full.
- `.claude/skills/harness/bin/harness_yaml.py` — `load_file` (237) vs `load_plan` (287),
  to check which one T-02's `parse_source_issues` should call.
- `.claude/skills/harness/bin/test-gh-sync.py` — grepped for fake-gh invocation logging
  (`FAKE_GH`, `FAKE_LOG`, `calls.log`, `read_calls`) to settle T-04's hedge.
- `.claude/skills/harness/bin/feature-schema.json`, `test-validate-feature-json.py`,
  `test-check-state.py`, `check-state.sh` — skimmed for existing shape T-01/T-05 model on
  (INV-21 block, existing `github.properties` block); matches what the plan already cites.

## What I checked for, per the dispatch's four named items

1. **New helper vs existing exports** (`_opt_int`, `_atomic_write`, `_record_status`,
   `load_recorded`/`save_recorded`, `harness_yaml` loaders): T-02 and T-03's intents name
   these exact functions and call them exactly where they already live — no restatement found.

2. **T-02's `parse_source_issues`**: genuinely new. No existing gh-sync.py function reads
   plan.yaml's top-level `source_issues` key. It correctly specifies `harness_yaml.load_file`
   (line 237) rather than `harness_yaml.load_plan` (line 287) — `load_plan` enforces
   `REQUIRED_TASK_FIELDS` on every task and would raise on a plan that doesn't carry that
   shape, which is the wrong tool for a lenient top-level-key read. Not a reuse gap.

3. **T-03's `_record_pr`**: genuinely new. No existing function derives a PR number from a
   branch via `gh pr list --state merged`. `_record_status` (445) is the nearest sibling and
   the intent explicitly models `_record_pr`'s error/absent-doc handling on it rather than
   restating it inline — correct reuse, not a gap.

4. **T-04's `cmd_closes`**: new function, but the intent's own hedge — "if the suite's fake
   gh does not already record its invocations, extend it" — resolves against the file.
   `test-gh-sync.py` already logs every invocation: docstring at line 4 ("The fake logs
   every invocation..."), `FAKE_GH` script writes to `env["FAKE_LOG"]` (line 116), and
   `calls.log` is read/asserted against repeatedly elsewhere in the suite (lines 123, 449,
   458, 465, 674, 679, 695, 1134). T-04's "no gh call" case should read `calls.log` and
   assert it's empty — no extension to the fake is needed. This is not a plan defect: the
   intent already anticipates and correctly defers to "if not already" — flagging it here
   only to confirm the condition resolves to "already does," so the doer does not spend a
   cycle building unneeded logging machinery.

## Findings

None that rise to a plan revision. All four charter items resolve in the plan's favor: the
named helpers are genuinely reused where they exist, and the two functions flagged as
candidate restatements (`parse_source_issues`, `_record_pr`, `cmd_closes`) are each
new surface with no existing equivalent in gh-sync.py or the test suites.

## Empty return

Real and expected per the dispatch. Confirmed by reading the surface, not a pre-emptive skip.

```yaml
VERDICT: PASS
DIGEST:
  headline: "REUSE angle over FEAT-26 plan.yaml/BRIEF.md finds no reuse gap — all named helpers (_opt_int, _atomic_write, _record_status, load_recorded/save_recorded, harness_yaml.load_file) are correctly reused, and T-02/T-03/T-04's three new functions have no existing equivalent; T-04's fake-gh logging hedge resolves to already-present (test-gh-sync.py already logs every invocation to calls.log)"
  tests_added: 0
  suite: n/a
  task: none
  open_questions: []
  files_touched:
    - .harness/harness/features/FEAT-26-pr-linkage-recorded/notes/receipt-harness-backend-dev-2026-08-18-2-reuse.md
  expertise_update: []
artifact: /Users/molchairuangutai/GitHub/harness/.harness/harness/features/FEAT-26-pr-linkage-recorded/notes/receipt-harness-backend-dev-2026-08-18-2-reuse.md
```
