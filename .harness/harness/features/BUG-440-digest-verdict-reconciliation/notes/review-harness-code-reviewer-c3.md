# Code Review — BUG-440-digest-verdict-reconciliation — cycle 3 (final)

**BLUF: PASS.** V-01 (the gating complexity finding) is RESOLVED — every changed function at the
pin passes its bar 3 test-code threshold, with margin. The restructure genuinely reduced complexity
rather than relocating it over-bar. One new, non-gating assertion-strength regression was found in
the restructure (informational/low) and is reported below; it does not change the verdict. All
prior clearances and open items (V-02 through V-08, SC-05) carry forward unchanged.

## Pin discipline
- `git rev-parse HEAD` = `442e0d24b25b92b1223eb18b7d16b3a0ff5b3280` (matches assignment pin).
- `git status --porcelain`: only feature-tracking files dirty (`feature.json`, `plan.yaml`, untracked
  `notes/*-c1.md`/`*-c2.md`), nothing under `tests/` or `.claude/skills/`. Source read via `git show`/
  `git diff` per protocol, not the working tree, for every claim below.
- `git diff a1a679..442e0d2 --stat`: **only** `tests/integration/test-check-state.py` changed
  (41 insertions / 22 deletions). Two commits in range, both `[harness:T-01]` — no
  `[harness:human]` commits, nothing to re-review outside the normal chain.
- `.claude/skills/harness/bin/check-state.sh` diff `a1a679..442e0d2`: **0 lines** — byte-identical.
  Cycle-1 spec-compliance clearances (REQ-01..04 incl. (a)-(e), D-07, PF-b884d6ee, SC-07) **carry
  forward by name**, not re-derived.

## V-01 — RESOLVED (was the sole gate)
`code-grade.py --base 772790be5277... --head 442e0d24...`, exit 0, `PASSING: 8`, no `SEVERITY:` /
`RESULT: FAIL` lines for any function:

| line | qualname | cyclo | cognitive | ABC | grade | driver | bar | result |
|---|---|---|---|---|---|---|---|---|
|4618|`_bug440_digest`|2|0|2.4|5|combined|3|PASS|
|4640|`_bug440_build`|3|3|13.8|4|abc|3|PASS|
|4654|`_bug440_validate_fixture`|6|1|20.2|3|abc|3|PASS|
|4666|`_bug440_validator`|1|0|5.0|5|combined|3|PASS|
|4675|`_bug440_mixed_case`|3|1|23.2|3|abc|3|PASS|
|4701|`_bug440_blocking_case`|2|1|6.6|5|combined|3|PASS|
|4709|`_bug440_clean_case`|2|1|6.6|5|combined|3|PASS|
|4717|`case_bug440_digest_verdict_reconciliation`|1|1|6.4|5|combined|3|PASS|

Worst remaining function: `_bug440_mixed_case` (test-check-state.py:4675), grade 3, driven by ABC
23.2 against bar 26 — comfortable margin, not at threshold; cyclomatic (3/10) and cognitive (1/15)
are nowhere near their bars either. **The fix genuinely reduced complexity** — it did not relocate
the original grade-1 function's mass (cyclomatic 22 / cognitive 12 / ABC 55.0 at the cycle-2 pin)
into a new helper that is itself at/over bar. The complexity that remains in `_bug440_mixed_case` is
irreducible assertion-count ABC cost (the seven-clause `all((...))` tuple), not structural nesting.

## Test-code correctness of the restructure (assignment §3)
Enumerated every conjunct of cycle-2's `mixed_ok` against c3's `_bug440_mixed_case` (both read via
`git show`, not working tree):

| c2 conjunct | c3 equivalent | verdict |
|---|---|---|
|`code == 1`|`code == 1`|carried|
|`len(inv37) == 1`|`len(lines) == 1`|carried|
|`len(mismatch) == 1` (inv37 line filtered for `"runs/M" in line`)|**absent**|**dropped** — see below|
|`unchanged`|`unchanged`|carried, still bound to `all()` tuple not `_` (3(b) satisfied)|
|`all(token in mismatch[0] for token in 6 tokens)`|`all(token in line for token in 6 tokens)`|carried, same 6-token set, now reads unfiltered `lines[0]`|
|`not any(f"runs/{n}" in joined for n in 6 silent names)`|`not any(n in joined for n in silent tuple)`|carried, same 6 names|
|`sum("runs/G" in line and "digest.md is missing" in line) == 1` (order-blind AND)|`out.count("runs/G: run is complete but digest.md is missing") == 1`|**strengthened** — contiguous literal substring, not order-blind AND|
|`sum("runs/X/digest.md" in line and "lead digest" in line) == 1`|`out.count("runs/X/digest.md: does not satisfy the lead digest") == 1`|**strengthened**, same reason|

**One genuine drop:** c2 filtered the single INV-37 line for the substring `"runs/M"` before taking
`mismatch[0]`; if that filter matched zero or two+ lines, `mixed_ok` failed outright, independent of
the six-token check. c3's `line = lines[0] if len(lines) == 1 else ""` drops that filter — the six-
token check (which includes bare `"M"` as one token, itself V-04's known order-blind weakness) is now
the only thing tying the line to run M. Traced against the real emitter
(`check-state.sh:1538-1553`): `_rid = os.path.basename(rundir)` and
`dg = os.path.join(rundir, "digest.md")` are both derived from the same `rundir` on adjacent lines,
so no plausible single-point mutation desyncs "run {_rid}" from the `dg` relpath the way V-04's two
adjacent `!r` fields can be transposed. **Rating: low/informational, non-gating** — a real strictness
loss on paper, but not independently exploitable given the emitter's current shape; treat as an
addendum to V-04 rather than a new open item.

(c) confirmed: `case_bug440_digest_verdict_reconciliation` (line 4717) still calls
`all((_bug440_mixed_case(...), _bug440_blocking_case(...), _bug440_clean_case(...)))` — a
materialized tuple, all three always evaluated, none short-circuited or orphaned — and
`ok_bug440 = case_bug440_digest_verdict_reconciliation()` still ANDs into the file's terminal gate
(test-check-state.py:4892, `... and ok_bug1305 and ok_bug440 and ok_i33 ...`).
(d) confirmed: all three sub-case returns are `bool`-typed expressions (`all(...)`, `code==N and
"X" in out`), none can be masked by a truthy non-boolean.

## Fail-open hunt (assignment §4)
`line = lines[0] if len(lines) == 1 else ""` (test-check-state.py:4684): the `""` fallback cannot
create a vacuous pass. `len(lines) == 1` is asserted as an independent conjunct in the same `all()`
tuple, so 0-or-2+ INV-37 lines already fails regardless of `line`'s value; and even if that guard
were absent, `all(token in "" for token in 6 non-empty tokens)` is `False`, not `True` — the fallback
fails closed on both counts. No fail-open here.

## V-02 / V-03 re-binding check
Fixture data is byte-identical to cycle-2 at both binding sites:
- V-02: `_bug440_blocking_case` (4701) still calls `_bug440_validate_fixture(tmp, ("M",), [("M",
  "harness-eng-lead", "complete", ...FAIL...)])` — exactly one run, exit 1 has exactly one possible
  cause. **Still bound.**
- V-03: run X's fixture text is still the literal `"VERDICT: FAIL\n"` in `_bug440_mixed_case`'s
  `runs` list (4682). **Still bound.**

## Carried forward unchanged (not re-derived, per assignment §5)
V-04 (med, OPEN, six-token order-blindness — see also the new low addendum above), V-05 (low, OPEN),
V-06 (info, RESOLVED c2), V-07 (info, OPEN), V-08 (info, OPEN) — all anchored in check-state.sh,
confirmed byte-identical at this pin. SC-05 note staleness (low, OPEN) — unaffected by a test-only
diff.

## Smoke verification
`python3 tests/integration/test-check-state.py` at the pin: `ok - BUG-440 INV-37 reconciles digest
verdicts without mutation`, full-suite exit 0.

## must_fix
None. No `severity_max >= high` item; the one new finding is informational/low and does not gate.
