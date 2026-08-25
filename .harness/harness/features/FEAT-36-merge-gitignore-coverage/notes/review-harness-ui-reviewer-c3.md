# UI review — FEAT-36 merge-gitignore coverage — c3

**BLUF: PASS.** The generated ship-review reading surface was inspected at the exact pinned tree. FEAT-36 introduces no UI requirement or UI regression; the one measured accessibility defect is the operator-ruled, pre-existing shared-renderer contrast concern and is non-gating for this feature.

## Measured scope and provenance

- Review SHA: `be27d99454352e581fdf7cbace20fb52d0f45133`; mode B; `in_scope: true` because the dispatch explicitly places the generated operator reading surface in this review.
- Artifact inspected: `.harness/harness/features/FEAT-36-merge-gitignore-coverage/notes/ship-review-c1.html` (13,026 bytes). It is a tracked object present at the review SHA, added on the feature range, not an uncommitted HTML edit. Its last path commit is `03c5903feecaac2a765b3ec54a9c18cddd022ca5`.
- The only pre-review working-tree trace edit observed was `feature.json`, changing `review_sha` from `f494553...` to `be27d994...`; it was excluded from the pinned-content judgment. The HTML body itself still identifies `f494553...` as its reviewed pin, so it is the extant reading surface to audit, not evidence that its narrative was regenerated for c3.
- The substantive feature delta is a behavioral test plus integration registration/configuration and the operator ruling. `merge-gitignore.sh` and the shared `render-brief.py` are unchanged from base `0fa8f336...` to the review SHA. BRIEF REQ-01–REQ-05 and SC-01–SC-06, and plan task `T-01`, specify behavioral coverage rather than a UI contract.
- `T-01` carries the exact verify command `python3 .agents/skills/harness/bin/test-merge-gitignore.py && .agents/skills/harness/bin/run-unit-tests.sh --kind all`; it was inspected but not run under this UI-only dispatch.

## Source-level surface audit

- **Readability/layout:** the source sets `16px/1.65` body text, a `56rem` page maximum, `65ch` prose lines, responsive page padding, and local horizontal scrolling for wide tables. This is a coherent reading treatment in source. Rendered wrapping, browser behavior, and actual pixel size were not verifiable here; human/UAT eyes would be required for those dimensions.
- **Accessibility structure:** `html lang="en"`, a descriptive `title`, one `h1` followed by eight `h2` sections, and three tables each with `thead`/`th` structure are present. The document is static: no links, buttons, scripts, or focus-changing state transitions exist, so keyboard reachability, focus preservation, loading, error, empty, and dynamic-state checks are not applicable. A global `:focus-visible` rule is present for any future focusable content.
- **Light/dark parity:** light and dark token sets exist both for OS preference and explicit `data-theme` overrides; reduced-motion handling is also declared. Measured primary/accent text contrast is sound (`--slate` on paper: 5.33:1 light / 7.50:1 dark; `--accent` on paper: 6.81:1 light / 7.99:1 dark). There is no in-document theme-toggle control; the default follows the OS, and the contract does not require a toggle.
- **Operator-ruled advisory:** light `--quiet: #7d8b99` measures 3.39:1 on `#fbfcfd` and 3.16:1 on `#f1f4f7`, affecting 10–11px metadata/table-header text. Dark quiet text measures 4.86:1 on paper and 4.43:1 on sunk. This is accessibility-relevant, but `notes/operator-ruling-rendered-review-scope.md` explicitly classifies the shared, pre-existing `render-brief.py` concern as outside FEAT-36 and non-gating. No renderer, test, or generated-HTML remedy is proposed or performed.

No in-scope contract violation or must-fix was found. No QA command, formatter, linter, build, or unrelated test was run.

```yaml
VERDICT: PASS
DIGEST:
  headline: "The pinned generated reading surface has no FEAT-36 UI regression; the measured shared-renderer contrast concern is operator-ruled out of scope and non-gating."
  mode: B
  in_scope: true
  severity_max: info
  findings: 0
  must_fix: []
  states_unspecified: []
  contract_violations: []
  a11y: []
  artifact_inspected: .harness/harness/features/FEAT-36-merge-gitignore-coverage/notes/ship-review-c1.html
  artifact_disposition: "Tracked and present at be27d994; source body names the earlier f494553 review pin, so it was audited as the extant surface rather than treated as regenerated c3 evidence."
  light_dark_observation: "Both theme token sets and OS/attribute selection exist; primary and accent text pass source-level contrast measurement in both themes."
  advisory_out_of_scope:
    - "Pre-existing light --quiet contrast is 3.39:1 on paper and 3.16:1 on sunk; operator ruling makes renderer/HTML rework non-gating and out of FEAT-36 scope."
    - "Rendered-size/layout is not verifiable from source; human or UAT check is required if visual confirmation is desired."
  open_questions: []
  files_touched: [.harness/harness/features/FEAT-36-merge-gitignore-coverage/notes/review-harness-ui-reviewer-c3.md]
  expertise_update: []
artifact: .harness/harness/features/FEAT-36-merge-gitignore-coverage/notes/review-harness-ui-reviewer-c3.md
```
