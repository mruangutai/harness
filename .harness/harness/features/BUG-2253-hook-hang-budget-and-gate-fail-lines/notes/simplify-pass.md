# Simplify pass — BUG-2253 T-01

Four read-only reviewer angles (reuse, simplification, correctness, altitude) over `git diff 3769919f 7f62b2d3 -- .claude tests`.

## Applied

| Finding | Angle(s) | Change |
|---|---|---|
| The `FAIL `/`MUTATED ` prefix match also listed per-case `FAIL <label>` lines echoed from a failing file's output | simplification, correctness | The gate matches only run_pool's one-token `(?:FAIL\|MUTATED) \S+` line. The buried case now carries a `FAIL  [x] some case: detail` line that must stay unlisted |
| The block probe's `ready` and whole-run `elapsed < 1.5` checks would flake under the host load this patch addresses | simplification, correctness | Only the real budgeted call is timed (`spent`), so setup and pre-call load no longer count. `ready` is the watchdog's pid channel, not a pass condition: `TimeoutExpired` already proves the child was alive at the budget. The signed budget + 0.5s bound stands |
| The hand-rolled globals rebinder silently added a misspelled name | reuse, simplification | `mock.patch.multiple` (raises on an unknown name). The budget alone is rebound with `create=True`, so a tree without the constant fails per site instead of crashing the group |
| The duplicated "other call" double | reuse, simplification | One `_bug2253_doubles(target, budgeted)` |
| Duplicated write+chmod, and unclosed `open().write()` | reuse | `_bug2253_executable` over `_write_verification_brief` |
| Docstrings: the drivers' return shape, the watchdog's role, the "passing control" claim, and an exception class used as a sentinel | altitude | Corrected. The sentinel is gone with the rebinder |

## Declined

- Dropping the second rebound value (0.10): kept, because the signed intent names both 0.05 and 0.10.

## Rework after validate cycle 1 (FAIL, run 2026-11-21-02-validate-validator)

Two of the simplify-pass changes above were unsound and are superseded:

- **One-token file-line regex → structural parse.** run_pool emits raw names, which may contain spaces (`MUTATED notes/my file.md`). The gate now walks run_pool's blocks: `FAIL <name>` counts only when it closes the open `----- <name> (exit N, Ss) -----` block, and `MUTATED <name>` counts only outside every block. Echoed case lines inside a block never qualify, whatever their shape. The regression covers names with spaces and in-block `FAIL`/`MUTATED` echoes.
- **Readiness dropped as a pass condition → restored.** The blocked-hook rows again require the child to have written its pid. The one-shot timer is replaced by a polling watchdog: from 2s until the probe ends it kills the child the moment its pid appears, so a late-starting child under a timeout that ignores the budget cannot survive. A containment case proves this with a 2.5s-delayed child under a 60s timeout.

Call-only timing stays (validated as sound). Receipts: `receipts/red-c2.*` and `receipts/green-c2.*`, with exact subject SHAs, a subject hash and separate streams. The cycle-1 receipts are left unchanged.

## Rework 2 after validate cycle 1 regate (FAIL, run 2026-11-21-03-validate-validator)

The operator extended the budget to 2 rounds / 70 min (`notes/rework-extension-2026-11-21.md`).

- **SC-01, echoed headers.** A file's echoed header-shaped line used to open a block that never closed, so the real `FAIL` was lost. Now:
  - A `PASS`/`FAIL <name>` line pops back to its own header (`_closes_failed_block`), which discards stray echoed headers.
  - `MUTATED` lines are taken as the run directly above run_pool's mutation note (`_run_pool_mutated_indexes`), not by block depth.
  - Regression: `_bug2253_echoed_header_case`, with unclosed echoed headers inside a failing block and inside a passing block.
- **SC-02, readiness-independent containment.** At the 2s deadline the watchdog now kills every direct child of the test process, with no pid handshake. The probe runs one hook at a time, so that child is the probed one. Readiness stays a pass condition of the block rows. Regression: `_bug2253_containment_cases`, with a 2.5s-delayed child and a never-ready child under a 60s timeout. Both must die before readiness, within 5s.
- Receipts:
  - `receipts/red-c3.*`: exact base, 14 failing.
  - `receipts/discriminate-c3.*`: the cycle-1 gate 6cbdc417 under the final tests; only the echoed-header case fails.
  - `receipts/green-c3.*`: fix b228c3a2, clean; the group and the full file pass.
- The unit-kind advisory is filed as #2281, per the operator.

## Rework 3 after validate cycle 2 (FAIL, run 2026-11-21-04-validate-validator)

SC-02 is met. For SC-01, a same-name `PASS` echoed inside a file's own block closed it early, which hid the genuine `FAIL`.

Pairing headers with closes cannot survive every verbatim echo, so the gate no longer pairs (`_is_failed_file_line`). `FAIL <name>` counts once any earlier run_pool header named that file, and nothing un-names it. `MUTATED` keeps the note-adjacency rule. The rule errs only toward listing.

The regression `_bug2253_echoed_header_case` adds same-name `PASS` echoes before both genuine closes.

Receipts:
- `receipts/red-c4.*`: exact base, 14 failing.
- `receipts/discriminate-c4.*`: the cycle-2 gate b228c3a2 under the final tests; only the echo case fails.
- `receipts/green-c4.*`: fix 3c6fb908, clean; the group and the full file pass.
