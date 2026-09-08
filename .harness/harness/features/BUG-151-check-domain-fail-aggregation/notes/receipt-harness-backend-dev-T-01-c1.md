# Receipt — harness-backend-dev — T-01 fix cycle c1 (closes review F-1)

## Shape (one line)

Extracted the discovery loop's tee+redirect_stdout+verdict sequence into
`_run_block_captured(block_fn, label, stream=None)`; `main()`'s loop and a new
`run_bug151_selfcheck_cases()` case both call the SAME function, so unhooking
the capture inside it reddens the permanent suite, not just a self-referential
copy of the logic.

## Change

`tests/integration/test-check-domain.py` only:
- `import io` added to the top import line (for the case's `io.StringIO()` passthrough).
- New `_run_block_captured(block_fn, label, stream=None)` (~5213-5224), between
  `_aggregation_verdict` and `run_bug151_selfcheck_cases`.
- `run_bug151_selfcheck_cases()` extended with one new case,
  `wiring-seam-catches-print-fail-return-zero` (~5233-5259): a locally-defined
  `_fake_fail_block()` (nested inside the case, never module-level, never
  discoverable) prints a column-0 `FAIL` and returns `0` — BUG-151's exact
  original shape — run through the real `_run_block_captured` with
  `stream=io.StringIO()` so its fake FAIL never leaks to real stdout.
- `main()`'s discovery loop (~5314-5320) now calls
  `total, block_verdict = _run_block_captured(block_fn, block_name)` instead of
  inlining tee/redirect_stdout/verdict. Comment above it (~5308-5313) updated to
  name `_run_block_captured()` instead of describing the inlined steps.
- SC-02 preserved: `for block_name, block_fn in list(globals().items())` with the
  `run_*`/callable filter is untouched; no hand-written block list returned.

## TDD: RED observed before GREEN (the deliverable itself)

Step 1: added the case referencing `_run_block_captured` while it was **undefined**.
Ran `m.run_bug151_selfcheck_cases()`:
```
ok    [bug151-selfcheck] printed-fail-zero-total
... (5 more ok lines, unchanged) ...
FAIL  [bug151-selfcheck] wiring-seam-catches-print-fail-return-zero
      | raised NameError("name '_run_block_captured' is not defined")
RETURN 1
```
Step 2: added `_run_block_captured` and rewired `main()`. Same call now GREEN
(RETURN 0, 7 `ok` lines, shown in full below under (a)).

## Acceptance (a) — mutation proof, both directions

Probe: removed the `with contextlib.redirect_stdout(tee):` wrap from
`_run_block_captured`, hashed the file before (`6eb8f932ebe830dcb1394944572d5b54`),
mutated, re-verified, restored, re-hashed — identical hash after restore, and
`git status --porcelain` (final, below) shows only the intended files.

**Mutated — unit call** (`run_bug151_selfcheck_cases()` directly):
```
ok    [bug151-selfcheck] printed-fail-zero-total
ok    [bug151-selfcheck] printed-ok-zero-total
ok    [bug151-selfcheck] printed-fail-nonzero-total
ok    [bug151-selfcheck] printed-ok-nonzero-total
ok    [bug151-selfcheck] indented-fail-does-not-count
ok    [bug151-selfcheck] two-printed-one-counted-agrees-on-zeroness
FAIL  fake-block-prints-fail-returns-zero
FAIL  [bug151-selfcheck] wiring-seam-catches-print-fail-return-zero
      | verdict=None (seam failed to capture)
RETURN 1
```
Note the stray `FAIL  fake-block-prints-fail-returns-zero` at column 0 in that
transcript: with the wrap gone, the fake block's print escapes the tee
entirely (empirical confirmation of assignment trap 4 — the helper's
`stream` passthrough default matters, and under mutation the whole capture
breaks, not just the passthrough).

**Mutated — full suite** (`python3 tests/integration/test-check-domain.py`):
`exit=1`. Relevant lines:
```
FAIL  fake-block-prints-fail-returns-zero
FAIL  [bug151-selfcheck] wiring-seam-catches-print-fail-return-zero
      | verdict=None (seam failed to capture)
FAIL  aggregation safeguard: run_bug151_selfcheck_cases: 0 printed column-0 FAIL line(s) vs total=1
```

**Restored — unit call**: `RETURN 0`, all 7 `ok` lines (shown under TDD step 2).
**Restored — full suite**: `exit=0`, 405 `ok` lines, 0 `FAIL` lines (below).

Mutation observed RED: **yes**, in both the unit call and the full suite, and
GREEN again after restore in both.

## Acceptance (b) — healthy tree unchanged

Predicted before running: baseline (pre-this-change) `ok` count was 404; this
task adds exactly one new case → predicted **405**. Confirmed:
```
exit=0
ok count: 405
FAIL count: 0
"aggregation safeguard" lines: 0
```

## Acceptance (c) — no case lost

Captured `^ok` line names before and after (sed-stripped of the `ok    ` prefix,
sorted):
- before: 404 names
- after: 405 names
- `comm -23 before after` (in before, missing from after): **empty**
- `comm -13 before after` (new in after): exactly
  `[bug151-selfcheck] wiring-seam-catches-print-fail-return-zero`

Before-set is a subset of after-set; nothing renamed or dropped.

## Acceptance (d) — conventions intact

New verdict lines: `ok    [bug151-selfcheck] wiring-seam-catches-print-fail-return-zero`
and, on mismatch, `FAIL  [bug151-selfcheck] wiring-seam-catches-print-fail-return-zero`
followed by an indented `      | ...` detail line — both column-0 `ok`/`FAIL`
plus 4-space-then-content, matching every existing case in the block. New
names: `_run_block_captured` (module-level private helper) and
`_fake_fail_block` (nested inside the case body, non-discoverable — confirmed
by `grep -n "def _fake_fail_block"` showing it indented under
`run_bug151_selfcheck_cases`, not at module level). No new module-level `run_*`.

## Acceptance (e) — no false comment

Updated the discovery-loop comment (~5308-5313) to say the loop "runs under
`_run_block_captured()`" instead of describing the now-extracted inline steps
— read against the code immediately below it, it matches exactly.

## Acceptance (f) — both approved verify commands, verbatim, from worktree root

Cross-checked byte-for-byte against `plan.yaml`'s `tasks[].verify` for T-01 and
T-02 before running — identical to the batch-context strings.

T-01:
```
ok    [bug151-selfcheck] printed-fail-zero-total
ok    [bug151-selfcheck] printed-ok-zero-total
ok    [bug151-selfcheck] printed-fail-nonzero-total
ok    [bug151-selfcheck] printed-ok-nonzero-total
ok    [bug151-selfcheck] indented-fail-does-not-count
ok    [bug151-selfcheck] two-printed-one-counted-agrees-on-zeroness
ok    [bug151-selfcheck] wiring-seam-catches-print-fail-return-zero
PASS
```

T-02:
```
0 405 0 24
PASS
```
(`405` matches predicted; `24` confirms no new module-level `run_*` block;
`0 0` is returncode/FAIL count.)

## Acceptance (g) — working tree

Final `git status --porcelain`:
```
 M .harness/harness/features/BUG-151-check-domain-fail-aggregation/feature.json
 M tests/integration/test-check-domain.py
?? .harness/harness/features/BUG-151-check-domain-fail-aggregation/notes/review-harness-code-reviewer-c0.md
?? .harness/harness/features/BUG-151-check-domain-fail-aggregation/notes/review-harness-qa-c0.md
?? .harness/harness/features/BUG-151-check-domain-fail-aggregation/notes/review-harness-security-reviewer-c0.md
?? .harness/harness/features/BUG-151-check-domain-fail-aggregation/notes/review-harness-ui-reviewer-c0.md
```
`feature.json` and the four review notes were already present/modified before
this dispatch began (lead/reviewer artifacts, not touched by this task — same
as noted in the prior c0 receipt for the analogous BRIEF.md/plan.yaml entries).
This receipt itself will appear as a new `??` entry once written. No commit
made, no branch or HEAD moved. Probe mutation was reverted and byte-verified
(md5 `6eb8f932ebe830dcb1394944572d5b54` before mutation and after restore)
before this status was captured.
