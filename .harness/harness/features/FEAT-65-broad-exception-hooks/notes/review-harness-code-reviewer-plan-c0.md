# FEAT-65 plan scope and architecture review

## Verdict

**FAIL.** The mission is warranted and the four cohorts cover the live 77-site requirement without an orphan task, but two execution contradictions prevent the plan from producing its promised evidence and preserving existing non-hook behavior.

## Findings

1. **Clean-pin receipt is self-invalidating**
   - reader: code-reviewer
   - scope: task
   - severity: high
   - kind: substance
   - refs: SC-08, D-05, T-04
   - consequence: T-04 requires `notes/clean-pin-byte-receipts.md` to exist at, and name, the exact eventual `review_sha`, but Harness pins `review_sha` only after all build tasks and the simplify pass. If T-04 writes the receipt before pinning, it cannot name the eventual pin; if it writes or amends the tracked receipt after pinning, the resulting commit changes the SHA and the receipt is no longer present at the SHA it names. Thus no clean checkout of the reviewed commit can contain the promised exact-pin receipt, and T-04 cannot produce its own clean-pin evidence.
   - recommendation: make clean-checkout execution a post-pin validation responsibility whose immutable output lives outside the reviewed commit, or weaken SC-08/D-05 to a reproducible pre-pin receipt that records the tested commit and is then reviewed at a later pin. Do not require a tracked file to contain its own commit ID.

2. **The single guard seam has no hook/direct invocation discriminator for shared command programs**
   - reader: code-reviewer
   - scope: task
   - severity: high
   - kind: substance
   - refs: SC-02, D-01, D-02, T-03
   - consequence: SC-02 requires unexpected failures in every one of the eleven programs, including `feature-record.py` and `inflight_registry.py`, to reach `hook_guard`; T-03 likewise says the nine programs route unexpected defects through it. Both are also direct command programs with authoritative callers, and `.omp/extensions/harness-hooks.ts` invokes them without a hook-mode argument (`feature-record.py` at lines 1159–1165; `inflight_registry.py` at lines 427–429 and 1145–1147). Wrapping their `main()` entry points makes an unexpected defect return the guard's fail-open 0 to direct state/claim commands as well, changing established CLI failure behavior and allowing a failed mutation or lookup to appear successful. Leaving them unwrapped violates SC-02. The plan forbids editing the only caller surface that could supply a mode signal, so the fixed T-03 scope cannot satisfy both contracts.
   - recommendation: distinguish hook/advisory invocation from authoritative CLI invocation at an existing seam (for example an explicit argument supplied by the extension), add that caller surface to scope, and test that only hook mode fails open while direct commands retain nonzero unexpected-failure exits. If the operator does not intend these shared programs to receive `hook_guard`, remove them from SC-02's “each of eleven” claim and from T-03's guard obligation.

## Architecture and scope judgment

`harness_boundary.hook_guard` is the correct deep module for one hook-own-failure policy: its interface is small, its process-control boundary is explicit, and centralizing the diagnostic improves locality. Typed recovery remains at each producer boundary; deleting rule-level absorbers serves that seam rather than creating a second adapter. The four task cohorts account for 24 + 18 + 35 sites and a terminal census/evidence task; no task is orphaned, and dependencies are topological. The partition is nevertheless not executable as signed because T-03 lacks the mode seam described above and T-04 depends on a pin that is created only after T-04 completes.

The cited production and test files exist. The site-classification artifact accounts for all 77 sites exactly once. Function anchors are broad but resolvable; their surrounding files contain the top-level entry logic the tasks must reshape. T-04 is correctly last for census and prologue-lock gates, so later planned code does not invalidate those gates; its post-pin receipt clause, rather than task ordering, is the collision.

## Spec violations

- mismatch — `plan.yaml` T-04 vs SC-08/D-05: a tracked build artifact cannot both name and be contained in its own eventual review commit.
- mismatch — `plan.yaml` T-03 vs SC-02/D-02: shared command programs have no planned adapter or input that separates hook fail-open behavior from direct CLI failure behavior.

## Open questions

None; both defects have concrete repair paths.

## Principles applied

- **Delete First** — retained the existing single guard and rejected a second wrapper; the necessary addition is only a mode discriminator at the existing caller seam.
- **Model the Domain** — hook invocation versus authoritative CLI invocation is a real two-mode state that the current task text leaves implicit, producing incompatible error contracts.
