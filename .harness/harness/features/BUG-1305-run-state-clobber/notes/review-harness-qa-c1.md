# QA review — gate-only test_matrix audit — BUG-1305-run-state-clobber (cycle 1)

**VERDICT (this audit): FAIL on SC-13's own literal FAILS-if clause; matrix floor (unit+integration)
itself PASSES.** Two genuine, real evidentiary/coverage gaps found beyond what
`notes/qa-testmatrix-c1.md` and `notes/qa-regate-sc01-c10.md` recorded. Both are reasoned findings
backed by a targeted replay I ran myself (not merely inherited from the prior notes), and both are
**ship-rulable without a source-logic change** — see §4.

## 1. Change type and matrix floor (re-derived, not restated)

Live (non-abandoned) tasks and `change_type` from `plan.yaml` at the pin: T-01/T-03 `logic`, T-02/
T-05/T-06/T-09 `bugfix`, T-08/T-11 `docs`. `bugfix`'s `touches_runtime_code` fires (all four rewrite
`check-domain.sh`/`check-state.sh`/`bash-write-guard.sh`/`harness_boundary.py`/`validate-digest.py`);
`fix_confined_to_tests_and_contract_docs` does not (production files touched); `__bug_class__` is the
repo's known-unresolvable placeholder (repo Expertise G-08). **Matrix-only floor: `unit`.** I concur
with the prior note's own addition of `integration` as a floor the diff plainly warrants (every
bugfix task's verify block requires `tests/integration/*.py`, and BRIEF Constraints mandates the full
integration suite before REQ-07 sign-off). `component`/`ui`/`typecheck` are `cmd: null` and detect no
touched surface — correctly not-applicable. Confirmed against `.harness/harness.json` directly, not
inherited.

Per constraints, I did **not** re-run the full suites (established green: unit 28/0/exit 0,
integration 46/0/exit 0). `matrix_ok: true` at the kind level.

## 2. SC-level adequacy audit (author-nothing; source read at `dc0e0313`, one targeted replay)

Re-verified independently, not merely restated:
- **SC-01** all eight-plus-one halves present: (a) Write+Edit via `_bug1305_marker_foreign_refusals`
  (Edit half graded on a PRESENT-no-uid prior, not literally "absent" as the SC's illustrative
  sentence says — but the FAILS-if clause only forbids grading on a *parsing prior that carries a
  uid*, which this isn't, so it does not trip; info-level looseness only). (b) both halves message-
  asserted (`U1`+`U2` in stderr), Write and Edit, confirmed at `test-check-domain.py:4995-5000`.
  (d)/(e)/(f) all present and correctly asserted. **(c)'s Edit half is weaker than its Write
  sibling** — see finding QA-F3.
- **SC-02/SC-09**: `case_bug1305_run_identity_invariant` (`test-check-state.py:4560-4615`) correctly
  demonstrates all four required states, including the two SILENCE cases (witness-less `Z`, witness-
  with-uid-over-checkpoint-without `L`) proven both by exact-count exclusion (`len(lines)==3`) in the
  dirty-tree fixture AND by a standalone all-silent clean-tree fixture (lines 4600-4609) — this is
  solid, not vacuous by omission.
- **SC-04/SC-05**: `run_bug1305_artifact_resolution_cases` (validate-digest) and
  `run_bug1305_digest_repair_cases` (check-domain) both cover their required halves with message
  assertions, confirmed at source.
- **SC-06**: confirmed directly — no comment in `check-domain.sh` at the pin claims the digest guard
  is Write/PRE-only (`grep -n "Write/PRE-only\|PRE-only" check-domain.sh` at the pin: zero hits on
  that guard; the one PRE-only comment left, line 1240, is about `RE_RUN_DIGEST`'s *content
  comparison*, a true and different statement). MET.
- **SC-10**: all four assertions present in `_bug1305_marker_post_mint_cases` /
  `_post_preservation_cases`, red-proofed under (mislabeled) heading `## SC-10` in the redproof note.
  MET.
- **SC-13: NOT literally MET — two real gaps, see §3.**

## 3. Findings

**QA-F1 (severity: high — trips SC-13's own FAILS-if clause literally; ship-rulable, no source
change required).** SC-13 requires tests asserting "a Write of `state.yaml` and a Write of
`digest.md` in the same run directory are unaffected" by the witness guard. The `state.yaml` half
*is* covered (`_bug1305_identity_allow_cases`'s `marker=True` absent/zeroed cases, `test-check-
domain.py:5012-5018`, witness present, Write succeeds at exit 0). **The `digest.md` half does not
exist anywhere in the suite**: every digest-write test uses `_feat50_digest_fixture()`
(`test-check-domain.py:3379-3386`), which never creates a `.run-identity.json` witness in the run
directory — grep for `run-identity.json` across the file shows the marker is created only alongside
`state.yaml`-fixture tests, never a digest fixture. Worse, the one place a witness-present +
`state.yaml`-write pairing was *attempted* in `_bug1305_marker_file_protection`
(`test-check-domain.py:4827-4846`) has an ordering bug: `os.unlink(identity)` (line 4834) removes the
witness **before** the "legal" state.yaml write (line 4836-4837) fires, so even that case doesn't
demonstrate what it appears to — it is redundant with the `marker=True` cases, not a bug in behavior,
just a misleading test. **Concrete failure scenario:** a future change that widens the witness guard
from filename-only to directory-scoped would refuse a legitimate `digest.md` Write beside a witness,
and nothing in this suite would go red. **Ship-rulable: yes, without a source change.** I confirmed
directly by reading `harness_boundary.py:43-45`'s `RE_RUN_IDENTITY` (anchored `$` on the exact marker
filename) and its own unit proof `test-harness-boundary.py::case_run_identity_pattern`
(lines 552-564, which explicitly asserts the pattern rejects sibling `state.yaml`/`digest.md` paths)
that the underlying mechanism is filename-scoped and cannot structurally reach `digest.md`. The gap
is a missing **integration-level** test proving the composed guard behavior, not a code defect — a
single new digest-write-with-witness-present case closes it, no guard script edit needed.

**QA-F2 (severity: med-high — required red-proof evidence absent; ship-rulable, evidence now
supplied by me).** SC-13 and D-09 both require every refusing case demonstrated red against the
pinned pre-change copy of its guard script. `notes/redproof-BUG-1305.md` has **no `## SC-13` section
and no red-proof at all for the two Bash-route witness cases** (`run_bug1106_bash_route`'s "overwriting
the write-once identity witness is refused" / "removing ... is refused", `test-bash-write-guard.py:
1413-1423`) — the note's only mention of the Bash route for this mechanism is one unsupported prose
sentence (line 82: "itself write-once on both Write/Edit and Bash mutation routes"), with no command
or output. **I settled this with a targeted replay** (permitted under this dispatch), using a
disposable detached worktree at pinned commit `c369fb1f`:
```
git worktree add --detach /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/qa-redproof-sc13-c1 c369fb1f
env -u HARNESS_AGENT_TYPE BASH_WRITE_GUARD_BIN=<that worktree>/.claude/skills/harness/bin/bash-write-guard.sh \
  python3 -c '<load test-bash-write-guard.py, call run_bug1106_bash_route()>'
```
Result on the pinned pre-change script: both cases **exit 0** (permitted — red, as required); 6/8
cases pass overall. Live tree: both refused at exit 2 (confirmed already by the existing suite pass).
**This demonstrates the mechanism is sound and discriminating** — the missing piece is purely that
the required evidence was never written into `redproof-BUG-1305.md`. Not something I may write myself
(no-edit constraint; also not my note to own). **The disposable worktree
`.claude/worktrees/harness/qa-redproof-sc13-c1` (detached HEAD `c369fb1f`) is left in place — its
removal is the main session's act, per the standing worktree-removal rule, not mine.**

**QA-F3 (severity: low — reasoned, not measured as exploitable; ship-rulable).** SC-01(c)'s Edit half
("modal collision Edit removing uid is refused", `test-check-domain.py:4993-4994`) asserts only
`returncode == 2 and "U1" in stderr` — materially weaker than its own Write sibling two lines above,
which additionally requires `"run identity" in stderr and "field disagreement" not in stderr`. This
is the same asymmetry class the cycle-10 re-gate found and fixed for SC-01(b)'s Edit half — recurring
here, unfixed, for (c). I read `run_identity.uid_conflict` (`run_identity.py:132-144`) and confirmed
that for this exact fixture (no marker file created, matching `run_id`s) the only code path that can
produce `U1` in stderr at exit 2 is the intended one — so I rate this **reasoned-low**, not a proven
exploitable gap, but it is the identical pattern class flagged before and worth closing in the same
pass as QA-F1/F2 rather than separately.

**QA-F4 (severity: info).** `redproof-BUG-1305.md`'s headings don't map 1:1 to the SCs they evidence
— `## SC-10` in fact carries the full `run_bug1305_marker_cases()` red run, which is also the primary
evidence for SC-01(a) and SC-13's Write/Edit halves. There is no `## SC-13` heading at all. This
mislabeling is very likely *why* QA-F2 slipped past the cycle-1 pass (`notes/qa-testmatrix-c1.md §4`
lists the same seven headings I found and declares "no section is vacuous" without checking that a
required heading for SC-13 exists at all).

## 4. Ship-ruling summary

None of QA-F1/F2/F3 requires a **source guard script** change — QA-F1 needs one new test case
(digest-with-witness Write), QA-F2 needs the redproof note updated with the command+output I already
produced (or the operator can accept my measurement in place of it), QA-F3 needs one assertion
strengthened. All three are **operator-rulable at ship with the finding in front of them** given the
cycle budget is exhausted at 9/9 — I do not believe any of the three changes anything about whether
the shipped mechanism is safe; they are gaps in the proof, not in the guard.

## Open questions

None blocking. QA-F1–F4 are for the validator lead's synthesis.
