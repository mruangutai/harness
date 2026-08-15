# Security review — PR #385 (detector hygiene), 3c75aa6..a714bd0

**Verdict: PASS.** Scoped IN (both flagged surfaces assessed, not assumed clean) — zero
findings, severity info.

**Provenance:** working tree at `HEAD` = `a714bd0` (`git rev-parse HEAD`), confirmed by
`git diff a714bd0 --name-only` returning empty for all 8 changed paths — Read/grep results
below are valid for the pinned SHA, not a stale checkout.

## Census
`git diff --name-status 3c75aa6..a714bd0` returns exactly the eight paths Mike listed. No
undisclosed files.

## Surface 1 — `layout_fixtures.py` (fixture writes, path traversal / shell / value leak)
- `STUB`, `FEATURES_READERS`, `DOCS_READERS` keys/values are hardcoded string literals
  authored in this file — repo-relative paths with no `..` segments, no absolute paths, not
  derived from any runtime/external input. Consumers (`test-layout-migration.py:88-100`,
  `test-check-state.py:1595-1599,2730-2771`) join `rel` (always one of the fixed literals)
  onto a tmp sandbox root — cannot escape the sandbox.
- Checked every `subprocess.run` in both test files (17 call sites): all list-form argv, no
  `shell=True`, none pass `STUB`/`FLEET_TEXT` content as a command argument — fixture
  strings are written to files, then `check-state.sh` is invoked separately against the
  sandbox and reads the files itself.
- `FLEET_TEXT` contains `workspace_root: /tmp/harness-fixture-workspaces`. Traced the
  consumer: `layout_migration.py`'s only fleet read (`_declared_repos`, line ~145-152) pulls
  `fleet.get("repos")` and nothing else — `workspace_root` is never read by the detector or
  by `check-state.sh`. It is schema filler required by the fleet YAML shape, matched as
  inert text, never consumed as a write root by anything in this diff's surface.
- **Confirmed: no path traversal, no shell injection, no live use of the `/tmp` value.**

## Surface 2 — `check-state.sh` INV-27 wording + `layout_migration.py:blame()`
- The diff extracts a duplicated blame computation (present twice pre-change: inline in
  `render()` and inline in `check-state.sh`, issue #379) into one `blame(rep)` function
  called from both sites. **This is a behavior change, not a pure relocation**: pre-change,
  `check-state.sh`'s `unreadable`/`neither` finding text was filtered via `_tagged(_form)`
  to readers matching that one form; post-change it renders `blame(rep)` whole (the diff's
  own comment: "No per-form filtering here"). Findings can now name more readers than
  before for the `unreadable`/`neither` cases specifically.
  - Security effect: none. The printable set is still bounded by `READER_TABLE`'s static
    reader paths and the fixed form enum (`legacy|migrated|both|neither|unreadable`) — no
    new field, no attacker-influenced content enters the line. The `render()` path (used at
    session entry) already rendered the unfiltered `blame()` set for MIXED with no
    single-form-disagreeing reader pre-change, so the unfiltered shape was already reachable
    pre-diff via the other call site; #379's point is exactly that the two sites must not
    diverge.
- `"%s [%s]" % (p, f)` is a static format string with tuple args — not attacker-controlled,
  no format-string injection.
- `p` values originate from `READER_TABLE` (`layout_migration.py:74`), hardcoded
  repo-relative paths (e.g. `.harness/team-config.yaml`) — same literal class as Surface 1.
  Never an absolute path, never `root`, never an environment value.
- **Pre-existing, unchanged by this diff, recorded per P-12 rather than omitted:** the
  sibling `no-evidence` finding (`check-state.sh`, both base and pinned SHA, line
  1304→1305 — identical text, only a line-number shift from the surrounding diff hunk)
  prints `f"no evidence of either shape under {root}"`, where `root` is an absolute
  filesystem path (home-dir-bearing at session entry). This is a real absolute-path
  disclosure into a printed finding, but it predates this diff and is untouched by it —
  assessed and dismissed as out of scope for *this* review, not denied.
- **Confirmed: no new injection hazard; the one behavior change (wider blame set) carries
  no new security-relevant content; the one absolute-path leak in the surrounding code is
  pre-existing and unchanged.**

## Routine sweeps
- Secret/credential sweep over the full diff (`grep -inE
  'api[_-]?key|secret|token|password|BEGIN (RSA|OPENSSH|PGP)|Authorization:|Bearer '`):
  zero hits.
- CI workflow / hook registration: `git diff --name-only` shows no `.github`, no
  `.claude/settings.json`, no hook file touched — confirmed none.
- `plan.yaml`, `DECISIONS.md`, `.harness/logs/2026-08-14.md` changes are prose-only
  (narrowing a claim per issue #366, logging the merge) — no code, no security surface.

## Scope reasoning
Dispatch named two surfaces as not-automatically-out-of-scope; both were traced to their
consumers (not assumed) and both close clean, with one real behavior change identified and
argued safe, and one pre-existing leak recorded rather than silently dropped. That is
scoped-IN work with a zero-finding result, not a scope-out.

Pre-briefed items (#365, #367, #368-375, #377, #378, #380, #381, #384, #279) not re-filed.
Duplicate `case_x` defs in test-check-state.py (already found by Mike) not re-derived.
