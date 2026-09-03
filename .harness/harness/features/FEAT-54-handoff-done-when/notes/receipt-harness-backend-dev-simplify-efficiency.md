# SIMPLIFY — EFFICIENCY — FEAT-54-handoff-done-when

## Outcome

PASS. No actual wasted work with a material or honestly measurable cost was found.

## Scope

Read-only assessment of base `b7956fc4` through current HEAD plus working-tree changes, limited to the task-declared files in `plan.yaml`: `.claude/skills/harness/bin/handoff_done_when.py`, `.claude/skills/harness/bin/check-domain.sh`, `.claude/skills/harness/bin/check-state.sh`, `.claude/skills/harness/templates/HANDOFF.md`, `.claude/skills/harness/SKILL.md`, `.harness/harness.json`, `.harness/harness/docs/DECISIONS.md`, `.harness/harness/docs/DECISIONS-INDEX.md`, `tests/unit/test-handoff-done-when.py`, `tests/integration/test-check-domain.py`, `tests/integration/test-check-state.py`, `tests/manual/probe-handoff-comprehension.py`, and `tests/integration/test-run-unit-tests-kinds.py`; plus active notes `notes/handoff-plan.md` and `notes/handoff-build.md`. The task-declared `notes/` directory was resolved to active `handoff-*.md` notes. Orchestration ledgers, run state, review records, and QA evidence were excluded.

## Measurements and derived costs

- Persisted state path: the repository has 143 tracked `notes/handoff-*.md` files; `.harness/harness.json` freezes 141 historical paths. At session entry, `check-state.sh:992-998` normalizes those 141 strings and performs one set membership check per note. Only notes already carrying `## Done when` enter `handoff_done_when.problems(..., resolve=False)` (`check-state.sh:1244-1251`), so the new parser performs in-memory line work for the two active FEAT-54 notes and opens zero authority targets. This adds 141 small string normalizations, 143 O(1) lookups, two in-memory parses, and zero pointer-target reads per entry—not a credible minutes-scale cost.
- Write-hook path: `check-domain.sh:1561-1567` imports and calls the validator only while checking a handoff-note write, not for ordinary writes. The proposed note text is already in memory. Resolution performs one target read per legal Authority line (`handoff_done_when.py:62-102`), bounded by the contract at one to four authorities (`handoff_done_when.py:117-119`), with no spawned process. There is no new general write-hook startup cost.
- Manual probe: `probe-handoff-comprehension.py:124-127` deliberately makes exactly two model calls per selected note, one per experimental arm. That paired work is the measurement itself and the probe is `locally_run`, not part of normal suites; it is not waste.
- Verification work: T-07's integration run plus real corpus scan, T-09's dry-run/layout checks, and T-12's runner/layout checks are one-shot boundary evidence. The deliberate unit/integration coverage in the changed test files was not classified as wasted suite execution.
- Retained scope: the validator retains no closure-backed or long-lived object graph. Its lists and parsed YAML exist only for a hook/check process lifetime.

## Findings

`findings: []`
