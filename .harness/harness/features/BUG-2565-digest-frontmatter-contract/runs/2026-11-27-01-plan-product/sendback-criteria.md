# Send-back criteria — draft step (written before return, P-05)

Send the draft back (one loop) if any holds:
1. Any task lacks `execution_mode: main-session-direct`.
2. No SC asserts that a harness-* task dispatch neither exposes nor is refused for outputSchema/schemaMode (task item schema = agent, name, solutionSpace, task) AND that the injection/refusal code (SCHEMA_CONTROLS, isInjectedCopy, schemaControlRefusal, withDigestSchemas) is deleted.
3. No SC asserts validate-digest.py-cannot-run → yield refused; or its task is not ordered at/before the frontmatter-route task (depends_on).
4. No SC asserts generated frontmatter `output:` drift from schemas/digest/*.json fails check-omp-port.py, with schemas/digest/*.json the only edited source; check-omp-port.py's task.structured==true rule (:96-97) not reconciled.
5. Historical observation notes in a task's `files:` (they must not be rewritten), or #2566 stale-hook detection planned.
6. README/BUILD/DECISIONS contract text not owned by any task; `decisions_affected:` empty without justification given the DECISIONS "Dispatch owns schema delivery" paragraph.
7. The two "Not yet specified" items (retry-budget interaction, crash-vs-refuse child message) silently decided rather than carried as plan decisions/open questions.
8. `plan-merge.py check` not reported passing.
