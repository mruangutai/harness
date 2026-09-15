# Goal-check — BUG-1563

## Conclusion

The approved outcomes are delivered at review SHA `c1e85b64d9871e07bdf3b6994ab8e4ee7a36ba11`. This goal-check inspected exactly the union of `.claude/skills/harness/bin/check-state.sh` and `tests/integration/test-check-state-plans.py` at that SHA, and graded the approved BRIEF against `plan.yaml`, `feature.json`, and `STATE.md`. No tests were executed by this reader.

## Perspective grades

| Perspective | Grade | Carrying SC | Evidence |
|---|---|---|---|
| operator | pass | SC-01 | At the pinned SHA, `.claude/skills/harness/bin/check-state.sh:219-231` recognizes the closing delimiter with YAML-specific single- and double-quote escaping, and `:243-279` preserves quote state across physical lines while retaining the plain-scalar INV-35 path. The pinned tests independently assert silence for multiline double-quoted and single-quoted `#217` values and detection for exact unquoted `notes: close out #217` at `tests/integration/test-check-state-plans.py:792-833`. Durable fail-first relay: `STATE.md:13` records pre-checker exit 1 with false positives from `inv35.l` and `inv35.m`, while `inv35.n` passed. Current automated evidence: `notes/review-harness-qa-c0.md:8-10` records the exact T-01 command exiting 0 with `inv35.l`, `inv35.m`, and `inv35.n` all producing their required outcomes. |
| code maintainer | pass | SC-02 | The pinned test defines three separate cases at `tests/integration/test-check-state-plans.py:792-833`, registers all three independently in `main()` at `:984-997`, and returns success only when every collected case is true at `:1024`. `STATE.md:13` durably records both added multiline cases failing before the checker edit; `notes/review-harness-qa-c0.md:8-11` records direct invocation of the approved command exiting 0 and identifies the three successful cases. |

## Task and trace cross-check

- `plan.yaml:23-35` contains the sole task, T-01, with status `done`, traces `[SC-01, SC-02]`, the exact two-file union above, and the exact verify command `python3 tests/integration/test-check-state-plans.py`.
- `feature.json:5` pins the reviewed SHA; `STATE.md:6,12-14` agrees on the SHA, T-01 commit, bounded product paths, fail-first relay, and post-fix result.
- REQ coverage is not applicable: the approved by-perspective BRIEF declares SC-01 and SC-02 and no REQ identifiers. Both SCs are traced by T-01.

## Validation finding outside the perspective outcomes

- **high / substance / T-01 / harness-qa** — `notes/review-harness-qa-c0.md:13-21` reports that the bugfix matrix requires unit-kind proof for changed executable checker code, but the changed regression coverage is integration-only. Concrete failure scenario: a checker regression outside the integration fixture's exercised route could ship without the matrix-required unit-level guard even while this direct integration command remains green. This separate QA gate failure does not erase the observed SC-01 or SC-02 outcomes, but it blocks the aggregate validation decision.

## Open questions

None.
