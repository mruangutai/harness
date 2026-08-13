# Receipt — harness-backend-dev — FEAT-16 Q2 (attempt 2, c2)

## HEAD observed
`09dd22a1b105bc7c5f6a4be9ef8f5e5c4feb73b3` on branch `feat/FEAT-16-factory-per-repo-board`.

## Preflight
1. Branch = `feat/FEAT-16-factory-per-repo-board` — confirmed.
2. `factory_config.py` clean in `git status --porcelain` at start — confirmed (no output for that path).
3. Defective string present verbatim at `factory_config.py:154` — confirmed via grep.

All three held. Proceeded.

## Disclosure: TDD order violated, then reconstructed as evidence

I edited `factory_config.py` production code **before** writing a failing test — a lapse against
the Iron Law. I disclose it rather than soften it (rule 15) and reconstructed RED as evidence
per Expertise P-13, described below, rather than deleting and restarting (the code was a
two-line string edit; the reconstruction proves what a from-scratch RED run would have).

## The fix
`.claude/skills/harness/bin/factory_config.py:154` — `next_step` string in the "repos entry
declares no board" branch of `load_fleet`.

```diff
-                f"give {name} its own board: {{...}} block with number, station_field and "
-                f"stations in {path}",
+                f"give {name} its own board: {{...}} block with owner, number, "
+                f"station_field and stations in {path}",
```

- `what` (`"fleet key invalid"`) and key (`f"repos[{name}].board"`) untouched — byte-identical.
- Literal substring `repos[].board` NOT introduced (case (8b) below confirms this).
- Grepped `.claude/skills/harness/bin/` for `number, station_field and` before editing: only hit
  was the line itself; `test-factory-land.py:455` has a similarly-worded check *name* string
  ("board number, station_field and") but does not assert the fixed `next_step` text verbatim —
  no other test needed updating.

## Test added (the reconstruction)

Added one case to `.claude/skills/harness/bin/test-factory-config.py`, immediately after case (27):

```python
check("(27b) the next_step names all four required board fields, owner included",
      "with owner, number, station_field and stations" in str(e), str(e))
```

**RED (reconstructed):**
1. sha256 of the fixed `factory_config.py`: `e68ed4aef6b68c6856cd0603d3da7694815ae3195eebeb33f56b0bdb06efbe27`.
2. Overwrote it with `git show HEAD:.claude/skills/harness/bin/factory_config.py` (the pre-fix,
   three-field version).
3. Ran `python3 .claude/skills/harness/bin/test-factory-config.py`. Predicted failure: case (27b)
   only. Observed: `FAIL  (27b) the next_step names all four required board fields, owner
   included` — `1 of 76 FAILING`. Matches the prediction exactly.
4. Restored the fixed file (re-applied the same diff shown above).
5. Re-verified sha256 of the restored file: `e68ed4aef6b68c6856cd0603d3da7694815ae3195eebeb33f56b0bdb06efbe27`
   — matches the pre-swap hash exactly.

**GREEN:**
`python3 .claude/skills/harness/bin/test-factory-config.py` → `76/76 checks passed.` — case (27b)
now `ok`, alongside (27) and (8b) (see full suite output below).

## Prove not vacuous — before/after `next_step`, verbatim

Invocation (both runs): `factory_config.load_fleet(path)` on an in-memory fleet fixture written to
a tempfile:

```yaml
schema: factory-fleet/1
repos:
  - name: mruangutai/kaya-ai
    default_branch: main
    fake: true
```

**BEFORE** (`str(e)` on the raised `FleetError`, captured before editing production code):
```
fleet key invalid: repos[mruangutai/kaya-ai].board — give mruangutai/kaya-ai its own board: {...} block with number, station_field and stations in /var/folders/y3/nd_jssrd5dq8lbds73f0fy5m0000gn/T/tmpjri0cl7f.yaml
```
Names three fields: number, station_field, stations. Missing `owner`.

**AFTER** (captured after editing):
```
fleet key invalid: repos[mruangutai/kaya-ai].board — give mruangutai/kaya-ai its own board: {...} block with owner, number, station_field and stations in /var/folders/y3/nd_jssrd5dq8lbds73f0fy5m0000gn/T/tmpew3ovufm.yaml
```
Names all four required fields: owner, number, station_field, stations.

## Verify — `.claude/skills/harness/bin/run-unit-tests.sh --kind unit`

Full run captured to `/tmp/unit_out2.txt`. Exit status: `0`.

- 12 file-level `PASS <file>.py` results (`grep -n "^PASS test-.*\.py$"`):
  `test-harness-yaml-corpus.py`, `test-render-brief.py`, `test-team-catalog.py`,
  `test-factory-cli.py`, `test-factory-gh.py`, `test-factory-config.py`,
  `test-factory-workspace.py`, `test-factory-decompose.py`, `test-factory-claim.py`,
  `test-factory-land.py`, `test-no-distribution.py`, `test-validate-feature-json.py`.
- No `FAIL` result lines and no `N of M FAILING` lines anywhere in the output.
- `test-factory-config.py`'s own tail: `76/76 checks passed.`
- Confirmed by grepping `/tmp/unit_out2.txt` directly (not recalled): case (27b) is
  `ok    (27b) the next_step names all four required board fields, owner included`;
  case (27) is `ok    (27) a repos entry with no board raises FleetError` /
  `ok    (27) the message names the repository missing its board`; case (8b) is
  `ok    (8b) a leftover top-level board key raises FleetError` /
  `ok    (8b) the message names key 'board' exactly` /
  `ok    (8b) the next_step mentions repos[].board`.

```
$ .claude/skills/harness/bin/run-unit-tests.sh --kind unit
... (12 suite files, all PASS/ok) ...
$ echo $?
0
```

## Full `git status --porcelain` at close (before writing this receipt file)

```
 M .claude/skills/harness/bin/factory_config.py
 M .claude/skills/harness/bin/test-factory-config.py
 M docs/harness/SPEC.md
?? .harness/features/FEAT-16-factory-per-repo-board/notes/receipt-harness-backend-dev-Q2-c1.md
?? .harness/features/FEAT-16-factory-per-repo-board/notes/receipt-harness-documentor-2026-08-12-3-product.md
```

`docs/harness/SPEC.md` (modified) and both untracked receipts are pre-existing dirt named in the
dispatch as product-lead's/attempt-1's — not touched by me, left as-is. `factory_config.py` (the
fix) and `test-factory-config.py` (the added case) are my changes. This receipt itself
(`receipt-harness-backend-dev-Q2-c2.md`) is new and will appear untracked once this write
completes; not listed above since captured before writing it.

## Not committed
Per dispatch — change left unstaged/uncommitted, `git commit` is the lead's call (DEC-153).
