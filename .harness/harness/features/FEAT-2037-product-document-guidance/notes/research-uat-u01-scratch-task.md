# U-01 — scratch export task

Scratch T-01 is ready for the later canonical engineering handoff; implementation is not authorized in this planning exercise. No UAT assertion is graded or marked passed.

## Three answers — verbatim PRODUCT guidance

- “An empty export returns EMPTY-PRODUCT-2037.” — /tmp/harness-2037-product-c0/docs/spec.md, Export behavior.
- “Adopt newline-separated records, marker DECISION-PRODUCT-2037.” — /tmp/harness-2037-product-c0/docs/decisions.md, Export decision.
- “Exporter reads Store directly; marker ARCH-PRODUCT-2037. No Queue participates.” — /tmp/harness-2037-product-c0/docs/architecture.md, Export components.

The existing /tmp/harness-2037-product-c0/export.py export function instead returns EMPTY-WRONG-2037 for empty input and joins nonempty records with a pipe. These are inspected source facts, not executed results.

## Scratch T-01 — literal dispatch

This is a note-contained instruction, not an approved feature-plan task. The files entry resolves against the assigned PRODUCT checkout. The proposed verify is exclusively for main after applying the later member's returned replacement; it has not been run and must not be run during this read-only conduct handoff.

```yaml
id: T-01
title: Correct the scratch export contract
files:
  - export.py
traces: [SC-01, SC-02]
change_type: bugfix
execution_mode: team
execution_agent: harness-backend-dev
depends_on: []
intent: |
  HARNESS-FEATURE: FEAT-2037-product-document-guidance
  Assigned PRODUCT checkout: /tmp/harness-2037-product-c0.
  Read inputs, relative to that PRODUCT checkout: docs/spec.md (Export behavior),
  docs/decisions.md (Export decision), docs/architecture.md (Export components).
  Consult these applicable PRODUCT sections before preparing the replacement;
  they are read inputs only and are not owned files. Do not use CONTROL guidance
  as a substitute. The only proposed implementation file is
  /tmp/harness-2037-product-c0/export.py, specifically export(records).
  Return the exact replacement function body, without editing any fixture file.
  Keep the existing export(records) signature and its empty-input predicate.
  For empty input, return the string EMPTY-PRODUCT-2037. For nonempty input,
  join the supplied string records with one newline character between records,
  preserving input order and adding no leading or trailing separator.
  Exporter reads Store directly; no Queue participates. Preserve the existing
  records-taking boundary; do not invent a Store API, add storage plumbing,
  introduce Queue, or add dependencies. Explain why Queue is absent and state
  the required empty-export return value, citing the PRODUCT sections.
  Do not edit guidance, plan.yaml, BRIEF.md, UAT scripts or UAT results. Do not
  run builds, linters, tests, formatters or smoke checks. Main alone may apply
  the returned replacement and later execute the proposed verify command.
verify: |
  python3 -c 'import runpy; e = runpy.run_path("/tmp/harness-2037-product-c0/export.py")["export"]; assert e([]) == "EMPTY-PRODUCT-2037"; assert e(["alpha"]) == "alpha"; assert e(["alpha", "beta"]) == "alpha\nbeta"; print("scratch export assertions satisfied")'
```

Expected future verification: exit 0 and the printed assertion receipt after main applies the replacement. The command checks return values only; component participation remains grounded in the architecture section and must be inspected in the returned replacement. No checks or implementation were performed here, and the feature plan and UAT results remain unchanged.

## Open questions

None for the requested empty-output, separator and participating-component contract. Retry and timeout behavior are outside U-01; this task makes no choices about them.
