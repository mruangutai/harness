# UI review — FEAT-25 claim feature root — Mode A (pre-build)

## Verdict: out of scope. No rendered UI surface in this feature.

## Census

**Feature directory enumerated** (`.harness/harness/features/FEAT-25-claim-feature-root/`):
`BRIEF.md`, `feature.json`, `plan.yaml`, `STATE.md`, `notes/research-FEAT-25-claim-feature-root.md`,
`runs/2026-08-18-1-product/{digest.md,state.yaml}`, `runs/2026-08-18-1-planreview-validator/state.yaml`.
No `notes/mockups/`, no `notes/prototypes/<FEAT>/`, no `DESIGN.md` anywhere in the tree — there is no
design contract for this role to judge, and none was expected: this is a bugfix to a path constant
and a CLI diagnostic, not a feature with a human-facing screen.

**Six surfaces named in `plan.yaml`'s `lanes.rows`** — all `file`-confirmed as plain Python:

- `.claude/skills/harness/bin/factory_claim.py`
- `.claude/skills/harness/bin/test-factory-claim.py`
- `.claude/skills/harness/bin/test-factory-integration.py`
- `.claude/skills/harness/bin/layout_migration.py`
- `.claude/skills/harness/bin/layout_fixtures.py`
- `.claude/skills/harness/bin/test-layout-migration.py`

**Extension census** (`find .claude/skills/harness/bin -iname '*.html|*.css|*.scss|*.tsx|*.jsx|*.vue|*.svelte|*.less'`):
zero matches. SC-08 additionally confines every change to `.claude/skills/harness/bin/` and explicitly
forbids touching `factory_config.py`, `fleet.yaml`, `harness.json`, `gh_board.py`, `check-domain.sh` —
none of which are UI surfaces either.

**What the feature actually does**: repoints a module-level path constant (`FEATURES_ROOT`), splits
a collapsed blocker-gate error case into two, and adds one row to a layout-migration detector's
reader table. No colour, spacing, typography, layout, theme, or interaction-state decision anywhere
in `BRIEF.md`, `plan.yaml`, or the six named files.

## The one human-facing text surface, handed to the right lens

REQ-02 / SC-04 / decision D-03 / task T-02 pin new stderr diagnostic wording (two new message texts,
naming an absolute path, kept distinct from the existing edge-(i) text by a `"no matching plan task"`
substring test). This is human-facing output, but it is CLI stderr text with no colour-only state
encoding, no theme, and no rendered layout — not a UI surface in this role's remit. The dispatch for
this run does not name it as an in-remit surface either (contrast: prior runs where a CLI/error-message
surface was explicitly handed down). Its wording is already contract-pinned in the plan with automated
distinctness checks (T-02's verify block asserts the absolute path appears in the text and that the
edge-(i) phrase does not); judging whether that wording is semantically correct and well-formed belongs
to `harness-code-reviewer` / `harness-qa`, not this lens.

## Accessibility / theme parity — explicitly n/a

Both sections are stated rather than omitted, per this role's own gotcha about a silent omission
reading as unchecked: this feature produces batch CLI stderr text only. There is no colour, no
rendered UI, and no light/dark theme surface for accessibility or theme-parity findings to attach to.

## Conclusion

No design contract exists or is warranted for this feature, and none of its six touched surfaces are
rendered UI. `in_scope: false` is a measured finding — enumerated directory, extension census, and
SC-08's containment — not a predicted absence.
