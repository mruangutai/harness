# UI review — FEAT-1928 — c3

**FAIL: newly authored operator instructions fail normal-text contrast in both themes.**

Reviewed immutable `b8e9f9c8f451cfe4b4e211eb97093525b7872c1b..828b3605d6334b96a6d21bfc8f93140b6b26a9c2`, using commit-object diffs, not HEAD. Read approved BRIEF, signed plan files/traces/change types/verification, and build handoff; its conclusions and counts are not evidence for this review.

## Scope and measured evidence

- Full census: 403 changed objects (`git diff --name-status`, complete output inspected). One HTML surface: `.harness/harness/docs/org.html`; no CSS/SCSS/LESS/JSX/TSX/Vue/Svelte/SVG changed objects. Remaining objects are enforcement/runtime code, tests, schemas, instructions, doctrine, or feature records/evidence, not additional rendered surfaces.
- **org.html is in scope:** it renders operator-facing digest instructions and an example; its provenance footer at line 363 says generated from SPEC, but neither makes this a disposable ship-review report nor prohibits editing, and signed T-03 explicitly authors its current prescriptive content.
- No feature DESIGN.md or approved prototype exists in the pinned feature-object listing. Existing inline design remains unchanged: card padding 14px/16px, code 12.5px/1.65, paragraph width 66ch, 10px paragraph separation, automatic and explicit light/dark tokens. New content follows those values; accessibility remains independently binding.
- SC-08 inspection, UI slice: `org.html:257–291` replaces the live text template with an object example and describes strict injection and validator-owned fenced durable output. This is not an all-repository SC-08 certification; code-review/goalcheck own that census.

## F-UI-01 — high / substance / task

**Owning task:** T-03; `change_type: docs`; `execution_mode: team`; `execution_agent: harness-documentor`; **original severity:** high; **raising reader:** ui-reviewer.

**Exact pinned path:** `828b3605:.harness/harness/docs/org.html:273–291` (new/replaced instructions), with unchanged styling at `:4,11,18,24,31–34,47`. The new schema, retry, and artifact-recovery paragraphs use `.sub`: 12.5px normal text, `--ink-3` on `--paper`. WCAG AA normal-text requirement is at least 4.5:1; actual light `#7c8798/#f7f8fa` is **3.421:1**, dark `#6b7688/#0c0f14` is **4.179:1**. Both automatic and explicit theme branches assign these same pairs.

**Consumer-visible reproduction:** open the pinned reference, navigate to “The digest,” and select either theme; the new essential operator instructions inherit insufficient contrast. Ratios were independently calculated from sRGB relative luminance with a Python arithmetic-only command; no browser, tests, validators under review, or suites were run. The low-contrast utility predates this change, but the newly added hook and artifact paragraphs are new affected consumers; this finding does not demand recoloring unrelated existing surfaces.

**Acceptance:** the changed digest instructions must reach at least 4.5:1 against their actual background in both themes, without losing the object example or refusal/recovery content. Prefer a local readable paragraph treatment using existing body-text tokens rather than a global palette change. Main should measure resulting contrast and perform the rendered check.

## Boundaries

Reading order remains heading → literal example → schema requirements → retry behavior → durable artifact behavior; PASS is also spelled out, not color-only. No controls, async state flips, focus transitions, loading/empty/error widgets, or dynamic collection states were added. The existing horizontal-overflow container is retained; **rendered-size/layout and keyboard access to overflow are not verifiable from source — human or UAT check required.** No independent assertion of pixel fidelity or browser accessibility is made. No source/test/doc changes or suites; only this report was written.

```yaml
VERDICT: FAIL
DIGEST:
  headline: New operator digest instructions fail text contrast in both themes.
  mode: B
  in_scope: true
  severity_max: high
  findings:
    - kind: substance
      scope: task
      severity: high
      reader: ui-reviewer
      summary: F-UI-01 — T-03 new digest instructions have 3.421:1 light and 4.179:1 dark contrast, below 4.5:1.
      why: 'Pinned 828b3605:.harness/harness/docs/org.html:273–291 uses the 12.5px .sub rule at :47 and tokens at :4,11,18,24. Task T-03, change_type docs, execution_mode team, execution_agent harness-documentor; original severity high. Reproduce by opening the digest section in either theme. Acceptance: changed instructions reach at least 4.5:1 in both themes with contract/recovery content preserved; no unrelated global restyle required.'
  must_fix:
    - F-UI-01 — Make the newly authored digest instructions readable at WCAG AA normal-text contrast in light and dark themes.
  states_unspecified: []
  contract_violations: []
  a11y:
    - F-UI-01 — Newly authored normal-size operator text fails WCAG AA contrast in both themes.
  open_questions: []
  files_touched: []
  expertise_update: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-1928-digest-object-contract/.harness/harness/features/FEAT-1928-digest-object-contract/notes/review-harness-ui-reviewer-c3.md
```
