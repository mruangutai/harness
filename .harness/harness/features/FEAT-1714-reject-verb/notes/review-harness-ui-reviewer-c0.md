# UI review — FEAT-1714-reject-verb — cycle 0

## Verdict

PASS, advisory finding only. Reviewed exactly `origin/main...82bdef1a6f7cd89005f661a06296725f5b1ad9b1` (pin resolved byte-for-byte). The diff has no rendered UI, TUI, or `DESIGN.md`, but it does add an operator-facing terminal confirmation flow in `gh-sync.py reject`; that surface is in scope.

## Measured surface census

- Full pinned diff: 46 paths — 24 `.py`, 18 `.md`, 2 `.json`, 2 `.yaml`.
- Rendered-UI extension census (`html/htm/css/scss/sass/less/tsx/jsx/vue/svelte/svg`): **0 paths**.
- Direct pinned-object check: `.harness/harness/features/FEAT-1714-reject-verb/DESIGN.md` is absent.
- Markdown census: skills/contracts, decisions, and feature records only; none specifies rendered spacing, colour, typography, layout, focus, or interaction states.
- User-facing changed output: `.claude/skills/harness/bin/gh-sync.py:1805-1894,2338-2409` adds reject validation, dry-run confirmation, execution success/failure text, and usage; `.claude/skills/harness/bin/check-state.py:3017-3068` adds actionable INV-44 terminal diagnostics. Other Python changes are shared station vocabulary/logic or tests.
- The assigned BRIEF, plan decisions/tasks, feature metadata/state, build/plan handoffs, signed answers, all five receipts, goal-check note, and prior UI plan review present under the feature at the pin were inspected before grading.

## Finding

- **UI-01 — med · substance · ui-reviewer · T-02.** The dry-run does not show the exact comment/reason the operator is about to publish. **Failure scenario:** a stale or mistyped one-line reason file is supplied; the operator sees only `would post comment ... link parent ...` and confirms `--yes`, publishing text they were never shown. **Evidence:** `gh-sync.py:1813-1824` constructs the actual comment from the reason, but `gh-sync.py:1829-1848,1857-1862` builds and prints only a disposition summary. The approved T-02 contract says the no-`--yes` report prints the exact comment. This is advisory under `advisory_unless_high`; it is not an accessibility exclusion or high-severity blocker.

## Accessibility, interaction, and theme

The flow is plain sequential terminal text: no colour-only encoding, pointer targets, focus management, spatial navigation, or light/dark tokens. Errors use explicit `ERROR` text and remedies; dry-run actions use repeated `would` text, so state is not conveyed by colour. Accessibility and theme parity are therefore not applicable beyond terminal readability. Rendered-size/layout is not verifiable from source, but no rendered surface exists here.

## Dismissed candidates

- Successful comment/label/milestone writes are silent while failures are explicit (`gh-sync.py:1875-1892`): not filed because the approved contract requires a complete preflight report, not a verbose success transcript, and failure attribution remains readable.
- `T-NN is terminal — no sub-issue created` replaces the abandoned-specific wording (`gh-sync.py:1151-1153`): not filed because it accurately covers both shared terminal states and names the skipped action.
- INV-44 messages are long: not filed because each line identifies the violated dimension and a concrete remedy; no truncation or colour dependence is introduced.
- Working tree drift after the pin is limited to `STATE.md` and `feature.json`; production/output surfaces audited above are byte-identical to the pinned object.
