# Handoff — FEAT-48, validate → ship — written at e64e863e, seq-5

## Next

**Do not ship. Three main-session-direct items, then a re-validation scoped to the touched code.**
The c8 panel (`runs/2026-09-02-c8-validator/digest.md`) — the first review the fix commit has had —
returned FAIL, `severity_max: high`, two `must_fix`. **(1) `code_grade: fail`** over
`d135364e..e64e863e`: 9 blocking records, three `high` (`run_pool.py main`,
`test-suite-independence.py _sink`, `:170 run_self_tests` at CYC 14 / COG 29 / ABC 49.7); a
non-relocating decomposition of `run_self_tests` preserves coverage verbatim. **(2)
`run_pool.py:37-38`**: the directory-symlink `os.lstat` has no `OSError` guard where the file loop
below does, so a failure there aborts the pool run — one edit with (1), same function.
**(3) SC-03's operator signature**: pm grades 9/10 SCs MET and SC-03 `unmeetable-as-written`,
recommending remedy **(B)** — the ten `ea6f51f` sites become a review-time automated check, under
which SC-03 reads MET at `e64e863e` with no code left to write. Not a fix cycle, not mine to waive.

## Trust

- All six in-file cases run unconditionally in CI and **all six DISCRIMINATE** — three monkeypatch
  probes, no edit to the checkout: blinding `scan_file` reddens the three red cases, an over-eager
  `scan_file` also reddens clean-controls and live-tree, patching `resolve_scan_root` reddens
  live-tree and root-refusal; never-red cases: NONE — `test-suite-independence.py:170-266` — mine,
  verified-at e64e863e.
- The c7 symlink HIGH (M1) is closed **with a red proof**: the same probe against
  `git show b86ce66a:run_pool.py` gives exit 0 / no MUTATED for a dangling AND a directory symlink,
  the shipped copy gives `exit 1 MUTATED dangling` and `MUTATED linked-dir`, and the clean control
  stays exit 0 in both — no false positive traded — mine, verified-at e64e863e.
- `run_pool.py:37-38` raises `FileNotFoundError` **out of** `snapshot()` when lstat fails on a
  directory symlink while the same injected failure at `:44-47` is swallowed — deterministic fault
  injection pinning `islink` True, not a raced repro — mine, verified-at e64e863e.
- **All 9 `code_grade` records are FEAT-48's own**: `gated_set` gates only a record with no
  pre-image or a WORSENED grade (`code_grade.py:427-431`) and 7 of 9 sit in three files absent from
  `main`, so the c8 review's "7 pre-existing" partition — retracted by its own lead — was
  unrepresentable — mine, verified-at e64e863e.
- SC-01 MET (`feature_schema.py` mtime_ns/size/sha256 identical after `test-check-domain.py` exit 0
  — never written, not restored); SC-04 MET (`--kind unit` exit 0, 33 files, emits its PASS line);
  SC-09 MET (DEC-211 carries all five items, the index is `cmp`-identical); suite green (`--kind
  all` exit 0, 63 files, 48.87s, zero FAIL/MUTATED, clean tree) — mine, verified-at e64e863e.
- SC-02, SC-05..SC-08, SC-10 MET on evidence pm re-took at the pin, incl. ten post-rewrite
  `--kind all` runs — `notes/research-FEAT-48-goalcheck-validate-c8.md` — pm's, not mine.
- M5 (same-size + restored-mtime swap) and M4 (no `__pycache__` leg) stay open at MED, and
  DEC-211:6601-6602 **overclaims** content-derived writes are caught — theirs, verified-at e64e863e.

## Dead ends

- Do not route any remedy to a dev squad: `.claude/skills/harness/bin/**` is `main-session-direct`
  by DEC-174 policy carve-out, not absence of a grant — `plan.yaml:15-23` — verified-at e64e863e.
- Do not re-run the six cases or re-litigate SC-03's first half — this note's Trust — at e64e863e.
- Do not call any `code_grade` record pre-existing debt — `code_grade.py:427-431` — at e64e863e.
- Do not read a red suite as a FEAT-48 defect before unsetting `HARNESS_AGENT_TYPE`, which fails 11
  checks in `test-plan-merge.py`, a file not in the diff — mine, verified-at e64e863e.
- Do not hand SC-03's ten-site clause back as a coding oversight — `.github/workflows/tests.yml:50`
  puts `ea6f51f` out of a bare `actions/checkout@v4`'s reach — verified-at e64e863e.

## Working set

- `.claude/skills/harness/bin/run_pool.py` (`snapshot` :29, unguarded `lstat` :37-38)
- `.claude/skills/harness/bin/test-suite-independence.py` (`run_self_tests` :170)
- `runs/2026-09-02-c8-validator/digest.md` · `notes/research-FEAT-48-goalcheck-validate-c8.md`
