# Goal-check remedies applied — BUG-1480 plan c0

**All six dispatched findings are applied.** `approval.status` is still `pending`, the task set is
still exactly `T-01, T-02`, `lanes:` and `D-01..D-03` survived, and T-02's `verify:`/`intent:` were
never opened. One process deviation: `plan-merge.py apply` cannot revise an existing task (below).

## What changed

**plan.yaml — T-01 only.**

- **F-05 (placement).** `intent:` now says the call goes as the LAST call INSIDE
  `with tempfile.TemporaryDirectory() as root:`, immediately after `_handoff_line_cap_cases(...)`
  and BEFORE `return _report_handoff_results(results)` — with the reason: that return is at
  `test-check-domain.py:4424`, outside the block, so a group placed there gets a deleted `root`.
  The DEFINITION placement (after `_handoff_line_cap_cases`) and the shared temp `root` are
  unchanged.
- **F-01 (row 3 needle).** Row 3's needles become
  `("SC-99", os.path.join("BUG-1480-wt", ".harness", "harness", "features", "BUG-1480-wt-fixture", "BRIEF.md"))`,
  and the row is restated as a SECOND red-then-green row, not a control. The intent carries why a
  trailing fragment and not the absolute `wt_path` (`checkout_relative` may return a realpath
  spelling — `/private/var` vs `/var` on macOS), and why the fragment is a safe substring
  (`_unresolved` at `handoff_done_when.py:112-113` emits one unwrapped line; `_record_handoff_result`
  at `:4132-4137` does a case-insensitive substring test). Row 2 is untouched and one clause says
  so explicitly, so exactly one vacuity control survives.
- **F-03 (verify conjunct).** `verify:` is one captured suite run plus two greps — the row-1 `FAIL`
  grep and a new `ok` grep on `handoff worktree-only main root has no feature dir`. Still a literal
  `|` block. Print shape re-derived at source before writing: `_report_handoff_results`
  (`test-check-domain.py:4402-4407`) prints `("ok   " if ok else "FAIL ")`, `name`, detail with the
  default `sep=' '`, so `^ok +NAME` and `^FAIL +NAME` both match and no `$` anchor is safe. The
  FAIL grep names row 1 by a prefix no other row shares, so F-01's now-red row 3 cannot satisfy it.

**BRIEF.md — direct write.**

- **F-02.** SC-05 cites call sites BY FUNCTION NAME: `_resolved_rel`, `_plan_route`, the
  `Edit`/`Write` target-assembly block in `__main__`, and the sweep's `targets.append`. All four
  confirmed present in `check-domain.sh` at HEAD (defs at `:1852`, `:1910`; assembly `:2042-2078`;
  `targets.append` `:2218`). `verify: inspection` kept; the criterion is still that `_norm`'s
  return contract is unchanged.
- **F-04.** SC-01/02/03 keep the shared suite command as the RUNNER and each gains a `row:` line
  naming its own printed evidence. SC-03 additionally states which control changes state across
  the fix (`brief-sc`, red→green) and which does not (`unresolvable pointer`, the vacuity control).
- **F-06.** New `REQ-06` (containment bound moves with the root; main-checkout notes unaffected via
  the helper's `root` fallback) and new `SC-07`, `verify: inspection`, evidence being
  `handoff_done_when._read_target`'s `relative_to(root)` check plus the new helper's fallback
  branch. No task added, T-02's intent untouched, REQ-02 untouched.

## The one deviation — write route

The dispatch specified `plan-merge.py apply` on a re-supplied T-01. `apply` unions but **refuses any
changed value**: it exited 7 `CONFLICT: id='T-01' in 'tasks' carries two different values`. The
sanctioned revision verb is the same tool's `amend --field <f> --expect-sha256 --value-file`, which
splices one field under the same lock. Both edits went through it (`AMENDED tasks:T-01.verify`,
`AMENDED tasks:T-01.intent`). No Edit, no Write, no redirect touched plan.yaml.

## Verification run

- Acceptance assertion (approval pending, tasks exactly `T-01,T-02`): **exit 0**.
- T-02 `verify:`/`intent:` unread by `amend` and byte-identical on re-read; `lanes.resolved_at`
  `75cef65b`, 2 rows; decisions `D-01,D-02,D-03`.
- `bash -n` on T-01's new verify: parses.
- `check-plan-routes.py <this plan>`: `0 violation(s)`, exit 0. The two `DEVIATION` lines are the
  expected DEC-174 carve-out output, not failures.
- The integration suite was NOT run (dispatch non-goal).

## Open — noted, not applied

`BRIEF.md`'s `## Constraints` BLOCKS entry still spells the `_norm` call sites with the same
pre-fix line numbers F-02 struck from SC-05 (`:1906`, `:1912`, `:2042-2048`, `:2073`, `:2077`,
`:2089-2090`). It already names the functions too and grades nothing, so it does not rot a review —
but it is the same numbers in the same file, and a later reader will trust them. Out of this
dispatch's scope; raise it before signature if the operator wants one spelling.
