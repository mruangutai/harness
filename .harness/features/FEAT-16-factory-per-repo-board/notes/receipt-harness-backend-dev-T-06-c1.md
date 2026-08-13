# Receipt — harness-backend-dev — T-06 — c1

## Verdict

PASS. Fixture-only migration, bounded by DEC-174. `check-domain.sh` was not touched;
no assertion, expected exit code, case name, or comment in `test-check-domain.py` was
changed. Only the fleet YAML strings the fixtures build were edited.

## Migration count — all FOUR fleet strings migrated

1. `good_repos` (case (d), `run_fleet`) — was block-style top-level `board:` with
   owner/number/station_field/stations. MIGRATED: all four keys moved onto the single
   `repos[0].board` entry, block style, same values.
2. The inline fixture behind case (c), built into `nows_root` — was a single-line flow
   mapping `board: { owner: nobody, number: 1 }` (owner+number only), repos entry flow
   style. MIGRATED: per the intent's stated exception, the new per-repo `board` is
   COMPLETE — `station_field: Status` and `stations: { ready: Ready, building:
   Building, review: Review }` were ADDED, not just carried over. See "deliberate
   repair" below.
3. `two_base_fleet` — was block-style top-level board, all four keys. MIGRATED: same
   four keys moved onto `repos[0].board`, block style.
4. `two_base_fleet_for(workspace)` helper — was block-style top-level board, all four
   keys. MIGRATED: same four keys moved onto `repos[0].board`, block style.

Confirmed by `grep -n "board:" test-check-domain.py` post-edit: all four remaining
occurrences are indented under a `repos` entry (`"    board:\n"` / inline
`board: {...}`), none at top level. No fifth site exists in the file (verified with the
same file-scoped `grep -n "board:"` before editing, which also returned exactly these
four lines).

## Deliberate repair — case (c), recorded so it is not read as drift

Before this task, case (c)'s fixture declared a top-level `board: { owner: nobody,
number: 1 }` with no `station_field` and no `stations`. `load_fleet` therefore raised
on the MISSING `board.station_field` key, and the case passed for a reason its own
name — "a fleet that parses but omits workspace_root" — never stated; `workspace_root`
was also absent, but the board error fired first.

After the migration, the repo's per-repo `board` mapping is COMPLETE (owner, number,
station_field, stations all present and valid), and `workspace_root` is still absent
(never added — that omission is the actual thing under test). `load_fleet` now raises
specifically on the missing `workspace_root` key, which is what the case has always
claimed to test. VERIFIED (not just inferred from the exit code, which case (c) never
distinguishes from a board-shape failure or a parse failure): fed the migrated fixture
text directly to `factory_config.load_fleet` outside the suite and observed
`FleetError: fleet key invalid: workspace_root — set it to an absolute path in
<path>` — no mention of `board` in the message.

**Verdict and exit code are unchanged** (case (c) still asserts `c.returncode == 2`).
Only the failure reason moved: `board.station_field` → `workspace_root`.

## Why `good_repos` matters most (case (d))

Case (d) asserts a well-formed fleet leaves both verdicts unchanged. The migrated
fixture — per-repo board on the one repos entry, no top-level board — is accepted by
both T-01's loader (top-level board optional, per-repo board permitted) and T-08's
future loader (per-repo board required, top-level board rejected), satisfying the
"safe at both boundaries" requirement the intent states.

## Verify — run exactly as specified

```
.claude/skills/harness/bin/run-unit-tests.sh --kind integration
```

Exit code: 0. Full output captured; relevant summary lines (verbatim):

```
27/27 T-12 cases passed.

ok    (c) a fleet that parses but omits workspace_root refuses the owned write
ok    (d) PAIR: a well-formed fleet leaves both verdicts unchanged
...
20/20 fleet cases passed.

10/10 --resolve cases passed.
...
PASS test-check-domain.py
...
PASS test-factory-integration.py
```

`test-check-domain.py` itself reported `PASS` inside the aggregate run, and the
integration runner's overall process exit code was `0` (confirmed via
`echo "EXIT:$?"` immediately after the run). No FAIL lines appear anywhere in the
captured output.

## Files touched

- `.claude/skills/harness/bin/test-check-domain.py`

## Out of bounds — confirmed untouched

- `.claude/skills/harness/bin/check-domain.sh` — not edited (DEC-174 carve-out).
- No assertion, expected exit code, case name, or explanatory comment changed in
  `test-check-domain.py` — diff is confined to the fleet-string literals.
- `.harness/factory/fleet.yaml` — not touched (T-07's surface).
- `factory_config.py` and no other source file touched.
