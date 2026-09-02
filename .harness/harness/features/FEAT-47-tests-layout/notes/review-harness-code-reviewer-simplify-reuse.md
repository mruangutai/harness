# FEAT-47 simplify pass — REUSE angle only

Scope: `origin/main..` diff in this worktree. Read-only, REUSE angle only (no correctness/style
review; that is the code-review stage, separately). Not flaggable: DEC-213 and its D-01..D-19
already settle the `suite_layout.py` / `run-unit-tests.sh` / `tests/manual/suite-census.py` split —
`tests/unit/test-suite-layout.py`'s `SOLE_IMPLEMENTATION_EXEMPTIONS`/`sole_implementations()` sweep
is a signed, tested boundary that names exactly those four sites as allowed to know the
`tests/unit` + `tests/integration` discovery shape. Re-litigating that is noise, so it is not
reported below.

## Finding: the same bin-path resolver is hand-rolled twice per file, across 61 files, introduced
by this diff

**What:** every relocated test file was given a new 4–5 line preamble, immediately after the
module docstring and before its real imports:

```python
import os as _anchor_os, sys as _anchor_sys
_anchor_tests = _anchor_os.path.dirname(_anchor_os.path.abspath(__file__))
_anchor_root = _anchor_os.path.abspath(_anchor_os.path.join(_anchor_tests, "..", ".."))
_anchor_bin = _anchor_os.path.join(_anchor_root, ".claude", "skills", "harness", "bin")
_anchor_sys.path.insert(0, _anchor_bin)
```

61 files carry it (`grep -rl "_anchor_os, sys as _anchor_sys" tests/` — 42 in `tests/integration/`,
19 in `tests/unit/`). On `origin/main` none of this existed; these files just had
`BIN_DIR = os.path.dirname(os.path.abspath(__file__))` because they lived in `bin/` itself
(confirmed against `origin/main:.claude/skills/harness/bin/test-harness-boundary.py:20`).

In the large majority of the 61 (e.g. `tests/unit/test-harness-boundary.py:16-20` vs `:24-26`,
`tests/integration/test-check-domain.py:15-19` vs `:22-28`, `tests/integration/test-validate-digest.py:13-17`
vs `:20`) the file **also** computes `TESTS_DIR` / `ROOT` / `BIN_DIR` / `HERE` a few lines later
using the un-aliased `os`/`sys` — the identical three-step arithmetic (test file → tests dir →
repo root → bin dir), done a second time, under a different name, and the `_anchor_*` block's own
`sys.path.insert(0, _anchor_bin)` is superseded by an identical `sys.path.insert(0, HERE)` a few
lines below it before any bin-relative import is reached. `test-check-domain.py` goes a step
further and recomputes `ROOT` a **third** time at line 28 from `HERE` with a different relative
depth (`"..","..","..",".."`).

In the files with no later block at all — `tests/unit/test-omp-hooks.py:5-9`,
`tests/integration/test-sync-agent-adapters.py:5-9` (used once, via `Path(_anchor_bin)`) — the
`_anchor_*` computation is either the sole live definition (fine on its own, but now spelled
differently from the other 59 files doing the exact same thing) or, in `test-omp-hooks.py`,
entirely dead: nothing in the rest of the file imports from `bin/`, so both the aliased import and
the `sys.path.insert` have zero observable effect.

**Cost:** this feature's own review record for `run-unit-tests.sh` (`git diff` header comment)
demonstrates that `.claude/skills/harness/bin`'s location is exactly the kind of path that gets
moved. A future move now has to be edited in up to 122 near-identical spots (two per file, times
61) under two different spellings (`_anchor_bin` vs `BIN_DIR`), instead of one. The two spellings
also give no signal which one is "real" per file — a future edit is as likely to update only the
`_anchor_*` copy (dead) as the `TESTS_DIR` copy (live), silently breaking nothing today and
silently drifting tomorrow.

**Smallest concrete edit:** delete the `_anchor_*` preamble from all 61 files. In the ~59 files
that also compute `TESTS_DIR`/`ROOT`/`BIN_DIR`/`HERE` a few lines later, that block is already the
complete replacement — no new code needed. In the handful without a later block
(`test-omp-hooks.py`, `test-sync-agent-adapters.py`), replace the one or two later references to
`_anchor_bin`/`_anchor_root` with the file's already-imported `os`/`sys` computing the same path
inline (the same two lines every other file already has as `TESTS_DIR`/`ROOT`/`BIN_DIR`). No
behavioural change either way — the early `sys.path.insert` is provably redundant with the later
one everywhere it isn't simply unused.

## Everything else checked, no finding

- `.claude/skills/harness/bin/suite_layout.py`, `tests/manual/suite-census.py`,
  `tests/integration/test-run-unit-tests-layout.py`, `tests/unit/test-suite-layout.py`: distinct
  responsibilities (production layout gate vs. one-shot migration census vs. runner-interface test
  vs. predicate-interface test), and the overlap between `suite-census.py`'s `tests()` glob and
  `suite_layout.py`'s internal glob is the explicitly reviewed, signed, and test-enforced exception
  (D-16, DEC-213) — not an oversight.
- `run-unit-tests.sh`'s `SCRIPTS=(tests/unit/test-*.py …)` globs vs. `suite_layout.py`'s globs:
  same shape, but this is the caller consuming the predicate's already-established directory
  contract, not a second implementation of the predicate itself — no finding.
- `.harness/harness.json`, `.github/CODEOWNERS`, `.claude/skills/harness/bin/validate-digest.py`:
  prose/config updates consistent with the relocation, no new duplicated logic.
