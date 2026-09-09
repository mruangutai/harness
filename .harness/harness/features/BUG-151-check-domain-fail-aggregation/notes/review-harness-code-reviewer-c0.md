# Code review — BUG-151 check-domain fail aggregation — c0

**BLUF: Stage 1 PASSES clean. Stage 2 finds one HIGH-severity gap: the safeguard's own wiring into
`main()`'s discovery loop has zero permanent regression coverage — a plausible future edit
silently reintroduces the exact defect class this feature exists to close, and I verified this
concretely.** Reviewed diff: `git diff 6d969ed3..e4efd774 -- tests/integration/test-check-domain.py`
(149 lines, +103/-46), the only file in scope. Stage 1 completed and passed before Stage 2 began.

## Stage 1 — spec compliance: PASS, no findings

Checked against BRIEF REQ-01..04/SC-01..05, plan.yaml T-01/T-02, D-01, D-02:

- **REQ-01/SC-01(a)** `_aggregation_verdict` (line ~5197): predicate is exactly
  `bool(printed) == bool(total)` → `None`, else diagnostic — nothing else. Matches D-01
  (agreement-of-zeroness, not strict equality).
- **`run_bug151_selfcheck_cases`** (~5213-5241): all six T-01 step-1 cases present, including
  `two-printed-one-counted-agrees-on-zeroness` named verbatim as the BRIEF suggested. Never prints a
  raw fixture string at column 0 — its own `FAIL` lines print only `name`/`exc`/truncated `verdict`
  text, all indented past the first line. SC-04-safe.
- **REQ-01 step 6**: `return fails + len(problems)` (~5288) — a safeguard trip alone (`fails==0`,
  `problems` non-empty) is truthy, and `sys.exit(1 if main() else 0)` is unchanged. Confirmed non-zero
  exit on a trip-only case.
- **CASES loop** (~5245-5263): wrapped in its own `cases_tee = _AggTee(sys.stdout)` /
  `redirect_stdout`, verdicted via `_aggregation_verdict("CASES", cases_tee.text(), fails)` — same
  treatment as blocks, confirmed the `fails` value at that call site is exactly the CASES-local total
  (blocks loop hasn't run yet).
- **REQ-02/SC-02**: `run_bug1305_cases` composite deleted (grep: zero matches); no hand-written name
  list survives in `main()`; discovery is `for block_name, block_fn in list(globals().items())` —
  dict/module-namespace order == definition order, never sorted. 24 `run_*` defs counted by hand
  (grep `^def run_`), all zero-argument, matching T-02's verify `len(blocks)==24`.
- **REQ-04/SC-05**: false "asserted non-negative" comment (old 5207-5210) deleted; replacement
  (~5269-5274) accurately describes discovery + live-tee capture + D-01/D-02 — verified word-for-word
  against the code it describes.
- **Naming convention preserved**: `bug1304_pre_change_hook`/`bug1304_assert_pre_change_allows`
  untouched by the diff, still non-underscore, still don't start with `run_`, still take required
  args — correctly excluded from discovery, no regression.
- **Column-0 convention**: swept every `print(f?"FAIL` site in the file (24 blocks) — every verdict
  line is `FAIL  ` (two spaces) at column 0, every continuation line indented. No block already
  violates the convention in a way that would falsely trip the new safeguard.
- **Imports/aliases**: no `from X import run_y`-shaped binding anywhere; no module-level `run_`-
  prefixed non-function assignment. Nothing but the intended 24 defs is discoverable.

SC-03 (the numeric no-regression equality) is evidence QA already re-derived independently
(`notes/qa-BUG-151-c0.md`: 398==398, symdiff 0) — not re-run here per the assignment's guidance to
cite, not sweep.

## Stage 2 — code quality

### Checked and cleared (no finding)
- **Partial-line writes across `write()` calls**: `_AggTee.text()` is `"".join(self.parts)`, so a
  column-0 `FAIL` split across two `write()` calls (e.g. content vs. `print`'s trailing `\n`)
  reconstitutes exactly — no truncation risk. Verified by reading `write`/`text`; concatenation is
  order-preserving regardless of call granularity.
- **Per-block reset vs. cumulative**: a fresh `_AggTee(sys.stdout)` is constructed inside the loop
  body for every discovered block and for CASES separately — never cumulative across blocks.
- **Bytes / non-str writes**: not reachable — subprocess output goes through
  `capture_output=True`, never through `sys.stdout`; nothing in this file writes bytes to stdout.
- **Discovered-block exceptions**: no `try/except` around `total = block_fn()`. An uncaught
  exception aborts the remaining discovery loop (later blocks never run) and crashes with Python's
  default nonzero exit (1) — still satisfies "non-zero on failure," and this is **pre-existing**
  behaviour (the old hand-written `fails += run_x()` chain had the identical property). Not a
  regression introduced by this diff; recorded per P-15, not filed as a finding.
- **Imported/aliased `run_`-prefixed callables entering discovery**: swept, none exist.

### Finding — HIGH — the safeguard's own wiring is untested; a plausible edit defeats it silently

`run_bug151_selfcheck_cases` (5213-5241) only unit-tests `_aggregation_verdict` in isolation on
hand-built strings. Nothing in the permanent suite exercises the actual plumbing at the discovery
loop (~5275-5283): `block_tee = _AggTee(sys.stdout)` / `with contextlib.redirect_stdout(block_tee):
total = block_fn()` / `_aggregation_verdict(block_name, block_tee.text(), total)`. That plumbing —
not the predicate alone — is what makes the safeguard see a block's real stdout.

**Verified concretely** (isolated repro, not the real 24 blocks/subprocesses, no source edited):
imported the real `_AggTee`/`_aggregation_verdict` from the pinned file and drove a synthetic block
that prints a column-0 `FAIL` line but returns `0` — precisely BUG-151's original defect shape.
With the `redirect_stdout` wrap intact: `verdict = "...1 printed column-0 FAIL line(s) vs
total=0"` (fires, correct). With the wrap removed (`total = block_fn()` executed without the
`with`, the one-line shape a "simplify this loop" edit would plausibly produce): `block_tee.text()`
is `''`, so `_aggregation_verdict` sees `printed=0`, `total=0`, `bool(0)==bool(0)` → `None` — no
diagnostic, no `fails` contribution, `main()` returns unaffected. The on-screen `FAIL` line is
absorbed exactly as in the original bug report, and **every committed test stays green**, because
none of them exercise `main()`'s loop with a genuine per-block defect — `run_bug151_selfcheck_cases`
tests the predicate only, and QA's own independent monkeypatch confirmation (`notes/qa-BUG-151-c0.md`)
proves the wiring works *today*, not that a regression in it would be caught tomorrow.

This is the sole automated detector for "prints FAIL, returns 0" in a suite that exists specifically
to guard a security-relevant write-domain hook. Per O-06, severity is set by downstream consequence,
not by the fact this trade-off was explicitly plan-authorized (T-01's intent: synthetic-only,
"never on a real suite run"; ruling #1 forecloses committing the 38s end-to-end red proof as a
permanent test) — that ruling correctly forecloses one specific remedy, not the underlying gap.
**I judge this gating.** severity: high.

should_fix (does not reopen ruling #1 — a different, cheap remedy, not the foreclosed 38s red
proof): a synthetic wiring test that injects one temporary fake `run_`-prefixed callable via
`globals()`/monkeypatch, runs it through the *actual* `redirect_stdout(_AggTee(...))` +
`_aggregation_verdict` sequence (extracted or exercised directly, not via a full subprocess run of
the suite), and asserts the diagnostic fires. Sub-second, no 38s cost, closes exactly the gap this
finding names without touching the foreclosed remedy.

## Verdict rationale

Stage 1: PASS, zero violations. Stage 2: one high-severity coverage gap on the safeguard's own
integration path, with a verified concrete mutation. `severity_max: high` → gating per the review
rubric regardless of `must_fix` list contents; I list it there too for consistency.
