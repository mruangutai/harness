# QA check — distill-apply verification, harness-validator-lead.md

Verdict: PASS. File is format-clean; no pre-existing entry lost, altered, or reworded.

## 1. Directory gate

```
$ .claude/skills/harness/bin/check-expertise.sh .harness/expertise/
OK   .harness/expertise/harness-backend-dev.md
OK   .harness/expertise/harness-code-reviewer.md
OK   .harness/expertise/harness-dev-ops.md
FAIL .harness/expertise/harness-documentor.md
  - line 43: G-04 is 53 words — cap is 50; a rule, not a story
OK   .harness/expertise/harness-eng-lead.md
OK   .harness/expertise/harness-orchestrator.md
OK   .harness/expertise/harness-pm.md
OK   .harness/expertise/harness-product-lead.md
OK   .harness/expertise/harness-qa.md
OK   .harness/expertise/harness-security-reviewer.md
OK   .harness/expertise/harness-ui-reviewer.md
OK   .harness/expertise/harness-validator-lead.md
OK   .harness/expertise/harness-visual-designer.md
EXIT:1
```

Failure set matches expectation exactly: only `harness-documentor.md` fails (G-04, 53 words vs 50-word
cap). `harness-validator-lead.md` reports `OK`. Not our fix — pre-existing, another squad's file, on
the backlog. No edit made or proposed.

## 2. Single-file gate

```
$ .claude/skills/harness/bin/check-expertise.sh .harness/expertise/harness-validator-lead.md
OK   .harness/expertise/harness-validator-lead.md
EXIT:0
```

## 3. Per-section counts (from the file, counted with awk/grep)

Total lines: 55

- `## Patterns` (7 entries): P-01, P-02, P-03, P-04, P-05, P-06, P-07
- `## Gotchas` (6 entries): G-01, G-02, G-03, G-04, G-05, G-06
- `## Outcomes` (2 entries): O-01, O-02
- `## Open` (0 entries): none

## 4. BEFORE state and DEC-125 wipe check

BEFORE (`git show HEAD:.harness/expertise/harness-validator-lead.md`) confirmed independently:
Patterns 7 (P-01..P-07), Gotchas 3 (G-01..G-03), Outcomes 0, Open 1 (OQ-01) — matches the stated
baseline exactly.

`git diff -- .harness/expertise/harness-validator-lead.md` shows:

- P-01, P-02, P-03, P-05, P-06, P-07, G-01, G-02, G-03: **no `-` lines at all** — untouched, not even
  re-wrapped.
- P-04: text changed (old "grep for the whole class" entry replaced by new "sweep the surface for
  further instances" entry) — as directed.
- OQ-01: removed, `## Open` section now empty — as directed.
- Exactly three new entries added to Gotchas: G-04, G-05, G-06.
- Exactly two new entries added to Outcomes: O-01, O-02.
- Nothing else changed (no other section touched, no reordering, no dropped entry).

No pre-existing entry was lost, altered, or silently reworded. The write behaved as a correct
read-modify-write.

## SC evidence

N/A — this is a measurement task on an already-written Expertise file, not a feature with SCs to
gate against.
