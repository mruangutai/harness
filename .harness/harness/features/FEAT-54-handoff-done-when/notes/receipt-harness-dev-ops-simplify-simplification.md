# FEAT-54 simplification assessment

## Scope

Assessed the task-declared source, test, config, and docs changes from `b7956fc4` through current HEAD plus working-tree changes: `.claude/skills/harness/bin/{handoff_done_when.py,check-domain.sh,check-state.sh,run-unit-tests.sh}`, `.claude/skills/harness/{SKILL.md,templates/HANDOFF.md}`, `.harness/harness.json`, `.harness/harness/docs/{DECISIONS.md,DECISIONS-INDEX.md}`, `tests/unit/test-handoff-done-when.py`, `tests/integration/{test-check-domain.py,test-check-state.py,test-run-unit-tests-kinds.py}`, and `tests/manual/probe-handoff-comprehension.py`. Also assessed active FEAT-54 handoff notes `notes/handoff-plan.md` and `notes/handoff-build.md`. Excluded orchestration ledgers, run state, and QA evidence. Settled contract, baseline, resolution split, probe status/routing, and absence of a per-section cap were not reconsidered.

## Findings

1. **File/line:** `.claude/skills/harness/bin/check-domain.sh:1554-1567`
   **Summary:** The write gate independently checks `## Done when` presence and then asks `handoff_done_when.problems()` to check the same presence again.
   **Concrete cost:** A missing section produces two differently worded violations, and the fifth-heading rule now has two enforcement spellings in one call path that must remain synchronized; changing either message or section spelling can make the gate disagree with itself.
   **Alternative:** Keep the existing required-heading check for the four narrative sections and let `handoff_done_when.problems()` exclusively enforce `## Done when`; this preserves the same refusal and all existing behavioral assertions while removing the duplicate diagnostic.

2. **File/line:** `.claude/skills/harness/bin/handoff_done_when.py:10-15,35-40,62-99`
   **Summary:** Authority type is encoded three times: in `LEGAL_PREFIXES`, in four regexes, and by reclassifying the already matched pointer with `startswith()` inside `_resolve()`.
   **Concrete cost:** Adding or renaming a type requires synchronized edits across three structures; a missed edit can advertise a prefix that parses but resolves through the wrong branch, or parse a type that the refusal message omits.
   **Alternative:** Define one ordered grammar table of `(prefix, regex)` entries, have `_grammar()` return the matched prefix with its match, derive the legal-prefix list from that table, and branch `_resolve()` on the returned prefix. Resolution behavior and pointer grammar remain unchanged.

3. **File/line:** `tests/manual/probe-handoff-comprehension.py:52-54`
   **Summary:** `done_when_facts()` tests for a colon after already requiring the line to start with `Scope:` or `Authority:`.
   **Concrete cost:** The redundant conjunct adds a second, impossible-to-differ condition to the parser and suggests colon absence is a meaningful case when the prefix test has already ruled it out.
   **Alternative:** Keep only `if line.startswith(("Scope:", "Authority:"))`; `split(":", 1)` remains safe and observable behavior is identical.

No other simplification findings were identified in the scoped files or active handoff notes.
