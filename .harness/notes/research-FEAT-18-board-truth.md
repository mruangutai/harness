# Research — FEAT-18 board truth during a build (#277)

**BLUF.** The design is fully determined by the grilling's eleven settled items plus five
measurements taken here at `2ccd7f0`. Nothing was left to invent; one item (who fires the
start-of-task move) is derivable and is recorded as D-04, not raised as a question. The grilling's
`## Facts I verified` at `a7c429c` were NOT re-derived except where a task's `verify:` rests on them.

## What I measured at 2ccd7f0 (not in the grilling)

1. **Board 3's Status field is identity-mapped to DEC-192.** `gh api graphql` on
   `user(login:"mruangutai").projectV2(number:3).field(name:"Status")` returns exactly six options,
   in order: `Backlog`, `Plan`, `Ready`, `Building`, `Review`, `Done` — byte-equal to DEC-192's six
   values. Board id `PVT_kwHOAAases4BfZ9Z`, field id `PVTSSF_lAHOAAases4BfZ9ZzhZtFWg`. **So no
   station-name mapping is needed for the harness board** — unlike `fleet.yaml`, which carries a
   `stations:` mapping because a product board may name its columns anything.
2. **The GraphQL machinery already exists and is tested.** `factory_gh.py` holds
   `_project_field_resolve(owner, number, field)` (one call, resolves board id + field id + every
   option id BY NAME), `issue_board_item_id(repo, number, board_number)` (targeted lookup, cost 1)
   and `project_field_set(owner, number, item_id, field, option)`. A third copy of this query is
   what D-06 exists to prevent.
3. **`mruangutai/harness` is deliberately absent from `fleet.yaml`** (DEC-174 am.1, stated in the
   file's own header). So the harness board cannot be declared there — hence D-05's
   `harness.json github.board`.
4. **`gh-sync.py`'s `gh()` calls `skip()`, and `skip()` calls `sys.exit(0)`** (`gh-sync.py:56-59`,
   `:91-96`). A station write routed through `gh()` cannot "continue" — it terminates the process.
   This is the single mechanical fact D-02 turns on.
5. **`parse_tasks()` does not read a task's `status`** (`gh-sync.py:152-198`) — it returns id, title,
   body, change_type, traces, absorbs. The station writer needs status added.
6. **`branch-create-gate.sh` cannot see `gh issue develop`.** Its four extraction regexes match
   `git checkout -b`, `git switch -c|--create`, `git worktree add -b` and `git branch <name>`. A
   `gh issue develop` + `git fetch` + `git checkout <existing-branch>` flow matches none of them and
   passes silently. Recorded as D-08 rather than fixed.
7. **`check-state.sh` shells out to `git` (INV-25) but never to `gh`.** INV-26 is the first `gh` call
   at session entry. INV-25's two precedents transfer: tool-absent records nothing (`:966-970`),
   module-unimportable is a VIOLATION naming the file to restore (`:981`).
8. **`check-domain.sh --resolve` at `2ccd7f0`** — full results are in `plan.yaml`'s `lanes:`.
   `.claude/skills/harness/SKILL.md` and `.claude/skills/harness/templates/harness.json` both
   resolve to **NOBODY**, so both edits are declared main-session-direct steps (DEC-179), not
   mid-run rejected writes.
9. **All four test files this feature touches are already registered** in `run-unit-tests.sh`
   (`test-gh-sync.py`, `test-check-state.py`, `test-check-plan-routes.py` in `INTEGRATION_SCRIPTS`).
   A NEW `test-gh-board.py` is not, and G-08 says an unregistered file fails the WHOLE run — T-02
   registers it in the same task.
10. **`harness_yaml.load_plan` does not validate task `status`** — `REQUIRED_TASK_FIELDS` is
    `(id, title, change_type, execution_mode, files, verify, intent)` (`harness_yaml.py:282`). The
    `pending | building | done` enum therefore lands in `check-plan-routes.py`, exactly as settled.

## The one thing a build would otherwise stall on

`gh-sync.py`'s failure posture is a **three-way** split, not the two DEC-138 and DEC-186 each
describe. D-02 states it precisely. The trap: a builder reading DEC-186's "the factory control-plane
tools exit non-zero instead" will make `gh-sync.py` exit non-zero and break the flow; a builder
reading DEC-138's "never a gate" will route the station write through `gh()` and get a silent
`SKIP` that exits the process mid-sequence. Both are wrong. See D-02.

## Open, non-blocking

- `github.board` is a harness.json key addition. DEC-160 requires a decision to say so; D-05 does,
  and the template gains `board: null` so `upgrade-config.py`'s additive merge propagates it. The
  operator sees it at signature (open_question Q1).
- Every automated criterion in this feature runs against a FAKE `gh` binary (`GH_SYNC_GH`, and the
  same pattern introduced for `check-state.sh`). Nothing proves the live API contract. Stated in
  BRIEF `## Verification gaps`.
