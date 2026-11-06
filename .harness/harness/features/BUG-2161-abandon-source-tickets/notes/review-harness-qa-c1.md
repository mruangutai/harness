# QA gate — BUG-2161 — fix c1 re-verification, tip b5929a92 (gate-only)

BLUF: PASS. HEAD = b5929a92e87a7792ddaa7ea99e3f849a699a82ab; no source/test dirt (`git status -- .claude tests` clean; only notes/plan/feature.json dirty). Both configured kinds green with HARNESS_AGENT_TYPE unset; signed T-01 chain green; F1 and GC-01 each have a red-before run I reproduced. Authored no tests/code.

## Matrix
- T-01 bugfix: unit required (gh-sync.py changed, touches_runtime_code over full feature diff, P-13); integration run too (external-interaction fix). T-02 docs: none. eval excluded; no locally_run surface.
- unit: `env -u HARNESS_AGENT_TYPE python3 .agents/skills/harness/bin/run-unit-tests.py --kind unit` -> exit 0, "pool: 8 workers, 57 files"; test-gh-sync-abandon-sources.py (exit 0) discovered and ran.
- integration: same `--kind integration` -> exit 0, "84 files"; 84/84 `(exit 0)`; test-gh-sync-abandon.py (exit 0) and test-gh-sync-ship.py (exit 0) ran. Integration discovery includes the unit files' kind only by its own list; not double-classified.
- Signed verify, verbatim, worktree root: `python3 tests/unit/test-gh-sync-abandon-sources.py && python3 tests/integration/test-gh-sync-abandon.py && python3 tests/integration/test-gh-sync-ship.py` -> three exit 0; unit 31 PASS/0 FAIL "ALL PASSED"; abandon 177 ok/0 FAIL; ship 78 ok/0 FAIL (c0: 20/164/78 -> +11 unit, +13 integration = the c1 cases).

## Fail-first (own reproduction; pinned checkout at 1ef80c26 = pre-fix gh-sync.py, tip's two test files laid over via `git checkout b5929a92 -- <tests>`; pin removed)
- Unit: exit 1, exactly 5 FAIL (matches receipt "5 FAILED"):
  - GC-01 source/task alias --yes; source/task alias dry run; source/parent alias --yes; source/parent alias dry run (each "ZERO writes name #41|#40 ... gap naming the flag"; pre-fix output shows reason posted on parent #40).
  - F1 "station write refused: runs/ pruned = False, and the gap is reported".
- Integration: exit 1, exactly 7 FAIL (matches receipt "7 FAILED"): source/task alias --yes (zero gh calls #41), its --yes and dry-run gap reports; source/parent alias --yes (zero calls #40), its --yes and dry-run gap reports; "station write refused (plan.yaml absent): runs/ is preserved...".
- Tier: natural RED (same tests, unmodified production), reproduced by me, corroborated by receipt counts. Not mutation proof.

## Per-finding binding
- F1 -> SC-03/D-02 (prune only after station recorded): unit test-gh-sync-abandon-sources.py:319-334 three-way table: refused (no prune, gap printed), recorded (prune), already-abandoned (prune) = negative with both positive counterparts; integration plan.yaml-absent case (~1225) with the positive prune case FEAT-06-abandon-adopted now staged with `add_plan_station` (assertion unchanged, test-gh-sync-abandon.py:57). Prune assertion is on `("prune", False) in events`, a structured seam log, not stdout.
- GC-01 -> SC-01: unit :282-316 loops source/task alias (41, other 40) and source/parent alias (40, other 41) x {--yes, dry run}; asserts zero writes naming the alias, gap names `--close-sources`, non-aliased entry still disposed, plus positive `--close-sources --yes` (commented once, closed once, reseated, labelled). Integration :1182-1213 same shape on gh call log (`_names(log, n) == []`, includes #52). Both task and parent aliases are discriminated separately.

## Coverage gaps
- None against Phase 1 for F1/GC-01. SC-07 UAT (live #1774) and SC-06 inspection are not QA's; no claim made. c0 advisory gap (SC-01 no-flag + task alias) is now closed by GC-01.

## Limits
- Only my own evidence examined the fix after raising (O-07); no independent second reader of the c1 diff is implied. Unit-kind cmd also exits 0 at 57 files; first unit run was ad hoc re-run for gh-sync lines (same 57).
