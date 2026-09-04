# SIMPLIFICATION receipt — FEAT-54 validation repairs c2

Verdict: PASS

The seven scoped files contain no simplification issue that gates the validation repairs. Four behavior-preserving candidates remain advisory; the three on Main-authored enforcement/test surfaces are backlog-only, and the probe candidate is for its engineering owner to consider. No source was edited and no validation was run.

## Findings

- id: S-01
  file: `.claude/skills/harness/bin/check-domain.sh`
  line: 1547
  summary: The changed comment narrates the addition of `## Done when` instead of stating the current five-section contract directly.
  concrete_cost: The phrase “including ## Done when” duplicates the immediately adjacent `required` list and makes future heading changes require another prose edit.
  alternative: Replace lines 1547–1548 with a present-tense statement such as “DEC-159: the handoff note is five-section, hard-capped working memory for a successor.”
  disposition: advisory-only; Main-authored enforcement surface.

- id: S-02
  file: `tests/integration/test-check-domain.py`
  line: 4215
  summary: The “60-line boundary” and “no per-section cap” cases invoke the identical 60-line payload and assert the identical exit status.
  concrete_cost: One redundant hook subprocess runs on every integration-suite execution, while the two result rows cannot distinguish different regressions.
  alternative: Backlog either one assertion, or redesign the no-per-section-cap fixture so it independently discriminates a per-section cap without weakening the 60-line boundary case.
  disposition: advisory/backlog only; removing or weakening an individual assertion is prohibited, and this is a Main-authored direct test.

- id: S-03
  file: `tests/integration/test-check-state.py`
  line: 2271, 2285
  summary: Two pre-existing test docstrings still describe a four-heading handoff after the repaired contract became five sections.
  concrete_cost: The stale narration contradicts `HANDOFF_GOOD` and can lead a maintainer to preserve the wrong fixture shape during later edits.
  alternative: Change “four headings” to “five headings” in both docstrings; keep every assertion and fixture unchanged.
  disposition: advisory-only; Main-authored direct test.

- id: S-04
  file: `tests/manual/probe-handoff-comprehension.py`
  line: 227
  summary: `if not evidence` is unreachable because the preceding comprehension always creates one entry for each of the two constant `ARMS`.
  concrete_cost: The dead branch suggests a note can be skipped after measurement and adds a state the function cannot produce.
  alternative: Remove lines 227–228 and increment `measured` unconditionally after `measure_note`.
  disposition: candidate for the engineering owner; behavior and bounded-input safeguards remain unchanged.

## Scope checked

- `.claude/skills/harness/bin/check-domain.sh`
- `.claude/skills/harness/bin/handoff_done_when.py`
- `tests/integration/test-check-domain.py`
- `tests/integration/test-check-state.py`
- `tests/unit/test-handoff-done-when.py`
- `tests/manual/probe-handoff-comprehension.py`
- `tests/unit/test-probe-handoff-comprehension.py`
