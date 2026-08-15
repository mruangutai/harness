# Research — FEAT-19 send-back cycle 1 — what I re-derived at source

**BLUF.** All seven `must_fix` findings hold at `63b83c7`; I re-ran each at source rather than
taking the review's word. Two of the review's own statements needed correcting, and both are
corrected in the artifacts rather than carried. The plan is now 7 tasks / 8 decisions / 7 lane
rows, `check-plan-routes.py` exits 0, approval stays `pending`.

## The seven findings, verified

| F | Evidence I ran | Verdict |
|---|---|---|
| F1 | `factory_config.py` — `FLEET_PATH = os.path.join(harness_root(), ...)` at module scope; `def load_fleet(path=FLEET_PATH)`. `harness_boundary.resolve_fleet` passes the path explicitly and its comment names this trap | real |
| F2 | Order defect in the first draft's own text; no fixture covered it | real |
| F3 | `load_fleet` → `harness_yaml.load_file`, one error type for absent and malformed alike | real |
| F4 | `harness_boundary.select_base` — `max((b for b in workspace_bases if inside(abs_target, b)), key=len)`, longest match wins, with a comment saying why | real |
| F5 | `harness-qa-gate/SKILL.md:45` reads `test_matrix` from `.harness/harness.json`; `gh-sync.py:122` joins the same path | real |
| F6 | `.harness/harness.json` puts `_test_kinds_note` at top level | real |
| F7 | `.harness/harness.json` `github.board._note` ends "PLACEMENT IS TEMPORARY: #206 moves github, test_matrix and test_kinds to the product" | real |

## Two corrections to the review, both load-bearing

- **`gh_board.board_config` does not exist.** The symbol is `gh_board.load_board(root)`, and its
  docstring is explicit that `None` means "not configured" — never an error — when `owner`,
  `number` or `station_field` is missing or empty. D-04 and T-05 now name the real symbol.
- **The BRIEF's four NOBODY surfaces all do resolve to NOBODY** — I ran the guard on each. The
  false half was "of this feature's surfaces": `fleet.yaml` and `templates/harness.json` are
  touched by no task. This feature has **three** NOBODY surfaces once T-07 exists.

## The rename is safe, and it buys a real invariant

`test-factory-config.py`'s SC-18 scan enumerates only `open(` and `harness_yaml.load_file(` call
sites whose first argument is fleet-bearing, across `factory_*.py`. F1's own remedy —
`factory_config.load_fleet(explicit_path)` — is neither of those call shapes, so
`factory_product_config.py` enters the enumeration with zero hits and the invariant still reads
"exactly one scope, `factory_config.load_fleet`". Renaming therefore costs nothing and puts a
standing guard on the new module against ever bypassing `load_fleet`. T-01's `intent:` says so.

## Gate results at authoring time

- `python3 .claude/skills/harness/bin/check-plan-routes.py <plan>` → **exit 0**, 7/7 tasks routed,
  0 violations. `.harness/harness.json` resolves to `harness-dev-ops`, so T-06 is a team task.
- `yaml.safe_load` over the finished plan: loads; no decision scalar truncates at a ` #`.
- DEC-174: no task's `files:` names any of the four gate scripts.
- Every `verify:` is a literal `|` block (7 of 7).
- **T-06 and T-07's verifies run as negative controls at HEAD**: both exit 1, each for the real
  reason, and every positive control inside them (`floor, not a ceiling`, `reproduces the bug`,
  `resolved BY NAME`) passes — so the section-slicing and JSON traversal locate real text rather
  than failing vacuously.

## Open for the operator, priced in the BRIEF

- **D-06** — one consumer (qa gate) is rewired; `gh-sync.py` is not. Goal and REQ-02 narrowed to
  match, explicitly.
- **D-08** — containment rule copied, not shared. The fuller remedy is priced; it acquires the
  review's unresolved DEC-174-in-substance question about `harness_boundary.py`.
- **D-07** — flag is `--which-config`. Decided, not asked: cheap, reversible only while pending.
