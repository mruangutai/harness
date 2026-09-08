# UI Review (Mode B) — BUG-151 check-domain fail aggregation — cycle 1

**Pin:** `9b7b27d074924af2be46194536d6baca4ad4dd18`
**Verdict: PASS.** No user-facing surface beyond terminal text output; that surface holds under
direct execution, and it now closes the exact gap flagged out-of-lens in cycle 0.

## What I opened

- `git diff 6d969ed3..9b7b27d0 -- tests/integration/test-check-domain.py` (full 139+/46-, read
  whole — not the elided summary).
- `BRIEF.md` Constraints (the load-bearing column-0 print convention, quoted below) and SC-01/
  SC-04/SC-05.
- Confirmed **no `DESIGN.md`** exists anywhere under this feature dir (directory listing of the
  full feature tree, zero matches) and no `notes/prototypes/`. This diff answers to no written
  design contract; BRIEF's Constraints section is the only contract, as in c0.
- **Executed the real module**, read-only, no source edits: `env -u HARNESS_AGENT_TYPE python3
  tests/integration/test-check-domain.py`, full ~41s run, output captured via pipe (not a
  redirect — this role is read-only for the write-guard; piping keeps the tree untouched).

## Corroboration of the lead's measurement

Full run at the pin: exit 0, `405` lines matching `^ok    `, `0` lines matching `^FAIL  `, `0`
lines containing `aggregation safeguard`. Matches the lead's cited numbers exactly (404 pre-existing
+ 1 new case = 405; the lead's own control/mutation simulation is consistent with what I observed
live). No disagreement to report.

## Terminal contract — checked point by point, against BRIEF's exact wording

BRIEF: *"Every per-case verdict line starts at column 0 with `ok    ` or `FAIL  `; every detail or
continuation line is indented."*

1. **New case `wiring-seam-catches-print-fail-return-zero` conforms.** Source shows
   `print(f"ok    [bug151-selfcheck] {wiring_name}")` on success (`"ok"` + 4 spaces, column 0) and
   `print(f"FAIL  [bug151-selfcheck] {wiring_name}\n      | verdict=None (seam failed to capture)")`
   on failure (`"FAIL"` + 2 spaces, column 0; continuation indented 6 spaces + `"| "`, identical to
   the pre-existing `"      | {l}"` idiom in the CASES loop). Live run confirms:
   `ok    [bug151-selfcheck] wiring-seam-catches-print-fail-return-zero` at column 0, byte-exact.
2. **Safeguard diagnostic prints at column 0 with `FAIL`.** `print(f"FAIL  aggregation safeguard:
   {problem}")` — same 6-char prefix, so a human `^FAIL`-scanning the transcript still catches it;
   unchanged from c0's finding, this cycle's edit didn't touch that line.
3. **Tee still writes through live.** `_AggTee.write` still does
   `self.parts.append(s); return self.real.write(s)`. The new extraction, `_run_block_captured`,
   defaults `stream` to `sys.stdout` when the caller passes none, and `main()`'s discovery loop
   calls it with no `stream` arg — so on-screen behaviour during the real ~38–41s run is unchanged.
   Confirmed empirically: my run took 41s and printed incrementally rather than only at the end
   (consistent with pass-through, not full buffering).
4. **Fixture leak — does not occur (SC-04).** The new wiring case calls
   `_run_block_captured(_fake_fail_block, "fake-block", stream=passthrough)` with
   `passthrough = io.StringIO()` — an explicit non-default `stream`. Inside `_run_block_captured`,
   `tee = _AggTee(passthrough)`, so the fake block's `print("FAIL  fake-block-prints-fail-returns-
   zero")` is captured by the tee and written through only to the `StringIO`, never to real
   `sys.stdout`. Verified empirically: `grep -c 'fake-block-prints-fail-returns-zero'` over the full
   captured run output = `0`. A human watching or grepping a healthy run never sees the fixture
   string. This is the correct, deliberate design for exercising the seam without polluting the
   transcript.
5. **Naming convention preserved.** `_fake_fail_block` is a nested function defined *inside*
   `run_bug151_selfcheck_cases()`, never module-level, never `run_`-prefixed — so `main()`'s
   `globals().items()` discovery loop cannot pick it up as a second, spurious block. `_run_block_
   captured` is itself `_`-prefixed (private helper), consistent with BRIEF's naming rule.

## Continuity with c0

c0's "out of my lens" note flagged: no permanent test pinned that `main()`'s discovery loop actually
routes captured output through `_AggTee`, as opposed to `_aggregation_verdict`'s predicate alone.
This cycle's fix — extracting `_run_block_captured` and adding the `wiring-seam-catches-print-fail-
return-zero` case that drives a real column-0-FAIL/return-0 block through the literal helper
`main()` calls — closes that gap directly, from this lens's own terminal-contract vantage: the case
proves the discovery-loop's *wiring*, not just the predicate's math, catches BUG-151's exact original
shape. I regard F-1 closed for the terminal-legibility dimension.

## Accessibility / theme parity

Not applicable — batch stdout text, no colour-only state encoding, no rendered surface (repo
Expertise P-03). Stated explicitly, not omitted.

## Findings

None. No `must_fix`. All terminal-contract clauses hold under direct execution at the new pin, not
just source reading.
