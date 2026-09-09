# QA gate — BUG-1507-ready-station-signature — cycle 0, review_sha ac5e24e5

GATE-ONLY audit at pin `ac5e24e5` (base `4b5dbb23`). No test authored, no source touched, no edit to
`notes/qa-BUG-1507-build.md` (that build-cycle note was read only, for context).

## matrix_ok: true

## Matrix derivation (read directly from `.harness/harness.json`, not taken on trust)

Tasks by `change_type` (from `plan.yaml`): T-01, T-02, T-05 = `bugfix`; T-03, T-04 = `docs`.

- `docs` → `always: []`. Nothing required. (T-03, T-04 graded by inspection only — see SC-04/SC-06/SC-07/SC-08 below.)
- `bugfix` → `always: []`, `when`: `unit` if `touches_runtime_code`, `integration` if
  `fix_confined_to_tests_and_contract_docs`, `__bug_class__` if `match_bug_class`.
  - `touches_runtime_code`: false. T-01/T-02 touch only `.md` instruction files; T-05 adds a test
    file, not production runtime code. **unit not required.**
  - `fix_confined_to_tests_and_contract_docs`: true — T-01/T-02 are instruction/contract-doc token
    fixes, T-05 is the test. **integration required.**
  - `match_bug_class`: per this repo's own qa Expertise (G-08, repository tier), this predicate is
    presently an unresolvable placeholder — no bug-class taxonomy entry fires for any diff yet.
    Not evaluated as firing.

**Floor: `integration` only.** `component`, `ui`, `typecheck`, `eval`, `functional` are
`unresolved`/`excluded`/null in `test_kinds` here and nothing in this diff obligates them — confirmed
by checking each against the five changed files (three `.md`, one `.py` docstring-only, one new
`tests/integration/*.py`). No criterion in the BRIEF rests on a `locally_run` kind either (BRIEF
verification notes says so explicitly and my own read of `test_kinds` agrees — the two `locally_run`
probes concern `inflight_registry.py`/session-accessor and issue-types, neither touched here).

## Per-kind table

| kind | state | cmd | exit | evidence |
|---|---|---|---|---|
| integration | **satisfied** | `env -u HARNESS_AGENT_TYPE .agents/skills/harness/bin/run-unit-tests.sh --kind integration` | 0 | pool: 8 workers, 50 files, 65.34s wall; every listed script ended `PASS`/`ALL PASSED`, none `FAIL`, no collection/import error |
| unit | not required | — | — | `touches_runtime_code` false for the three `bugfix` tasks (see above) |
| component/ui/typecheck/functional | not applicable | — | — | `unresolved`/`excluded` in `test_kinds`, diff does not touch their surfaces |
| eval | not applicable | — | — | `excluded` (DEC-187), no `ai_behavior` change_type in this feature |
| locally_run kinds | not applicable | — | — | diff does not touch `inflight_registry.py` session resolution or issue-types path |

`(HARNESS_AGENT_TYPE` unset per this repo's qa Expertise G-07 — with it set `test-plan-merge.py`
fails 11 unrelated checks and falsely reddens the whole suite.)

## SC-09's two named suites, run individually

| suite | cmd | exit | result |
|---|---|---|---|
| `tests/integration/test-gh-sync.py` | `env -u HARNESS_AGENT_TYPE python3 tests/integration/test-gh-sync.py` | 0 | tail of the standing run shows this script's block ending `PASS test-gh-sync.py`, all `ok` lines, none `FAIL` |
| `tests/integration/test-board-station.py` | `env -u HARNESS_AGENT_TYPE python3 tests/integration/test-board-station.py` | 0 | 16 `PASS` lines incl. "board-station refuses a CAPITALISED station, exit 2, nothing written" and "the refusal NAMES all six stations", trailer `all pass` |

**SC-09: met.** Both suites pass at `review_sha`, individually run, non-zero-assertion evidence (not
just an aggregate exit code) for each.

## The witness — observed counts, not just its own exit code

`tests/integration/test-station-argument-spelling.py`'s `check()` helper (source read directly,
lines 34-36) prints a `detail` string **only when a case fails** — a passing run's stdout carries no
numbers, only `PASS - <label>` lines. So I did not accept its green exit as assurance; I imported the
module's own `scope_files`/`occurrences`/`offenders` functions directly (read-only introspection, no
file authored, no test edited) and measured what it actually saw at `ac5e24e5`:

- **Scope size: 37 files** (`.claude/commands/*.md` ∪ `.claude/skills/**/*.md`), enumerated by
  `os.path.relpath` listing — not empty, not narrowed to a handful.
- **Occurrence count: 6** — exactly `MIN_OCCURRENCES`, the number the BRIEF says was measured at
  `4b5dbb23`. Listed in full:
  - `harness-plan.md`: `board-station.py … plan`, `gh-sync.py status … ready`
  - `SKILL.md`: `gh-sync.py status … review`
  - `github-mirror.md`: `gh-sync.py status … ready`, `gh-sync.py status … review` (×2, incl. the
    line-wrapped occurrence at :55-56 — collapsed-whitespace matching confirmed working)
- **`basenames seen` = `{SKILL.md, github-mirror.md, harness-plan.md}`** — all three files SC-02
  requires named are actually present in the swept set, not merely claimed.
- **`offenders` = `[]`** — zero non-lowercase / non-accepted tokens among the six.

This clears SC-02's "at least the six occurrences measured at 4b5dbb23, naming all three files" with
margin exactly at the boundary (6 found, 6 required) rather than an inflated or narrowed set —
**satisfied, not merely green.**

**SC-03** (reddens on a reintroduced capital): the second case (`case_reddens_on_a_reintroduced_capital`,
read at lines 107-138) copies the instruction files into a `tempfile.TemporaryDirectory` scratch
root, restores one capitalized argument, reruns `offenders()` against the mutated root and asserts
the offender is found by path/tool/token, with an unmutated copy of the same root as the negative
(anti-false-red) control. Both assertions passed under direct run (`PASS - the unmutated scratch copy
reports no offender`, `PASS - the sweep reddens on a reintroduced capital`). Implementation is
in-process function calls, not a subprocess or an env-var scope override — matching plan panel
finding `PF-4d48a7518cc7333294cad13b27fdaed6`'s resolution (T-05) that such machinery should not
exist. **SC-03: met.**

## SC-08 / SC-10 (inspection-verify SCs I could additionally ground from the diff)

- **SC-08**: `git diff 4b5dbb23 ac5e24e5 -- .claude/skills/harness/bin/gh-sync.py` = 16 insertions, 0
  deletions, hunk anchored at `@@ -1309,6 +1309,22 @@ def cmd_status`, entirely inside the triple-quoted
  docstring (new "Building:" bullet). No line outside the docstring changed. **Met.**
- **SC-10**: `git diff 4b5dbb23 ac5e24e5 -- factory_config.py .harness/harness.json plan-merge.py
  gh_board.py` = empty (0 lines). **Met.**

## SCs my lens cannot reach

SC-01, SC-04, SC-05, SC-06, SC-07 are `verify: inspection`, graded from transcripts/`git show` reads
that are the pm/orchestrator's own recorded acts (SC-01/SC-05 are post-signature/post-dispatch
run-time observations on this feature's own actors, not something a gate command re-derives). Not in
this gate's scope; qa's `sc_evidence` below covers only the `verify: automated` and directly
diff-groundable ones.

## Findings

None with severity ≥ `low`. One `info`:

- **info**: `match_bug_class` in the `bugfix` matrix row is a currently-unresolvable placeholder
  (repository Expertise G-08) — this is a pre-existing harness-config state, not something this diff
  introduces or could resolve, noted for completeness of the matrix derivation above only.

## What I did not do

No test authored or edited. No source file touched. `notes/qa-BUG-1507-build.md` read only, never
written to.

```yaml
VERDICT: PASS
DIGEST:
  headline: "integration gate satisfied at ac5e24e5 — full suite (50 files) exits 0, both SC-09 suites pass individually, witness's own scope/occurrence counts measured directly (37 files, 6 occurrences, 3 expected basenames present, 0 offenders) rather than trusted from its exit code"
  suite: pass
  failures: 0
  matrix_ok: true
  kinds:
    - { kind: integration, state: satisfied, cmd: "env -u HARNESS_AGENT_TYPE .agents/skills/harness/bin/run-unit-tests.sh --kind integration", named_tests: 50 }
    - { kind: unit, state: not_applicable, cmd: "n/a — touches_runtime_code false for the bugfix tasks", named_tests: 0 }
  coverage_gaps: []
  sc_evidence:
    - { id: SC-02, test: "tests/integration/test-station-argument-spelling.py::case_every_argument_is_accepted (measured: 37 scope files, 6 occurrences, offenders=[])" }
    - { id: SC-03, test: "tests/integration/test-station-argument-spelling.py::case_reddens_on_a_reintroduced_capital" }
    - { id: SC-08, test: "git diff 4b5dbb23 ac5e24e5 -- .claude/skills/harness/bin/gh-sync.py (16 insertions inside cmd_status docstring only)" }
    - { id: SC-09, test: "tests/integration/test-gh-sync.py and tests/integration/test-board-station.py, run individually, both exit 0" }
    - { id: SC-10, test: "git diff 4b5dbb23 ac5e24e5 -- factory_config.py .harness/harness.json plan-merge.py gh_board.py (empty)" }
  open_questions: []
  files_touched: []
  expertise_update: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-1507-ready-station-signature/.harness/harness/features/BUG-1507-ready-station-signature/notes/review-harness-qa-c0.md
```
