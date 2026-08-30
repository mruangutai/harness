# QA Regate — pin `37676244`

**VERDICT: PASS.** Every gate check is green at the re-pin. One handed-down numeral in the contract
is FALSE (the "28 -> 27" baseline) but it does not change the outcome: the correct baseline is 29,
the resolution still drops exactly the two ghost registrations, and both are confirmed absent from
the tree.

## Matrix (floor)

All 28 `plan.yaml` tasks are `change_type: docs` (16), `logic` (6), or `config` (6) — no `api`,
`cross_module`, `feature`, `frontend`, `bugfix` or `ai_behavior` task exists. `docs`/`config` require
nothing (`always: []`); `logic` requires `always: [unit]`. **Floor = `unit` only.**
`matrix_ok: true` — unit exists, ran, passed (below). No kind added beyond the floor; nothing the
diff warrants sits outside it.

## Full suite (observed, not inferred)

`bash .claude/skills/harness/bin/run-unit-tests.sh` (no flag — runs unit+integration together),
output captured to file, exit code read from `$?` immediately after, `FAIL ` count from a Python
scan of the captured file (never grep, never a tail):
- **Exit code observed: `0`.**
- **`FAIL ` line count: `0`.**
- Runtime ~175s.

## `--check-kinds`

`bash .claude/skills/harness/bin/run-unit-tests.sh --check-kinds` → **exit `0`**,
`"check-kinds: the script arrays and test_kinds.integration.detect agree."` Mechanical half of
conflict resolutions 1 and 2 holds.

## Discovery is real, not silently empty

Ran `--kind integration` alone (separate 156s pass, exit `0`, `FAIL ` count `0`) and counted
distinct `PASS <script>.py` markers in Python: **26 scripts discovered and executed.**
`test_kinds.integration.detect` at the pin has **27 entries** — the 26 concrete files plus
`tests/integration/**`, a glob matching 0 paths because `tests/integration/` does not exist in this
tree. 26 executed = 26 concrete entries. Discovery is intact; nothing is silently empty.

## Per-entry file existence (Python, per line)

All 26 concrete `test_kinds.integration.detect` entries: `os.path.exists()` → **True, every one**
(includes `test-check-decision-anchors.py`, the retained-anchor-checker's test). Neither
`test-context-watch-cli.py` nor `test-context-watch-hook.py` appears in the detect list at the pin,
and both are confirmed absent from disk and from `git ls-files` at HEAD — the union-resurrection
defect the resolution exists to prevent did not ship. `test_kinds.unit.detect`'s 5 patterns are all
globs (no concrete-file entries to falsify); the one non-trivial glob
(`.claude/skills/harness/bin/test-*.py`) matches 52 files, all present by construction of the glob
itself.

## Entry-by-entry arithmetic — **the reported "28 -> 27" is FALSE**

Computed in Python over `git show <sha>:.harness/harness.json`, never grep:

| side | sha | `test_kinds.integration.detect` entries |
|---|---|---|
| branch (parent 1) | `4c192ab` | **29** |
| main (parent 2) | `6d6d1cea` | **26** |
| pin | `37676244` | **27** |

`main`'s 26 entries are a strict subset of `branch`'s 29 (`main`-only = `{}`). So
**union(branch, main) = branch = 29**, not 28. `dropped-from-union-at-pin = {test-context-watch-cli.py,
test-context-watch-hook.py}` — exactly the 2 the contract names, both verified absent from the tree
— so `29 - 2 = 27`, matching the pin. **The direction and justification in the contract are correct
and verified; only the numeral "28" is wrong — it should read "29 -> 27" (drop 2, not "28 -> 27"
drop 1).** This is the third handed-down premise in this feature caught by re-measurement rather
than by the sender.

`.harness.json`'s own `_matrix_provenance` (`api`/`cross_module`/`feature`, all DEC-187-signed) is
untouched by this reconciliation and not implicated.

## `.agents/skills` vs `.claude/skills` — **claim holds, no defect**

`.agents` is a tracked symlink (`.agents/skills -> ../.claude/skills`); `os.path.realpath()` on both
`test_kinds.*.cmd`'s `.agents/skills/...run-unit-tests.sh` and the `detect`/dispatch spelling
`.claude/skills/...run-unit-tests.sh` resolve to the byte-identical file. The configured `cmd`
resolves and runs (proven above — it's the exact command used for the full-suite and
`--check-kinds` runs). Not a BLOCKED-class gate defect.

## DECISIONS-INDEX.md conflict resolution — spot-checked, holds

`gen-decisions-index.py --stdout` diffs byte-clean against the tracked `DECISIONS-INDEX.md` at the
pin (exit 0, `diff -q` clean) — corroborates SC-05's clean-diff clause and the contract's claim that
the third conflict was purely generated anchors.

## Not this gate's job

Source/test-content quality, SC-01–SC-18 individually, and B-25/B-26/B-39 are out of scope here per
the dispatch; a separate panel and pm own those. Nothing above required editing any file.
