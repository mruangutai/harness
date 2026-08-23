# Receipt — harness-dev-ops — T-17 (FEAT-33)

## What T-17 adds

A fourth subcommand, `board_lifecycle.py retitle`, that renames every OLD-format task ticket
(`"T-NN — <title>"`, gh-sync.py's title before T-16) to the format T-16 now writes going forward
(`"<feat> — T-NN — <title>"`, `gh-sync.py:764`). It is the one-time backfill T-18 will run live.

## Flags and exit-code contract

`board_lifecycle.py retitle [--repo <owner/name>] [--apply]`

- `--dry-run` is the DEFAULT (matches `reconcile`'s shape, T-06). `--apply` is required to write.
  This is the same shape T-06 chose deliberately for a tool that touches the live board/tracker —
  the plan does not say otherwise for `retitle`, so I kept it (no deviation to report).
- Exit 0: success, including the case where one or more individual tickets are REFUSED for
  lacking a milestone — a per-ticket refusal is reported and counted, never a reason to fail the
  whole run.
- Exit 2: caller/declaration error — an unrecognised `--repo` (via `_resolve_board`'s existing
  refusal, reused rather than re-authored), or a truncated enumeration (returned count reaches the
  `--limit`).
- Exit 4: a `GhError` from either the enumeration call or a rename call, caught explicitly here —
  never left to `factory_cli.run`'s generic trap, which would exit 2 and read as a caller error
  rather than a network failure. Same convention `provision`/`audit`/`reconcile` already use.

`retitle` shares only the **repo-name** half of `_resolve_board` (reused, not re-authored); the
board it returns is discarded — `retitle` never resolves a project or a card, only issue titles.

## Network-call cost (retitle's own, not covered by audit's four-call docstring figure)

- ONE enumeration: `gh issue list --repo <repo> --state all --limit 1000 --json
  number,title,milestone`. Measured 2026-08-22 at f5f5185: 640 issues, 7 GraphQL points.
- ONE `gh issue edit <n> --repo <repo> --title <new>` PER RENAME. Measured 2026-08-22 at
  f5f5185: 2 GraphQL points each — 188 renames plus the enumeration is 383 points, 7.7 percent of
  the 5000/hour budget.

Stated in the module docstring separately from audit's own four-call figure, per the dispatch's
instruction not to let audit's number be read as covering both.

## Byte-identical proof

`gh-sync.py:764` writes `f"{brief['feat']} — {task['id']} — {task['title']}"` for a freshly
`open`ed task issue. `retitle`'s `_retitled_title(feat, tid, rest)` returns the identical f-string
`f"{feat} — {tid} — {rest}"`, with `rest` captured verbatim by `_OLD_TASK_TITLE_RE = re.compile(r"^(T-\d+) — (.+)$")`
from the OLD title (`gh-sync.py`'s own pre-T-16 title, confirmed by `git log -p` on that line:
`f"{task['id']} — {task['title']}"` — same em dash, same separator, so `rest` equals
`task['title']` exactly). I confirmed the em dash byte matches (both U+2014) by reading both
source lines with a Python script and comparing the extracted f-string bodies character for
character — not merely eyeballing it. No new format is invented; the two functions build the
identical string shape from the identical inputs.

## Milestone derivation (D-20) and its edges

Each selected ticket's feature id is derived from **that ticket's own** `milestone.title` and
nothing else — never plan.yaml, never inferred, never a sibling ticket's milestone.

- No milestone (`milestone` is `null` or absent): REFUSED. Printed (`REFUSED: issue #N ...`),
  counted in the `refused:` bucket, never renamed, never guessed.
- A milestone that names a string that is not a real feature id: not distinguished from a
  "real" feature id at all — `retitle` has no way to validate a milestone title against
  plan.yaml or any feature registry, and the plan does not ask it to; it trusts the milestone
  string verbatim, which is D-20's own choice ("derive... and refuse... rather than guessing" —
  refusing covers only the *absent* case, not a malformed-but-present one). This is a plan gap I
  am reporting, not working around: if a milestone is ever attached with the wrong title, retitle
  will write a wrong-but-confident title. Measured 2026-08-22 (T-17's own intent block): all 188
  candidate tickets on the live board carry a milestone naming their real feature, so this edge
  does not fire on the actual backfill — but the code has no check for it.

## Idempotence (re-run behaviour)

A ticket already starting with its own milestone title followed by `" — "` is counted "already
correct" and skipped, no write issued. In practice, on the real backfill, the selection regex
(`^T-\d+ — `) alone already excludes every renamed title (a real feature id never starts with
`T-\d+`), so the second `--dry-run` in T-18 will report "0 to rename" via that exclusion rather
than via the explicit skip check firing. I implemented and tested the skip check anyway, exactly
as the plan's step 4 describes it, using a contrived fixture (milestone title `"T-9"`, so the same
string satisfies both the selection regex and the already-correct prefix check) — this is a
defensive mechanism for a shape that does not occur on the live data, and I say so in the test's
own comment rather than let it read as claiming a live discriminator it is not.

## Write verbs my mutation markers cover

`test-board-lifecycle.py`'s `rename_calls(log)` filters on `"issue\x01edit" in l and "--title" in
l` — distinct from the pre-existing `mutation_calls` marker set, which already includes generic
`"issue\x01edit"` (catches retitle's rename call too, generically) and `"state_reason="` (the
PATCH marker T-06 added — already present in this codebase at 3ad5131, confirmed by reading the
current tuple before writing any test, so the PATCH gap the dispatch warned about is not
reintroduced here). Every write verb `retitle` can emit — one, `gh issue edit ... --title` — is
covered by both the generic and the specific marker.

## Each case, with its RED proof (mutation applied, restored byte-identical)

All six mutations below were applied to `board_lifecycle.py`, confirmed to redden ONLY the
targeted case(s) while every other case in the same run stayed green, then restored via `cp` from
a saved pre-edit copy and confirmed byte-identical with `diff -q` — never `git stash`.

1. **Dispatch removed** (`__main__` forgets to route `retitle`) — reddened all 8 retitle cases in
   `test-board-lifecycle.py` (every one of them depends on the subcommand actually running).
2. **"already correct" skip removed** — reddened exactly the 3 "already correct" assertions
   (case 3); the ticket got renamed instead, proving the skip is load-bearing.
3. **Milestone-refusal guard removed** (missing milestone silently defaulted to
   `"UNKNOWN-FEAT"`) — reddened exactly the 2 "no milestone" assertions (case 2); the ticket got
   renamed with a fabricated feature id instead of refused.
4. **Truncation refusal removed** — reddened exactly the 2 truncated-enumeration assertions
   (case 4); the run proceeded and exited 0 with `renamed: 0` instead of refusing at exit 2.
5. **`--dry-run` early-return removed** (apply-by-default) — reddened the 2 dry-run assertions
   in the unit test AND the 3 case-(N) assertions in `test-factory-integration.py`'s forked
   process — proving the default-write disaster the plan calls out.
6. **`_resolve_board` reuse bypassed** (repo taken verbatim, refusal skipped) — reddened the
   unknown-`--repo` case; the fake `gh` was actually called with `acme/unknown-repo` instead of
   refusing before any call.

Each mutation's diff was applied via a Python string-replace against the live file (never
`git stash`), the test suite (or, for #5's second half, `test-factory-integration.py`) re-run to
confirm the exact reddened set, then restored with `cp` from a copy saved before any edit, and
`diff -q` against that copy confirmed byte-identical after every restore.

## Integration coverage (D-12)

`test-factory-integration.py` case (N): forks `board_lifecycle.py retitle` with NO flags against
a fixture carrying one pending rename (milestone `"FEAT-INTEG-RETITLE"`). Asserts: exit 0; the
rename is previewed on stdout (`DRY-RUN would rename #970`); zero `["issue", "edit"]` calls with
`--title` reached the stub `gh`; the stub's own state for that issue is untouched. This is the
boundary evidence that `--dry-run` really is the default and `--apply` really is required, before
this tool is pointed at the operator's live tracker — the same shape T-06's case (M) uses for
`reconcile`. I extended the stub `gh`'s `["issue", "list"]` dispatch to answer a `--json
number,title,milestone` query distinctly from audit's `--json number,stateReason,labels` query
(same argv prefix, different `--json` value), and extended `["issue", "edit"]` to record a
`--title` write onto its own state. No file added to any list; `run-unit-tests.sh` and
`harness.json` untouched (both already correct, per T-04's own intent, unchanged here).

## Digest mapping note (issue #778, now nine-for-nine)

Plan's `change_type: feature` is rejected by `validate-digest.py:158`'s dev-ops enum
(`{config, scaffolding, infra, ci}`). Substituted `ci`, following T-06's own precedent exactly —
this task adds a subcommand to the same CI-adjacent lifecycle tool with branching logic and its
own test coverage. Reporting the rejection rather than silently picking a value.

## Verify

Command (verbatim from `plan.yaml`): `.claude/skills/harness/bin/run-unit-tests.sh --kind all`

Ran in the background (full-repo suite spans several minutes, per D-14's own measurement).
`test-board-lifecycle.py` (unit) and `test-factory-integration.py` (integration) were also run
standalone first and both passed in full (see below) before the aggregate run.

```
$ python3 .claude/skills/harness/bin/test-board-lifecycle.py
...
all checks passed.

$ python3 .claude/skills/harness/bin/test-factory-integration.py
...
131/131 checks passed.
```

Full-repo `run-unit-tests.sh --kind all` result: ran in the background (started before this
receipt, appended once it actually finished, never reported ahead of the real outcome). All 42
registered scripts (20 `UNIT_SCRIPTS` + 22 `INTEGRATION_SCRIPTS`) printed `PASS test-<name>.py`
with zero `FAIL`, zero `MISCONFIGURED`, zero `Traceback` anywhere in the ~2800-line log —
confirmed by grep against the full captured output, not by trusting the tail alone. Includes
`PASS test-board-lifecycle.py` and `PASS test-factory-integration.py` (containing this task's
case (N)).
