# Code review — FEAT-40 — review_sha 3a548fe8c3eb1905d5b1cb9936266a30bc9b7489

## Verdict: FAIL — critical (must_fix non-empty)

Diffed `cc84b29..3a548fe` (68 files). No `[harness:human]` commits sit in this range — the seven
found on `git log --all` predate FEAT-40 and belong to #202. Reviewed the pinned SHA via
`git show 3a548fe:<path>` for every file cited below; `git diff 3a548fe --stat` over the whole
scoped file set returned clean at time of writing (a transient in-worktree mutation to
`cmd_ship`'s `write_done` — QA's own mutation-proof, see `notes/qa-2026-08-25.md` §2 — was present
and reverted during this review; confirmed clean before relying on any read).

## Stage 1 — spec compliance

Every change in scope traces to a `REQ`/`D`. No scope creep found. One omission-class gap, doc-only:

- **SC-05 wording vs. delivered code (low, doc-accuracy, not gating).** SC-05 says `parent_origin`
  "appears in no file under `.claude/skills/harness/bin/`." At 3a548fe it still appears in
  `factory_decompose.py` and its two tests (explicitly exempted by **D-09** — a different ledger,
  reasonable) **and** in `test-gh-sync.py`'s own fixture, which T-05's own test list requires
  ("load_recorded over a github block that still contains parent_origin does not crash"). T-05's
  actual `verify:` block is scoped to `gh-sync.py`/`feature-schema.json`/`feature.json` only — narrower
  than SC-05's sentence — so the code is correct and the decision (D-09) is sound; the BRIEF's SC-05
  text is what's stale. Same class as QA's already-filed SC-16 finding (signed wording drifting from
  what the plan actually decided). Not raised as new risk, just recorded so it isn't rediscovered.

- **SC-07 is false as literally written (folded into the Stage 2 finding below, not double-counted).**
  "A Bash call containing `gh issue close` is denied" is false for two commands that contain that
  exact substring: `eval "gh issue close 728"` and `bash -c 'gh issue close 728'`. See below.

## Stage 2 — code quality

### Finding 1 (critical, must_fix) — `gh-close-gate.sh` has real, reachable false-ALLOWs

Independently reproduced against the pinned-SHA script (JSON hook payload piped into
`bash .claude/skills/harness/bin/gh-close-gate.sh`, `github.sync: true`), not reasoned about:

| command | result | why the regex misses it |
|---|---|---|
| `gh "issue" close 728` | ALLOW | quote sits between `gh` and `issue`; anchor set has no quote char |
| `gh 'issue' close 728` | ALLOW | same |
| `/opt/homebrew/bin/gh issue close 728` | ALLOW | `gh` preceded by `/`, not an anchor char |
| `eval "gh issue close 728"` | ALLOW | `gh` preceded by `"` |
| `bash -c 'gh issue close 728'` | ALLOW | `gh` preceded by `'` |
| `x=$(gh issue close 728)` | ALLOW | `gh` preceded by `(` |
| `gh api repos/o/r/issues/9 -f state="closed"` | ALLOW | quote breaks the literal `state=closed` |

All seven really execute the close (shell strips the quoting/substitution before `gh` sees its argv;
verified equivalence by inspection of what bash actually passes). `eval "gh issue close 728"` and
`bash -c 'gh issue close 728'` are especially damning: **both contain the literal, contiguous
substring `gh issue close`**, which is exactly what SC-07 and the gate's own header comment ("where
the two cannot be distinguished... IT DENIES") claim is sufficient to deny. It isn't.

This corroborates `notes/review-harness-security-reviewer-2026-08-25.md` (verdict FAIL, critical),
which found the same root cause plus additional live bypasses I did not re-derive (a JSON PATCH
body, the GraphQL `closeIssue` mutation, `$(echo gh)` indirection). Two independently-run
measurements landing on the same regex-vs-tokenization root cause — this is not a maybe.

`test-gh-close-gate.py` (884/0 green) never exercises any of these forms, so the suite gives no
signal here; passing green is consistent with the gap, not evidence against it.

**Why this ranks above everything else in this review**: the operator's own framing puts an
unrecoverable false-ALLOW at the gate second only to a false Done, and this is a false ALLOW an
ordinary agent reaches with `bash -c` or `eval` — not an adversarial edge case.

**Route**: `gh-close-gate.sh` and its test are enforcement layer under DEC-174. Reporting only, per
this review's execution-route bound — no fix, no dispatched-fix recommendation.

### Finding 2 (high) — `cmd_abandon`'s `--yes` path aborts the whole batch on the first `gh()` failure, unlike every other multi-card writer this feature touches

Walked each step's failure per the operator's ask:

- **Detach fails** (`_detach_from_parent`): best-effort, prints one line, close proceeds anyway —
  matches the file's own documented posture ("attached-but-closed is worse than detached, better
  than not closing"). Fine.
- **Backlog write fails** (`_to_backlog`): catches `gh_board.BoardError`, prints one line, continues.
  Fine.
- **A close fails mid-list** (`cmd_abandon`'s issue/milestone/parent branches, `gh-sync.py:1103,
  1110, 1114`): these call `gh()`, **not** `gh_try()`. `gh()` turns *any* non-zero `gh` exit into
  `skip()` — one `gh-sync: SKIP — ...` line and an immediate `sys.exit(0)` for the **whole
  process**. Concretely: if the PATCH for sub-issue #3 of 5 hits a transient failure (rate limit,
  token expiry, network blip — the same class of event `gh-sync.py`'s own docstring spends several
  paragraphs on), the run stops there. #4 and #5 stay open and still attached to the parent, the
  milestone is never closed, the parent is never closed, and `_record_status(feat_dir,
  "Abandoned")` — the last statement of the successful path — never runs. `feature.json`'s status
  silently stays whatever it was before the operator typed `--yes`.

This is the exact defect shape the rest of this diff was built to eliminate for `ship`
(`gh_board.BoardError` caught, per-card, loop continues, `HELD`/`FAILED` literals name exactly
which cards). `cmd_abandon` inherits `gh()`'s all-or-nothing behaviour byte-identical from
`cc84b29` (verified: `git show cc84b29:.../gh-sync.py`'s `cmd_abandon` uses the same `gh()` calls
for every close), so this is not new code. **What is new is the exposure**: under D-12/DEC-203 item
8, `abandon` is now the **only** sanctioned close path in the mirror, and the Bash gate's refusal
text actively routes every blocked operator toward `gh-sync.py abandon ... --yes`. Before this
feature, a single-ticket drop could go through `close-task` (unaffected by a multi-item batch
failure); now every drop, however small, funnels through the one command whose write loop is not
best-effort.

The `--yes` line the operator confirms is a *promise* ("re-run with --yes to close the issues
listed above"); a mid-list failure breaks that promise silently past the one generic SKIP line, with
no per-card accounting of what did or didn't land — unlike `ship`'s `HELD`/`FAILED` summary two
commits earlier in this same diff.

No test in `test-gh-sync.py` exercises a mid-list `gh()` failure for `abandon` (checked: its abandon
blocks only assert the happy path and caller-error paths on `--reason-file`). Neither
`notes/review-harness-security-reviewer-2026-08-25.md` nor `notes/qa-2026-08-25.md` names this —
their `abandon` coverage focuses on the renderer/`--yes`-parsing contract and the origin-removal
privilege question, not the write loop's failure posture.

### Everything scrutiny items 1, 3 (structure), and 4 asked for — confirmed clean

- **False-Done, exhaustively traced.** `write_done` (`gh-sync.py:1214`) is the single call site that
  ever writes the `done` station anywhere in this file (`grep -n 'stations\]\["done"\]\|set_station'`
  shows exactly one such call, at `:1223`, inside `write_done`); the in-place map refresh
  (`stations[int(num)] = done`) lives inside that one helper, so both step 4 and step 5 go through
  it — confirmed by reading, and independently by QA's mutation proof (disabling the refresh turns
  `ship ORDERING`/`ship REFRESH` red).
- A `sub_issues` read failure raises inside `first_open_child`, caught by the `except Exception` in
  the step-5 loop, which prints one stderr line and `continue`s **without** calling `write_done` —
  unknown is never treated as childless.
- `gh_board.read_station`'s two failure reasons (`"not on the board"`, `"no station set"`) are both
  read in `first_open_child` and both fail the `station == done` test, so both count as OPEN, and the
  parenthetical correctly distinguishes them per D-03/DESIGN Contract 2.
- Children-before-parents (D-04) and the refresh-scope requirement (a `source_issues` entry that is
  itself the parent's child, landed earlier in the same `sources + parents` loop) are both
  structurally satisfied by the single-map, single-helper design — not by luck.
- **D-10's premise re-verified at this SHA**, not inherited from the plan's own assertion: `grep -n
  'rec\["issues"\]'` shows the only writer is `cmd_open` (`:796`, sourced from
  `attach_sub_issue_args(repo, rec["parent"], child_id)` — always the parent, never another task
  issue), and `load_recorded` only mirrors what `cmd_open` already wrote. The exemption is sound at
  this SHA.
- `HELD`/`FAILED` literal shapes match DESIGN.md Contract 2 character-for-character; `FAILED` only
  fires on a real write failure and never covers a held card; no new line contains `gh-sync: SKIP`.
- `cmd_ship` issues no `gh issue close` and no `state=closed` PATCH on an issue anywhere (`grep`
  confirms every `state=closed` PATCH in `_ship_close_milestone`/`cmd_ship` targets
  `repos/{repo}/milestones/...`, never `.../issues/...`).
- `_ship_audit` runs exactly once, after step 7's summary, never gates (catches the audit's own
  exception, prints one line, continues), and no audit line can carry the `SKIP`/`FAILED` substrings
  under normal station naming.
- `board_lifecycle.py`'s `audit_findings`/`cmd_audit` split matches the plan's byte-identical-output
  requirement: confirmed by diffing `cc84b29`'s inline `_out()` call sites against 3a548fe's
  `notes`-list construction — the original code already printed the workflow header and the STATUS
  skip line *before* any finding (since findings were only printed by the caller after the function
  returned), so collecting them into a `notes` list printed first by `cmd_audit` reproduces that
  order exactly, not a regression.
- **`INV-31`** (`check-state.sh:1700-1758`): both findings append to `bad`; both subjects differ
  (config value vs. file); the CANNOT-RUN path is a violation, not a pass; realpath comparison
  correctly passes an absolute `core.hooksPath` naming the same directory. `test-check-state.py`
  exercises all six named states including the absolute-path-passes case.
- **`post-merge-sweep.sh`**: `gh-sync: FAILED` added as a second, independent condition beside
  `SKIP` in the positive-signal gate; `HELD` deliberately excluded; removal declined without
  changing the sweep's own exit code. Matches D-11/T-04 step 7b exactly.

### Not raised as new (already covered elsewhere)

`abandon`'s unconditional-parent-close privilege question, the STATUS/REASON/LABEL audit classes,
and `gh_issues.py`'s argv-only discipline are already assessed cleanly in
`notes/review-harness-security-reviewer-2026-08-25.md` and not re-litigated here.

## What would flip this to PASS

Finding 1 alone gates (`critical`), independent of Finding 2. Finding 1 cannot be fixed through this
review's own execution route (DEC-174 — enforcement layer). Recommendation, stated for the record
and not as an instruction to any dispatched agent: tokenize the command the way the shell would
(e.g. `shlex.split`-style normalization before the boundary test) rather than matching a fixed
character-class boundary, so `gh issue close` is recognized as adjacent words regardless of quoting
or indirection — the same fix direction the security review already named.
