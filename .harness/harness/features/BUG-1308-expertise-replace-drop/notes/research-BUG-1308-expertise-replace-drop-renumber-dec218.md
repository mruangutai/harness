# BUG-1308 amendment — DEC-216 renumbered to DEC-218

**Done. All ten live references moved to DEC-218 across `plan.yaml` and `BRIEF.md`; the one excluded
cycle-1 panel-finding summary is byte-identical; `approval:` is unchanged (same sha256 before and
after); the plan parses and `check-plan-routes.py` exits 0.** No commit, no linters, no project-wide run.

## Site-by-site

| Site | Route | Status |
|---|---|---|
| `plan.yaml` D-11 `choice` | `amend` CAS | done |
| `plan.yaml` D-13 `choice` | `amend` CAS | done |
| `plan.yaml` T-04 `title` | `amend` CAS | done |
| `plan.yaml` T-04 `verify` (3 occurrences: `sed` anchor, `MISSING:` echo, index grep) | `amend` CAS | done — 0 `216` remain in block |
| `plan.yaml` T-04 `intent` item 2 (2 occurrences) | `amend` CAS | done |
| `plan.yaml` T-04 `intent` item 3 (2 occurrences) | `amend` CAS | done |
| `BRIEF.md` SC-10 | Edit | done |
| `plan.yaml` D-16 (new decision) | `apply --proposal -` → `ADDED D-16` | done |
| `plan.yaml` panel finding summary (now line 246) | — | **excluded, untouched** |

The dispatch expected 4 `216`s in the `verify:` block; the file carried 3 (the index grep line has
one, not two). The binding requirement — zero `216` in the block — is met either way.

Folded scalars D-11/D-13 were re-emitted by `amend` as one long line on first pass; I re-amended
with the original line wrapping so the committed diff is the digits and D-16 only. A `>-` fold makes
both renderings the same loaded value.

## Acceptance — actual output

1. `grep -n 'DEC-216' plan.yaml BRIEF.md` → exactly one line:
   `plan.yaml:246:      sentence, T-04 omits SPEC's 10/11/12 and DEC-216's Over/Because/Tradeoff content.`
2. `grep -c 'DEC-218' plan.yaml` → `11`
3. `grep -n 'DEC-218' BRIEF.md` → `115:- SC-10: ... carries a \`DEC-218\` row whose hand-written ruling` (one hit)
4. T-04 `verify:` read back via `plan-merge.py amend --show` (sha256 `052ccdb6…`) — see DIGEST for the
   full block. The literal `replace and drop through the ops subcommand` is unchanged; `DEC-66`,
   `DEC-95`, `DEC-145` unchanged.
5. `sed -n '/^approval:/,/^[a-z]/p' plan.yaml | sha256sum` → `03adcfe71f22a4a3d46ce8b9c81cf2f157728883e02d1c7f2b82b5bd169825d1`
   **before and after**. `plan-merge` printed only `AMENDED`/`APPLIED`/`ADDED D-16` — no APPROVAL line.
6. `python3 -c "import yaml; yaml.safe_load(...)"` → `parsed ok; decisions= 16 tasks= 4`;
   `check-plan-routes.py plan.yaml` → `0 violation(s) across 1 plan(s)`, exit 0.

## Ambiguity raised, not guessed

The dispatched D-16 wording ("DEC-218 rather than DEC-216, because BUG-1303 landed DEC-216 and
DEC-217 first") would itself have put two or three more literal `DEC-216` tokens in `plan.yaml`,
contradicting acceptance criterion 1, which admits exactly one and calls any other hit an incomplete
amendment. I honoured the falsifiable gate: D-16 states the same facts using the bare numerals
`216`/`217` and names DEC-218 and DEC-215 in full, so no new `DEC-216` token exists. Substance,
keys, ordering and indentation match the other D-NN entries; `dec: none`.
