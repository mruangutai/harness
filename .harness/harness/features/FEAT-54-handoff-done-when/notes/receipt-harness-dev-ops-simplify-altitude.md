# ALTITUDE review — FEAT-54-handoff-done-when

## Conclusion

One seam-placement finding: the new shared validator earns its depth and is exercised through its public interface, but `check-domain.sh` retains a second authority for whether `## Done when` exists.

## Scope

Read-only review of `b7956fc4` through current HEAD plus working-tree changes, restricted to the task-declared files from `plan.yaml`: `.claude/skills/harness/bin/handoff_done_when.py`, `.claude/skills/harness/bin/check-domain.sh`, `.claude/skills/harness/bin/check-state.sh`, `.claude/skills/harness/templates/HANDOFF.md`, `.claude/skills/harness/SKILL.md`, `.harness/harness.json`, `.harness/harness/docs/DECISIONS.md`, `.harness/harness/docs/DECISIONS-INDEX.md`, `tests/unit/test-handoff-done-when.py`, `tests/integration/test-check-domain.py`, `tests/integration/test-check-state.py`, `tests/manual/probe-handoff-comprehension.py`, and `tests/integration/test-run-unit-tests-kinds.py`; plus active handoffs `notes/handoff-build.md` and `notes/handoff-plan.md`. Orchestration ledgers, run state, receipts other than this one, research records, and QA evidence were excluded.

The deletion test supports the new module: deleting `handoff_done_when.py` would redistribute block grammar and pointer semantics across both write-time and persisted gates. Unit tests call `problems()` as the interface, while integration tests cross the real `check-domain.sh` and `check-state.sh` seams. No resource adapter or adapter-lifetime obligation was introduced.

## Findings

- file: `.claude/skills/harness/bin/check-domain.sh`
  line: 1554
  summary: `check-domain.sh` duplicates the shared module's ownership of `## Done when` presence.
  concrete_cost: A missing section is evaluated by both the caller's five-heading list and `handoff_done_when.problems()` (`handoff_done_when.py:107-110`), so the write gate can emit two diagnoses for one defect and any future section-name or presence-policy change must update two authorities; `check-state.sh:1212-1251` already demonstrates the cleaner split by retaining local narrative-heading checks while delegating the Done when block to the module.
  alternative: Keep only the four narrative headings in the caller's local required-section check and let `handoff_done_when.problems()` own Done when presence and block validation; fold-in
  recommendation: fold-in
