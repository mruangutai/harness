# PLAN — FEAT-09 Plan-time route check

## Lanes — resolved here, not at build time

Resolved against `.harness/team-config.yaml` at `ae2443d`, by reading the lines, not recalling them.

| Surface | Lane | Grant |
|---|---|---|
| `.claude/skills/harness/bin/**` — the new checker, its test, `run-unit-tests.sh` | `harness-backend-dev` / `harness-dev-ops` | `team-config.yaml:155`, `:197` |
| `.claude/skills/harness/bin/check-domain.sh` | **main session, DEC-174 carve-out** | deviation from the row above — D-03 |
| `.claude/skills/harness/templates/PLAN.md` | **main session** (declared step) | ungranted — nothing in `team-config.yaml` names `templates/**` |
| `.claude/skills/harness-spec-driven/SKILL.md` | **main session** (declared step) | ungranted — nothing names `.claude/skills/harness-*/SKILL.md` |

`check-domain.sh` sits under `bin/**`, which IS granted, so T-01 is the one deviation from this
table and D-03 records why. Ordering constraint for the two ungranted rows: T-03 must land before
T-02, because T-02's test asserts the template's shape; T-04 lands last, because its rule names the
script T-02 creates.

`.claude/agents/harness-pm.md` is deliberately NOT in this table — D-06.

## Concurrency — one shared surface with FEAT-08

Every path in the table above is this feature's alone, with ONE exception:
`.claude/skills/harness/bin/run-unit-tests.sh` is a **shared surface with the in-flight FEAT-08**,
and both features edit the same line. T-02 here APPENDS `"test-check-plan-routes.py"` to the
`SCRIPTS` array at `:6`; `FEAT-08/PLAN.md:243,250-252` REMOVES `"test-cost-report.py"` from that
same array at that same line, asserting the other twelve entries are left unchanged.

Whichever lands second, if it writes a remembered array rather than re-reading `:6`, drops the
other's edit. The result is not a quiet merge artefact: either the drift detector (`:9-22`) finds an
unlisted `test-*.py` and exits 2, or the runner invokes a listed-but-deleted script and FAILs.
Because `run-unit-tests.sh` is the FEAT-07 whole-suite rider in nearly every `verify:` of BOTH
plans, **every remaining task in both features then reddens for an unrelated reason** — the red-suite
window FEAT-07 D-02 exists to prevent.

This is disclosed, not resolved. Sequencing is an orchestrator/user call, not the planner's. The
options are: (a) order the two `SCRIPTS` edits explicitly across features; (b) reassign the edit so
one feature owns `:6` and the other declares a dependency on it; (c) accept and rebase, with
whichever lands second re-reading `:6` before writing. Raised as a blocking open question.
No FEAT-08 path appears in any `files:` here.

## Decisions

- D-01: **The plan-time checker is a NEW script, `.claude/skills/harness/bin/check-plan-routes.py`,
  invoked by pm at PLAN write — not a mode of `check-domain.sh` and not an invariant inside
  `check-state.sh`.** — rationale: fog patch 1 was "new script, mode, or invariant", and the answer
  follows from when it must fire. It must fire while the plan is still being written, when the
  author can still move a task's lane; an entry-time sweep reports it after the plan is finished.
  `check-domain.sh` is a `PreToolUse` hook whose contract is a JSON payload on stdin and `exit 2`;
  making it also a plan-phase CLI multiplies its invocation contracts on the one file DEC-174
  carves out. `--resolve` is the *matcher access point*, not the checker. tradeoffs: a fourteenth
  script in `bin/`, and a check that runs when pm remembers rather than at every `/harness` entry —
  see the open question about promoting it to a `check-state.sh` invariant once FEAT-08 releases
  that file.
- D-02: **`--resolve <path>` prints newline-separated, sorted agent names, or the literal token
  `NOBODY`, and exits 0 on any successful resolution; exit 2 is reserved for an unreadable,
  unparseable or duplicate-keyed manifest.** — rationale: `.claude/skills/harness/bin/**` is granted
  to TWO agents (`:155` and `:197`), so "which agent may write this" has a set-valued answer on the
  happy path of this very plan; a single-winner precedence rule would have to invent an ordering the
  manifest does not express. `NOBODY` is a token rather than empty output because the measured
  failure mode of this script is a silent exit 0 (see T-01), and a caller cannot distinguish "no
  agent" from "did not run" if both are empty. tradeoffs: the caller must parse multiple lines, and
  answer-versus-health is split across stdout and the exit code rather than encoded in the exit code
  alone.
- D-03: **T-01 edits `check-domain.sh` and `test-check-domain.py` as one main-session-direct task,
  deviating from this plan's own lanes table, which grants `bin/**` to `harness-backend-dev` (`:155`)
  and `harness-dev-ops` (`:197`).** — rationale: DEC-174 — the harness plans its own work but does
  not dispatch changes to its own enforcement layer through a team run whose gates are the thing
  being changed; `check-domain.sh` is a registered `PreToolUse` hook and is named in DEC-174
  explicitly. Guard and test ship together for FEAT-07 D-02's reason: the diff only vouches for
  itself if it contains the test that proves it. tradeoffs: the main session does work a member is
  granted, and the deviation is recorded here because `templates/PLAN.md:9-11` requires a
  `## Decisions` entry for any departure from a `team-config.yaml` convention. **Consequence the
  checker must not swallow:** T-01's paths ARE granted, so a checker that only asks "does anyone
  grant this?" passes T-01 without ever reading its `main-session-direct` declaration — the single
  most important routing deviation in this plan would be invisible to the mechanism the plan
  builds. T-02 therefore emits a non-failing `DEVIATION` line for granted-but-declared-main-session
  tasks (SC-12), so the carve-out is disclosed by the machine and not only by this paragraph.
- D-04: **A `files:` entry containing a wildcard is reported as an explicit `UNRESOLVED-GLOB` line
  and does not affect the exit status. Resolving a glob that spans two domains is DEFERRED.** —
  rationale: fog patch 2. Nobody has hit it, so the shape of the right answer cannot be stated; but
  silence is not a legitimate deferral. The named failure mode: a task written as
  `files: docs/**` whose glob covers both a granted and an ungranted subtree is reported, not
  routed, and the planner resolves it by writing literal paths. tradeoffs: a planner can defeat the
  check by globbing — mitigated by the report line being loud rather than absent, and by the
  spec-driven rule already forbidding directories in `files:` ("exact paths, not directories",
  `templates/PLAN.md:44`).
- D-05: **The `## Lanes` table stays hand-written; generating it is deferred.** — rationale: fog
  patch 3. The checker validates task→route resolution, which is the falsifiable part; the table is
  a human-readable summary of surfaces and carries the *reason* for a lane, which is not derivable
  from `team-config.yaml`. tradeoffs: the table can drift from the tasks below it — the checker
  catches the consequence (an unroutable task) but not the drift itself.
- D-06: **The rule lives ONLY in `.claude/skills/harness-spec-driven/SKILL.md`;
  `.claude/agents/harness-pm.md` is not edited.** — rationale: DEC-126's shape — one canonical home
  for a rule delivered by `skills:` preload, and `harness-pm.md:8-12` already preloads
  `harness-spec-driven`. Restating the rule in the agent file creates two copies that drift, and
  DEC-11 already puts capability in frontmatter and policy elsewhere. tradeoffs: an agent whose
  preload fails sees no rule at all; the compensating control is that the check is mechanical, so a
  plan written without the rule still fails the checker.
- D-07: **`execution_mode:` has exactly two legal tokens — `team` and `main-session-direct`.** —
  rationale: the field was invented ad hoc twice and already has three spellings in the tree —
  `squad-dispatched` (`FEAT-06/PLAN.md:689`, `FEAT-07/PLAN.md:783`), `team`
  (`FEAT-08/PLAN.md:237`) and `main-session-direct` (all three). A checker cannot read a vocabulary
  with synonyms. `team` wins over `squad-dispatched` because `team` is the live noun on every
  surface (DEC-119). tradeoffs: prior plans use a token the checker will not recognise — they are
  history and are not re-written, so the checker must treat an unknown token as "not a declared
  main-session step", which is the safe direction.
- D-08: **`check-plan-routes.py` re-uses `check-state.sh`'s task-block regex
  (`^(?:-\s*|#+\s*)(T-\d+)\b...`, `check-state.sh:93-94`) by copying it, not by sharing it.** —
  rationale: `check-state.sh` is owned by the in-flight FEAT-08 and cannot be touched here, and
  PLAN.md is markdown, not YAML, so PyYAML does not apply. This is a duplicated *task-block* parser,
  never a duplicated *path matcher* — the constraint the feature exists to protect (D-02, SC-08) is
  untouched. tradeoffs: two places know how a task block is spelled; consolidation is raised as an
  open question rather than done silently.

## Approval

status: approved
approved-by: Mike Ruangutai
date: 2026-08-05
## Features

- FEAT-09: Plan-time route check
  traces: REQ-01, REQ-02, REQ-03, REQ-04, REQ-05, REQ-06
  tasks: T-01, T-02, T-03, T-04

## Tasks

- T-01: Add a `--resolve <path>` mode to `check-domain.sh` that short-circuits before stdin is read
  files: `.claude/skills/harness/bin/check-domain.sh`, `.claude/skills/harness/bin/test-check-domain.py`
  intent: In `check-domain.sh`, BEFORE line 26's `payload=$(cat)`, add a branch that fires when
    `$1` is exactly `--resolve`. On that branch the script must never read stdin — not with a
    timeout, not non-blockingly, not at all — because two failure modes were measured on the current
    tree: with stdin an open pipe the script blocks indefinitely (a plan-time check that looks slow,
    not broken), and with stdin closed or `/dev/null` it reaches the Python body with an empty
    payload, resolves no agent identity, and exits 0 printing nothing — a fail-open answer
    indistinguishable from "clean". The branch runs the same embedded Python with a mode flag,
    reaching the SAME `matches()`/`glob_to_re()` functions at `:215`/`:190`; no second matcher, and
    `matches()` is not modified. Behaviour: read `.harness/team-config.yaml` via `harness_yaml`,
    normalise the argument to a repo-relative path the way the hook does (`os.path.relpath` against
    the derived root, plus the `.claude/worktrees/<id>/` strip at `:187`), and for every agent in
    the manifest test its `domain` write globs with `matches()`. Print the granting agent names,
    sorted, one per line; print the literal token `NOBODY` when none match; print
    `SHARED <pattern>` as an additional line when the path matches a top-level `shared:` entry.
    Exit 0 on any successful resolution. Exit 2 only when the manifest is missing, unparseable or
    carries a duplicate key, re-using the existing `DuplicateKeyError` / `YamlParseError` messages.
    A `.` read-only entry is never a write grant (`matches()` already returns False for it). The
    hook path — no `--resolve` in argv — must be byte-for-byte unchanged in behaviour. In
    `test-check-domain.py` add EIGHT separately named cases, one per clause: (a) a singly-granted
    path returns exactly one name; (b) `.claude/skills/harness/bin/**` returns both
    `harness-backend-dev` and `harness-dev-ops`; (c) an ungranted path prints the literal `NOBODY`;
    (d) that same ungranted call exits 0, and its stdout is not empty; (e) `--resolve` with stdin an
    open pipe nobody writes to answers within 10s; (f) `--resolve` with stdin closed gives the
    byte-identical answer to (e); (g) with no `--resolve` in argv, an out-of-domain Write payload on
    stdin still exits 2; (h) with no `--resolve` in argv, an in-domain Write payload on stdin still
    exits 0.
  change_type: logic
  verify: `python3 -c "import subprocess,os;B='.claude/skills/harness/bin/check-domain.sh';q=lambda p:sorted(subprocess.run([B,'--resolve',p],stdin=os.pipe()[0],capture_output=True,text=True,timeout=10).stdout.split());assert q('.harness/harness.json')==['harness-dev-ops'];assert q('.claude/skills/harness/bin/run-unit-tests.sh')==['harness-backend-dev','harness-dev-ops'];assert q('.claude/skills/harness-spec-driven/SKILL.md')==['NOBODY'];print('OK')" && python3 .claude/skills/harness/bin/test-check-domain.py && .claude/skills/harness/bin/run-unit-tests.sh`
    — expected: `OK`, then every `PASS`, exit 0.
  traces: REQ-04, REQ-05, D-02, D-03
  execution_mode: main-session-direct — reason: DEC-174 carve-out. `check-domain.sh` is a registered
    `PreToolUse` gate script named in DEC-174; it is never dispatched through a team run whose gates
    are the thing being changed. This deviates from the lanes table's `bin/**` row — D-03.
  feature: FEAT-09
  status: pending

- T-02: Add `check-plan-routes.py`, its test, and register the test in the unit runner
  files: `.claude/skills/harness/bin/check-plan-routes.py`, `.claude/skills/harness/bin/test-check-plan-routes.py`, `.claude/skills/harness/bin/run-unit-tests.sh`
  intent: `check-plan-routes.py` takes one or more PLAN.md paths as argv (defaulting to
    `.harness/features/*/PLAN.md` when given none) and, for each, extracts task blocks with the
    regex `^(?:-\s*|#+\s*)(T-\d+)\b(.*?)(?=^(?:-\s*|#+\s*)T-\d+\b|\Z)` under `re.M|re.S` — copied
    from `check-state.sh:93-94` per D-08. From each block it reads the `files:` line, splitting on
    commas and stripping backticks and whitespace, and the `execution_mode:` line, taking the first
    whitespace-delimited token after the colon. For each literal path it shells out to
    `.claude/skills/harness/bin/check-domain.sh --resolve <path>` with `stdin=DEVNULL` and reads the
    lines; it MUST NOT implement any path matching itself — no `fnmatch`, no glob-to-regex, no
    `startswith` prefix comparison (D-02, SC-08). Verdicts per task: at least one granting agent →
    OK; `NOBODY` for any path AND `execution_mode:` token is `main-session-direct` → OK, printed as
    a declared main-session step; `NOBODY` for any path and the token is anything else, missing, or
    unrecognised → VIOLATION, printing a line naming the task id, the offending path and the legal
    tokens (D-07: `team` and `main-session-direct`). Separately, a task whose paths ALL resolve to a
    granting agent but which declares `main-session-direct` prints
    `DEVIATION <T-NN> <path> granted to <agents> but declared main-session-direct` and does NOT
    affect the exit status — that is the DEC-174 carve-out shape (T-01 here), and it must be
    surfaced rather than silently read as a normal team task. A path entry containing `*` or `?` is printed
    as `UNRESOLVED-GLOB <T-NN> <entry>` and does not affect the exit status (D-04). A missing
    `files:` line is a VIOLATION naming the task. Exit 0 when there are no violations, 1 when there
    are, 2 when a PLAN path does not exist or `check-domain.sh` itself exits 2. Output is one line
    per finding plus a final summary count; no finding may be reported by silence.
    `test-check-plan-routes.py` writes temporary PLAN fixtures under `tempfile.mkdtemp()` and
    asserts, as separate named cases: (1) an ungranted-and-undeclared task exits non-zero;
    (2) its output contains the task id; (3) its output contains the offending path; (4) a plan
    whose every task resolves to a granting agent exits 0; (5) a plan whose every ungranted task
    declares `main-session-direct` exits 0; (6) a wildcard entry produces an `UNRESOLVED-GLOB` line;
    (7) that same wildcard plan's exit status matches the same plan with the wildcard task removed;
    (8) `check-plan-routes.py`'s own source contains the string `check-domain.sh`; (9) that source
    contains no `fnmatch`; (10) `templates/PLAN.md` contains `## Lanes`;
    (11) it contains `execution_mode: team`; (12) it contains `execution_mode: main-session-direct`;
    (13) `run-unit-tests.sh`'s `SCRIPTS` array lists `test-check-plan-routes.py`; (14) a task with
    granted paths that declares `main-session-direct` produces a `DEVIATION` line; (15) that same
    plan still exits 0; (16) that source contains no `glob_to_re` — a separate named case from (9),
    because one case asserting two strings is one fixture for two clauses; (17) the BEHAVIOURAL
    guard for the third prohibition (SC-08 clause 4, no `startswith`/prefix comparison): a fixture
    task whose `files:` is
    `.harness/features/FEAT-09-plan-time-route-check/runs/1-eng/notes.md` — granted to
    `harness-eng-lead` ONLY through the mid-pattern wildcard `.harness/features/*/runs/*-eng/**`
    (`team-config.yaml:278`) — must be reported OK, with no VIOLATION line naming it. A hand-rolled
    prefix comparison on the text before `/**` answers False for that path and would report it
    ungranted, so this case fails on any reimplementation regardless of what its variables are
    named. It is the exact bug `check-domain.sh:190-197` records.
    Add `"test-check-plan-routes.py"` to the `SCRIPTS` array in `run-unit-tests.sh` in the same
    task — the runner's drift detector (`run-unit-tests.sh:9-21`) exits 2 on any `test-*.py` under
    `bin/` that is not listed, so omitting it fails the whole suite rather than skipping one file.
    **HARD CONSTRAINT — `run-unit-tests.sh` is shared with FEAT-08 (see `## Concurrency`).**
    `FEAT-08/PLAN.md:243` puts this same file in its T-03 `files:`, and `:250-252` removes
    `"test-cost-report.py"` from the SAME `SCRIPTS` array on the SAME line `:6`. The `SCRIPTS` edit
    here is therefore an **append that must preserve whatever entries are present at land time**:
    re-read `:6` in the working tree immediately before writing and add one element to what is
    actually there. Do NOT reproduce a remembered thirteen-entry array — that silently reverts
    FEAT-08's removal, after which either the drift detector (`:9-22`) exits 2 on an unlisted
    `test-*.py` or the runner invokes the deleted-but-listed `test-cost-report.py` and FAILs. Either
    way the whole suite goes red and every other task's `verify:` in BOTH features reddens for an
    unrelated reason. Change nothing else in `run-unit-tests.sh`.
  change_type: logic
  verify: `python3 .claude/skills/harness/bin/test-check-plan-routes.py && .claude/skills/harness/bin/run-unit-tests.sh && python3 .claude/skills/harness/bin/check-plan-routes.py .harness/features/FEAT-09-plan-time-route-check/PLAN.md`
    — expected: the new test's own output, then every `PASS` including
    `PASS test-check-plan-routes.py`, then for this plan **zero violations and exactly one
    `DEVIATION` line naming T-01**, exit 0.
  traces: REQ-02, REQ-03, REQ-04, D-01, D-03, D-04, D-07, D-08
  execution_mode: team — `harness-backend-dev` or `harness-dev-ops` (`team-config.yaml:155`, `:197`)
  depends_on: T-01, T-03
  feature: FEAT-09
  status: pending

- T-03: Give `templates/PLAN.md` a `## Lanes` section and a mandatory `execution_mode:` field
  files: `.claude/skills/harness/templates/PLAN.md`
  intent: Insert a `## Lanes` section immediately after the H1 and before `## Decisions`, with a
    one-line instruction and a three-column table skeleton — Surface | Lane | Grant — stating that
    the lane is resolved against `.harness/team-config.yaml` at a named SHA and that the Grant
    column cites the granting line number, or records that nothing grants the surface. Add
    `execution_mode:` to the mandatory-fields paragraph alongside `change_type:` and to the T-01
    example stanza, naming exactly two legal tokens (D-07): `execution_mode: team — <agent>
    (team-config.yaml:NN)` and `execution_mode: main-session-direct — reason: <why>`. State in the
    same paragraph that `check-plan-routes.py` reads these two fields and that a task resolving to
    no agent without `main-session-direct` fails it. Keep the file's existing HTML-comment
    instructional style and the `## Approval` block untouched — the template's ownership comment at
    `:1-3` stays first. The file is 50 lines today; the addition must stay under 80. The DURABLE
    evidence for this task's outcome is `test-check-plan-routes.py` cases 10-12 (T-02), which assert
    the same three strings the greps below check; the greps are the land-time gate, the cases are
    what the goal-check cites for SC-09.
  change_type: docs
  verify: `grep -q '^## Lanes' .claude/skills/harness/templates/PLAN.md && grep -q 'execution_mode: team' .claude/skills/harness/templates/PLAN.md && grep -q 'execution_mode: main-session-direct' .claude/skills/harness/templates/PLAN.md && grep -q 'check-plan-routes.py' .claude/skills/harness/templates/PLAN.md && [ "$(grep -c '' .claude/skills/harness/templates/PLAN.md)" -lt 80 ] && .claude/skills/harness/bin/run-unit-tests.sh && .claude/skills/harness/bin/check-docs.sh`
    — expected: exit 0; today the first grep alone exits 1.
  traces: REQ-01, REQ-06, D-05, D-07
  execution_mode: main-session-direct — reason: `.claude/skills/harness/templates/**` is granted to
    nobody in `team-config.yaml` — the FEAT-05 "third recurrence" note names this exact gap. Declared
    step, ordered before T-02 because T-02's test asserts this file's shape.
  feature: FEAT-09
  status: pending

- T-04: Add the plan-time route rule to `harness-spec-driven/SKILL.md`
  files: `.claude/skills/harness-spec-driven/SKILL.md`
  intent: Add a section titled `## Routing is resolved at plan time` after `## Every task needs four
    things`, stating: every task carries `execution_mode:` with one of the two legal tokens (D-07);
    a PLAN opens with a `## Lanes` table resolved against `.harness/team-config.yaml` at a named
    SHA; and before handing a plan back, run
    `python3 .claude/skills/harness/bin/check-plan-routes.py <plan path>` and fix every violation —
    a non-zero exit is not a plan that is ready for signature. Name the failure it prevents in one
    sentence (a task dispatched to an agent whose domain denies the write, discovered mid-build) and
    state that an ungranted surface is legitimate — it becomes a declared main-session step with its
    ordering constraint written down, not a task that silently fails. Add one row to the existing
    `## Red flags` table: "I'll sort out who executes this at build time" → "Then the build
    discovers it, three features running. The checker answers it now." Do NOT restate the rule in
    `.claude/agents/harness-pm.md` (D-06). The file is 110 lines today; keep it under 140.
  change_type: docs
  verify: `grep -q 'check-plan-routes.py' .claude/skills/harness-spec-driven/SKILL.md && grep -q 'execution_mode' .claude/skills/harness-spec-driven/SKILL.md && grep -q '## Lanes' .claude/skills/harness-spec-driven/SKILL.md && [ "$(grep -c '' .claude/skills/harness-spec-driven/SKILL.md)" -lt 140 ] && .claude/skills/harness/bin/run-unit-tests.sh && .claude/skills/harness/bin/check-docs.sh`
    — expected: exit 0; today the first grep alone exits 1.
  traces: REQ-01, REQ-02, REQ-06, D-01, D-06
  execution_mode: main-session-direct — reason: `.claude/skills/harness-*/SKILL.md` is granted to
    nobody in `team-config.yaml` — the FEAT-04 handoff note records the same denial. Declared step,
    ordered last because it names the script T-02 creates.
  depends_on: T-02
  feature: FEAT-09
  status: pending

## Fixture map — one fixture per clause, counted before the tasks were written

| SC | Clauses | Fixtures | Where |
|---|---|---|---|
| SC-01 | 2 | 2 | T-01 cases (a), (b) |
| SC-02 | 2 | 2 | T-01 cases (c), (d) |
| SC-03 | 2 | 2 | T-01 cases (e), (f) |
| SC-04 | 2 | 2 | T-01 cases (g), (h) |
| SC-05 | 3 | 3 | T-02 cases 1, 2, 3 |
| SC-06 | 2 | 2 | T-02 cases 4, 5 |
| SC-07 | 2 | 2 | T-02 cases 6, 7 |
| SC-08 | 4 | 4 | T-02 cases 8, 9, 16, 17 — case 17 is behavioural, not a source grep |
| SC-09 | 3 | 3 | T-02 cases 10, 11, 12 |
| SC-10 | 2 | 2 | T-02 case 13, plus `run-unit-tests.sh` in every task's `verify:` |
| SC-11 | 2 | 2 | inspection — the rule's single `file:line` in `harness-spec-driven/SKILL.md`, and an empty `git diff` for `.claude/agents/harness-pm.md` over the feature branch |
| SC-12 | 2 | 2 | T-02 cases 14, 15 |

## Verify receipts — executed at `ae2443d`, before this plan was written; the last two rows re-executed at revision

| Task | Command run | Result today | Result once the task lands |
|---|---|---|---|
| T-01 | the `--resolve` probe, verbatim | `HANG on .harness/harness.json`, exit 1 — the open-pipe branch blocks past 10s | `OK`, exit 0 |
| T-01 | `check-domain.sh --resolve <path> </dev/null` | exit 0, **stdout empty** — the fail-open half of the hazard | one or more agent names, or `NOBODY` |
| T-02 | `python3 .claude/skills/harness/bin/check-plan-routes.py` | `can't open file … No such file or directory` | zero-violation summary, exit 0 |
| T-03 | the four greps | exit 1 at `grep -q '^## Lanes'` | exit 0 |
| T-04 | `grep -q 'check-plan-routes.py' …SKILL.md` | exit 1 | exit 0 |
| all | `run-unit-tests.sh` | exit 0, 13 `PASS` — **green today, so non-discriminating alone**; it is the FEAT-07 whole-suite guard, paired with a discriminating probe in every `verify:` | exit 0, 14 `PASS` |
| all | `check-docs.sh` | exit 0 | exit 0 |
| T-02 case 17 (new) | the real matcher via the hook: a `harness-eng-lead` Write payload for `.harness/features/FEAT-09-plan-time-route-check/runs/1-eng/notes.md` (and a deeper `…/1-eng/deep/notes.md`) | **exit 0 — granted** by `matches()` through `team-config.yaml:278` | unchanged; case 17 asserts `check-plan-routes.py` reports it OK, i.e. reproduces this answer |
| T-02 case 17 (new) | `python3 -c "print('.harness/features/FEAT-09-plan-time-route-check/runs/1-eng/notes.md'.startswith('.harness/features/*/runs/*-eng'))"` — the naive prefix comparison the case exists to catch | **`False`** — a prefix matcher calls the granted path ungranted, so the two answers differ and the case discriminates | unchanged; a reimplementation making case 17 pass would have to be the real matcher |
