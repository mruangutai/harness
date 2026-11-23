# Receipt — simplify · reuse — FEAT-2397 (plan surface, flag-only)

BLUF: 2 low findings, no blockers. The plan already names its main reuse targets (`harness_boundary.load_repo_module` at harness_boundary.py:532, `check-instruction-paths.py::violations` at :130, the existing nested regex, `resolveContextWarnTokens`/`resolveBudgetNumber`, existing `check-plan-routes.py` and `check-state.py` gates). The two gaps are unnamed or non-importable targets that invite a second spelling.

## Findings

1. low · T-04 (SC-10/SC-11) · plan.yaml:492-493 — nested-session regex is not importable
   - Existing: `tests/manual/probe-omp-session-accessor.py:143` defines the nested-transcript regex as a local variable inside `main()`. Case 6 (:151) already expresses "flat" only as `not nested.search(...)`.
   - Cost: the intent says to reuse "the EXISTING nested session-file regex" and to add "small importable helpers" for identity classification, "mains by flat session-file shape". The new offline test `tests/unit/test-session-accessor-probe.py` cannot import a local variable. The path of least resistance is a second hand-copied regex in the test (or a separate flat-shape regex in the probe). Two patterns for one path concept then need the same flags and anchors in lockstep, and the test copy goes stale silently.
   - Alternative: say the regex is hoisted to a module-level constant plus one `is_nested(path)` helper in the probe. Flat is defined as `not is_nested(path)` plus a `.jsonl` suffix, with no second pattern. The unit test imports that helper.

2. low · T-01 (SC-12) · plan.yaml:379 — "existing OMP config accessor" is unnamed
   - Existing: `check-omp-port.py::artifact_accessors.load_omp_config` (referenced by test-check-omp-port.py:326) is the config reader. The same test file otherwise mutates `.omp/config.yml` through raw `read_text().replace(...)` (:145, :159, :185-190).
   - Cost: the plan does not name the accessor or where the test reaches it. The new perCallModel pin (absent/on/eval must fail) could be written as a fourth text-replace mutator or a bare yaml parse instead. That duplicates config parsing, and the pin then goes blind to the duplicate-key and strict-parse behavior the accessor already enforces.
   - Alternative: name `load_omp_config` as the reader for the pin's assertion that `task.perCallModel == "off"`. Mutate with the file's existing fixture-copy helper, then assert through the accessor or the check's exit.

Not flagged (settled or verified fine):
- T-02's transient inline AST verify is by design (SC-04 panel ruling). Nothing else in bin/ already checks workflow env names.
- T-05 repeats the canonical-reader audit and instruction-path gate that T-03/T-01 also run. That is the intended cumulative gate, and it reuses the existing scripts rather than reimplementing them.
- The frozen test-local `_capped_body` baseline is a deliberate oracle that must not share code with production. It is not duplication.
- Everything in the settled list: #9-#12 scope, DEC-174, KEEP items, the panel rulings and the mandatory not-overspecification items.

## Principles applied
- Migrate Callers, Then Delete Legacy APIs (read this run): T-01 and T-02 already migrate all callers in the same task as each deletion (dispatch-guard, the CLAUDE fallbacks, and the JSONL reader with its imports). No shim is left. I raised nothing there.

## Open questions
none
