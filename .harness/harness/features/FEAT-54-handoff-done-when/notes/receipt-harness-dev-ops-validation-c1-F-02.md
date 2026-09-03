# Receipt — validation c1 F-02 secure manual probe

PASS: the manual comprehension probe now rejects untrusted note targets before any model invocation, while valid handoffs and dry-run behavior remain intact.

## Implementation

- `tests/manual/probe-handoff-comprehension.py:54-108` centralizes containment, name, symlink, regular-file, UTF-8, and 1 MiB bounded-read validation. The seam returns an already-read `ValidatedNote`, so neither measurement nor `omp` can precede validation.
- Both explicit CLI selection and default discovery flow through that one deep interface (`note_paths` -> `validate_note`); no hypothetical adapter was added.
- `measure_note` was split only at its existing arm-reporting boundary (`tests/manual/probe-handoff-comprehension.py:181-211`), preserving its report semantics while reducing its risk grade.
- Focused coverage is in `tests/unit/test-probe-handoff-comprehension.py`.

## TDD evidence

RED command (before production edits):

```sh
python3 tests/unit/test-probe-handoff-comprehension.py
```

Exit 1. Five tests ran; two failed. The pinned implementation made two model-stub invocations for an explicit absolute outside file and two for a repository-contained symlink. This directly demonstrated the pre-fix disclosure path; non-regular rejection, valid two-arm measurement, and dry-run were already green.

Final GREEN command:

```sh
python3 tests/unit/test-probe-handoff-comprehension.py
```

Exit 0. Six tests passed. Rejected repository-outside, absolute-outside, traversal, explicit/default symlink, directory, wrong-basename, and oversized inputs all reached zero model-stub calls. A valid handoff reached both arms, and dry-run reached plan preparation with zero calls.

## T-09 verification

The dispatch's T-09 verify text was cross-checked against `.harness/harness/features/FEAT-54-handoff-done-when/plan.yaml:634-655`; it matches. Per dispatch, only the two applicable dry-run/model-call clauses were run:

```sh
cd "$CLAUDE_PROJECT_DIR" && python3 tests/manual/probe-handoff-comprehension.py --dry-run && python3 -c "
import runpy, sys
P='tests/manual/probe-handoff-comprehension.py'
BLOCKED=('socket.connect','socket.getaddrinfo','subprocess.Popen','os.system','urllib.Request')
def hook(event, args):
    if event in BLOCKED: raise SystemExit('probe made a %s call during --dry-run' % event)
sys.addaudithook(hook)
sys.argv=[P,'--dry-run']
try:
    runpy.run_path(P, run_name='__main__')
except SystemExit as e:
    if e.code not in (0, None): raise
print('ok: dry run made no model call')"
```

Exit 0. Both runs selected `handoff-build.md`, printed two planned calls as not executed, and the audit-hook clause printed `ok: dry run made no model call`. The registration assertion and `run-unit-tests.sh --check-layout` clauses were intentionally not rerun because this fix forbids registration edits and broad validation.

## Risk grade

Scoped mandatory command:

```sh
python3 .claude/skills/harness/bin/code-grade.py tests/manual/probe-handoff-comprehension.py tests/unit/test-probe-handoff-comprehension.py
```

Exit 0, `PASSING: 29`. `measure_note` is grade 4 (cyclomatic 3, cognitive 0, ABC 12.7); `validate_note`, `read_regular_file`, and `measure_arm` are grade 4 or better, and every focused test function is grade 4 or better.

For transparency, the skill's commit-range example was also run verbatim with `--base "$(git merge-base origin/main HEAD)" --head HEAD`; it exited 1 because it inspects committed HEAD rather than these worktree edits and includes pre-existing failures in prohibited sibling files. Its old-HEAD `measure_note` result was grade 2; the required worktree-scoped command above proves the refactor is grade 4.

## Files touched

- `tests/manual/probe-handoff-comprehension.py`
- `tests/unit/test-probe-handoff-comprehension.py`
- `.harness/harness/features/FEAT-54-handoff-done-when/notes/receipt-harness-dev-ops-validation-c1-F-02.md`
