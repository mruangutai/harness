# Receipt — harness-backend-dev — simplify/apply — FEAT-38-decisions-current-knowledge

## BLUF
Applied the one authorized fix: narrowed `parse_decisions` in
`.claude/skills/harness/bin/gen-decisions-index.py` from a 3-tuple
`(decisions, lines, headings)` to `(decisions, headings)`, dropped the unread
`"title"` entry from the per-decision dict, and updated the sole call site
(`build_index`). Full unit suite is green (exit 0, 0 FAIL lines, 55/55
registered scripts ran), and generator output is byte-identical to the
tracked `DECISIONS-INDEX.md`. No commit made.

## Pre-edit authorization check (both premises held)
Ran a Python scan (not shell grep) over `.claude/skills/harness/bin/`:
- Exactly one call site of `parse_decisions(` outside its own `def` line:
  `build_index` at line 172 (`decisions, _, headings = parse_decisions(text)`).
- No reader of `"title"` on a decision dict anywhere under that directory,
  including `test-gen-decisions-index.py` — every `"title"` hit found belongs
  to unrelated gh-issue/task dicts (`board_lifecycle.py`, `factory_claim.py`,
  `wayfind.py`, `gh-sync.py`, etc.), never a decision dict from
  `parse_decisions`.

## Edit
`gen-decisions-index.py` (line numbers pre-edit):
- `:125-131` — `parse_decisions`'s per-decision dict literal dropped the
  `"title": lines[idx][1],` line; return statement narrowed to
  `return decisions, headings`.
- `:172` — `build_index` updated to `decisions, headings = parse_decisions(text)`.
- Docstring at `:110` already read `{"num": int, "line": int, "body": str}`
  before the edit — matched the new shape exactly, no change needed.
- `strip_trailing_clauses`/`had_ok_stale`, the :204-209 incident comment, the
  `MalformedRow`/`parse_argv` comments, and `check-decision-anchors.py` /
  `test-check-decision-anchors.py` were not touched.

## Verify
- `bash .claude/skills/harness/bin/run-unit-tests.sh`: exit status `0`.
- FAIL-line count, counted in Python
  (`sum(1 for l in lines if l.startswith("FAIL "))`): `0`.
- Registered vs. ran: `UNIT_SCRIPTS` (27) + `INTEGRATION_SCRIPTS` (28) = 55
  registered (parsed from the script's own arrays); every registered name
  appeared as a top-level `PASS <name>.py` line and none as `FAIL`. (The
  earlier apparent "60 PASS lines" figure was a false read: 4 are a script's
  own internal sub-run echoes for the same top-level name — `test-feature-
  worktree.py`, `test-expertise-merge.py`, `test-plan-merge.py`,
  `test-observations-merge.py` — and one, `case_floor_inflight_registry.py`,
  is a sub-test label printed by `test-inflight-registry.py`, not a
  registered top-level script. Set-diffed registered vs. observed names in
  Python: zero missing, zero unexpected top-level scripts.)
- Wall-clock: `174s` (orchestrator baseline `168.96s` — within run-to-run
  variance; no correctness signal).
- `.claude/skills/harness/bin/gen-decisions-index.py --stdout | diff - .harness/harness/docs/DECISIONS-INDEX.md`:
  exit `0`, no output — byte-unchanged.

## git status --porcelain (verbatim, from worktree root)
```
 M .claude/skills/harness/bin/gen-decisions-index.py
?? .harness/harness/features/FEAT-38-decisions-current-knowledge/notes/qa-ship-gate.md
?? .harness/harness/features/FEAT-38-decisions-current-knowledge/notes/receipt-harness-backend-dev-simplify-simplification.md
?? .harness/harness/features/FEAT-38-decisions-current-knowledge/notes/receipt-harness-data-engineer-simplify-reuse.md
?? .harness/harness/features/FEAT-38-decisions-current-knowledge/notes/receipt-harness-dev-ops-simplify-altitude.md
?? .harness/harness/features/FEAT-38-decisions-current-knowledge/notes/receipt-harness-dev-ops-simplify-efficiency.md
?? .harness/logs/2026-08-29.md
```
`check-decision-anchors.py` and `test-check-decision-anchors.py` are absent
from this output — confirmed untouched.

No commit was made; the commit pen belongs to the orchestrator (DEC-153).
