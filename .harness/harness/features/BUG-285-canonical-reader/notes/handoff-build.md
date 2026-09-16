# Handoff — BUG-285-canonical-reader, build → review — reconstructed after validation, original seam at da8932a0, seq-26

## Next

Dispatch the `review` team to `harness-validator-lead` at review SHA `da8932a0`. Grade all signed criteria, require the repository-policy test matrix rather than the narrower temporary migration gate, and send every substantive finding through the bounded fix loop before ship review.

## Trust

- All nine plan tasks were at station `done` before review entry — `plan.yaml` — verified at `da8932a0`.
- The final permanent AST audit reported 120 canonical rows, 42 exemptions, zero migrations, and zero unresolved reader sites across 69 Python files — T-07 evidence and `runs/2026-09-15-t07-ownership-amend-product/digest.md` — verified before `da8932a0`.
- The temporary 29-program normalized enforcement comparison passed 29/29 before removal — T-07 evidence — verified before `da8932a0`.
- The four-angle simplify pass applied only one stale-comment cleanup, with no reuse, efficiency, or altitude change — `runs/2026-09-15-simplify-eng/digest.md` — verified at `be6b75b0`.
- This note was missed at the actual seam and is reconstructed rather than backdated. The initial review did run at the recorded pin, returned four findings, and fix round c1 later resolved them all — `runs/2026-09-15-validate-validator/digest.md` and `runs/2026-09-15-fix-c1-validator/digest.md`.

## Dead ends

- Do not treat the temporary 29-case baseline as the permanent gate; it was deliberately retired after byte-equivalence was established.
- Do not accept the first review's narrow T-02 gate as repository-policy coverage; final QA had to exercise the proper unit and integration matrix.
- Do not broaden strictness beyond the signed nested-field contracts while closing review findings.

## Working set

- `.claude/skills/harness/bin/artifact_accessors.py`
- `.claude/skills/harness/bin/test_artifact_accessors.py`
- `.claude/skills/harness/bin/check_canonical_artifact_readers.py`
- `.claude/skills/harness/bin/test_check_canonical_artifact_readers.py`
- `tests/unit/test-feature-json-reader.py`
- `.harness/harness/features/BUG-285-canonical-reader/plan.yaml`

## Done when

Scope: the review and bounded fix loop return with all signed criteria supported, the required matrix complete, and no must-fix finding.
Authority: brief-sc:SC-01
Authority: brief-sc:SC-04
Authority: brief-sc:SC-07
