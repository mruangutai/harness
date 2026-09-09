# Code review — BUG-1507-ready-station-signature — review_sha `ac5e24e5`

**VERDICT: PASS.** Stage 1 (spec compliance) is clean across all six REQs and all ten SCs. Stage 2
(quality) turns up one grade-2 test function (reasoned, non-blocking) and one latent verify-string
fragility (low, not currently exploited by anything that runs). No must_fix.

## Census — exactly the five files, plus expected feature bookkeeping

`git diff --stat 4b5dbb23 ac5e24e5` lists 21 changed files: the five under review
(`.claude/commands/harness-plan.md`, `.claude/skills/harness/references/github-mirror.md`,
`.claude/skills/harness/SKILL.md`, `.claude/skills/harness/bin/gh-sync.py`,
`tests/integration/test-station-argument-spelling.py`) plus 16 more, **every one of them** under
this feature's own `.harness/harness/features/BUG-1507-ready-station-signature/` tree (`BRIEF.md`,
`STATE.md`, `feature.json`, `plan.yaml`, `observations/harness-pm.md`, and eleven `notes/*`
records). This is ordinary feature-tree bookkeeping accumulated as the plan/build ran, not a sixth
production file. `feature.json` is one of the sixteen — I confirmed the pin-writing commit
(`25179569`, HEAD of the worktree, one commit past `ac5e24e5`) is **not** in this range: `git diff
--name-only ac5e24e5 25179569` touches only `feature.json`, and it is a distinct, later write on
top of the one already inside `4b5dbb23..ac5e24e5`. So this review is at the correct pin, not
accidentally reading the pin-write commit.

## SC-08 — measured, not inspected

`git diff -U5 4b5dbb23 ac5e24e5 -- .claude/skills/harness/bin/gh-sync.py` is **one hunk**, `@@
-1309,6 +1309,22 @@`, 16 insertions/0 deletions, entirely inside `cmd_status`'s docstring (the
`- Building:` bullet and its `D-02` paragraph). Byte comparisons:
- tuple line: `diff <(git show 4b5dbb23:...|sed -n '1347p') <(git show ac5e24e5:...|sed -n '1363p')`
  → empty diff, **identical**.
- ready-approval refusal block: `diff <(git show 4b5dbb23:...|sed -n '1327,1331p') <(git show
  ac5e24e5:...|sed -n '1343,1347p')` (shifted +16 lines by the docstring insertion) → empty diff,
  **identical**.
`python3 -c "import ast; ast.parse(...)"` on the `ac5e24e5` blob parses clean. **SC-08: met.**

## SC-10 — measured, not inspected

`git diff 4b5dbb23 ac5e24e5 -- factory_config.py .harness/harness.json plan-merge.py gh_board.py`
— all four **empty**. **SC-10: met.**

## Per-task `verify:`, run verbatim from the worktree root at the pinned tree

| Task | Exit | Binds what it claims, or a proxy? |
|---|---|---|
| T-01 | 0 (`['plan', 'ready']`) | Real: counts exactly the two CLI-argument occurrences and requires both lowercase — matches the LEAVE LIST distinction (column words `Plan`/`Ready` at lines 11/25/26 stay capitalized; I read them directly, both untouched). |
| T-02 | 0 (`['review', 'ready', 'review']`) | Real: three lowercase CLI args plus the literal `plan-merge.py set-feature-station --station building` substring-in-collapsed-text — I read the Building row directly and the backtick span opens before `plan-merge.py` and closes only after `building`, exactly as T-02's intent mandates (mis-closing after `set-feature-station` would break this exact literal check, so the check is discriminating, not decorative). |
| T-03 | 0 (`True 741`) | Real: slices `## The build phase` .. `## Routing a lead`, then further slices on `'The eng segment.'`..`'The qa segment'` before requiring the literal command inside — binds to segment 1 specifically, not the whole build-phase block (this is what closed panel finding PF-0274cfb4). I read the added text: three things stated, no more (feature-not-task, start-task doesn't cover it, timing is "as dispatching starts"), matching intent word for word. |
| T-04 | 0 / 0 | `ast.parse` proves the file still compiles; the docstring-bullet regex is real (I read the bullet, it opens `- Building: `); the `grep -qF` on the tuple line is a byte-exact positive check, not an absence check, so it cannot pass on a variant that also deleted the tuple's other members. |
| T-05 | 0 (8/8 PASS rows) | Real, see quality section below — this is the one genuine code artifact. |

## Stage 1 — spec compliance

REQ-01 (kickoff Plan write + signature Ready write succeed): **met**. T-01 lowercases both
`harness-plan.md` occurrences (line 11 `board-station.py <issue-number> plan`, line 24 `gh-sync.py
status <feature-dir> ready`); SC-01's own transcript (`notes/sc01-ready-write-transcript.md`) shows
the main session ran the post-fix command and got `gh-sync: plan.yaml station -> ready`, exit 0.

REQ-02 (feature's own plan record advances to `building` at build dispatch): **met**. T-03 adds the
instruction to `SKILL.md` segment 1; SC-05's transcript
(`notes/sc05-building-write-transcript.md`) shows the orchestrator running `plan-merge.py
set-feature-station --station building` and `plan.yaml` reading `status: building` immediately
after.

REQ-03 (written contract for `gh-sync.py status <dir> building`): **met** — T-04's docstring bullet.

REQ-04 (github-mirror.md names the feature-station writer): **met** — T-02's Building row now names
both writers and which writes the card vs. the plan.

REQ-05 (reintroduced capital fails a test): **met** — T-05's `case_reddens_on_a_reintroduced_capital`
is a real, in-process negative control (see below).

REQ-06 (vocabulary/schema/observable-behaviour unchanged): **met** — SC-10 (empty diffs on the four
vocabulary/schema files) and SC-08 (zero executable-line changes to `gh-sync.py`) jointly prove this
directly rather than by inspection.

No scope creep found: every changed line in the five files traces to a named `REQ`/task. No omission
found: every REQ has a corresponding change. Decisions D-01..D-06 all honored — verified D-04's
column-vs-argument split by reading every touched line in `harness-plan.md` and `github-mirror.md`
directly (not just the diff), confirming every LEAVE-LIST/column-label occurrence (`Ready`,
`Building`, `Review`, `Done`, `Plan` as prose or table-label) stayed capitalized while every CLI
argument went lowercase.

`SC-01`: **partial**, as BRIEF pre-declares (zero recorded sub-issues on this feature — not a
defect, not re-raised). `SC-04..SC-07`: **met**, each read at `git show ac5e24e5:<path>` directly
(github-mirror.md Building row names both writers and which does which; `cmd_status` docstring
Building bullet states plan-recorded/no-card; SKILL.md segment 1 addition present and scoped).
`SC-09`: **met** — I independently ran both regression suites (`test-gh-sync.py`,
`test-board-station.py`) at the pinned tree, both exit 0. `SC-02`/`SC-03`: **met**, see quality
section — verified the regex against the actual pre-fix text of both defect files (see below), not
just trusted the test's own self-report.

## Stage 2 — code quality: `tests/integration/test-station-argument-spelling.py`

**Fail-open hunt.** `case_every_argument_is_accepted` cannot pass on an empty or near-empty sweep:
`len(scope) > 0` and `len(found) >= MIN_OCCURRENCES` (6) are separate asserted rows, not just a
non-empty check — a narrowed sweep that found, say, 2 occurrences fails outright rather than passing
quietly. `ACCEPTED_STATIONS` is genuinely derived (`set(factory_config.MANDATED_STATIONS) |
{TERMINAL_MARKER}` / `set(factory_config.MANDATED_STATIONS)`), not a hand list — I independently
loaded `gh-sync.py`'s own `STATION_VALUES` (`('backlog','plan','ready','building','review','done',
'abandoned')`) and `board-station.py`'s validation source (`factory_config.station_names`, which is
`MANDATED_STATIONS`-derived) and both match the test's derivation exactly.

**Regex vs. the real defect (not a detail the real instances lack).** I ran the exact `TOKEN_PATTERN`
against `git show 4b5dbb23:.claude/commands/harness-plan.md` and
`git show 4b5dbb23:.claude/skills/harness/references/github-mirror.md` myself, in-process:
`harness-plan.md -> [('board-station.py','Plan'), ('gh-sync.py status','Ready')]`;
`github-mirror.md -> [('gh-sync.py status','Review'), ('gh-sync.py status','Ready'),
('gh-sync.py status','Review')]` — 5 offending tuples across the two files, including the
line-wrapped `:55-56` occurrence (only visible because of the whitespace-collapse, confirmed: it is
one of the three `github-mirror.md` matches). The regex genuinely catches the real historical
defect; it is not anchored on a detail the real instances lack.

**Negative control genuinely reaches the code path.** `case_reddens_on_a_reintroduced_capital` runs
the anti-false-red control (`clean == []`) **before** mutating, then does a substring replace with an
`assert before != after` guard against a silent no-op, then asserts both that `offenders(tmp)` is
non-empty **and** that one tuple exactly names `(plan_copy, "gh-sync.py status", "Ready")` — this
attributes the red to the reintroduced token specifically, not to any incidental scratch-root
difference. Confirmed both PASS rows in a live run.

**Grep for scope-repoint machinery** (`os.environ`/`os.getenv`): zero hits — `offenders → occurrences
→ scope_files` is a plain parameter chain, matching plan D-05/panel finding
`PF-4d48a7518cc7333294cad13b27fdaed6`'s resolution (no env override, no subprocess, no recursion
guard).

**F-01 (low) — T-05's chained `verify:` string is fragile under `pipefail`, a false-negative risk,
not exploited today.** Running the literal three-command `&&`-chain from `plan.yaml` under `bash -uo
pipefail` (the exact flags `run-unit-tests.sh` itself sets at its line 2) reproduces a
`BrokenPipeError` on legs 2 and 3 that changes the **pipe's** exit code from 0 to 1: `grep -q`
closes its stdin the instant it matches, and the producer's later `print()` calls throw
`BrokenPipeError`, which is unhandled and makes the python process itself exit non-zero; under
`pipefail` that propagates to the whole pipe. Concrete scenario: if any future automation invokes
plan.yaml's literal `verify:` string under a strict shell (rather than running the file directly,
which is what `run-unit-tests.sh --kind integration` actually does, and which is unaffected — I
confirmed `python3 tests/integration/test-station-argument-spelling.py` alone exits 0 cleanly), it
would report this passing task as FAILED. Not exploited by anything in this diff: default bash (no
pipefail) takes the last command's exit code, so the literal chain exits 0 as intended, and I
confirmed `run-unit-tests.sh`'s own kind-runner calls the script directly, never through this piped
string. `qa-BUG-1507-build.md` independently observed and recorded the same `BrokenPipeError`
without flagging the pipefail exposure — recording it here per P-15/G-10 rather than letting it
recur unremarked.

**F-02 (med) — code-risk grade: `case_reddens_on_a_reintroduced_capital` is grade 2.**
`code-grade.py --base 4b5dbb23 --head ac5e24e5` (merge-base(origin/main, ac5e24e5) = `4b5dbb23`,
confirmed matching): `LINE: 107, CYCLOMATIC: 9, COGNITIVE: 6, ABC: 33.4, GRADE: 2, DRIVER: abc, BAR:
3, RESULT: FAIL, SEVERITY: med, REASON REQUIRED`. All six other new functions pass their bar
(`check`, `scope_files`, `occurrences`, `offenders`, `case_every_argument_is_accepted`, `main` — all
grade 4 or 5). Reason for this one: the function is one coherent negative-control procedure (stage
two scratch copies, prove the unmutated copy clean, mutate, prove the mutation reddens) whose ABC
size comes from sequential setup statements (`os.makedirs`, `shutil.copy`, two `open`/`read`/`write`
pairs, two `check()` calls), not from branching — cyclomatic 9 and cognitive 6 are both well under
what would indicate tangled control flow. Splitting the anti-false-red control out of the
mutation-and-assert step would separate the "clean copy proven first" guarantee from the mutation it
must precede, which is exactly the ordering SC-03 requires a reader to see co-located. Grade 2 does
not block per `harness-code-risk-grading`; recorded here as the required written reason, not as a
`must_fix`.

**Info, not a finding — `check()`'s success path omits the numeric detail.** `check()` (byte-identical
to `tests/integration/test-check-instruction-paths.py`'s own helper, the sibling harness this task
was told to match) only prints `detail` when `not ok`. On a passing run this means the printed
`PASS - at least the measured number of station-argument occurrences are found` line never shows the
count on stdout. This does **not** weaken the gate itself — `len(found) >= MIN_OCCURRENCES` is a real
assert, not a cosmetic message, so an empty/narrowed sweep cannot exit 0 regardless of what gets
printed — only the human-readable log is terse on success. Matches established convention; not a
quality regression this diff introduces.

## Already-adjudicated (not re-opened)

- R1 (task-card Ready exclusivity / `gh_board.py` derivation) — disclosed limit in BRIEF's own
  Constraints section, out of scope by the issue's scope line. Not re-raised.
- R2 (T-05/D-06 stay; T-01/T-02 stay `bugfix`) — plan-signed, honored as written.
- SC-01's `partial` verdict — pre-declared by BRIEF's own text for the zero-recorded-sub-issue case.
  Not a defect.

## Open questions

None — no reversible/irreversible ambiguity found that needs the operator.

```yaml
VERDICT: PASS
DIGEST:
  headline: Spec compliance clean across REQ-01..06/SC-01..10; one reasoned grade-2 test function, one non-exploited pipefail fragility in T-05's verify string — nothing gates.
  severity_max: med
  findings: 2
  must_fix: []
  spec_violations: []
  code_grade: grade_2
  reviewed: "4b5dbb23..ac5e24e5"
  human_commits_in_scope: []
  open_questions: []
  files_touched: []
  expertise_update: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-1507-ready-station-signature/.harness/harness/features/BUG-1507-ready-station-signature/notes/review-harness-code-reviewer-c0.md
```
