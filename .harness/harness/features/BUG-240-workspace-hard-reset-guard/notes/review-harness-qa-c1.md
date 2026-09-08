# QA gate re-run — BUG-240-workspace-hard-reset-guard — cycle 1 — GATE ONLY

**matrix_ok: true.** F-PANEL-01 is RESOLVED at `bae47f3c`: the identity check is now
`os.path.samefile(path, _control_plane_root())` with a `realpath`-string fallback only inside the
`OSError` arm (`factory_workspace.py:142-148`). Author-nothing audit — no test, fixture, or source
was written or edited by this run (`git status --porcelain` clean before and after).

## Change type and required kinds

Diff `6d969ed..bae47f3c` (two files): `.claude/skills/harness/bin/factory_workspace.py` (+54, T-02,
`change_type: bugfix`) and `tests/unit/test-factory-workspace.py` (+239/-3, T-01,
`change_type: scaffolding`). `.harness/harness.json` `test_matrix.bugfix`:
- `unit` `if: touches_runtime_code` → **fires** (production file touched) → **required**.
- `integration` `if: fix_confined_to_tests_and_contract_docs` → does not fire (production file was
  touched, not tests-only) → not required.
- `__bug_class__` `if: match_bug_class` → per repo Expertise (G-08) this predicate has no resolvable
  taxonomy entry for any diff yet → not required (floor stays at `unit`).

`scaffolding`'s own row (`always: []`) adds nothing. **Required floor: `unit` only.**

## Per-kind result

| kind | state | evidence |
|---|---|---|
| unit | **satisfied** | `python3 tests/unit/test-factory-workspace.py` exit 0; `bash .agents/skills/harness/bin/run-unit-tests.sh --kind unit` exit 0 |
| integration | not applicable | predicate does not fire for this diff |
| `__bug_class__` | not applicable | predicate unresolvable project-wide (repo Expertise G-08) |

## Unit run detail (both commands run with `env -u HARNESS_AGENT_TYPE`, per G-07/mechanical fact (a))

- `python3 tests/unit/test-factory-workspace.py`: captured exit status in a variable = **0**.
  Final line: `39/39 checks passed.` Separately counted `^FAIL` lines = **0**, `^ok` lines = **39**,
  `^skip` lines = **0**. Matches the expected 39-checks/0-FAIL state exactly.
- `bash .agents/skills/harness/bin/run-unit-tests.sh --kind unit`: exit status = **0**, `^FAIL`
  count = **0** (per-script `PASS`/exit-0 summary; unrelated to the source's own `FAIL ` idiom).
- **Case 8 RAN on this host** (no `skip` line was printed): the case's own probe
  (`os.path.isdir(wr/PROBE)` after creating `wr/probe`) found this tmpdir volume case-insensitive,
  so the case-mismatch fixture executed for real, not vacuously. On a case-sensitive host this same
  suite would still read `39/39 checks passed` with one `skip` line instead of the case-8 `ok` line,
  and the count (not the exit code) would be the tell that the case never exercised anything — that
  did not happen here.

## Case 8 binds F-PANEL-01 (reasoned, from reading — no mutation of source performed, per
author-nothing scope)

Traced by inspection, not by flipping the source (disallowed this cycle):
`checkout_path(wr) = wr/widget` (real dir, created); `_control_plane_root` stubbed to
`wr/Widget` (never created as a distinct directory). Because the tmpdir volume is
case-insensitive, `os.stat("wr/Widget")` resolves via case-insensitive lookup to the SAME inode as
`wr/widget`, so **post-fix** `os.path.samefile(...)` returns `True` with no `OSError` — the
identity check fires, refuses (exit 2, no `fetch`/`reset`/`clone` recorded), matching the case's
assertion. **Pre-fix**, `os.path.realpath` is a pure lexical resolver (no on-disk case
canonicalization) and returns each path in the case it was given — `"…/widget"` vs `"…/Widget"` —
which are unequal strings, so `is_control_plane` would be `False`, the refresh would proceed, and
`fetch` would appear in `rec.calls`, failing the case's own `not any(k in (...))` conjunct. This is
exactly the F-PANEL-01 defect shape (string comparison blind to case-insensitive identity) and the
case is red pre-fix / green post-fix by construction. I did not literally revert the source and
re-run in this dispatch (author-nothing), so this is a reasoned trace of the mechanism, not a
freshly-measured redden — flag it as such per Expertise O-03.

## SC binding (which assertion binds which SC — none newly authored, restating what already exists)

- SC-01 (dirty tracked, refused, file survives) → BUG-240 cases 1/2/3.
- SC-02 (ignored-only dirt not refused) → BUG-240 case 4.
- SC-03 (self-checkout refused, names condition) → BUG-240 case 5, extended by case 8 for the
  case-insensitive-spelling variant of the same identity predicate.
- SC-04 (order preserved, clone-vs-refresh unchanged) → the existing-checkout-order check appended
  inside case (B), plus unchanged cases (A)/(B)/(C).
- SC-05 (`run-unit-tests.sh --kind unit` exits 0) → directly measured above, exit 0.
- SC-06 (no bypass, inspection) → BUG-240 case 7 (`--force`/`--yes`/`FACTORY_FORCE` absent from
  source text) plus argparse rejecting `--force`; verified by inspection per the SC's own
  `verify: inspection`, not this gate's job to re-adjudicate.

## Restated cycle-0 backlog (non-gating, per dispatch — not re-opened here)

- F-PANEL-02 (TOCTOU, med), F-PANEL-03 (docstring mechanism, low), F-PANEL-04 (refusal-copy noun
  phrasing, low), F-PANEL-05 (`_main` ABC grade_2, med), ALT-5 (dirty check over untracked-ignored
  scope, med) — all already dispositioned by the lead; restated for completeness, not blocking.
- qa F-01/F-02 (low) — restated; F-02 is `PF-d795aab03bf4a49e7ef3ef6614024cdf`, KEPT (open, low) by
  the operator at signature — not a new finding, not gating.

## Files touched by this run

None. Only this note was written. `-c0.md` untouched. No test or source file created or modified —
confirmed via `git status --porcelain` (clean, both before and after this run).
