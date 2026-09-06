# BUG-1305 regression delta

## Removed or altered assertions

BLUF: no assertion was weakened or deleted to make BUG-1305 pass. Against the approved baseline `c369fb1f`, the feature makes these deliberate assertion changes:

- `tests/integration/test-validate-digest.py`: the existing-run-directory/no-`digest.md` case changes from fail-open exit 0 with an INV-15 diagnostic to fail-closed exit 2 naming the missing durable digest. The no-feature-root lookup case remains exit 0, but now expects the truthful “not found from the hook's vantage” diagnostic instead of INV-15. Absolute, compliant, non-compliant, and non-digest controls were added.
- `tests/integration/test-check-state.py`: the aggregate success predicate now includes `case_bug1305_run_identity_invariant`; its dirty fixture requires INV-36 for run-id or run-uid disagreement while its owned and legacy fixture requires exit 0 with no INV-36. The unrelated BUG-1304 aggregate return retained from `origin/main` was restored during rebase conflict integration.
- `tests/unit/test-code-grade.py`: the former `validate_digest.py:main` exception was removed from the complexity allowlist. Mutation anchors moved to the extracted helpers without changing their behavioral expectation.
- `tests/integration/test-check-plan-routes.py`: the isolated resolver fixture now copies the new direct dependency `run_identity.py`; the route assertions and expected exit codes are unchanged.
- `tests/integration/test-run-unit-tests-kinds.py` and `tests/integration/test-run-unit-tests-layout.py`: isolated runner fixtures copy `run_identity.py`; all runner assertions are unchanged.
- `tests/integration/test-check-domain.py`: BUG-1305 adds explicit identity, witness, marker, POST, digest-repair, and negative-control assertions. Two BUG-1106 assertions deliberately strengthen from exit 0 to exit 2: an unmatched `old_string` and a non-unique `old_string` on governed artifacts now fail closed instead of delegating refusal to the editor. The former timing-sensitive concurrent-sweep proof was replaced with a FIFO-gated deterministic proof of the same observable contract: a write made during a sweep remains visible to the next sweep.
- `tests/integration/test-bash-write-guard.py` and `tests/unit/test-harness-boundary.py`: new marker/witness and run-identity refusal/allowance pairs cover the shared boundary behavior. No prior assertion was relaxed.
- `tests/unit/test-run-identity.py`: new focused tests cover the identity parser, witness read/mint behavior, precedence, and malformed/unreadable fail-closed paths; there was no predecessor assertion to alter.

The following required allow controls were observed at exit 0:

- T-02 seed-field denial: `_bug1305_identity_allow_cases` — `legacy checkpoint without uid remains allowed`.
- T-09 ownership: `_bug1305_identity_allow_cases` — `DEC-154 resumed owner with same uid remains allowed across sessions`, `recovering owner with absent checkpoint remains allowed`, and `recovering owner with zero-byte checkpoint remains allowed`.
- T-06 digest repair: `run_bug1305_digest_repair_cases` — `digest Edit append repair remains allowed`.
- T-02 POST / T-03 INV-36: `case_bug1305_run_identity_invariant` — `BUG-1305 INV-36 detects clobbers and stays silent on owned/legacy runs`; the clean owned/legacy fixture exits 0.
- T-05 artifact resolution: `_bug1305_relative_artifact_cases` — `located compliant digest passes`; `_bug1305_other_artifact_cases` — `unresolvable artifact lookup still fails open`.
- T-02 witness guard: `run_bug1305_marker_cases` — `run_uid is a legal checkpoint key beside identity witness`; `run_bug1305_digest_repair_cases` — `digest Write append remains allowed` and `digest Write append remains allowed beside identity witness`; `run_bug1106_bash_route` — `bug1106 Bash route NEGATIVE CONTROL: an unrelated file in the same run directory is still ALLOWED — this is not a blanket run-dir Bash ban`.

## Newly refused writes

BLUF: foreign writers still cannot mutate an already minted run without its durable identity. In addition, an Edit of a governed run artifact whose complete candidate cannot be reconstructed now fails closed and routes the caller to a whole-file Write.

- `_bug1305_identity_refusal_cases` — `modal collision Write omitting uid is refused`: exit 2, preserves prior `run_uid: U1`, and names the run-identity/carry-the-exact-`run_uid: U1` remedy.
- `_bug1305_identity_refusal_cases` — `modal collision Edit removing uid is refused`: exit 2 with the same precedence and preservation guarantee.
- `_bug1305_identity_refusal_cases` — `different minted uid Edit is refused`: exit 2 and names both prior `U1` and incoming `U2`, completing SC-01(b)'s Write/Edit pair.
- Existing witness overwrite, false-witness creation, digest replacement, and digest insertion paths are likewise refused; same-owner resume, legacy checkpoints, append-only digest repair, and unrelated run-directory writes remain allowed as listed above.
- Unreconstructable Edits of `state.yaml`, `digest.md`, and `handoff-*.md` — including OMP's path-only Edit payload — now exit 2 with an instruction to `Write the complete file instead`. On OMP every Edit payload is path-only, so every Edit of these governed artifacts takes that refusal and must use Write. This is paired with `uniquely reconstructable state Edit remains allowed`, `digest Edit append repair remains allowed`, and `handoff valid reconstructable PRE-Edit remains allowed`, so the rule is fail-closed on missing candidate bytes rather than a blanket path denial.

## Suite results

- `.claude/skills/harness/bin/run-unit-tests.sh --kind unit`: exit 0; 28 files; 0 lines beginning `FAIL`; 3.97s pool wall time.
- `.claude/skills/harness/bin/run-unit-tests.sh --kind integration`: exit 0; 46 files; 0 lines beginning `FAIL`; 63.70s pool wall time at the cycle-16 seam.
- From the control-plane root `/Users/molchairuangutai/GitHub/harness`, `bash .claude/skills/harness/bin/check-state.sh`: exit 0 with notes only; a search of the verbatim output found 0 `INV-36` lines.
- Cycle-10 targeted replay of `run_bug1305_identity_cases`: exit 0; 10/10 cases passed. Against pinned pre-change hook `592e88dcf0b6dfcd75ca4c1d49451fa9003d2802`, exit 4; 6/10 passed, with the new different-uid Edit case red.
