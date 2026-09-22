# Receipt — T-17 (main-session-direct): Mode B trace replay — 2026-09-19

fail-first: `python3 tests/unit/test-ui-reviewer-policy.py` at 5e4ae209 with the four new clauses in the test → nonzero, FAILED (8):
```
FAIL  Mode B carries traces-every-traced-record — pattern 'every traced record[^\\n]*`traced_check_ids`' not found
FAIL  mutant of traces-every-traced-record is rejected — mutation did not apply or detector still matched
FAIL  Mode B carries traces-opened-not-just-present — pattern 'open[^\\n]*`npx playwright show-trace`[^\\n]*filmstrip[^\\n]*DOM snapshot[^\\n]*assertion' not found
FAIL  mutant of traces-opened-not-just-present is rejected — mutation did not apply or detector still matched
FAIL  Mode B carries traces-cite-judged-step — pattern 'cite the exact (?:judged )?step' not found
FAIL  mutant of traces-cite-judged-step is rejected — mutation did not apply or detector still matched
FAIL  Mode B carries traces-still-only-is-fail — pattern '[Aa] traced check graded from its still[^\\n]*(?:is|are) (?:a )?`?FAIL`?' not found
FAILED (7)
```
Post-fix (agent text extended, one clause per line): PASS, 50 ok — 18 clauses × (present + mutant rejected) + shape checks. Mutants rejected: every trace → sample; open → file-presence; step citation → outcome summary; still-only → acceptable.
SC-08. DEC-233: only .omp/agents/harness-ui-reviewer.md exists; no adapter to regenerate (T-17 files/verify amended by pm at 9f3c9efc).
