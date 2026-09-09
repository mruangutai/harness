# Code review — BUG-151 check-domain fail aggregation — c1 (re-pin at 9b7b27d0)

**BLUF: PASS, clean, no findings on either stage. c0's sole HIGH finding (F-1: the safeguard's own
wiring into `main()`'s discovery loop had zero permanent coverage) is CLOSED — pinned and
non-vacuous, verified independently below. Looked past F-1 for anything the extraction itself could
have broken; found nothing. My measurements agree with the lead's exactly.**

Reviewed diff: `git diff 6d969ed3..9b7b27d074924af2be46194536d6baca4ad4dd18 --
tests/integration/test-check-domain.py` (139+/46-, one file). This is the only file in scope;
`.harness/` bookkeeping and the two out-of-scope sibling suites (R-2) were not read.

## Stage 1 — spec compliance: PASS, no findings

- **REQ-01/SC-01(a)**: `_aggregation_verdict` unchanged from c0's review — `bool(printed) ==
  bool(total)` → `None`, else diagnostic (D-01, agreement-of-zeroness). Untouched by this cycle's
  diff.
- **REQ-02/SC-02 (explicit re-check per this cycle's instruction)**: `run_bug1305_cases` is still
  absent (grep confirms zero matches in the reviewed diff and in the file at the pin). Discovery is
  still `for block_name, block_fn in list(globals().items())` filtered on `startswith("run_")` +
  `callable` — module/dict insertion order, i.e. definition order, never sorted. **No hand-written
  enumeration of block names has come back into `main()`.** The new helper the fix adds,
  `_run_block_captured`, is named with a *leading* underscore (`_run_...`), so
  `"_run_block_captured".startswith("run_")` is `False` — it is correctly invisible to discovery,
  confirmed empirically: the full suite still reports exactly one new `ok` line
  (`[bug151-selfcheck] wiring-seam-catches-print-fail-return-zero`), not two, so no stray block was
  accidentally made discoverable.
- **REQ-03/SC-03/SC-04 (healthy tree unchanged)**: full suite run below — 405 `ok` (404 baseline +
  the one new permanent case), 0 `FAIL`, 0 "aggregation safeguard" lines, exit 0. Matches BRIEF's
  no-false-alarm requirement.
- **REQ-04/SC-05**: comment above the discovery loop (diff context) is untouched by this cycle and
  still reads accurately against the code (already verified at c0; this cycle only edited the
  comment immediately above the discovery loop to name `_run_block_captured()`, which I read against
  the code below it and it matches).
- **Naming convention**: `_run_block_captured` (leading underscore, private helper — correct) and
  `_fake_fail_block` (nested inside `run_bug151_selfcheck_cases`, never module-level — confirmed by
  reading the diff's indentation) are the only two new names. Neither is discoverable, neither
  violates the `run_*` / `_*` convention.
- **Column-0 print convention**: `_fake_fail_block` prints `"FAIL  fake-block-prints-fail-returns-zero"`
  at column 0, but it does so *inside* `contextlib.redirect_stdout(tee)` where `tee`'s real target is
  `io.StringIO()` (the `stream=passthrough` argument) — so this fixture FAIL never reaches the real
  terminal or the outer safeguard. Confirmed empirically: my full-suite run's captured stdout
  contains no `fake-block-prints-fail-returns-zero` line anywhere (SC-04-safe).

## Stage 2(a) — F-1, in two parts, as required

**(i) Is the seam PINNED?** Yes. `_run_block_captured` is defined exactly once
(`tests/integration/test-check-domain.py`, between `_aggregation_verdict` and
`run_bug151_selfcheck_cases`). Both call sites resolve to that single definition via ordinary
module-global lookup at call time: `main()`'s discovery loop calls
`_run_block_captured(block_fn, block_name)`; the permanent case calls
`_run_block_captured(_fake_fail_block, "fake-block", stream=passthrough)`. There is no second,
self-referential copy of the tee/redirect/verdict sequence anywhere in the case — it is the same
function object `main()` uses.

**(ii) Is the case NON-VACUOUS?** Yes, demonstrated independently of the builder's own proof, per
the assignment's preferred technique — importlib-loaded the real module by path twice (control,
mutant) and patched only the *mutant* instance's own `contextlib.redirect_stdout` to a no-op context
manager, without editing the source file:

```
=== CONTROL (real redirect_stdout) ===
... 6 unchanged ok lines ...
ok    [bug151-selfcheck] wiring-seam-catches-print-fail-return-zero
control return: 0

=== MUTANT (redirect_stdout patched to no-op on module m2) ===
... 6 unchanged ok lines ...
FAIL  fake-block-prints-fail-returns-zero
FAIL  [bug151-selfcheck] wiring-seam-catches-print-fail-return-zero
      | verdict=None (seam failed to capture)
mutant return: 1
```

Control returns 0 with `ok [bug151-selfcheck] wiring-seam-…`; mutated returns 1 with
`FAIL [bug151-selfcheck] wiring-seam-…` — matching the lead's own measurement exactly, both in the
printed lines and the return values. **F-1 is closed: PINNED and NON-VACUOUS.**

## Stage 2(b) — past F-1: what the extraction itself could have broken

Hunted fail-open/silent-failure specifically in `_run_block_captured` and its two call sites; no new
findings.

- **`stream=None` default**: `tee = _AggTee(stream if stream is not None else sys.stdout)` resolves
  `sys.stdout` at *call* time (not def time), so `main()`'s real loop (which never passes `stream`)
  ties to whatever the real stdout is; the test's `io.StringIO()` passthrough is honored because
  `stream is not None`. No branch collapses these two paths.
- **Per-block tee freshness**: `tee = _AggTee(...)` is a fresh local object constructed on every
  call to `_run_block_captured` — no accumulation across blocks or across the CASES loop and the
  discovery loop (which use separate tees entirely).
- **Write-through to real stdout**: `_AggTee.write` calls `self.real.write(s)` unconditionally, so
  for `main()`'s call (`stream=None` → real `sys.stdout`) a human watching the run still sees
  verdicts live — confirmed empirically: my full 405-line suite run printed every block's ordinary
  `ok`/`FAIL` output to the captured stdout exactly as before.
- **Exception propagation**: no `try/except` wraps `total = block_fn()` inside
  `_run_block_captured`. An uncaught exception aborts the loop and crashes the process with Python's
  default nonzero exit — this is unchanged from the pre-extraction shape (already noted at c0, not a
  regression introduced by this diff).
- **Label passed to `_aggregation_verdict`**: `main()`'s call passes `block_name` (the discovered
  name) unchanged; the CASES loop (which this diff does not touch — still inlined, per ruling R-3,
  not re-litigated here absent a new drift scenario) still passes the literal `"CASES"`.
- **`(total, verdict)` tuple consumption at the call site**: `total, block_verdict =
  _run_block_captured(...)`; `fails += total`; `if block_verdict is not None:
  problems.append(block_verdict)`; final `return fails + len(problems)` — a safeguard trip alone
  (`fails == 0`, `problems` non-empty) is truthy and non-zero. Confirmed both by my own full-suite
  run (exit 0, 0 problems, correct on a healthy tree) and by the backend-dev receipt's independently
  recorded mutated full-suite run (exit 1, with the printed
  `FAIL  aggregation safeguard: run_bug151_selfcheck_cases: 0 printed column-0 FAIL line(s) vs
  total=1` line) — I did not re-run that mutation myself (one full-suite run budget already spent on
  the control measurement below), but the receipt's transcript is internally consistent with the
  code I read and with my own unit-level mutation above.

### Code-risk grading

Ran the grader against the pinned range (`--base 6d969ed3 --head 9b7b27d0...`, the same true-code
range this review used, not `origin/main`'s stale merge-base): 8 records reported
(`_AggTee.__init__/write/flush/text`, `_aggregation_verdict`, `_run_block_captured`,
`run_bug151_selfcheck_cases`, `run_bug151_selfcheck_cases._fake_fail_block`), all `RESULT: PASS`
against the test-code bar of 3 (worst: `run_bug151_selfcheck_cases` at grade 3, driver
cognitive+abc — the six-case table plus the wiring block, acceptable at the test-code bar). `main()`
itself is not listed: per this checkout's own tooling behavior (repo Expertise G-06), the grader only
emits a record for a function with no pre-image or a *worsened* grade versus base; `main()` had a
pre-image at 6d969ed3 and this extraction strictly reduced its branching (the inline tee/redirect/
verdict sequence moved out), so its grade did not worsen and it is correctly absent, not silently
skipped. Grader exit: 0. `code_grade: pass`.

## Measurement corroboration

Ran the full suite once (budget respected — exactly one run), via `env -u HARNESS_AGENT_TYPE`:

```
returncode 0
ok 405
FAIL 0
aggregation-safeguard-lines 0
stderr-len 0
```

This **matches the lead's reported numbers exactly**: exit 0, 405 column-0 `ok`, 0 column-0 `FAIL`,
0 `aggregation safeguard` lines. No disagreement to report.

## Rulings not re-litigated

R-1, R-2, R-3 stand; nothing in this cycle's diff bears on any of them, and I found no concrete
drift scenario for R-3 (the CASES loop's own inline tee) beyond what was already ruled non-gating.

## Verdict rationale

Stage 1: PASS, zero violations, SC-02's discovery-order requirement explicitly re-checked. Stage 2:
F-1 closed (pinned + non-vacuous, independently reproduced), no new findings from grading the
extraction itself for fail-open behavior. `severity_max: none`.
