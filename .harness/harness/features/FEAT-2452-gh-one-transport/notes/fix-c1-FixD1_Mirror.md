# Fix c1 — FixD1_Mirror: H1, G1, F1

Ungoverned builder for the main session (DEC-174). Worktree HEAD `15a240bc`. `HARNESS_AGENT_TYPE`
and `CLAUDE_PROJECT_DIR` were unset for every run. Raw outputs are in `fix-c1-FixD1_Mirror/`, and
each one ends with its own `exit=` line. No git writes were made, and no formatter was run.

Files changed:
- `.claude/skills/harness/bin/gh-sync.py`
- `tests/integration/test-gh-sync-abandon.py`. There is no `test-gh-sync-reject.py`; the reject
  cases already live in this file (`_reject_fixture`, R0–R7), so the reject regression is here too.
- `tests/integration/gh_sync_support.py`
- `.claude/skills/harness/references/github-mirror.md`

## H1: a label-create failure no longer mirror-SKIPs abandon and reject

**Change.**
- `ensure_labels(repo, labels)` keeps the pinned label-exists matcher unchanged:
  `text = …lower()`, `exists = (isinstance(result.status, int) and result.status != 0 and
  "label with name" in text and "already exists" in text)`, `if not (result.ok or exists):`.
- What changed is what happens on failure. It now **returns** the first failure line
  (`label <l> could not be created on <repo>: <diagnostic>`), or None when every label exists.
  The check still runs before any dependent label attachment. The caller applies its own policy:
  - **Mirror flows keep SKIP/0.** The new `mirror_labels(repo, labels)` is `ensure_labels` plus
    `skip()` on failure. Every former SKIP caller now uses it: `_open_ensure_labels` (both branches)
    and the recover-terminal branch of `_finish_replacement`. Start-task never called
    `ensure_labels`.
  - **abandon:** `label_gap = ensure_labels(repo, {"abandoned"}) if plan else None`. The new
    `_label_abandoned(repo, num, label_gap)` attaches the label only when the create succeeded.
    Either failure, the create or the attachment, prints the existing per-ticket line
    `#N closed but not labelled \`abandoned\`: …`. Closes, reseats, comments, detaches, the
    milestone close and the local `abandoned` station all run as before, and the exit is 0.
  - **reject:** `_RejectWrites.label` raises `_RejectHalt(failure)`. `_run_reject_steps` then
    prints its report (what landed, what did not run, station not written) and exits 1.
- The unit seam in `tests/unit/test-gh-sync-abandon-sources.py`, which patches
  `gh_sync.ensure_labels` with a None-returning lambda, still intercepts abandon's create, and
  None reads as success. That test is unchanged and green (`03-green-unit-abandon-sources.txt`).

**Regressions.** The new helper `label_create_fails(script, response)` in `gh_sync_support.py`
makes any fake's `label create` print `HTTP 403: Resource not accessible by integration` and exit
1. It raises if the fake has no such branch. Two new module-level cases in
`test-gh-sync-abandon.py` use it, called from `main()` next to #13 and next to R4:
- `abandon_label_create_failure_case`:
  - no SKIP, exit 0, and the failed create named with its 403;
  - 41, 42 and the parent 40 each closed and reseated to Backlog, and the milestone closed;
  - no `--add-label`, and each closed ticket reports the gap;
  - station `abandoned`.
- `reject_label_create_failure_case`:
  - exit 1, no SKIP, and `ERROR - label superseded could not be created … HTTP 403`;
  - the halt report names the close and the comment as landed, and the backlog return and the
    milestone close as NOT run, and says the station was NOT written;
  - no `--add-label`, backlog or milestone write, and the station is not `rejected`.

**Red against HEAD 15a240bc.**
- `01-red-label-create-head.txt`: the test run before any production edit, with gh-sync.py
  untouched (exit 1, 6 FAILED). Abandon logs only `auth status` and `label create abandoned`, then
  `gh-sync: SKIP — label abandoned could not be created …`, with the station still `building`.
  Reject logs `parent #40 closed` and then SKIP, rc=0, with no halt report.
- `05-red-final-tests-at-15a240bc.txt`: the same red with the final test text. I extracted
  `git archive 15a240bc` (`.claude/skills/harness`, `tests`, `.harness/team-config.yaml`,
  `.harness/factory`) into a scratch tree and copied the final test and support files over it.
  HEAD's gh-sync.py blob is `86ddc86f`, and the file says so. Result: exit 1, exactly the 6 new
  checks FAIL, and every legacy check passes. The scratch tree was removed afterwards.
- One check is green in both reds: reject's "no --add-label, backlog or milestone write, and no
  station" also holds under SKIP. It guards the halt and was never meant to discriminate.

**Green.** `06-verify-T-02.txt`: all 7 new checks pass. The open guard `failed first label create:
SKIP, exit 0, and no dependent issue create` and the existing-label acceptance also stay green.

**Grades** (`04-grades.txt`, produced by `grade.py` with `code_grade.grade_source` on the
working tree against `b788e9da` and `15a240bc`):

| Function | Grade now | Grade at base |
|---|---|---|
| `ensure_labels` | 4 | 5 (4 at HEAD) |
| `mirror_labels` | 5 | new |
| `_label_abandoned` | 5 | new |
| `cmd_abandon` | 4 | 4 |
| `cmd_abandon._close_and_reseat` | 5 | 4 |
| `_RejectWrites.label` | 5 | 5 |
| `_open_ensure_labels` | 5 | 5 |
| `_finish_replacement` | 4 | 4 |

- New test functions grade 4 or 5, and `label_create_fails` grades 5.
- The test file's `main()` is legacy: grade 1 at base, HEAD and now. Its only change is two call
  lines, so the grade is informational.

## G1: #13 failing-first evidence

H1's abandon regression, `abandon_label_create_failure_case`, is the #13 failing-first evidence.
#13's subject is abandon's continue policy: a failed write must not stop later item writes or the
local abandoned station. At `15a240bc` that policy is broken by a label-create failure. The run
SKIP-exits 0 before any close, reseat, milestone close or station write. The red is real, not a
preservation check:
- `01-red-label-create-head.txt`, and `05-red-final-tests-at-15a240bc.txt` with the final test
  text, show 4 FAIL lines. They are "every item still closes and reseats, the milestone closes"
  (log: `auth status`, `label create abandoned` only) and "the abandoned station is still recorded
  locally" (`building`), plus the SKIP and gap-report checks.
- It is green after H1 (`06-verify-T-02.txt` lines 688–691).
- The earlier `t02-red-green/05-red-abandon-old-override.txt` stays what it was, a preservation
  receipt for the close-failure case. It is not relabelled.

## F1: github-mirror.md (after H1)

- **Checked label create row:** the exists answer passes. Any other failure goes to the caller's
  policy:
  - `open` and `recover-terminal`: SKIP, exit 0.
  - `abandon`: one stderr line per closed ticket, continues, exit 0. Closes, reseats, the
    milestone close and the local `abandoned` station still land; only the label is missing.
  - `reject`: halt report, exit 1. Close and comment have already landed; backlog, milestone and
    the `rejected` station do not run, and the report lists what did and did not land.
- **Milestone row:** the cut-history sentence is removed. The row now says only: on any failure,
  look the milestone up by title; no match is the SKIP, exit 0.
- **Wayfind row:** `resolve --apply` comments on and closes the ticket before the mandatory map
  gist. A failing gist (map read, missing `## Decisions so far`, map edit) exits 1 after both have
  landed, so exit 1 is not "no mutation". Recovery is to fix the map and add the gist line by hand,
  because re-running `resolve` would post the comment again. This matches `wayfind.py`
  `cmd resolve`: `do([comment, close])` and then `append_gist`.

## Literal verifies

| Task | File | Result |
|---|---|---|
| T-02 | `06-verify-T-02.txt` | exit 0. 12/12 PASS (pool, 4 workers). |
| T-05 | `07-verify-T-05.txt` | exit 0. `PASS policy vocabulary, exit-2 correction, enforcement-ticket readback, live capability receipt and retired-override absence`. |

Extra runs:
- `03-green-unit-abandon-sources.txt`: the unit seam test, exit 0.
- `08-doc-reader-station-spelling.txt`: `test-station-argument-spelling.py`, which reads
  github-mirror.md, exit 0.
