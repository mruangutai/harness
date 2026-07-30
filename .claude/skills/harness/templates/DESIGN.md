<!-- TEMPLATE — harness-visual-designer owns this file. It is the design CONTRACT:
     frontend-dev implements against it and ui-reviewer audits against it, so an
     unstated value is one each of them will invent differently.

     Established by init's design pass; skip the file entirely for a project
     with no user-facing surface (harness-init has the why). -->

# DESIGN — <project name>

## Substrate

<Per the Product team convention in team-config.yaml, UI implements against the
Astryx design system (`@astryxdesign/core`, pinned). Name the pinned version and
say what this project adds on top. Introducing a second component substrate
requires a PLAN ## Decisions entry.>

- system: @astryxdesign/core@<pinned version>
- provisioned: <yes | no — dev-ops verified this at init>

## Palette

<Every token in BOTH themes. A single-theme palette guarantees a dark-mode
regression that ui-reviewer will find late.>

| Token | Light | Dark | Used for |
|---|---|---|---|
| bg | <#hex> | <#hex> | page background |
| surface | <#hex> | <#hex> | cards, panels |
| text | <#hex> | <#hex> | body copy |
| text-muted | <#hex> | <#hex> | secondary copy |
| accent | <#hex> | <#hex> | primary action |
| border | <#hex> | <#hex> | dividers, inputs |
| danger | <#hex> | <#hex> | destructive, errors |

- contrast: <state the minimum ratio met for body text in both themes, e.g. WCAG AA 4.5:1>

## Type

- family: <body> / <mono>
- scale: <e.g. 12 / 14 / 16 / 20 / 24 / 32 — the whole ramp, no in-between sizes>
- weights: <the two or three actually used>

## Spacing and layout

- unit: <base, e.g. 4px — all spacing is a multiple>
- radius: <values>
- container: <max width, gutters>
- breakpoints: <the ones this project actually implements>

## Component direction

<How things should feel and behave, stated so a reviewer can call a violation.
"Dense over airy." "Destructive actions always confirm." "No modal deeper than
one level." Vague direction is unreviewable direction.>

- <principle>

## Out of scope

<What this contract deliberately does not cover, so its absence is not read as an
oversight.>

- <item>
