# Receipt — harness-backend-dev — T-01 — c1

## BLUF
T-01 done: `resolve_ops`/`cmd_ops`/`ops` subparser added to
`.claude/skills/harness/bin/expertise-merge.py`; `tests/unit/test-expertise-ops.py` created with
all 15 cases (u1,u2,u3,u5..u16). Both acceptance commands exit 0. Apply path (`compute_union`,
`cmd_apply`, `parse_expertise`, `render`, `CAPS`, `UNION_APPLY`, `require_expertise_destination`)
untouched — confirmed by the still-green integration suite. Test-first order was followed and
verified: the suite was written and run before any change to `expertise-merge.py`, and it failed
with an `AttributeError` (resolve_ops did not exist), captured below.

## RED evidence (captured before any production-code change)
```
$ python3 tests/unit/test-expertise-ops.py
Traceback (most recent call last):
  File ".../tests/unit/test-expertise-ops.py", line 23, in <module>
    resolve_ops = expertise_merge.resolve_ops
                  ^^^^^^^^^^^^^^^^^^^^^^^^^^^
AttributeError: module 'expertise_merge_ops_under_test' has no attribute 'resolve_ops'
EXIT=1
```

## GREEN evidence — Acceptance 1 (T-01 verify: block, verbatim from plan.yaml)
Cross-checked against `plan.yaml:339-344` byte-for-byte — matches. Grep-loop passed silently
(no `T-01 MISSING CASE` line), then:
```
$ python3 tests/unit/test-expertise-ops.py
PASS  u1: merged Patterns still has 15 entries
... (all 58 checks) ...
PASS test-expertise-ops.py
$ echo $?
0
```
Full output captured in this run's transcript; every one of u1,u2,u3,u5-u16 prints `PASS` lines,
zero `FAIL`.

## GREEN evidence — Acceptance 2 (pre-existing integration suite, unmodified)
```
$ python3 tests/integration/test-expertise-merge.py
PASS  case1: naive last-writer-wins loses P-02
... (all cases through case10) ...
PASS test-expertise-merge.py
$ echo $?
0
```
`test-expertise-merge.py` was not edited (T-02's file); this is REQ-07/SC-06 evidence the apply
path is intact.

## Implementation notes (pointers, not payloads)
- `resolve_ops` (`expertise-merge.py:~299`) is pure: no IO, no `sys.exit`; raises
  `harness_merge.MergeRefusal`. Broken into small helpers (`_parse_op`, `_resolve_replace_or_drop`,
  `_resolve_add`, `_check_proposal_ambiguity`, `_rebuild_section`, `_apply_resolved`,
  `_check_caps`, `_build_outcomes`) to keep each at grade 4+ per `harness-code-risk-grading`.
- Step D (`_rebuild_section`) walks base entries by `(section, id)` key only, never by index —
  the invariant D-15's HIGH panel finding demanded. u11 (both orders) and u12 (two distinct-index
  drops) exercise it directly.
- `cmd_ops` (`expertise-merge.py:~484`) mirrors `cmd_apply`'s shape: destination refusal to
  stderr/exit 9, all other refusals to stdout, same `harness_merge.locked_update` lock file.
- `--ops` help text (`expertise-merge.py:~549`) literally reads "path to a JSON list of
  add/replace/drop ops, or - for stdin" — names all three verbs plus "JSON", per point 5.
- u10 is the permanent red case, feeding `compute_union` (untouched) the u1 fixture directly —
  reverting `resolve_ops` to the union path would redden it. Never trimmed.

## Underdetermined points
None encountered that required a design choice beyond the plan's intent — see `open_questions`
in the DIGEST for one message-format point I resolved by convention rather than by an explicit
spec sentence (op-index token spelling in Step A refusal lines), recorded there for visibility,
non-blocking.
