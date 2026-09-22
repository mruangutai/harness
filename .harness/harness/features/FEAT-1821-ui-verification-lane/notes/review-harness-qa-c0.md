```yaml
VERDICT: BLOCKED
DIGEST:
  headline: "The pinned UI lane is structurally blocked: component loading is broken and committed FEAT-53 evidence is stale against the review pin; its intentional product RED is preserved."
  reviewed_sha: "711ba16227eda39ddb397ed574e4ca199fbc5984"
  suite: fail
  failures: 3
  matrix_ok: false
  required_kinds:
    - "unit (logic)"
    - "component (frontend)"
    - "ui (frontend + has_interaction_flow)"
  kinds:
    - kind: unit
      state: misconfigured
      cmd: "env -u HARNESS_AGENT_TYPE .agents/skills/harness/bin/run-unit-tests.py --kind unit"
      named_tests: 0
      evidence: "All named scripts shown passed, but the runner exited 1 because the concurrent configured component command changed dashboard/client/node_modules/.vite/vitest/.../results.json under its watched tree; no assertion failure was reported."
    - kind: component
      state: misconfigured
      cmd: "npm --prefix .claude/skills/harness/bin/dashboard/client run test"
      named_tests: 0
      evidence: "Vitest loaded five suites but each failed before collection with Cannot find module '@testing-library/dom' from @testing-library/react/dist/pure.js."
    - kind: ui
      state: missing
      cmd: "HARNESS_UI_FEATURE=FEAT-53-metrics-dashboard HARNESS_UI_RUN_ID=qa-c0-list npm --prefix .claude/skills/harness/bin/dashboard/client run test:ui -- --list"
      named_tests: 23
      evidence: "Exit 0; 23 tests in 6 files. The required committed-bundle gate below exits 1 structurally on stale served_bundle_commit, separately from product predicate RED."
  ui_contract:
    cmd: "python3 .claude/skills/harness/bin/ui_contract.py gate --design .harness/harness/features/FEAT-53-metrics-dashboard/DESIGN.md --results .harness/harness/features/FEAT-53-metrics-dashboard/runs/FEAT-1821-initial-red/ui/results.json --feature FEAT-53-metrics-dashboard --run-id FEAT-1821-initial-red --served-bundle-commit 711ba16227eda39ddb397ed574e4ca199fbc5984 --repo-root . --client-package .claude/skills/harness/bin/dashboard/client --changed .claude/skills/harness/bin/dashboard/client/e2e/colour-placement.e2e.spec.ts --changed .claude/skills/harness/bin/dashboard/client/e2e/contrast-hatch.e2e.spec.ts --changed .claude/skills/harness/bin/dashboard/client/e2e/geometry.e2e.spec.ts --changed .claude/skills/harness/bin/dashboard/client/e2e/tables-a11y.e2e.spec.ts --changed .claude/skills/harness/bin/dashboard/client/feat-53.e2e.spec.ts --changed .claude/skills/harness/bin/dashboard/client/ui-evidence.ts"
    status: fail
    evidence: "Exit 1: results served_bundle_commit is 0ef52107fde67b1f42cb51a16c773635dc73a408, not pin 711ba16227eda39ddb397ed574e4ca199fbc5984. The gate also reports the expected FEAT-53 predicate RED; results.json has 18 failed, 1 passed (SRC-TOKENS), and 4 inspection-evidence records, i.e. the documented 22 non-green executable predicate outcomes are product evidence, not this finding."
  sc_evidence:
    - { id: SC-01, test: ".claude/skills/harness/bin/dashboard/client/e2e/*.e2e.spec.ts: listed by configured UI command" }
    - { id: SC-02, test: ".claude/skills/harness/bin/dashboard/client/ui-evidence.ts:10-27" }
    - { id: SC-03, test: ".harness/harness/features/FEAT-53-metrics-dashboard/runs/FEAT-1821-initial-red/ui/results.json:2-1092" }
    - { id: SC-04, test: ".claude/skills/harness/bin/dashboard/client/feat-53.e2e.spec.ts:108-128" }
    - { id: SC-05, test: "tests/unit/test-ui-verification-contract.py:204-303" }
    - { id: SC-06, test: "tests/unit/test-ui-verification-contract.py:218-281" }
    - { id: SC-10, test: "tests/unit/test-ui-verification-contract.py:293-303; tests/unit/test-suite-layout.py:663-671" }
    - { id: SC-11, test: "tests/unit/test-ui-verification-contract.py:286-291" }
  fail_first:
    - { sc: SC-01, evidence: "runs/build-eng-t03-eng/digest.md:39 records the exact list command exiting 1 before test:ui existed." }
    - { sc: SC-02, evidence: "GAP — no pinned behavioral pre-fix WebP/results-record failure." }
    - { sc: SC-03, evidence: "GAP — no pinned pre-lane failing test receipt binds the committed initial RED bundle." }
    - { sc: SC-04, evidence: "GAP — no pinned pre-fix behavioral pixel-baseline exclusion failure." }
    - { sc: SC-05, evidence: "GAP — no pinned pre-fix failure for applicable-record/title/contract refusal." }
    - { sc: SC-06, evidence: "GAP — no pinned pre-fix failure for results schema, identity, or WebP contract." }
    - { sc: SC-10, evidence: "GAP — no pinned pre-fix failure of runner misconfiguration/contract blocking behavior." }
    - { sc: SC-11, evidence: "GAP — no pinned pre-fix failure showing a client change without every title is refused." }
  coverage_gaps:
    - "Component matrix kind cannot import @testing-library/react because @testing-library/dom is absent."
    - "Committed FEAT-53 result bundle is not bound to review SHA 711ba16227eda39ddb397ed574e4ca199fbc5984."
    - "SC-02 through SC-06 and SC-10 through SC-11 lack pinned fail-first evidence; SC-03 is also not shown failing before the lane existed."
  findings:
    - { kind: substance, severity: high, task: T-03, owner: harness-frontend-dev, summary: "Configured component coverage cannot load.", scenario: "Any frontend change requiring the matrix component kind stops before test collection because @testing-library/dom is absent, so the required component assertions never execute.", evidence: ".claude/skills/harness/bin/dashboard/client/package.json:21-30; configured component command output." }
    - { kind: substance, severity: high, task: T-06, owner: main-session-direct, summary: "Committed evidence is stale for the immutable review pin.", scenario: "A reviewer can consume a FEAT-53 run from ancestor 0ef5210 rather than the reviewed bundle and accept evidence that does not bind to the surface at 711ba16.", evidence: "results.json:6; ui_contract.py gate output; git merge-base --is-ancestor 0ef5210 711ba16 exit 0." }
    - { kind: form, severity: med, task: T-01, owner: main-session-direct, summary: "Pinned automated SC fail-first record is incomplete.", scenario: "A green future suite could be credited for SC-02..SC-06/SC-10/SC-11 without proof its named test discriminated the newly added behavior.", evidence: "BRIEF.md:19-40; no pinned receipt or run record located beyond SC-01's list-command red at runs/build-eng-t03-eng/digest.md:39." }
  open_questions: []
  files_touched: ["/Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-1821-ui-verification-lane/.harness/harness/features/FEAT-1821-ui-verification-lane/notes/review-harness-qa-c0.md"]
  expertise_update: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-1821-ui-verification-lane/.harness/harness/features/FEAT-1821-ui-verification-lane/notes/review-harness-qa-c0.md
```

# QA gate — pinned SHA 711ba16227eda39ddb397ed574e4ca199fbc5984

BLOCKED. Matrix inference over the feature diff is logic + frontend interaction flow + config/docs; the non-empty floor is unit, component, and ui. The UI list discovers all 23 applicable tests, but component loading is broken and the exact required ui-contract invocation refuses the committed bundle because its served-bundle pin is stale. The expected FEAT-53 RED remains evidence, not a lane defect.
