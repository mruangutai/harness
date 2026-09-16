# Research note — BUG-276 — plan cycle 2: the verify blocks are now executable shell

The plan of record is `.harness/harness/features/BUG-276-expertise-merge-duplicate-id/plan.yaml`.
This note no longer carries a copy of the proposal: the earlier copy held cycle 1's prose
`verify:` blocks, and a stale duplicate of a plan is a trap for the next context. Read plan.yaml.

## The cycle-1 defect and the fix

Both tasks' `verify:` blocks opened with the interpreter invocation and then continued in
English ("Expected exit 0, ... carries at least one PASS line ..."). `verify:` is executed as
shell by the member and by the qa gate, so those lines ran as commands, exited 127, and the
block's status was the LAST command's — a correct implementation would have reported FAIL, and
the case-name expectation was checked by nobody.

Both blocks are now command-and-`#`-comment shell only, following
`.harness/harness/features/BUG-1302-suite-layout-fail-closed/plan.yaml:92-95`:
`out=$(<suite>) && printf '%s\n' "$out" | grep -q '^PASS  <case name>'`, one grep per new
sub-case. `env -u HARNESS_AGENT_TYPE` stays on each interpreter invocation.

## Why a green suite alone could not be the gate

Measured at 6d969ed3 in this worktree: `tests/unit/test-expertise-ops.py` exits 0 and
`tests/integration/test-expertise-merge.py` exits 0 — both already green without the new cases.
A block that asserted only the suite's exit status would therefore pass today, before any work.
The greps carry all of the discrimination.

## Markers asserted, and the discrimination proof

T-01 greps three unit check names — `u23a: different texts refuse with code 11`,
`u23b: identical texts refuse with code 11`, `u23c: no base refuses with code 11`.
T-02 greps three integration check names — `case27a: duplicate ids exit 11`,
`case27b: identical duplicate ids exit 11`, `case27c: absent destination exits 11`.

Both suites print a passing check as `PASS`, TWO spaces, then the name
(`test-expertise-ops.py:387`, `test-expertise-merge.py:1342`), which is why the grep patterns
carry two spaces; each task's `intent:` now hands the member those exact strings and says the
verify greps for them.

- Each block, loaded verbatim from plan.yaml with `safe_load` and run through `bash -c` at
  6d969ed3: **exit 1** for T-01 and **exit 1** for T-02. The cases do not exist yet.
- Positive control: the six marker names fed through the same printer expression
  (`print(f"PASS  {name}")`) satisfy every grep — exit 0. The greens are reachable, not merely
  assumed (they would otherwise be an unfalsifiable clause).
- Wall time: unit block ~0.1s, integration block ~7.3s. Both inside the 60s bound.

## State

`check-plan-routes.py` on this plan: 0 violations, exit 0. `approval.status: pending`, no
`panel:` key, `lanes.resolved_at: 6d969ed3`, both tasks carry every required field. Every write
went through `plan-merge.py amend --expect-sha256 --value-file` (four amends: `verify` and
`intent` on each task); `apply` was not usable here because it exits 7 CONFLICT on a changed
value. BRIEF.md needed no follow-on edit — its SC `evidence:` kinds name test kinds, not case
names.

## Open

None. The plan is ready for the panel / signature route.
