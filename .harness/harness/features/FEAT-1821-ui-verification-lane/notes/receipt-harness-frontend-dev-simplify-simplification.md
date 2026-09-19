# SIMPLIFICATION receipt — FEAT-1821

**Finding: one behavior-preserving simplification is available; no assertion need change.**

## Findings

1. **File / line:** `.claude/skills/harness/bin/dashboard/client/e2e/colour-placement.e2e.spec.ts:58-75` (duplicated capture implementations also at `contrast-hatch.e2e.spec.ts:37-54`, `geometry.e2e.spec.ts:24-41`, `keyboard.e2e.spec.ts:25-40`, and `tables-a11y.e2e.spec.ts:25-37`).
   **Summary:** Five near-identical `capture` helpers repeat the WebP capture, anchored evidence-path, duplicate-label, header-validation, and attachment pipeline.
   **Concrete cost:** A future evidence-protocol change requires five coordinated edits; the already divergent keyboard soft-assertion variant makes drift in reporting behavior more likely.
   **Alternative:** Extract one shared capture helper beside `ui-manifest.ts`, parameterized by `page`, `testInfo`, `check`, and label; preserve the exact rooted output path, duplicate refusal, RIFF/WEBP checks, and attachment name. This is behavior-preserving, does not remove or weaken an assertion, and is owned by `harness-frontend-dev`.

## Skipped candidates

- **Settled:** The signed 23-test split, exact titles/projects, `harness-ui-results/1` reporter/gate contract, CI Chromium install, Mode B evidence policy, active UI test kind, unchanged FEAT-53 evidence status, and 41 committed WebPs are expressly out of this pass.
- **Assertion-affecting:** The repeated `load` helpers in the same E2E files also encode per-suite assertion wording and strict/soft expectation choices; consolidating them would touch assertions, so it is not an apply candidate after QA.
- **False-positive:** `ui_contract.py`'s repeated manifest/result accounting is independently validating untrusted evidence at distinct contract boundaries, not accidental duplication to collapse.
- **Out-of-scope:** Plan/BRIEF and generated run/evidence records are not implementation simplification surfaces for this reader.
