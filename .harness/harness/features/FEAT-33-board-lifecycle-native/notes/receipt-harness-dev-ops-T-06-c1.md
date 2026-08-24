# Receipt — harness-dev-ops — FEAT-33 T-06

## BLUF

`reconcile` (T-06) is built, tested, and green. It runs `audit`'s own `_audit_findings` once,
attempts the write for every finding a write can fix, catches and continues past a single
failed write, re-runs detection to compute the residual truthfully, and exits accordingly.
One plan ambiguity found and resolved by inference (documented below); no plan defect worth
blocking on.

## Exit-code contract

| Code | Meaning |
|---|---|
| 4 | `GhError` from either detection pass — the run could not complete (never 0 or 1) |
| 0 (`--dry-run`, the default) | always, once detection succeeds — a preview attempts nothing, so nothing can be reported as "surviving" a fix never tried |
| 0 (`--apply`) | no STATION, REASON, LABEL, or STATUS(non-Done) finding survives the post-fix re-detection |
| 1 (`--apply`) | at least one of those survives; DECLARATION, WORKFLOW, and STATUS(Done) residuals are printed but never counted |

## Plan inconsistency found, and how I resolved it

The plan's exit-code paragraph literally enumerates "STATION, REASON or LABEL" — omitting
STATUS — right after a paragraph that calls STATUS "a FOURTH fixable class beside the three
below" with no stated exemption from the exit count. I read this as an editing omission, not
a deliberate exclusion: the paragraph's own header ("THE EXIT CODE COUNTS ONLY THE CLASSES
RECONCILE CAN FIX") generalizes to all fixable classes, and there is no WORKFLOW-style
structural reason to exclude a class this tool DOES write. I implemented STATUS as counted,
**except** for status `Done`, which the plan explicitly says reconcile never writes for — that
one status value I treat as fixable-class-but-never-attempted, exactly like DECLARATION and
WORKFLOW, for the identical "counts only what it fixes" reason the plan gives for WORKFLOW
(counting it would permanently gate exit 0 on a class this tool never touches). This is a
decision, not a workaround; flagging it here rather than silently picking one reading.

## Network-call cost

`--dry-run`: exactly audit's 4 calls, nothing more. `--apply`: those 4, plus one write per
fixed finding (LABEL costs 2: the direct label-create shell-out plus the issue edit), plus a
second, identical 4-call detection pass to compute the residual rather than assume every write
landed. Documented in `board_lifecycle.py`'s module docstring, explicitly stated as NOT
covered by audit's own four-call contract.

## Partial failure mid-write

Each fixable finding's write is wrapped in its own `try`/`except (gh_board.BoardError,
factory_gh.GhError)`. A failure prints `factory: board_lifecycle: fix failed -- <exc>` on
stderr and the loop continues to the next finding — never `break`, never re-raise. Proven by
mutation: adding `break` after the except clause reddened two tests (`test-board-lifecycle.py`
"reconcile (partial failure): the run continues..." and "...#50 survives..., #51 does not")
before I restored the file. Whatever writes DID land before the failure stay landed —
`reconcile` never rolls back. Re-running `reconcile --apply` is always safe: it is pure
detection-then-fix-per-finding, and a finding that is already correct is not re-emitted by
`_audit_findings`, so nothing gets double-applied.

## Idempotence

Re-running `--apply` against an already-correct board: 4 detection calls, zero fixable
findings, zero writes attempted, exit 0. Proven directly — `test-board-lifecycle.py`'s clean-
board case runs `reconcile --apply` twice and asserts zero mutations both times.

## RED proof (each new discriminating case, mutant applied then restored byte-identical)

No `git stash` used anywhere — every mutation was applied via a Python one-liner directly to
`board_lifecycle.py`, verified against a `cp` copy taken before editing, and restored with
`cp` + `diff -q` (byte-identical confirmed each time; `git status --short` shows only my two
intended files changed throughout).

1. **Continue-past-failure**: added `break` after the `except` in the apply loop → reddened
   "the run continues past issue #50's failed write to issue #51" and "#50 survives..., #51
   does not" in `test-board-lifecycle.py`. Restored, re-verified green.
2. **Exit-code gating**: removed the `if fixable_residual: sys.exit(1)` line → reddened
   "reconcile (partial failure): exits 1..." (the only check tied to that exact statement).
   Restored, re-verified green.
3. **Label colour**: changed `_ABANDONED_LABEL_COLOR` from `b60205` to `factory_gh`'s own
   `5319e7` → reddened "LABEL -- creates the abandoned label with b60205 directly...".
   Restored, re-verified green.
4. **Integration boundary (case M)**: forced `cmd_reconcile(args.repo, True)` regardless of
   `args.apply` → reddened all three (M) checks in `test-factory-integration.py`, including
   "ZERO mutations reached the stub gh" once I added `PATCH` to that check's marker list (an
   earlier version of the marker set missed the REASON fix's PATCH call — found and fixed
   before finalizing). Restored, re-verified green.

## Test cases added

`test-board-lifecycle.py` (+377 lines): reconcile GhError (exit 4); `--dry-run` zero
mutations + preview text + feature.json untouched; `--apply` fixing one of each fixable class
(argv asserted by content, not count, for each: `number=10`+`OPT_Done`, `number=40`+
`OPT_Building`, `issues/20`+`state_reason=completed`, `label`+`create`+`abandoned`+`b60205`
and `issue`+`edit`+`30`+`abandoned`) plus feature.json byte-unchanged; partial-failure
continuation (BoardError on issue #50, #51 still fixed, #50 survives as residual, exit 1);
DECLARATION+WORKFLOW residuals never gating exit 0; Done-status STATUS finding never
auto-fixed (exit 0, no `set_station` call for #85); clean-board idempotence (twice, both zero
mutations).

`test-factory-integration.py` (+101 lines, case M): `reconcile` with **no flags** against a
fixture with one REASON finding — exits 0, previews the finding, zero mutations. This is the
boundary evidence that `--dry-run` really is the default before this tool is pointed at a live
board.

`test-board-lifecycle.py`'s bash fake `gh` gained cases for `projectItems`, `project
item-edit`, `label create`, `issue edit`, and any `state_reason=` PATCH, plus a
`FAKE_STATE`-marker before/after switch (`_after` helper) so a write's effect can be reflected
in the SECOND detection pass without a fully stateful fake.

## Digest mapping note (issue #778, now eight-for-eight)

Plan's `change_type: feature` is rejected by `validate-digest.py:158`'s dev-ops enum
(`{config, scaffolding, infra, ci}`). I substituted `ci` — this task adds a subcommand to a
CI-adjacent lifecycle tool with branching logic and its own test coverage, closer to `ci` than
to `config`/`scaffolding`. Reporting the rejection rather than silently picking a value.

## Verify

Command (verbatim from `plan.yaml`): `.claude/skills/harness/bin/run-unit-tests.sh --kind all`

Ran in background (full-repo suite), completed exit code 0. Tail of output (last 80 lines,
piped through `tail -80` per my own invocation) shows unrelated suites (inflight-registry,
dispatch-guard) all passing; the aggregator's own exit code is the authority here:

```
[exited with code 0]
```

Independently also ran directly, unpiped, and both are green:
- `python3 .claude/skills/harness/bin/test-board-lifecycle.py` → `all checks passed.` (exit 0)
- `python3 .claude/skills/harness/bin/test-factory-integration.py` → `127/127 checks passed.`
  (exit 0)

## Scope discipline

Touched only my three assigned files:
`.claude/skills/harness/bin/board_lifecycle.py`,
`.claude/skills/harness/bin/test-board-lifecycle.py`,
`.claude/skills/harness/bin/test-factory-integration.py`.
Did not touch `gh-sync.py`, `DECISIONS.md`/`DECISIONS-INDEX.md`, `check-state.sh`,
`test-check-state.py`, `test-gh-sync.py`, or `plan.yaml` — those carry sibling tasks (T-16,
T-19, main session) already in progress in this worktree; their presence in `git status` is
not mine. No approval or `plan.yaml` field was touched. No commit was made.
