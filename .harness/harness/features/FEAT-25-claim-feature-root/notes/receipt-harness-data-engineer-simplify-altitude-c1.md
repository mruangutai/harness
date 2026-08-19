# ALTITUDE receipt — harness-data-engineer — FEAT-25 simplify pass c1

BLUF: No ALTITUDE findings. The new `no_plan` blocker kind and its supporting `_BlockerCache`
methods land in the same single-authority sites the existing blocker kinds already use — nothing
bolted onto a caller, nothing duplicated across two homes.

## What I checked and judged correctly placed

1. **`factory_claim.py:99-131` — new `_BlockerCache.plan_path()`, `_plan()`, `plan_loaded()`,
   `root_exists()`.** `_plan()` remains the sole file-read seam (LEAVE item 7 — verified: `task()`
   and the new `plan_loaded()` both route through `_plan()`, still one `try/except
   harness_yaml.YamlParseError`). `plan_path()` and `root_exists()` are thin filesystem accessors
   scoped to the cache that already owns `self._features_root` — the right home, not a helper
   dropped at the call site. `PlanSchemaError` subclasses `YamlParseError`
   (`harness_yaml.py:261`), so the single `except` clause in `_plan()` already covers both a
   missing-directory read failure and a schema failure — no second exception path was added.

2. **`factory_claim.py:154-198` — `_blocker_gate` / `_blocker_reason_text` gain a `no_plan`
   branch.** This is the existing declared pattern for every other blocker kind (`edge_i`,
   `unresolvable`, `open`) — one function decides the kind, one function renders its text. The new
   kind extends that pair rather than introducing a parallel classification path. Confirmed no
   second "why did this fail" mechanism exists elsewhere in the diff.

3. **`layout_migration.py` `READER_TABLE` new row + `layout_fixtures.py` new `STUB` entry for
   `factory_claim.py`.** Follows the same Row/STUB shape as every existing entry; the import-time
   raise on key mismatch (LEAVE item 6) is the one shared authority keeping them from drifting —
   nothing here proposes a second one.

4. **`layout_migration.py` docstring** — moving `factory_claim.py` off the DO-NOT-READ list with a
   one-line reason is documentation of a state change, not a new rule; the fixed literal in
   `factory_claim.py:45` (LEAVE item 1) remains the single source of truth for the resolved path.

5. **Test-file changes** (`test-factory-claim.py` B5-ter cases, sc13b's eighth reason,
   `test-factory-integration.py` path updates, `test-layout-migration.py` case 22) — these pin
   behavior at the same altitude as the existing sibling cases they extend; no new shared
   assertion infrastructure was introduced that duplicates existing check()/ok-line machinery
   (LEAVE items 3 and 4 untouched).

No changes proposed, so no `verify:` grep-collision check applies — I am proposing nothing.

## Angle discipline

Did not carry REUSE, SIMPLIFICATION, or EFFICIENCY. `root_exists()` re-stat'ing the filesystem per
blocked candidate rather than caching is an efficiency question for a peer, not an altitude one —
noting it here only so it isn't silently missed, not as an ALTITUDE finding.
