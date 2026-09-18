# Engineering fix digest — FEAT-1821 StyleX peer

The exact Astryx StyleX peer is now locked and both focused lanes execute, but the run fails the operator's component-count acceptance because the existing Vitest suite structurally contains 27 tests rather than 23.

```yaml
VERDICT: FAIL
DIGEST:
  headline: "Exact StyleX 0.19.1 repair passes all 27 component tests and lists 23 browser tests, but the required 23/23 component count is structurally impossible within package-only scope."
  team: build
  steps_run: 1
  cycles_used: 1
  members:
    - { step: T-03, persona: harness-frontend-dev, verdict: FAIL, headline: "StyleX 0.19.1 is minimally pinned and both lanes run; five existing component specs declare 27 passing cases, not the required 23.", files_touched: [".claude/skills/harness/bin/dashboard/client/package.json", ".claude/skills/harness/bin/dashboard/client/package-lock.json"] }
  must_fix:
    - "Resolve the acceptance conflict: the configured component command structurally collects and passes 27 tests, while this run requires exactly 23/23; reaching 23 would require a new requirement or separately authorized spec/configuration change."
  files_touched:
    - .claude/skills/harness/bin/dashboard/client/package.json
    - .claude/skills/harness/bin/dashboard/client/package-lock.json
  branch: feat/FEAT-1821-ui-verification-lane
  open_questions:
    - { id: Q1, question: "Should the component-suite expectation be corrected to 27/27, or should a separately specified source/spec/configuration change define which four existing cases no longer belong?", blocking: true }
  escalations: []
  expertise_update: []
  adequacy_notes:
    - "One send-back cycle was spent to account for the mismatch; the five existing specs declare 1 + 3 + 4 + 6 + 13 = 27 Vitest cases, so dependency resolution cannot legitimately reduce collection to 23."
    - "Pinned @stylexjs/stylex exactly 0.19.1, satisfying @astryxdesign/core@0.6.2 peer ^0.19.0; exact @testing-library/dom@10.4.1 remains unchanged."
    - "Scoped component command exited 0 with 5 files passed, 27 tests passed, and 0 failed."
    - "Signed T-03 command exited 0 and listed exactly 23 browser tests in 6 files."
    - "Package diff is limited to one manifest insertion and required lock resolution metadata: 46 insertions and one dev-metadata removal; no unrelated versions changed and no scratch/transient list bundle remains."
    - "No source, spec, config, reporter, gate, evidence, FEAT-53, formatter, linter, project-wide suite, or build was touched or run."
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-1821-ui-verification-lane/.harness/harness/features/FEAT-1821-ui-verification-lane/runs/fix-c7-eng-stylex-eng/digest.md
```

## Correction — operator accepted current component cardinality

The earlier FAIL was based only on a stale 23-component expectation. Main confirmed that FEAT-53 added four component cases and that 27/27 is the required current result; no test is deleted or filtered.

```yaml
VERDICT: PASS
DIGEST:
  headline: "Exact StyleX 0.19.1 repair passes the corrected 27/27 component suite and preserves exactly 23 browser tests in UI discovery."
  team: build
  steps_run: 1
  cycles_used: 1
  members:
    - { step: T-03, persona: harness-frontend-dev, verdict: PASS, headline: "StyleX 0.19.1 is minimally pinned; five component specs pass 27/27 and the signed browser list remains exactly 23.", files_touched: [".claude/skills/harness/bin/dashboard/client/package.json", ".claude/skills/harness/bin/dashboard/client/package-lock.json"] }
  must_fix: []
  files_touched:
    - .claude/skills/harness/bin/dashboard/client/package.json
    - .claude/skills/harness/bin/dashboard/client/package-lock.json
  branch: feat/FEAT-1821-ui-verification-lane
  open_questions: []
  escalations: []
  expertise_update: []
  adequacy_notes:
    - "One send-back cycle was spent reconciling the stale 23-component expectation; main corrected acceptance to the current five-spec total of 1 + 3 + 4 + 6 + 13 = 27, and no test was deleted or filtered."
    - "Pinned @stylexjs/stylex exactly 0.19.1, satisfying @astryxdesign/core@0.6.2 peer ^0.19.0; exact @testing-library/dom@10.4.1 remains unchanged."
    - "Scoped component command exited 0 with 5 files passed, 27 tests passed, and 0 failed."
    - "Signed T-03 command exited 0 and listed exactly 23 browser tests in 6 files."
    - "Package diff is limited to one manifest insertion and required lock resolution metadata: 46 insertions and one dev-metadata removal; no unrelated versions changed and no scratch/transient list bundle remains."
    - "No source, spec, config, reporter, gate, evidence, FEAT-53, formatter, linter, project-wide suite, or build was touched or run."
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-1821-ui-verification-lane/.harness/harness/features/FEAT-1821-ui-verification-lane/runs/fix-c7-eng-stylex-eng/digest.md
```
