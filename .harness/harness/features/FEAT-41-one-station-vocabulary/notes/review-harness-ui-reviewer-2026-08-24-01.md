# UI review — FEAT-41 one-station-vocabulary (Mode A, pre-build)

## BLUF
PASS, scoped out. No design contract is required for this feature. The 57 `files:` entries are
all `.py`/`.sh`/`.json`/`.md`/`.yaml`; zero are UI-shaped (no `.tsx/.jsx/.vue/.css/.scss/.html`,
no `web/`/`component` dirs — the four `/templates?/` regex hits are Harness's own scaffold
templates `.agents/skills/harness/templates/{feature.json,harness.json,plan.yaml,
settings.snippet.json}`, config not markup). `change_type` values in use: `api`, `bugfix`,
`config`, `cross_module`, `docs` — no `frontend`. No `DESIGN.md` exists for FEAT-41 (checked
`.../features/FEAT-41-one-station-vocabulary/` — only `plan.yaml`, `feature.json`, `STATE.md`,
`BRIEF.md`, `notes/`, `observations/`, `runs/`); the repo does use `DESIGN.md` elsewhere (found
under FEAT-19, FEAT-40, FEAT-11, FEAT-10), so its absence here is a measured fact, not an assumed
convention.

## The board counter-argument, weighed
BRIEF.md states explicitly, under Constraints: "Out of scope, from the source ticket: the board's
column names themselves. They are correct." The six station values are supplied by DEC-203
section 6, not invented by this feature (BRIEF: "DEC-203 ... SUPPLIES the six values"). SC-01
pins them as "one ordered lowercase list" declared once in `harness.json` — a naming/ordering
decision, but one already made upstream of this plan, not one this feature is free to design.
What this feature does is enforce that every consumer (`gh-sync.py`, `check-plan-routes.py`,
`feature-schema.json`, `check-state.sh`, `board_lifecycle.py`) reads that one vocabulary instead
of drifting copies — a single-source-of-truth/correctness refactor, verified by SC-01–SC-13
(grep counts, exit codes, INV-26 behavior), not a visual/interaction contract. The "orphaned
station a card can land in and never leave" risk the dispatch raises is real but is exactly what
SC-04 (`set_station` has one policy site) and SC-13 (INV-26 traces the same function it writes)
already pin, as automated/checkable criteria — the mechanism a design contract would need
("checkable") is present, just not framed as a DESIGN.md. A GitHub Projects board's column
set/order/colour is GitHub's own rendering of Project settings, outside this repo's source tree
entirely and explicitly untouched here. Conclusion: the board is a **mirror of `plan.yaml` state**
through this feature's lens, not a surface being designed — no new station names, ordering, or
visual grouping choice is on the table.

The only user-facing text this feature adds is refusal/error message wording (SC-01, SC-03, SC-05,
SC-06, SC-07, SC-13: exit codes naming an offending file/value). This is CLI/hook diagnostic
output, not a rendered UI surface, and the dispatch did not name it as an adjacent surface to
audit — no finding filed against it here.

## Applicability
- **Accessibility**: not applicable — no rendered markup; the only human-facing artifact is CLI
  exit-code text and an unmodified GitHub Projects board.
- **Dark/light theme parity**: not applicable — no colour or theme is declared or altered by this
  feature; board colours are GitHub's own, out of scope per BRIEF.
- **Visual fidelity**: not applicable — no spacing/type/colour values are introduced; nothing here
  is renderable from source in this repo.

## Verdict
No DESIGN.md is required and none should be written for FEAT-41. Findings: none.
