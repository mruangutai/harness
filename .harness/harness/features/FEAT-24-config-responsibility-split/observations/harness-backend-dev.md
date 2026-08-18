# Observations — harness-backend-dev — FEAT-24

- 2026-08-18: T-02 c2 mutation sweep, headline finding. No fixture in `test-factory-config.py`
  exercises "remote read raises AND a checkout exists on disk" — the two closest fixtures cover
  disjoint halves (remote fails / no checkout; remote succeeds / checkout present). A
  fallback-to-checkout-on-failure implementation of `product_config` passes 78/78, contradicting
  the module's own "no fallback, no default" docstring. F-5 in
  `notes/receipt-harness-backend-dev-T-02-c2.md`.
- 2026-08-18: T-02 c2 mutation sweep. A "reddens exactly one case" claim from the c1 receipt about
  `_STATION_KEYS` was wrong — dropping a station key breaks all five `accepts...` cases at once
  (set-equality collateral), only the `rejects missing <k>` cases are truly key-specific. Full
  finding F-1 in `notes/receipt-harness-backend-dev-T-02-c2.md`.
- 2026-08-18: two fixtures in `test-factory-config.py` call `fc.board_for(...)` with no
  `try/except` (lines ~464-465, ~480) — a mutation that makes those specific calls raise crashes
  the module instead of producing a named FAIL line for that case. Worked around by mutating for a
  wrong VALUE instead of a raise where that mattered (mutation 6 in the c2 receipt). Same class of
  fragility as the module-death pathology the T-02 c2 dispatch warned about, just triggered from
  inside the fixture rather than from an import failure.
- 2026-08-18: the "raises naming repo, path and ref" case's ref assertion is satisfied by either
  `human_path` (the FleetError value slot) or `next_step`'s own `at {ref}` clause — removing ref
  from only one of the two leaves the case green. F-4 in the same receipt.
- 2026-08-18: T-03. `factory_decompose._validate_stations` (unchanged source) already validates
  EVERY declared station key against the live board's options, not just ready/building/review —
  so migrating `test-factory-decompose.py`'s fixtures to D-06's five-key stations map required
  widening `Recorder.field_options` to five options too, or every decompose case failed with
  "station option not offered: backlog='Backlog'". `test-factory-claim.py` and
  `test-factory-land.py` did NOT need this: claim only validates ready/building/review (three),
  and land never validates at all (direct `board["stations"]["review"]` index). Same five-key
  requirement, three different blast radii depending on which tool's own (unrelated to this
  task) validation breadth you're fixturing against.
- 2026-08-18: fix-c2. Writing a RED case that calls `file_at_ref` bare (no try/except) and asserts
  on the return value crashes the whole test script with an unhandled `GhError` traceback the
  moment the mutation makes it raise — every case after it in file order never runs, and the runner
  still reports the earlier cases as `ok`, which can misleadingly look like a clean single-case
  reddening in a truncated view. Wrap ANY new happy-path `file_at_ref`/similar call in
  try/except and compare against a sentinel, even when you expect it never to raise post-fix —
  that's what let the actual RED run (`1 of 163 FAILING`) stay legible instead of stopping the
  script partway through.
- 2026-08-18: fix-c2. Setting `validate=False` in the b64decode call (even briefly, to test whether
  the existing "undecodable content" case discriminates the `validate` flag) tripped the auto-mode
  Bash classifier — it blocked running the test suite while that line was in place. Verified the
  discrimination question a different way instead (`base64.b64decode(s, validate=False)` on the
  bare string in an isolated `python3 -c` snippet, not touching the source file): `"not-valid-base64!!!"`
  raises under BOTH `validate=True` and `validate=False` (a padding error either way), so that
  existing case proves nothing about the `validate` flag itself.
- 2026-08-18: fix-c2. The commit an orchestrator makes after a member's edits stabilize can land
  faster than the member's own return — `git log` showed my exact 2-line diff already committed as
  HEAD mid-session, before I'd called advisor() or returned anything. Don't assume "the tree is
  still uncommitted, per my dispatch" without checking `git status`/`git log` again right before
  reporting; the dispatch's stated branch/commit can go stale during your own run.
- 2026-08-18: T-03. `test-factory-integration.py`'s `factory_config.py --show` path does not
  call `board_for`/`product_config` at all — it just echoes `fleet["repos"]` verbatim. The
  D-config integration case therefore needed NO gh stubbing once the fleet fixture stopped
  carrying `board`; the only change there was inverting the assertion that used to read
  `payload["repos"][0]["board"]["number"]`. Worth checking whether a tool actually resolves a
  board before assuming an integration fixture needs the `contents` fake-gh plumbing.
