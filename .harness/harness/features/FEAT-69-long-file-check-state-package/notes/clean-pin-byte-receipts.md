# FEAT-69 — clean-checkout implementation-pin receipts (reviewed record)

The generated file `notes/clean-pin-byte-receipts.generated.md` is the measurement, committed exactly as `receipt-scripts/feat69-cleanpin.py` wrote it. This file is the operator-facing reading of it and adds nothing the generated file does not carry.

## Identity and chronology

- Implementation pin: `db488aa7c78e392c788bd5839a43ebf4ba562ea1` — the last build commit (T-01 `89c7020e`, T-03 `76723e90`, T-02 `3975a8bf`, simplify pass `264f534a`, amendment 1 `cebe2d69`, amendment 1b `db488aa7`).
- Baseline: `a726bad8f74d23e6c1f07409383bb88d1da8fbcf` — `origin/main` when the worktree was cut (amendment 1 corrected the signed plan's `e6f8493b`, which predates INV-49).
- Checkouts: `.claude/worktrees/harness/feat69-cleanpin-db488aa7` and `.claude/worktrees/harness/feat69-base-a726bad8`, both created detached by the script, both asserted at their SHA with `git status --porcelain` empty before any measurement.
- Chronology: the committed generated receipt is the amendment-2 execution (its `Written` line carries the timestamps); two earlier executions over the same pin and baseline (20:48:57Z–20:51:18Z, 20:52:45Z–20:55:06Z) are superseded and their differences ledgered; the receipt scripts, the generated receipt, this file, `red-first-receipts.md` and `build-divergences.md` were committed together AFTER the pin, in the commit that follows it. Nothing in the pin references any receipt.

## Reproduction, exactly as run

From the worktree root `/Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-69-long-file-check-state-package`:

```
python3 .harness/harness/features/FEAT-69-long-file-check-state-package/notes/receipt-scripts/feat69-cleanpin.py db488aa7 a726bad8
```

That one command creates or reuses both detached checkouts, runs `feat69-baseline.py <checkout> /tmp/feat69-<label>-<sha8>.json` once in each (every measurement executed exactly once per checkout; every byte, sha1, diff line and verdict in the generated file derives from those two JSONs), runs `feat69-grade-assert.py` in the pin checkout (green, with the baseline JSON for moved/new classification) and in the baseline checkout (red), and writes the generated receipt.

## What was measured (SC-02), and the result

Thirteen measurements per checkout: the full-table `check-state.py` run over every feature except this feature's own record (in a scratch copy of the checkout with that directory removed); `check-state.py --list`; the nine owning suites (`test-check-state`, `-entry`, `-plans`, `-records`, `-handoff`, `-worktrees`, `-inv26`, `-feat59`, `-table`); clean-tree `feat62_findings`; clean-tree `consolidation_findings` (`check-plan-routes.py --consolidation-audit`). Comparison after the one normalisation (each checkout's absolute root → `<checkout>`).

- Identical: 13 of 13 — exit status, stdout bytes and stderr bytes — with the full table measured over every feature except this feature's own record (amendment 2, operator-ruled after validate c0; `notes/amendments-2-full-table-scope.md`). The generated receipt's "exact lines" block reads `none`; `build-divergences.md` is empty apart from the superseded executions' record.

## SC-01

Green at the pin: 295 functions over the entry plus twelve package files, 119 at 5 and 176 at 4, none below; the four named functions present and at 4; 287 moved functions with grade kept or raised; 8 new functions at 4–5. Red at the baseline: no package, four functions below 4. Verbatim outputs in `red-first-receipts.md`.

## T-04 `verify:`, verbatim as plan.yaml spells it, and its output (exit 0)

```
python3 -c 'import re,subprocess; rel=".harness/harness/features/FEAT-69-long-file-check-state-package/notes/clean-pin-byte-receipts.generated.md"; receipt_commit=subprocess.check_output(["git","log","-1","--format=%H","HEAD","--",rel],text=True).strip(); assert receipt_commit,"receipt commit not found"; text=subprocess.check_output(["git","show",f"{receipt_commit}:{rel}"],text=True); pins=re.findall(r"(?m)^implementation_pin: ([0-9a-f]{40})$",text); assert len(pins)==1,pins; pin=pins[0]; assert pin!=receipt_commit,"receipt commit must postdate implementation pin"; subprocess.run(["git","merge-base","--is-ancestor",pin,receipt_commit],check=True); subprocess.run(["python3",".harness/harness/features/FEAT-69-long-file-check-state-package/notes/receipt-scripts/feat69-cleanpin.py",pin,"a726bad8"],check=True)'
```

Output (this re-executes the clean-pin script; the generated receipt it rewrote is byte-identical to the committed one apart from its `Written` timestamps):

```
tate-worktrees.py` | 0→0 | 72b810ba8d6f / 72b810ba8d6f | da39a3ee5e6b / da39a3ee5e6b | yes |
| `tests/integration/test-check-state-inv26.py` | 0→0 | edd834ea9673 / edd834ea9673 | da39a3ee5e6b / da39a3ee5e6b | yes |
| `tests/integration/test-check-state-feat59.py` | 0→0 | b74d42ffd34e / b74d42ffd34e | da39a3ee5e6b / da39a3ee5e6b | yes |
| `tests/integration/test-check-state-table.py` | 0→0 | 66f526ae3414 / 66f526ae3414 | da39a3ee5e6b / da39a3ee5e6b | yes |
| `feat62_findings` | 0→0 | 01fc388f4736 / 01fc388f4736 | da39a3ee5e6b / da39a3ee5e6b | yes |
| `consolidation_findings` | 0→0 | 2fb3441a33fe / 2fb3441a33fe | da39a3ee5e6b / da39a3ee5e6b | yes |

All identical (normalised): **yes** (13/13).

### Differences after the one normalisation, exact lines

none

## SC-01: feat69-grade-assert.py at the pin (with the baseline record for moved/new classification) — green

run in the pin checkout → exit 0
```
moved: 287 (grade kept or raised: 287); new: 8 -> [('_inv41_span_invokes', 4), ('_inv41_span_script', 4), ('_inv49_graded', 4), ('_inv49_hits', 4), ('_inv49_unnamed', 5), ('_quoted_escape', 4), ('_comment_hash_at', 5), ('_handoff_done_when', 5)]
295 function(s) over 13 file(s): 5 -> 119, 4 -> 176, 3 -> 0, 2 -> 0, 1 -> 0
GREEN: every function on check-state.py + check_state/** at grade >= 4; required functions present
```

## SC-01 red-first: the same assertion in the baseline checkout — red

run in the baseline checkout → exit 1
```
287 function(s) over 1 file(s): 5 -> 114, 4 -> 169, 3 -> 2, 2 -> 2, 1 -> 0
RED:
  package files present [] != expected ['__init__.py', 'board.py', 'brief.py', 'ctx.py', 'feature_record.py', 'host.py', 'plan.py', 'run_state.py', 'runner.py', 'seams.py', 'table.py', 'worktrees.py']
  below bar 4: [('.claude/skills/harness/bin/check-state.py', '_quoted_scalar_closed', 3), ('.claude/skills/harness/bin/check-state.py', '_unquoted_hash_digit', 2), ('.claude/skills/harness/bin/check-state.py', '_inv41_invocation', 2), ('.claude/skills/harness/bin/check-state.py', 'inv_49', 3)]
```

## code_grade records (from the same two executions)

- baseline: 287 function(s) over ['.claude/skills/harness/bin/check-state.py']; below bar 4: [('_quoted_scalar_closed', 3), ('_unquoted_hash_digit', 2), ('_inv41_invocation', 2), ('inv_49', 3)]
- pin: 295 function(s) over ['.claude/skills/harness/bin/check-state.py', '.claude/skills/harness/bin/check_state/__init__.py', '.claude/skills/harness/bin/check_state/board.py', '.claude/skills/harness/bin/check_state/brief.py', '.claude/skills/harness/bin/check_state/ctx.py', '.claude/skills/harness/bin/check_state/feature_record.py', '.claude/skills/harness/bin/check_state/host.py', '.claude/skills/harness/bin/check_state/plan.py', '.claude/skills/harness/bin/check_state/run_state.py', '.claude/skills/harness/bin/check_state/runner.py', '.claude/skills/harness/bin/check_state/seams.py', '.claude/skills/harness/bin/check_state/table.py', '.claude/skills/harness/bin/check_state/worktrees.py']; below bar 4: []
```
