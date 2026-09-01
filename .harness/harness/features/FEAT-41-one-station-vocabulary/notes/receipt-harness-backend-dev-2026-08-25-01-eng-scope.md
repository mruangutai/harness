# receipt — harness-backend-dev — FEAT-41 — targeted follow-up (2026-08-25-01)

## BLUF

All seven numbered items in issue #845's "What this feature does" have covering task(s) in
`plan.yaml`. No ABSENT scope item. The lead's premise — "the task-to-issue map moves into
plan.yaml" — is code-true (verified below) but is **not one of the seven numbered items**; it
appears only in the grilling notes (lines 27-28), which is broader than the ticket. That is not
a defect: the grilling is scoped, `plan.yaml` need not exhaustively adopt every grilling bullet.

## Seven-row table (issue #845 vs plan.yaml)

| # | Item text (verbatim, one line) | Covering task(s) | Verdict |
|---|---|---|---|
| 1 | "Mandate the six station names. `Backlog`, `Plan`, `Ready`, `Building`, `Review`, `Done`. Operators may not rename them. Extra columns they add still survive untouched." | T-01 (declares `MANDATED_STATIONS`, mandate wording in `_board_note`); T-11 (deletes the renamed-board test the mandate makes unreachable) | COVERED |
| 2 | "One list, in `harness.json`. The key and the name are the same word, so `factory_config.py:41`'s `_STATION_KEYS` is deleted and replaced by a read. The exact column name is derived at the GitHub write — `.capitalize()` reproduces all six." | T-01 (deletes `_STATION_KEYS`, adds `station_column`) | COVERED |
| 3 | "`plan.yaml` adopts that vocabulary, lowercase. `pending`/`building`/`done` retires." | T-04 (`LEGAL_TASK_STATUSES` deleted, migration of all live plans) | COVERED |
| 4 | "`plan.yaml` projects onto the board. One function reconciles every card. The ten policy sites collapse to one." | T-06 (`gh_board.project()`, collapses `gh-sync.py`'s per-site station decisions) | COVERED |
| 5 | "`plan.yaml` gets ONE writer, and it is code. `plan-merge.py` is extended and renamed, gaining verbs that validate a station before touching the file. Every LLM `Edit` of `plan.yaml` is denied; `plan.yaml` joins the post-Bash sweep so `sed -i` cannot route around it. The approval signature goes through the same tool, gated on `agent_type`." | T-03 (verbs), T-05 (playbook doc, closes write-window ordering), T-08 (identity-gated sign-approval hook), T-09 (deny Edit/Write, post-Bash sweep), T-13 (rename to `plan-write.py`) | COVERED |
| 6 | "`feature.json.status` is deleted. Its four readers repoint to `plan.yaml`." | T-07 (deletes `status` from schema, migrates data, repoints readers) | COVERED — count of readers (T-07's title says eleven vs item's "four") is out of scope per dispatch ("skip any measured count") |
| 7 | "The two `ship` defects are fixed here. The `Done` write is never committed... and `ship` accepts a feature dir inside a worktree that is about to be deleted." | T-10 (both defects, plus FEAT-40 repair) | COVERED |

## The specific lead — settled

Grilling notes lines 27-28: `"The task-to-issue map moves into `plan.yaml`. Today the key and
the value live in different files."` — marked SETTLED.

**Verified against code (T-06, T-07 as landed in this worktree):**
- T-06's `project(plan_doc, rec, board)` (`plan.yaml:386-398`) *consumes* `rec["issues"]`; it
  does not relocate it. `rec` still comes from `gh-sync.load_recorded`.
- `gh-sync.py:458` initializes `rec = {..., "issues": {}, ...}`, populated from `feature.json`'s
  `gh.issues` (`gh-sync.py:515-520`) and written back the same way (`gh-sync.py:701`,
  `:782-804`). No `plan.yaml` write of an issues map exists anywhere in this worktree's
  `gh-sync.py` or `plan-merge.py`.
- T-07 (`plan.yaml:422-489`) deletes only the top-level `status` key from `feature.json`'s
  schema and readers; it does not touch `gh.issues`.

So the lead's code observation is accurate: no task moves the task-to-issue map into
`plan.yaml`, and the map still lives in `feature.json` after all thirteen tasks.

**But checked against the issue itself** (`gh issue view 845`, body's "## What this feature
does"): the task-to-issue map is **not named in any of the seven numbered items**. Re-reading
each of the seven verbatim (table above) — none mentions `rec["issues"]`, sub-issue numbers, or
"the same file" for the map. Item 4 is about station *projection direction* (plan.yaml → board),
not about where the id→issue-number map is stored. Item 6 is about `feature.json.status`
specifically, not the issues map.

**Verdict: NOT one of the seven.** It is a grilling-only bullet — the grilling is broader than
the ticket, which is expected and not a defect. No blocking finding follows from this lead.

## What I did not review

Per dispatch: the six mandated names, lowercase-everywhere, DEC-174 lane assignment, the
`plan-write.py` rename, the `status:` field choice, and any measured count (11-file rename list,
37 feature.json, 8 test files, BRIEF.md's "thirteen of fourteen tasks") — all out of scope, not
re-litigated here.

## Cost / alternative

None — no ABSENT item, no blocking finding. If a future ticket *does* want the issues map moved
into `plan.yaml` (matching the grilling's fuller ambition), that is a new numbered item / new
task, not a gap in FEAT-41 as scoped by #845.
