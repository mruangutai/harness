# FEAT-48 re-plan — the panel answered, finding by finding

## BLUF

`D-09` is rewritten: **FEAT-48 ships whole and first**, against today's array-driven
`run-unit-tests.sh`. No task waits on FEAT-47, so VL-01's census deadlock and F-06's unenforceable
cross-feature edge both dissolve rather than being patched. **The `bin/test-*.py` list in the batch
contract is UNCHANGED** — still exactly `test-suite-independence.py` and `test-run-pool.py`, plus the
non-test helpers `isolated_bin.py` and `run_pool.py` which stay in `bin/`. The old T-04 is split:
T-04 builds `run_pool.py` and its test, **T-06** (new) wires the runner, registers the integration
test and records the measurements. `T-05` now depends on `T-06`.

Every verify block that changed was **proved by mutation**, not by reading: a reference
implementation was built in `/tmp`, each block run green against it, then each new conjunct broken
one at a time and observed to redden. Evidence is in the table at the bottom.

## Disposition of every finding

| id | disposition | where |
|---|---|---|
| VL-01 | **fixed by ordering.** FEAT-48 lands first and whole; FEAT-47 absorbs both new test files into its move set and counts. Contract stated in `D-09` and BRIEF `## Constraints` | `plan.yaml` D-09 |
| F-01 | **fixed.** `resolve_scan_root(start)` calls `harness_boundary.root_above(dirname(realpath(__file__)))` and exits 2 when it returns None. Not `root_from_script` (`:44-50`, pure arithmetic, the thing that breaks on a move); not `resolve_root` (`:53-79`, reads `HARNESS_PROJECT_DIR`, so a stray override aims the scan at another checkout). `root_above` (`:83-98`) is a marker walk with no depth arithmetic and no env read | T-03 intent, verify asserts printed `root` == `git rev-parse --show-toplevel` |
| F-02 | **fixed, and the rationale now agrees with the paths.** Under the new order `bin/` is correct because FEAT-47 has not run, not by accident. T-04 is told not to branch on FEAT-47's layout at all | T-04 intent |
| F-03 | **fixed, and made stronger than the reader asked.** `>= 8` is gone. The block asserts each of the ten sites individually (`want - sites` empty), not a count. It deliberately does NOT forbid extra findings on the three historical files — the false-positive gate is the LIVE half, where an over-reporting scanner cannot reach zero | T-03 verify + intent |
| F-04 | **fixed.** The guard prints `root <abs>` and `discovered <n>` in both modes; the plan-level verify requires exactly one of each, `discovered >= 50`, and the root to equal the repo top. A walk that finds nothing now reddens at the plan level, not only inside the unwritten file | T-03 verify |
| F-05 | **fixed.** T-04's verify no longer trusts `test-run-pool.py`'s exit code: it builds its own fixtures, drives `run_pool.py` directly and independently reconstructs attribution, failure propagation, the reported worker count, the mutation check reddening, and the non-checkout exit 2 | T-04 verify |
| F-06 | **dissolved.** There is no cross-feature edge left to enforce | `D-09` |
| F-07 | **fixed as far as a file can be.** T-06's verify parses the measurements note: ten `run <i> exit <rc> <wall>s` rows all zero, `control broken reads` > 0, `post-fix broken reads 0`, a `pool:` line at or under 120s, and the `PASS test-suite-independence.py` line. What it cannot prove is that the numbers were measured rather than typed; the note carries fenced verbatim output for the reviewer, and BRIEF `## Verification gaps` says so plainly | T-06 verify, BRIEF |
| F-08 | **fixed.** BRIEF SC-09 no longer cites `--check`; it names the `--stdout`-into-comparison form and cites `gen-decisions-index.py:9-10` and `:253-259` | BRIEF SC-09 |
| F-09 | **fixed.** T-05's verify slices the section under the entry's own heading (bounded both sides by the next `## DEC-`), requires fourteen phrases INSIDE it, and imposes a 300-word floor. A stub naming the phrases fails | T-05 verify |
| reader's dismissals (orphan traces, intra-plan DAG, the `\| grep .` idiom, T-02's `except OSError`, T-02 launch failure, the taint rule set) | **accepted as dismissed**, re-checked only where the re-plan moved something: the DAG is now T-01 -> T-02 -> T-03 -> T-04 -> T-06 -> T-05 and still linear; no `\| grep .` idiom was introduced | — |
| lead's dismissals (`old.returncode` ambiguity, the `:1482` anchor, FEAT-47 scope, PYTHONPATH direction) | **accepted**, unchanged | — |

## The independent reader's low finding: ADOPTED, as `D-11`

The proposal was right and its reasoning is recorded in `D-11`. `REQ-01` was enforced at runtime
exactly once — at fix time — and thereafter only by a static scan whose blind spots this feature's
own research note documents (`research-FEAT-48-independence-invariant.md:137-140`: subprocess calls
are not sinks; and taint does not cross a call boundary, so a mutation wrapped in a helper is
invisible).

`run_pool.py --mutation-check ROOT` snapshots `(size, st_mtime_ns)` for every `git ls-files` path
before the first child and after the last, prints `MUTATED <path>` for each difference, and fails
the run. Measured cost: **14ms for 2,069 tracked files**, twice, against a ~47s run.

Proved, not assumed — a reference implementation caught a write made by
`subprocess.run(['sh','-c','echo y >> t.txt'])`, the exact vector the static scan cannot see:

```
MUTATED /var/folders/.../t.txt
run_pool: a tracked file changed while the suite ran — this violates REQ-01.
```

Three design points that are the difference between a gate and a decoration:

- **The flag is not optional in the one caller CI runs.** `run-unit-tests.sh` always passes it, and
  T-06's verify asserts the flag is on that invocation line — otherwise "off" is a silent state.
- **A non-checkout root exits 2**, never "clean". An empty snapshot that reports no findings is the
  #979 shape all over again.
- **The trade is accepted, not hidden.** Editing a tracked file by hand DURING a run trips it; the
  failure line says so. Narrowing the watched set is what makes a guard blind.

New `SC-10` grades it, including the subprocess leg and the non-checkout leg.

## Mutation evidence

Reference implementations under `/tmp/f48proof` and `/tmp/f48scan`; blocks extracted from
`plan.yaml` verbatim via `harness_yaml.load_plan`.

| block | mutation | result |
|---|---|---|
| T-03 | (correct implementation) | **exit 0** |
| T-03 | root resolved two levels too high | exit 1 |
| T-03 | discovery returns zero files | exit 1 |
| T-03 | scanner loses one of the ten sites | exit 1 |
| T-03 | run against the UNFIXED live tree (pre T-01/T-02) | exit 1 |
| T-04 | (correct implementation) | **exit 0** |
| T-04 | output streamed instead of block-buffered | exit 1 |
| T-04 | mutation check disabled | exit 1 |
| T-04 | empty snapshot instead of exit 2 when git fails | exit 1 |
| T-04 | one queued file skipped | exit 1 |
| T-04 | `HARNESS_TEST_WORKERS` ignored | exit 1 |
| T-04 | failing child dropped from the verdict | exit 1 |
| T-06 | (compliant runner + note) | **exit 0** |
| T-06 | `--mutation-check` dropped from the invocation | exit 1 |
| T-06 | serial `for` loop survives beside the pool | exit 1 |
| T-06 | integration test unregistered | exit 1 |
| T-06 | nine runs / one run failed / zero control / 147s wall / no SC-04 line / no note | exit 1 each |

`check-plan-routes.py` on the plan: **0 violations**; six `DEVIATION` lines, all the DEC-174
carve-out the `lanes:` block declares by design.

## Open, for the tier above

- The five `panel_friction` items in the validator digest (PF-A..PF-E) are harness defects, not plan
  defects; PF-A structurally blocks `harness-code-reviewer` from yielding on any unsigned plan.
  Carried up in the DIGEST, fixed nowhere here.
- FEAT-47's T-06 verify uses `gen-decisions-index.py --check` (does not exist) and the
  `\| grep .` masked-status idiom. Routed to the FEAT-47 re-plan directly; not touched here.
- Both `## Approval` and `approval:` remain **pending**. Re-planning after the panel resets nothing
  because nothing was ever signed.
