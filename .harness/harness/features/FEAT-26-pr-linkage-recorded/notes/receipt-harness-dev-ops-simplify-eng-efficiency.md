# EFFICIENCY receipt — simplify-eng, HEAD = 9a30ea5

BLUF: one real (small) finding — INV-28 adds a fourth independent full walk-and-parse of
every `feature.json` in `check-state.sh`, on top of three that already existed pre-diff.
Measured cost is ~8ms per run on 33 files, dwarfed by the script's own ~10s `gh auth
status` network call that runs regardless. `gh-sync.py`'s new work (`parse_source_issues`,
`_record_pr`, `cmd_closes`) adds no repeated I/O and no new subprocess on any non-one-shot
path. Nothing here rises above `later-feature`.

## Finding 1 — check-state.sh: a 4th independent glob+parse loop over feature.json (fold-in-later)

- **File/line (HEAD):** `.claude/skills/harness/bin/check-state.sh:1063` (`for fy in
  glob.glob(os.path.join(H, "*", "features", "*", "feature.json")):` inside the new INV-28
  block, `:1043-1084`).
- **Summary:** INV-28 walks and re-parses every `feature.json` independently. This is the
  **6th** occurrence of that exact glob pattern in the file at HEAD (verified: `grep -c`
  → 6, at lines 177, 573, 708, 914 [INV-21], 953 [INV-24], 1063 [INV-28, new]). INV-21 and
  INV-24 already established this pattern pre-diff; INV-28 is one more instance of an
  existing shape, not a new one.
- **Measured cost:** isolated the glob+`harness_yaml.load_file` loop against this
  checkout's real `.harness/` tree (33 `feature.json` files, confirmed via `find`):
  3 runs averaged **0.0082s** per full walk-and-parse. Full `check-state.sh` at HEAD vs
  HEAD~1 (5-8 runs each, same tree, both via `env CLAUDE_PROJECT_DIR=<worktree> bash
  <script>`): HEAD real times `9.91/10.04/11.62/12.25/11.06/10.34/12.54/11.29`s (avg
  ≈11.1s), HEAD~1 `10.98/10.65/9.53/10.15/10.78`s (avg ≈10.4s). The two distributions
  overlap; the ~0.7s "delta" is inside the noise of the network-bound `gh auth status`
  call at `check-state.sh:1251` (pre-existing, unrelated to this diff, and itself the
  reason both distributions are 10s+ rather than sub-second). The real, attributable cost
  of INV-28's own loop is the isolated **8ms** figure, not the noisy full-script delta.
- **Alternative:** none needed at this size. If a 7th or 8th invariant adds another full
  walk, collapsing INV-21/INV-24/INV-28 (all three are `github.sync`-gated, all three walk
  the same glob) into one shared parse-and-dispatch pass would remove ~16ms of redundant
  I/O — real, but two orders of magnitude below the dominant `gh auth status` cost that
  already sets the floor for how fast this script can run. Not worth doing for 8ms.
- **Rank: later-feature.** Correctness is unaffected; the existing three-loop pattern this
  joins was itself never flagged, and it would be inconsistent to gate one new instance
  when the pre-existing form was accepted.

## Finding 2 — gh-sync.py: no wasted work found (empty result, reported plainly)

- Checked for: new subprocess calls on a non-one-shot path, repeated parses within a
  single invocation, module-import-time I/O.
- `parse_source_issues` (`:312-341`) is called exactly once, from `cmd_open` (`:680`) —
  no loop, no re-parse.
- `_record_pr`'s `gh pr list` subprocess (`:536-603`, call at `:571`-ish inside) is reached
  only from `cmd_ship` (`:925`) and the `record-pr` subcommand (`:1045`) — both one-shot
  operator-invoked commands, not a hot/startup path.
- `cmd_closes` (`:868-883`) was measured directly: `python3 gh-sync.py closes
  <FEAT-01 dir>` → `real 0.07s`, confirming the docstring's "makes no GitHub call" claim
  empirically rather than by trusting the comment.
- **No finding here.** An empty return is the honest result, not a gap in the search.

## Finding 3 — check-state.sh timing across HEAD/HEAD~1: the boundary-step full-suite runs are NOT waste

Not flagged. The commit message's "Full suite --kind all: 45 PASS, 0 FAIL" and the
per-task `VERIFY-OK` runs are exactly the evidence a ship-boundary step exists to produce
— excluded from this review per the dispatch's own instruction.

## Not re-raised (per dispatch)

`test-gh-sync.py`/`test-check-state.py` classification, the docstring corrections, DEC-186
scope, and the signed plan/BRIEF are out of scope here and were not touched.
