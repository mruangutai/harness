# Goal-check c5 — SC-07 re-grade @ `review_sha 252a18a9` (amendment seam)

**SC-07 is `met`.** The cycle-16 amendment cured the criterion-internal conflict that made it
`not_met` at c4, and it did so at the SAME cost it set for itself: the widened carve-out's own
FAILS-if leg — an exit-0 permit for a uniquely reconstructable, content-valid Edit of EACH governed
class — is satisfied for all three classes at the pin, including the handoff arm that no case
reached before. All other live criteria carry from c4 unchanged (production byte-identical to
`154ff2a0`). **The feature meets its goal; Mode A and Mode B are each independently declarable
delivered.** Three advisory findings, none gating; two Advisor-bound, one cycle-18-eligible.

Everything below read with `git show 252a18a9:<path>`; nothing was edited this cycle.
`git status --porcelain` was **empty (no output)** on entry, and after my two permitted writes is
verbatim:

```
 M .harness/harness/features/BUG-1305-run-state-clobber/observations/harness-pm.md
?? .harness/harness/features/BUG-1305-run-state-clobber/notes/research-BUG-1305-goalcheck-build-c5.md
```

## Leg 1 — direction one, nothing removed: **satisfied, justifications TRUE at the pin**

`## Removed or altered assertions` present (note `:3`), 8 bullets covering the 10 test files this
feature touched. The two BUG-1106 flips (note `:12`) verified at source, not merely present:
`test-check-domain.py:3838-3842` (unmatched `old_string`) and `:3847-3851` (non-unique) both assert
exit 2 + `Write the complete file instead` at the pin; at `c369fb1f` the same two cases asserted
exit 0 and were captioned "not this gate's problem" (`c369fb1f:tests/integration/test-check-domain.py:3816-3819`,
`:3824-3827`). Strictly more refusing → fail-closed strengthening, as claimed. FIFO replacement
(`test-check-domain.py:1044-1064`, `:1353-1361`), check-state aggregate (`test-check-state.py:4767`),
resolver fixtures copying `run_identity.py` (`test-check-plan-routes.py:438`) all confirmed.
The five other test files changed in `c369fb1f..252a18a9` (`test-suite-layout.py`,
`test-inflight-registry.py`, `test-config-shape-matrix.py`, `test-plan-merge.py`,
`test-hooks-install.py`) are sibling-feature/rebase traffic, outside "files this feature touched";
their only assertion change (`test-suite-layout.py`, INAPPLICABLE print → hard `check`) strengthens.

## Leg 2 — direction two, nothing newly refused beyond the two disclosed classes: **satisfied**

Note `:33` pairs the reconstruction-`None` branch with its permits, names the omp blast radius
honestly ("On OMP every Edit payload is path-only, so every Edit of these governed artifacts takes
that refusal and must use Write" — the c4 F-02 advisory is cured), and the three cited case names
resolve and assert what is claimed (see leg 3). All six permitted-write pairs present at the pin
and none asserted non-zero: legacy update `test-check-domain.py:5161`; resumed owner `:5155` and
both recovering-owner cases `:5157`, `:5159`; digest append repair `:3891`; `check-state.sh`
legacy/owned silence `test-check-state.py:4560-4612` (clean tree `clean_code == 0`, `:4609`);
validate-digest `located compliant digest passes` / `unresolvable artifact lookup still fails open`
(`test-validate-digest.py:1973`, `:1984`); witness-guard siblings `test-check-domain.py:4970`,
`:3911`, `:3918` plus the Bash negative control `test-bash-write-guard.py:1409`.

## Leg 3 — the amendment's own new leg: **all three permits present**

| class | case name | location at the pin | exit |
|---|---|---|---|
| `state.yaml` | `uniquely reconstructable state Edit remains allowed` | `_bug1305_omp_edit_cases`, `test-check-domain.py:4827-4833` (`status: building`→`review`, unique) | 0 |
| `digest.md` | `digest Edit append repair remains allowed` | `run_bug1305_digest_repair_cases`, `:3888-3892` (unique prefix, append-shaped) | 0 |
| handoff note | `handoff valid reconstructable PRE-Edit remains allowed` | `_handoff_valid_pre_edit_cases`, `:4276-4293`, reached via `run_handoff_done_when` `:4410`/`:4420` | 0 |

The handoff case is the one that landed this cycle (`154ff2a0..252a18a9` adds exactly these +14
lines). Its `old_string` `Scope: build complete` occurs once in the fixture (`valid`, `:4414`) and
the replacement keeps the note contract-valid, so it is a genuine reconstructable-and-valid permit,
not a shape stub; `_record_handoff_result(..., 0)` gates on exit 0.

## Leg 4 — `## Suite results`

Integration line (`note:38`) **is** the pin measurement: exit 0, 46 files, 0 `FAIL`, 63.70s,
explicitly labelled "at the cycle-16 seam" — identical to main's seam figures. The unit line
(`note:37`, exit 0, 28 files, 3.97s) is **not** a pin measurement: last written at `dee707e9`, and
`bash-write-guard.sh`, `check-domain.sh` and `run_identity.py` all changed after it. No FAIL line
and no non-zero exit is recorded, so the criterion's FAILS clause does not fire → **F-02, advisory.**

## Leg 5 — the amended sentences, read in place: **coherent**

`BRIEF.md:379-385` (two disclosed classes) and `:392-397` (the FAILS-in-turn leg) parse cleanly and
agree with each other on the class list and on the permit obligation; the parenthetical naming the
three payload shapes matches `_edit_reconstructed_content`'s two `None` returns plus the path-only
payload. No transcription near-miss found. One residual imprecision → F-03.

## Findings

- **F-01 — Advisory · Advisor-bound.** Note `:9` names the removed complexity-allowlist row as
  `validate_digest.py:main`; the row actually removed is `("validate-digest.py",
  "check_artifact_file"): 2` (present `c369fb1f:tests/unit/test-code-grade.py:260`, absent at the
  pin — the sole deletion in that file). Substance true (an exception removed = strengthening),
  identifier false. Remedy: replace `main` with `check_artifact_file` in note `:9`.
- **F-02 — Advisory · Advisor-bound.** Unit suite figure stale (leg 4). Remedy: re-run
  `run-unit-tests.sh --kind unit` at the pin and restate note `:37` with the seam label, or state
  the sha at which it was observed.
- **F-03 — Advisory · cycle-18-eligible.** `BRIEF.md:385` requires each disclosed class be stated
  "with the test that pins its message"; for class 2 the note quotes the message verbatim but names
  only the three PERMIT cases, not a refusal case. The message is in fact pinned by
  `bug1106 Edit route: an unmatched old_string fails closed` (`:3839`) and by
  `{label} {shape} Edit fails closed` (`:4860-4864`). Mechanical if the Advisor wants it named.

## Verdicts

- **SC-07: `met`** (method `inspection`; evidence `notes/regression-delta-BUG-1305.md:3,25,33,35-40`
  + `tests/integration/test-check-domain.py:4827-4833`, `:3888-3892`, `:4276-4293` at `252a18a9`).
- SC-01..SC-06, SC-09, SC-10, SC-11, SC-13: **not re-graded this cycle**; carried from
  `notes/research-BUG-1305-goalcheck-build-c4.md`. Production is byte-identical to `154ff2a0`
  (`git diff 154ff2a0 252a18a9 -- .claude/skills` empty), so none can have moved.
- SC-08, SC-12: retired at signature; nothing grades them.

**Goal.** Met. Mode A (prevention, detection, actionable detection, witness protection) and Mode B
(automatic grading, legitimate repair, truthful guard record) are each independently declarable
delivered. The residuals the operator signed — copied-`run_uid` forgery, the pre-mint first-write
window, end-to-end PostToolUse delivery unmeasured (REQ-01), directory-level removal (#1376) —
are unchanged by this cycle and remain accepted, not closed.
