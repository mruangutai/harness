# Code review — plan c0

**BLUF:** FAIL. The architecture and traceability otherwise carry the confirmed package ownership, combined transitive lock, scanner/test/fixture/consumer migrations, grade repairs, byte-identity proof, nine suites, clean-tree runs, main-session-direct routing, and pending approval. One terminal proof command targets the wrong commit after the receipt commit it requires.

## Finding

1. **high · substance** — `plan.yaml:136-139,148` / SC-01, SC-02, SC-04: T-04 requires receipt scripts and receipts to be committed only after the immutable implementation pin, but its verify command passes `$(git rev-parse HEAD)` as the pin. Once T-04 completes its own required receipt commit, HEAD is the later receipt commit rather than the implementation pin. The terminal gate therefore measures a different tree and cannot prove the named immutable pin's byte identity, grade, or receipt chronology. Make the terminal verify resolve and pass the recorded implementation-pin SHA independently of HEAD (and assert the receipt commit postdates it).

## Traceability and architecture

- No orphan SC ids or nonexistent traces: T-01 through T-04 cover SC-01 through SC-04, and every task serves the live package split, package-aware enforcement, compatibility migration, or immutable proof requirement.
- Dependencies are topological: T-02 consumes T-01's package, T-03 consumes the package and package-aware locks, and T-04 follows all implementation/test migration work.
- Apart from the T-04 HEAD collision above, no successor invalidates an earlier task-local gate; T-04 is intended to rerun the complete terminal evidence set.
- The design has useful depth and locality: the unchanged forked entry is the interface; `table.py` owns selection discretion, `runner.py` execution, `ctx.py` shared context, and read-family modules invariant logic. The combined module-qualified call graph is the enforcement seam needed to preserve transitive declared-read checks across imports; it is not a pass-through adapter layer.
- The plan explicitly carries the operator-set eight-family ownership and order, runner boundaries, package-aware FEAT-62 transitive walk and reads-family rule, both text scanners, every named scratch copy/patch site, the ten fixture re-keys, external consumers, per-package-file broad-catch mutants, all four below-grade functions, exact receipts, all nine suites, both clean-tree runs, the roughly 150-line entry budget, `cross_module` plus `main-session-direct` on every task, and pending approval.

## Open questions

None.
