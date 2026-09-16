# UI Reviewer — cycle 2 remedy audit — BUG-285-yaml-loader-pin

## BLUF

PASS. The remedy has no rendered UI, theme, accessibility-semantic, or `DESIGN.md` surface. It does change one operator-facing terminal state, so that narrow presentation surface is in scope: a non-object `factory` member now emits a plain stderr refusal naming `feature.json`, the invalid shape, and why execution cannot safely continue. The message is legible and the prior cycle's no-finding result is **CLOSED (still clean)** rather than sustained as a defect.

## Measured remedy census

- `git diff --name-status 592e6412..ab0c9987` contains **8 paths**: **3 Python** and **5 Markdown**. The only product-code change is `.claude/skills/harness/bin/factory_decompose.py`; the other two Python paths are integration tests, and the five Markdown paths are review/receipt notes.
- A rendered-surface and design-contract path check across the pinned remedy diff for `DESIGN.md`, HTML, CSS, SCSS, TSX, JSX, Vue, Svelte, and Less returns **zero paths**.
- The production diff is 11 insertions and 7 deletions in `load_factory`. It changes no layout, colour, typography, focus handling, keyboard interaction, hit target, reading order, or light/dark theme value.

## Narrow terminal-presentation audit

Input: a present, parseable `feature.json` whose `factory` member is not a JSON object. Caller: `factory_decompose.py::load_factory`, reached by the `decompose` CLI. The remedy replaces silent empty-factory continuation with `factory_cli.refuse(...)` and supplies the operator-facing explanation that the file "has a factory key that is not a JSON object, so what is already mirrored cannot be known".

Observable result: the existing shared CLI message path emits a plain stderr refusal that identifies the invalid file through the `feature.json invalid` call, names the wrong shape, and explains the safety consequence. This is sufficient to diagnose the required repair (restore `factory` to an object) without colour-only meaning or a traceback. No presentation defect is present.

The other remedy behavior—coercing quoted numeric parent/issue members through `opt_int`—does not add or alter terminal presentation.

## Limits

No pixels or rendered layout exist in the remedy. Accessibility and theme parity are not applicable to this plain stderr-only change; no colour or visual-only state encoding is introduced.

## Findings

None. `must_fix: []`; `severity_max: none`.
