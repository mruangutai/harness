# BRIEF — BUG-1480 handoff note checkout root

## Problem

No feature can write the `notes/handoff-<phase>.md` note DEC-159 requires at each phase seam, because
every feature lives in a linked worktree until it merges. In `check-domain.sh`, `_norm` (lines
1114-1149) asks `harness_boundary.checkout_relative` for the pair `(checkout_root, path relative to
that checkout)`, keeps `_ck[1]` and discards `_ck[0]`. The handoff branch of `shape_problems` (lines
1746-1748) then calls `handoff_done_when.problems(rel, content, root, resolve=True)` with a `rel`
relative to the WORKTREE and a `root` that is the MAIN checkout. `handoff_done_when._feature_dir`
(handoff_done_when.py:51-54) joins the two, so authority resolution looks for
`<main-checkout>/.harness/harness/features/<FEAT>/plan.yaml` and `BRIEF.md` — files that do not exist
for a feature planned inside an unmerged worktree. Every `plan-task:`, `brief-sc:`, `finding:` and
`approval:` pointer is therefore reported unresolved and the note's write is refused. Measured three
times (FEAT-54, BUG-201 cycle 0, BUG-201 cycle 1) with one identical note body: worktree root gives
`problems: []`, main root gives every Authority pointer unresolved. BUG-201 shipped with two handoff
rows it could not write.

## Goal

A handoff note is validated against the checkout it stands in. An agent working in a worktree can
write the note DEC-159 mandates, and nothing about validation in the main checkout changes.

## Requirements

- REQ-01: A well-formed handoff note whose feature directory exists only in a linked worktree — with
  no copy of that feature directory in the owning main checkout — is accepted, its authority
  pointers resolved against the worktree's own `plan.yaml` and `BRIEF.md`.
- REQ-02: Validation of a handoff note written in the main checkout is unchanged — same verdicts,
  same messages, for every case the suite already covers.
- REQ-03: The shape phase gains no fail-closed dependency: the `harness_boundary` import inside it
  keeps absorbing every failure and falling back to the base-relative answer, so a broken
  `harness_boundary` cannot block the write that repairs it.
- REQ-04: A genuinely unresolvable authority pointer is still refused, and the refusal still names
  the pointer — in the main checkout AND in a worktree.
- REQ-05: The behaviour change is defended by a regression test in the harness integration suite
  that fails against the pre-fix script and passes after it.
- REQ-06: The note's safe-path containment bound moves with the resolved checkout, INTENDED: a
  handoff note standing in a worktree may only point at targets inside that worktree, so a
  `finding:` or `approval:` pointer from a worktree note into the MAIN checkout is refused as
  escaping the root. Notes written in the main checkout are unaffected, because the resolution
  helper falls back to `root` for every path that does not stand in a different checkout.

## Constraints

- SUPPLIES — `harness_boundary.checkout_relative(abs_path)` (harness_boundary.py:115) already returns
  the checkout root; the defect is that `_norm` throws it away. No new boundary logic is needed.
- SUPPLIES — the integration suite already carries every fixture helper the regression test needs:
  `make_linked_worktree(root, wt_path, wt_id)` (tests/integration/test-check-domain.py:138),
  `_handoff_done_when_fixture(root)` (:4155), `_handoff_text(body, trust_lines=1)` (:4140),
  `_invoke_handoff(root, target, content)` (:4148), `_record_handoff_result(...)` (:4132), and the
  aggregator `run_handoff_done_when()` (:4410).
- BLOCKS — `_norm`'s return contract is a path STRING and must not change. Eleven other call sites
  feed it straight into pattern matching, cited BY FUNCTION NAME as SC-05 cites them: `_resolved_rel`,
  `_plan_route`, the `Edit`/`Write` target-assembly block in `__main__`, and the sweep's
  `targets.append` — all in `check-domain.sh`. Any new information is exposed by a SIBLING helper or
  resolved at the handoff call site.
- BLOCKS — this lands STANDALONE off `origin/main` at `6d969ed375f8458e32c47502ecdcc85bb9916635`, on
  its own PR. No cherry-pick into BUG-201, and no scope beyond this one defect and its regression
  test.
- BLOCKS — DEC-174: `.claude/skills/harness/bin/**` and `tests/integration/**` are enforcement-layer
  files, so every task executes `main-session-direct`. There is no team lane in this plan.

## Verification gaps

None. Both test kinds this feature rests on — `integration` and `unit` — have live runners in
`.harness/harness.json`; the changed surfaces are a gate script and its own integration suite, and
no `cmd: null` kind covers them.

## Success Criteria

- SC-01: A handoff note citing a non-terminal task in a `plan.yaml` that exists ONLY inside a linked
  worktree exits 0, with no copy of that feature directory in the owning main root.
  verify: automated  evidence: integration
  command: cd /Users/molchairuangutai/GitHub/harness && env -u HARNESS_AGENT_TYPE python3 tests/integration/test-check-domain.py
  row: the printed row `handoff worktree-only feature dir resolves` reads `ok`. The suite's exit
  code alone does not discharge this criterion — that row name must be quoted from the output.
- SC-02: Every pre-existing handoff case in `run_handoff_done_when()` — grammar, pointer, unsafe
  path, pre-edit, validator-exception, existing-edit and line-cap — reports `ok`, so main-checkout
  behaviour is unchanged.
  verify: automated  evidence: integration
  command: cd /Users/molchairuangutai/GitHub/harness && env -u HARNESS_AGENT_TYPE python3 tests/integration/test-check-domain.py
  row: every row emitted by `_handoff_grammar_cases`, `_handoff_pointer_cases`,
  `_handoff_unsafe_cases`, `_handoff_pre_edit_cases`, `_handoff_validator_exception_case`,
  `_handoff_existing_edit_cases` and `_handoff_line_cap_cases` still prints `ok` — each row
  individually, not the aggregate exit code.
- SC-03: The two negative-control rows in the new worktree group print `ok`, so SC-01 cannot pass
  vacuously: an authority pointer that genuinely does not exist in the worktree's `plan.yaml` is
  still refused with exit 2 and the refusal still names that pointer.
  verify: automated  evidence: integration
  command: cd /Users/molchairuangutai/GitHub/harness && env -u HARNESS_AGENT_TYPE python3 tests/integration/test-check-domain.py
  row: the rows named exactly `handoff worktree-only unresolvable pointer refused` and
  `handoff worktree-only brief-sc pointer refused` both read `ok`. They differ in what they prove
  and the difference is part of the criterion: the `unresolvable pointer` row is green BOTH before
  and after the fix and is therefore the vacuity control, while the `brief-sc` row is RED before
  the fix and GREEN after — its needles include the worktree's own `BRIEF.md` path fragment, so it
  is a second red-then-green row proving BRIEF.md is read from the worktree copy.
- SC-04: The `harness_boundary` use in the shape phase remains absorbing: a reviewer reads
  `git show <review_sha>:.claude/skills/harness/bin/check-domain.sh` and cites file:line showing the
  new checkout-root resolution wrapped in `try/except Exception` with a fallback to `root`, raising
  nothing and exiting nowhere.
  verify: inspection
- SC-05: `_norm` still returns a path string and no call site of it changed shape: a reviewer reads
  `git show <review_sha>:.claude/skills/harness/bin/check-domain.sh` and cites `_norm`'s return
  statements plus each call site BY FUNCTION NAME — `_resolved_rel`, `_plan_route`, the `Edit`/
  `Write` target-assembly block in `__main__`, and the sweep's `targets.append`. Call sites are
  named, never numbered: T-02 inserts a helper after `check-domain.sh:1149`, which shifts every
  line number below it, so a numbered anchor sends the reviewer to unrelated code at `review_sha`.
  verify: inspection
- SC-06: The regression test was RED before the fix: a reviewer confirms from `git log` on the
  feature branch that the test commit precedes the fix commit, and that the new case fails when the
  suite is run with `check-domain.sh` at the test commit.
  verify: inspection
- SC-07: The containment bound of REQ-06 holds as intended: a reviewer reads
  `git show <review_sha>:.claude/skills/harness/bin/check-domain.sh` and
  `handoff_done_when.py`, and cites (a) `_read_target`'s `resolved.relative_to(root)` containment
  check, which bounds a target by whatever root it is handed, and (b) the fallback branch of the
  new helper in `check-domain.sh` returning `root`, which is why a main-checkout note's bound is
  unchanged. The cited pair must show that the bound follows the resolved checkout rather than
  widening to both trees.
  verify: inspection

## Approval

status: approved
approved-by: mruangutai
date: 2026-09-07
