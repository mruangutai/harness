# Grilling — #845 one vocabulary from harness.json — 2026-08-25

## Destination
Station names live in `harness.json` alone. `plan.yaml` is the state machine that projects
onto the GitHub board. No file holds a second vocabulary, and no code derives one
vocabulary from another.

## Settled
- **The six stations are MANDATED**: Backlog, Plan, Ready, Building, Review, Done. An
  operator may not rename a column. Extra columns an operator adds still survive untouched
  — that is a different thing and is not affected.
- **The key/value map dies.** Under the mandate the key and the name are THE SAME WORD, so
  there is one list, not two. `harness.json` holds it; `factory_config.py:41`'s
  `_STATION_KEYS` is deleted and replaced by a read. The exact column name is derived when
  the GitHub write needs it — verified: `.capitalize()` reproduces all six declared names
  with no mismatches.
- **Everything the harness stores or compares is lowercase.** The board's exact spelling is
  used at ONE place only: the GitHub write.
- **`plan.yaml` projects onto the board.** One function reads `plan.yaml` and reconciles
  every card. The ten policy sites collapse to one. No other code writes a station.
- **Whatever writes `plan.yaml` must read `harness.json`.** Today nothing does, and three of
  the four writers are an LLM. This is the sync break.
- **`plan.yaml`'s per-task status adopts the station vocabulary**, lowercase.
  `pending`/`building`/`done` is retired.
- **`feature.json.status` is DELETED, not moved.** `plan.yaml` gains a feature-level station
  field written by `gh-sync.py`. The four gates that read it repoint.
- **The task-to-issue map moves into `plan.yaml`.** Today the key and the value live in
  different files.
- **The two `ship` defects fold into this work** rather than becoming a separate ticket.
- **`plan.yaml` gets ONE writer, and it is code.** No LLM opens the file. pm, the
  orchestrator and the main session all reach it through a command that takes VERBS
  (`add-tasks`, `set-task-station`, `set-feature-station`, `sign-approval`), never fields.
- **A station argument is validated against `harness.json` before anything is written.** A
  value outside the mandated six exits non-zero. An LLM can ask for a station and be
  refused; it cannot type a dead word into the file.
- **The approval signature also goes through the command**, gated on agent identity: a
  PreToolUse Bash gate refuses `sign-approval` when `agent_type` is present, so only the
  main session can invoke it. DEC-120 becomes mechanical rather than documentary.
- **The writer is `plan-merge.py`, EXTENDED and RENAMED** — not a second tool. It already
  owns the four things a station writer needs: the lock (`harness_merge.locked_update`), the
  text splice, the ownership check (exit 9) and the signature refusal (exit 8). A second
  tool would duplicate all four, which is how two writers start disagreeing.
- **Add-only stops being a property of the TOOL and becomes a property of the `apply` VERB.**
  `#628`'s fix is the lock and the splice, not add-only; a value change under the same lock
  does not reintroduce it. The docstring and tests must say which verb holds which promise.
- `Backlog` does not participate in the sync. `Abandoned` stops being a station name and
  becomes a terminal marker with no column.

## Not yet specified
NOTHING. The frontier is empty. Two items that stood open were resolved rather than
carried:

- Whether `pm` can author a full first draft through a proposal pipe. **Yes** —
  `plan-merge.py:138` writes a proposal whole when the base does not exist, and
  `test-plan-merge.py:501` asserts it. The only constraint is that the proposal carry no
  `approval` key, which pm never writes anyway. This was a fact, not a decision.
- Whether `harness.json` declares the six. **Yes**, and it becomes the only place. See
  Settled.

Two remaining items are pm's work at plan time, not user decisions:

- The renamed tool's name, and the feature-level station field's name in `plan.yaml`.
  Both are naming details inside files pm owns; the plan carries them to signature.
- Whether the rename lands in this feature or a follow-up is a scope call the operator
  makes by signing or striking that task.

## Out of scope
- The board column names themselves. They are correct.

## Facts I verified (so pm does not re-derive them)
- `harness.json` declares six station names under six fixed keys — read from
  `.harness/harness.json` `github.board.stations`, at ee66ae2.
- **The board write needs the EXACT name.** `factory_gh.py:951` matches the single-select
  option with `if o["name"] == option`. A lowercased value raises "project field option
  not found". This is the one place the exact spelling must survive.
- **The case hazard is already documented in this repo.** `check-plan-routes.py:337`:
  "Building (the board's own spelling, capital B) is the typo a person will actually make,
  and today it would read as not-done forever." A case slip does not error; it silently
  reads as unfinished.
- **Every board write already goes through ONE function**, `gh_board.set_station` — ten
  call sites across `gh-sync.py`, `board_lifecycle.py` and `board-station.py`. The scatter
  is in the POLICY (which station, which cards, what order), not the mechanism.
- The six KEYS are legitimately hardcoded today: `factory_config.py:131-141` requires
  `harness.json` declare exactly them, so a literal key cannot KeyError.
- The NAMES are separately hardcoded and tied to nothing: `gh-sync.py:104`
  `STATUS_VALUES` is a seven-value literal that equals the board today by coincidence.
- An accessor already exists and is half-ignored: `factory_config.py:325`
  `station_for(fleet, repo, key)`. The factory uses it; `gh-sync.py` uses raw subscripts.
- **NO CODE WRITES A TASK STATUS.** `gh-sync.py:815`'s docstring claims `cmd_start_task`
  "records the task's status as building in plan.yaml (D-04)". Its 54-line body contains
  zero `plan.yaml` writes. The orchestrator writes it by hand
  (`harness-orchestrator.md:77`), which that file records as having lost five task
  statuses once already.
- **NO CODE CREATES `feature.json`.** `harness/SKILL.md:22` tells the orchestrator to copy
  the template; `gh-sync.py:692` refuses when absent and prints that instruction back.
- `feature.json.status` has four code readers: `check-plan-routes.py:418`,
  `check-state.sh:1425`/`:1500`, `board_lifecycle.py:503`, `gh-sync.py:243`.
- **The `ship` Done write is NEVER COMMITTED.** `main` at HEAD reads `Review` for FEAT-40,
  the main working tree reads `Review`, the worktree copy reads `Done`. A grep of the flow
  for `git add` / `git commit` after `ship` returns zero hits.
- `post-merge-sweep.sh` is NOT the cause. Line 163 resolves the feature dir to the main
  checkout on purpose, citing FEAT-35's `Review / pr:null` divergence. FEAT-40 broke
  because `ship` was hand-run with the worktree's path.
- Nothing enforces `plan.yaml`'s approval reset. `check-state.sh:134-139` only reads
  `approval.status` and warns on `pending`; no hash of the signed bytes is recorded.
- `check-domain.sh` cannot see a script write to `plan.yaml`. Its grant fires on
  `PreToolUse Write|Edit`, which `gh-sync.py`'s `open()` never traverses, and `plan.yaml`
  is excluded from the `PostToolUse Bash` sweep (`check-domain.sh:1011`). This is what
  makes "code writes it, the LLM is denied" mechanically possible.
- The denial mechanism already exists: `check-domain.sh:508` `approval_guard` denies a
  governed agent's `Edit` of a fragment the main session owns, firing on the ALLOW path
  because pm is granted `plan.yaml` whole.

- **A hook CAN tell the main session from a subagent.** `check-domain.sh:135` reads
  `agent = (d.get("agent_type") or "") or argv_agent`, and line 512 records that an absent
  `agent_type` IS the main session. This is what makes an identity-gated `sign-approval`
  possible with no new machinery.
- **`plan-merge.py` is the ONLY code that writes `plan.yaml` today.** Verified by scanning
  every non-test module in `bin/` for a write against a `plan.yaml` path. It splices text
  under `harness_merge.locked_update`, never re-renders through a YAML dumper, exits 7 on a
  changed value and 8 on a proposal whose approval mapping differs from the base's.
- **Denying `Edit` is not sufficient on its own.** `check-domain.sh:18` states it cannot see
  writes made via Bash and names `sed -i` as a common bypass shape. A `PostToolUse` sweep
  reads what landed on disk, but `plan.yaml` is deliberately excluded from it
  (`check-domain.sh:1011`). `plan.yaml` must join that sweep or the bypass just moves.

## What the mandate breaks, stated plainly
- `test-check-state.py:1660-1680` declares a fully renamed board
  (`Icebox`/`Drafted`/`Primed`/`WIP`/`Review`/`Shipped`) to catch a build that hardcodes the
  DEC-192 spellings. It is DELETED, not retargeted. Once the six names are mandated,
  `harness.json` can only ever hold those six strings and every read lowercases them, so
  there is no declaration variability left for a test to exercise.
- `test-board-lifecycle.py:771-798` is NOT affected. It guards an operator's EXTRA column
  (`Icebox` alongside the six) against deletion. Extra columns still survive.

## Migration size, measured
- **The `plan-merge.py` rename touches 11 live files**, measured by grep excluding worktrees
  and the historical FEAT-32 receipts (which record what was true and are not callers):
  `test-plan-merge.py` (13 refs), `check-domain.sh` (3), `test-observations-merge.py` (2),
  `harness-orchestrator.md` (2), and one each in `DECISIONS.md`, `harness.json`,
  `test-check-domain.py`, `run-unit-tests.sh`, `harness_yaml.py`, `expertise-merge.py` and
  `harness-spec-driven/SKILL.md`.
- 37 `feature.json` on disk carry a `status` key; the schema lists it in `required` with
  `additionalProperties: false`.
- 8 test files assert on a capitalised `feature.json` status value.
