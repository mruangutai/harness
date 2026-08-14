# Research — FEAT-19 — anchors re-derived, and the resolution mechanism

**All measurements below were taken at `63b83c7` on branch `main`, working tree clean except
`.harness/logs/2026-08-13.md`.** The dispatch warned that the session snapshot showed
`89ecc11` on `feat/FEAT-18-board-truth`; `git rev-parse HEAD` returned `63b83c7` and
`git branch --show-current` returned `main`. The snapshot was stale, the dispatch's SHA was right.

## BLUF

The mechanism is already in the tree and needs one new consumer, not a new idea.
`factory_config.workspace_path(fleet, name)` maps a fleet `name` to `workspace_root/<segment
after the slash>`, and `harness_boundary.resolve_fleet` / `select_base` already run that map in
reverse to decide which base a path belongs to. Product config resolution is the same reverse
lookup with a different payload: cwd under `workspace_root` → fleet entry → repo segment →
`<harness root>/.harness/products/<segment>/harness.json`. Nothing new is keyed, nothing is
written into the product checkout.

## The grilling's own refresh is stale in one clause — correcting it precisely

The refresh at `862d270` says of the four anchored regexes: *"gone entirely … no `[^/]` anchor
survives in either file."* At `63b83c7` that is **false as written and true in substance**.
`grep -n '\[\^/\]'` returns seven hits:

| File | What the anchor is |
|---|---|
| `check-domain.sh` | one worktree-relative match, plus `RE_FEATURE_JSON`, `RE_STATE_YAML`, `RE_HANDOFF`, `RE_STATE_MD` — feature-path shape regexes |
| `harness_boundary.py` | `WORKTREE_REL_RE`, plus two inside `glob_to_re`'s translator |

None of them is workspace resolution — that moved to `resolve_fleet` and `select_base` as the
refresh says. But the sentence "no `[^/]` anchor survives" is not true of either file, and the
surviving anchor that matters most to this feature is the one in `glob_to_re`: `*` becomes
`[^/]*` and **cannot cross a path segment**. That is the fact that settles the per-product path
shape below.

## The five FEAT-10 numbers, re-derived at `63b83c7`

FEAT-10 recorded "No product level in `.harness/`" as settled on these. The operator has
overturned the ruling; these now size the work rather than argue against it.

| FEAT-10 said | At `63b83c7` | Command |
|---|---|---|
| 473 references across 152 files | **3411 occurrences across 462 files** | `git grep -o '\.harness' 63b83c7 -- . \| wc -l`; `git grep -l` for files |
| 40 live + 22 template domain globs `upgrade-config.py` refuses to rewrite | **77 `.harness/`-prefixed globs in `.harness/team-config.yaml`**; the refusal still stands and is deliberate — `upgrade-config.py`'s docstring: YAML is REPORTED ONLY because `safe_dump` strips the comments that justify every glob | `python3` walk of `safe_load`; `upgrade-config.py` module docstring |
| four anchored `[^/]+` regexes at `check-domain.sh` | workspace resolution moved to `harness_boundary.resolve_fleet` / `select_base`; four *feature-path* regexes remain (see above) | `grep -n '\[\^/\]'` |
| CI assertions in `tests.yml` | present but **not** at `:134-141`; that range is the `check-plan-routes.py` step. The live assertions are the plan-count guard and the zero-directories guard | `grep -n 'harness' .github/workflows/tests.yml` |
| no layout-migration machinery | **still true.** `upgrade-config.py` merges `harness.json` key-wise and knows nothing about a second config location | read `upgrade-config.py` |

**The first number does not dimensionally reconcile with FEAT-10's** — 462 files against 152 is
not two features of growth. FEAT-10's figure is not reproducible from its recorded methodology,
so the row above is the new baseline with its command, not an attempt to reproduce theirs.

## Routing — every candidate path delegated to `check-domain.sh --resolve` at `63b83c7`

| Path | `--resolve` | rc |
|---|---|---|
| `.harness/products/kaya-ai/harness.json` | NOBODY | 0 |
| `.harness/factory/fleet.yaml` | NOBODY | 0 |
| `.claude/skills/harness-init/SKILL.md` | NOBODY | 0 |
| `.claude/skills/harness/templates/harness.json` | NOBODY | 0 |
| `.harness/harness.json` | harness-dev-ops | 0 |
| `.claude/skills/harness/bin/product_config.py` | harness-backend-dev harness-dev-ops | 0 |
| `.claude/skills/harness/bin/test-product-config.py` | harness-backend-dev harness-dev-ops | 0 |
| `.claude/skills/harness/bin/run-unit-tests.sh` | harness-backend-dev harness-dev-ops | 0 |
| `.claude/skills/harness/bin/upgrade-config.py` | harness-backend-dev harness-dev-ops | 0 |
| `.claude/skills/harness/bin/gh_board.py` | harness-backend-dev harness-dev-ops | 0 |
| `docs/harness/DECISIONS.md`, `DECISIONS-INDEX.md` | harness-documentor | 0 |

**Four of this feature's surfaces are granted to NOBODY**, so they are declared main-session
steps under DEC-179 — an ungranted surface is legitimate, not a task that silently fails.
`check-state.sh` resolves to backend-dev/dev-ops but is one of DEC-174's four and is
main-session-direct for a different reason. The two reasons are kept distinct in the plan.

## The per-product path — settled by evidence, not preference

`workspace_path` is explicit that it is the one place the derivation exists: `name.split("/",
1)[-1]`, so `mruangutai/kaya-ai` → `<workspace_root>/kaya-ai`. Using the same segment for
`.harness/products/<segment>/` gives one derivation in one place.

The alternative — `.harness/products/<owner>/<repo>/` — is refused on measured grounds:
`glob_to_re` translates `*` to `[^/]*`, which cannot cross a segment, so every future domain
glob over a two-segment product path would need `**` and would be a wider grant than intended.

**Named, not fixed:** `a/x` and `b/x` collide under a single segment. That collision already
exists in `workspace_root` itself, so this feature inherits it rather than introducing it.

## The DEC-187 trap on kaya's config — the thing nobody named

DEC-187 (uncited in the dispatch, reached via the index) sets a **closure invariant**: every kind
the matrix names must exist in `test_kinds` and be `active` — a `cmd` someone has run and seen
pass — or `excluded` with `excluded_because` and a `signed` value naming a decision that resolves
**in the project's decisions file**. `unresolved` blocks.

Two facts collide with authoring kaya's config centrally:

1. **Nobody has run kaya's commands from here**, and this effort does not clone kaya. Marking any
   kind `active` would be an unverified claim of the exact shape DEC-187 exists to stop.
2. **Kaya has no decisions file**, so an `excluded` kind's `signed` value has nowhere to resolve.

The existing reference `.claude/skills/harness/templates/examples/harness.kaya-ai.json` also
carries the defect DEC-187 names by name: `bugfix.always` is `["__bug_class__"]`, a predicate
placeholder present in no `test_kinds`, so kaya's bugfix type can never resolve, and `unit` was
dropped from it. Copying that file forward unchanged ships a matrix that cannot resolve.

This is a decision, not a task detail, and it is in the BRIEF as D-03.

## Fail-open probes — the unnamed half of the named hazard

The hazard the tree already handles loudly: a checkout under `workspace_root` belonging to no
`fleet.yaml` entry exits 2. Two adjacent states are **not** yet handled and both fail open toward
the control plane's own config, which is the worst outcome this feature can produce:

- **registered but unconfigured** — in `fleet.yaml`, no `.harness/products/<segment>/harness.json`
- **configured but unregistered** — a `products/` directory with no fleet entry

Each gets its own success criterion.

## Facts confirmed unchanged at `63b83c7`

- `.harness/products/` does not exist.
- `mruangutai/kaya-ai` is the only `repos:` entry; `mruangutai/harness` is deliberately absent.
- `.harness/harness.json` has 16 top-level keys; `github` is `{sync, repo, board{owner, number,
  station_field}}` and its own `_note` already says the placement is temporary and that #206 moves it.
- `harness-init/SKILL.md` is 286 lines with nine numbered steps.
- Nothing in `check-state.sh` enumerates `.harness/`'s children, so adding `products/` trips no
  inventory invariant. `dirty_tree_whitelist` is `.harness/**`, which already covers it.
- `run-unit-tests.sh` keeps explicit `UNIT_SCRIPTS` / `INTEGRATION_SCRIPTS` arrays with a drift
  detector over their union: a new test file unregistered there fails the whole run.

## Open — for the eng-lead architecture review that runs after this plan

The resolution mechanism is proposed as D-02, not silently fixed. Its alternatives and their
prices are in the BRIEF. The specific questions worth an architect's eye:

- Does position-derived resolution hold for a session that is neither in the harness root nor
  under `workspace_root`? Proposed answer: it does not resolve, and that is a loud refusal.
- Should the fleet entry carry an explicit `config:` pointer as well, making the indirection
  visible in the file the operator edits, at the cost of a second thing to keep in sync?
- Is an env override (`HARNESS_PRODUCT`) an escape hatch or a hole?
