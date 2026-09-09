# Plan amendment — panel cycle 1 findings F1–F4 (BUG-1309)

**All four findings are closed in one amendment.** T-12 is new (the missing `rstrip`, which T-11
forbade itself from fixing); T-11 now depends on T-12, no longer forbids what the plan requires,
and its case list dropped from 29 to **18** after the duplication cross-check finally covered all
five integration files. `approval` and `panel` are byte-identical; `check-plan-routes.py` exits 0.

## F1 — the defect got its own task

`T-12` — *Strip the trailing separator before taking the feature identity in the Build refusal
preflight*. One line: `gh-sync.py:1360` `os.path.basename(feat_dir)` →
`os.path.basename(feat_dir.rstrip("/"))`, matching `feature_schema.py:326` on the same argument
(both read at source; the def is `gh-sync.py:1357`, `recovery_command_for` at
`feature_schema.py:324`). `traces: [REQ-06]` only — REQ-01 is about naming Build entry, which this
does not touch. `depends_on: [T-04, T-06]`: T-04 authored the function and the five sibling cases,
T-06 authored `BUILD_ENTRY_ERA_EXEMPT` and `recovery_command_for`, the two symbols the disagreeing
comparison reads. `change_type: bugfix`, `status: ready`, `files:` the two it touches.

**Lane — `main-session-direct`.** `check-domain.sh --resolve` returned, verbatim, from inside the
worktree: `.claude/skills/harness/bin/gh-sync.py` → `harness-backend-dev` / `harness-dev-ops`
(exit 0); `tests/integration/test-gh-sync.py` → `harness-backend-dev` / `harness-dev-ops` /
`harness-qa` (exit 0). Both disagree with the carve-out, and the carve-out governs: the plan's
`lanes` row *"gh-sync.py start-task refusal"* already places that surface main-session-direct
under DEC-174, and the edited line is inside that preflight. `check-plan-routes.py` prints T-12's
`DEVIATION` line identical to T-04's and still exits 0 — only `VIOLATION` gates.

**DEC-217, both legs, in T-12's intent.** Integration: one new case in the T-04 block,
`"T-12 era-exempt trailing slash continues"` — era fixture passed through argv *with* a trailing
slash, exit 0, `predates` on stderr; red before the edit, green after; the only mutation that
reddens it and nothing else in that file is reverting line 1360, because every other case builds
`feat_dir` with `os.path.join`. Unit: **option (a)** — discharged by T-11's BE-23, which runs after
T-12; BE-23 is not thereby ceremonial (below). `verify:` runs
`tests/integration/test-gh-sync.py`, fails on `^FAIL`, `grep -qF "ok    T-12 era-exempt trailing
slash continues"`, `echo VERIFY-PASS`.

## F2 + F3 — one amendment, 11 struck, 1 re-aimed, 18 survive

Criterion applied uniformly: a case survives only if it constructs an input state, or observes an
observable, that **no** assertion in the five files makes. Struck with their anchors: **BE-05,
BE-07** (`test-check-state.py:4687-4699`, same states, same observables, in-process); **BE-13,
BE-16** (`test-gh-sync.py:3440` + `:3576`); **BE-15** (`:3481`); **BE-17** (`:3430`, the
`_NO_RECORD` call site is `gh-sync.py:288-289`); **BE-18** (`:3450`); **BE-20** (`:3574`,
`recover-terminal` reaches `skip` unarmed); **BE-26** (`:3563`); **BE-22** (below); **BE-01**
(below). **BE-08 re-aimed** to a three-task plan — none `done` → `open`, only the *last* `done` →
`recover-terminal`, proving the `any()` at `feature_schema.py:335-337` scans every task; that
fixture writes exactly one task, so it cannot be built there. Eight of the eleven are beyond the
panel's three: the T-02/T-03 CLI blocks (`:3403-3494`, `:3505-3566`) already drive those rows end
to end. **Q1 flags the size of the strike set for the operator.**

**BE-01 — struck as vacuous, not as a duplicate.** Its state (era member, no `plan.yaml` at all) is
unreachable in that fixture, so it is not a duplicate — but it satisfies *two* independently
sufficient paths to `recover-terminal`: the era short-circuit (`:326`) and the `except` leg
(`:331-332`). Delete the era short-circuit and it still passes through `except`; break `except` and
the short-circuit still carries it. It is green under **every** single-point mutation, while BE-02
and BE-03 each redden one of those two alone. T-11's own rule ("a case no mutation can redden is
vacuous") strikes it. It can redden only a double mutation.

**BE-22 — struck.** Its written justification was "no fixture can be this input"; T-12 falsifies it
by passing the slash through argv at the same observable (exit 0, `predates`). **BE-23 kept** — its
state (era + trailing slash + recorded `recovery-required`) is built by nothing: T-12's case passes
an *absent* outcome and `:3623` passes `recovery-required` with no slash, so reverting the `rstrip`
reddens BE-23 while `:3623` stays green. Its observable is the era branch at `:1380-1385`, not the
`predates` line.

**How each of the five was checked.** `grep` for
`recovery_command_for|_build_entry_preflight|_build_entry_recovery_notice|record_build_entry|_recover_terminal_*|BUILD_ENTRY_ERA_EXEMPT|load_recorded|save_recorded`
across all five: **test-post-merge-sweep.py, test-merge-gate.py, test-validate-feature-json.py →
"No matches found"** (they touch the surface only through the shell sweep, the gate's own reason
string, and the value enum at `test-validate-feature-json.py:528`, none of them these seams);
**test-check-state.py** → the four in-process calls at `:4680-4699`, read in full with their
fixture `:4622-4648`; **test-gh-sync.py** → `_ghs` in-process calls listed by `grep '_ghs\.\w+'`
(`load_recorded`/`save_recorded` only, `:1390-2290`) plus the T-02/T-03/T-04 CLI blocks read at
`:3403-3624`. Also `grep -c reopened tests/integration/test-gh-sync.py` → `0`, and a grep for a
trailing-slash argument in that file → no matches, which is what makes T-12's mutation claim true.

## F4 — no change needed

Once T-12 lands, **no case in T-11 is deliberately red at HEAD**, so the clause "a case no mutation
can redden is vacuous" is coherent as written and needs no exempting sentence. What I did change is
the paragraph that *asserted* a red phase: it now says no case is expected red, and names the
`rstrip` revert as BE-23's mutation.

## Open question

- **Q1 (non-blocking):** eight strikes are beyond the panel's F2/F3 enumeration (BE-13, BE-15,
  BE-16, BE-17, BE-18, BE-20, BE-26, plus BE-01 on vacuity). Each names the existing assertion it
  duplicates. Confirm at re-signature, or restore any of them with a discrimination argument I
  could not find. The unit floor still holds for every task: T-02 → BE-11/12/14/19, T-03 →
  BE-25/27/28/29/30, T-04 → BE-23/24, T-06 → BE-02/03/04/06/08/09/10.
