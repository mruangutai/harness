# Code review — BUG-2294 — c1

PASS. T-01 satisfies the reviewed scope; no substantive or form findings. Python risk grade: pass.

Reviewed `c1724230c4d931ad46d433c8ba93df8cf312f898..70981edd6f9f110965a0148b4490ed2673d262dc` using pinned git show/diff, without moving HEAD. Merge-base is the supplied base. Current feature.json binds the dispatched pin; its dirty changes are feature bookkeeping only. Human commit included: `128a7158 [harness:human] BUG-2294-prune-keeps-run-digests: operator signature (rework 1 round / 45 min, main-session-direct T-01)`.

## Stage 1 — compliance

- SC-01: `.claude/skills/harness/bin/prune-run-evidence.py:118-129` limits deletion to existing non-kept UI directories; missing UI and repeated prune are no-ops, and dry-run skips deletion. `tests/unit/test-prune-run-evidence.py:100-135` checks exact UI membership, retained UI bytes, all run directories and non-UI bytes, repeat behavior and explicit keep.
- SC-02: `tests/unit/test-prune-run-evidence.py:138-194` builds ten hash-bound runs, final BLOCKED, no UI/PASS/pin-bound run; hashes and real check-state INV-7 are checked before/after. The accepted INV-7 narrowing is appropriate to cycle evidence. Red-first record reports actual lost digests, not setup failures; independent runtime acceptance belongs to QA.
- SC-03 inspection: pinned pruner `:47-115,134-145` and baseline diff confirm unchanged passing-validator selection, pin selection, CLI, explicit-keep validation and refusals. Pinned `.omp/commands/harness-ship.md:38-54` preserves step placement, both invocations (`:43-44`) and commit instruction while documenting UI-only removal and protected records. `.harness/harness/docs/DECISIONS.md:7986-8000` preserves Abandon/INV-51 and keep policy while narrowing only the ship deletion clause with #2177 rationale; DECISIONS-INDEX changes are coupled regeneration metadata.
- D-01 and all five T-01 product paths are accounted for. Other range changes are this feature's intake, signature and lifecycle evidence, not unrelated product scope. No departure weakens the BRIEF or decision. Product docs/spec.md, docs/decisions.md and docs/architecture.md remain absent; no substitute product guidance was assumed.

## Stage 2 — quality

Deletion remains localized in the existing pruner; no new caller contract or fallback bypasses refusals. Changed assertions observe subprocess behavior and filesystem bytes, with positive kept-record/UI checks beside absence checks. No newly introduced silent-failure path identified in the supported directory layout.

Ran only the explicitly required pinned Python risk grader: `code-grade.py --base c1724230c4d931ad46d433c8ba93df8cf312f898 --head 70981edd6f9f110965a0148b4490ed2673d262dc`: exit 0, 13 passing records, no severity or reason-required records. Production `_ui_targets` grades 5; lowest emitted test grade is 3 (its bar). No tests, builds, linters or formatters run by this reviewer. QA owns `python3 tests/unit/test-prune-run-evidence.py` and fail-first confirmation.

## Principles applied

- Delete First: accepted the localized replacement of whole-run deletion rather than changing keep rules or adding ship-side machinery (`prune-run-evidence.py:124-129`).

Open questions: none.
