# FEAT-53 cycle-8 scoped check repair experiment

Date: 2026-09-16

## Conclusion

The requested plan-only repair is blocked by the installed checker contract. With the precise task ownership and approved routing restored, the exact scoped check exits 1 with 31 tasks, 62 anchors resolved, and 63 failures. No valid `plan.yaml`-only edit can make those failures disappear without contradicting D-02/T-01, erasing exact task file ownership, or executing forbidden build/grant work.

Exact command:

`python3 /Users/molchairuangutai/GitHub/harness/.agents/skills/harness/bin/plan-merge.py check --file /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-53/.harness/harness/features/FEAT-53-metrics-dashboard/plan.yaml --root /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-53`

## Concrete failure classes

Both the initial invocation and the final invocation after restoration report the same two classes:

- 45 future-file anchor failures. The planned `dashboard/`, `dashboard/client/`, `dashboard/client/src/`, `dashboard/client/dist/`, and fixture files do not exist and neither do their immediate parent directories.
- 18 execution-agent route failures. T-18, T-13, T-14, T-15, T-21, and T-28 correctly name `harness-frontend-dev`, but the live manifest does not grant that agent the future client subtree until planned predecessor T-01 executes. The live resolver currently reports only `harness-backend-dev` and `harness-dev-ops` for those paths.

No trace-id, schema, dependency, panel, or approval failure is present.

## Irreducible checker limitation

The installed `plan-merge.py check` resolves an absent bare future file only when that file's immediate parent directory already exists. A `{path, quote}` anchor is not a future-file escape hatch: it requires the target file itself to exist and contain the quote. This feature deliberately creates the entire dashboard subtree during build, while this dispatch forbids creating any implementation directory or file.

The route half resolves grants only from the live domain manifest. It does not apply `plan.yaml` lanes, model the T-01 dependency, or project T-01's planned `.claude/skills/harness/bin/dashboard/client/**` grant before checking later client tasks. Therefore the pre-build check cannot validate the route that becomes legal only after T-01.

The only plan-only shapes that made the command exit 0 were invalid substitutions: replacing precise future-file ownership with the broad existing `.claude/skills/harness/bin/` directory, which manufactured a 21-task overlap and erased ownership, and rerouting six frontend tasks to `harness-dev-ops`, which contradicted D-02, T-01, and consult-when. Those substitutions were a failed experiment, not an acceptable repair.

## Restoration

All experimental plan changes were reversed through `plan-merge.py apply`:

- The precise pre-experiment `files` lists were restored on all 21 affected tasks.
- T-18, T-13, T-14, T-15, T-21, and T-28 were restored to `execution_agent: harness-frontend-dev`.
- Task intent, verify, dependencies, traces, status, scope, decisions, lanes, panel, and approval were never changed.

The final exact check reproduces the honest known result: exit 1, 31 tasks, 62 anchors resolved, 63 failures. Its `OVERLAP` lines remain advisory and non-failing; they describe the plan's deliberate shared files and do not justify invented dependencies.

## Preserved record

- `panel.cycle` remains 8.
- All twelve cycle-8 findings remain `resolved`; zero cycle-8 findings are open.
- `approval.status` remains `pending`, with `approved_by: none` and `date: none`.
- The cycle-8 panel contents and dispositions are unchanged.
- No BRIEF, DESIGN, implementation, build, test, formatter, linter, or project-wide validation was run or changed.
- No file under `notes/prototypes/FEAT-53/` was read, written, rebuilt, or otherwise touched.

## Required resolution outside this dispatch

One authority outside the present constraints must change: either the checker must gain a first-class future-subtree anchor and planned-grant model, or the live grant and parent directories must exist before the check runs. Both are outside a plan-only, no-build correction and require the tier above to choose the contract change.
