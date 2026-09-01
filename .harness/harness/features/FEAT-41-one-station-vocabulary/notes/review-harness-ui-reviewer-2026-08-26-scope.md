# UI review — FEAT-41 one-station-vocabulary — self-scope re-check (Mode A)

## BLUF
Scope-out confirmed, PASS. Re-read `plan.yaml` and `BRIEF.md` directly from the pinned commit
`e5afc19` (`git show e5afc19:...`, never the working tree) per this dispatch's instruction, since
the predecessor panel's false claim came from reading a file another agent held mid-edit.

## Measured evidence at e5afc19
- Extension census over every `files:` entry in `plan.yaml`: 93 `.py`, 17 `.json`, 15 `.md`,
  14 `.sh`, 11 `.yaml`. Zero `.html/.css/.scss/.less/.tsx/.jsx/.vue/.svelte`
  (`grep -E '\.(html|css|scss|less|tsx|jsx|vue|svelte)\b'` over the whole plan returns nothing).
- `grep -in 'DESIGN.md|design contract|dark mode|light mode|accessib|contrast|focus'` over the
  full plan returns exactly one hit: D-12, which states the design-contract gate **re-fires at
  build** if any task lands "a UI-shaped file, a rendered surface or operator-facing output" — the
  plan authors already built in the re-trigger this role would otherwise have to demand.
- Read all 13 tasks (T-01–T-13) in full: `harness.json` station declaration, `gh_board.py`
  case-boundary refactor, `plan-merge.py` verb additions, `check-plan-routes.py`/`check-state.sh`
  vocabulary migration, `feature-schema.json` key deletion, a new PreToolUse hook
  (`plan-sign-gate.py`), `check-domain.sh` shape-gate denial, `gh-sync.py` ship fixes, a stale-test
  deletion, and a `DECISIONS.md`/`SPEC.md` documentation task (T-12, executed by
  `harness-documentor`, not this role). Every task is a validator, hook, config key, CLI verb, or
  decision-record change. None touches a rendered surface.
- `BRIEF.md` Constraints: "Out of scope, from the source ticket: the board's column names
  themselves. They are correct." The six station values are supplied by DEC-203 §6, not designed
  here. The GitHub Projects board's own rendering (columns, colour, layout) is untouched — this
  feature only makes `plan.yaml` the single source `gh_board.project` reads to pick which existing
  column a card lands in.
- This matches my prior note at
  `notes/review-harness-ui-reviewer-2026-08-24-01.md` (same conclusion, independently re-measured
  here against the pinned commit rather than trusted from that note).

## Applicability
- Accessibility / dark-light theme parity / visual fidelity: not applicable — no rendered markup,
  no colour or spacing values, nothing renderable from source anywhere in this diff's surface.
- CLI/hook refusal text (SC-01, SC-03, SC-05–SC-07, SC-13) is diagnostic exit-code output, not a
  rendered UI surface, and the dispatch does not name it as an adjacent surface in this role's
  remit (contrast with P-06, which applies when a dispatch explicitly hands down such a surface —
  this one does not).

## Verdict
`in_scope: false`. No UI surface exists in this plan. D-12 already carries the re-fire condition
for any future task that introduces one, so no action item is owed back to pm/lead.
