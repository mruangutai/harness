# QA Gate — FEAT-45-adversarial-plan-panel — build tip fc42462

**VERDICT: PASS.** Every matrix-required kind is `active` and green on both counters; no
task under-declares executable logic; the load-bearing `test-plan-panel.py` assertions
mutation-tested RED with no vacuity and no crash-not-caught; both suite invocations are
`rc=0` / `0 FAIL` lines.

## 1. Change-type audit (plan.yaml `change_type:` vs diff character)

| Task | Declared | Files | Diff character | Verdict |
|---|---|---|---|---|
| T-01 | docs | DECISIONS.md, DECISIONS-INDEX.md | prose + generated index | agree |
| T-02 | config | teams/plan-panel.yaml | data-shaped step/prompt YAML, same class as review.yaml | agree |
| T-03 | docs | SKILL.md | prose section | agree |
| T-04 | docs | harness-plan.md | prose bullet edit | agree |
| T-05 | config | templates/plan.yaml, harness-spec-driven/SKILL.md | template keys + <=16-line prose subsection, no logic | agree |
| T-06 | config | .omp/…validator-lead.md, .claude/…(generated) | `spawns:` list entry (data) + prose section, no logic | agree |
| T-07 | logic | check-state.sh | new INV-32 python-heredoc pass, real branching | agree |
| T-08 | logic | test-check-state.py | 9 new test cases incl. mutation proof | agree |
| T-09 | logic | panel_findings.py, its test, run-unit-tests.sh | new hashing module + CLI | agree |
| T-10 | logic | test-plan-panel.py, run-unit-tests.sh | new wiring-assertion test | agree |
| T-11 | config | sync-agent-adapters.py | **checked closely** — diff (`git diff 1d3e5db..HEAD`) is exactly one list-literal string append (`"fable-advisor",`) plus a comment; zero new functions, branches or control flow touched. Consumed unconditionally by pre-existing `bootstrap_one()`. Data change in a `.py` file, not logic. | agree — not under-declared |
| T-12 | logic | test-harness-yaml-corpus.py | constant `2`→`3` inside an existing `check()` condition + comment rewrite | agree |

No task under-declares executable logic. T-11 was the closest call and is the one verified
by direct diff read, not by trusting the plan's own framing.

## 2. Kind resolution (DEC-187)

Declared change_types in this plan: `docs` (T-01,03,04), `config` (T-02,05,06,11), `logic`
(T-07,08,09,10,12). No task is `cross_module`. Matrix floor: `logic.always=[unit]`,
`config.always=[]`, `docs.always=[]`.

| Kind | Required by floor? | `cmd` | State | Result |
|---|---|---|---|---|
| unit | yes (logic tasks) | `run-unit-tests.sh --kind unit`, `status: active` | active, ran, green | satisfied |
| integration | no (no cross_module task) | `run-unit-tests.sh --kind integration`, `status: active` | ran anyway (T-08's `test-check-state.py` lives there), green | satisfied (extra, above floor) |
| functional/component/ui/eval/typecheck | no | n/a to this diff | not applicable | soft skip, matches BRIEF's own "Verification gaps" |

`matrix_ok: true`. No kind is `missing` or `blocked`.

## 3. Suite runs (rc captured immediately, `^FAIL ` counted, never a tail read)

- `run-unit-tests.sh` (all): `rc=0`, `grep -c '^FAIL ' = 0`. 1012 `PASS`-labelled lines,
  56 registered scripts (29 unit + 27 integration) all discovered and executed — confirmed
  `test-panel-findings.py`, `test-plan-panel.py`, `test-check-state.py`,
  `test-harness-yaml-corpus.py` all appear in the log (lines 19, 1433/1461, 2001).
  Full output: `artifact://163`.
- `run-unit-tests.sh --kind unit`: `rc=0`, `grep -c '^FAIL ' = 0`. All four target files
  present.

No discovery shrinkage; no KIND-DRIFT failure (would have exited 2 before any script ran).

## 4. Test-first audit (`git log --oneline 1d3e5db..HEAD -- <file>`)

All four files land in a single squashed commit alongside their production code
(`test-check-state.py`+`check-state.sh` in `7ee3f65`; `test-panel-findings.py`+
`panel_findings.py` in `5178bb1`; `test-plan-panel.py`+`test-harness-yaml-corpus.py` in
`fc42462`), so **git history alone cannot order test vs. code within a commit — same-commit,
cannot-determine from git for all four.** Two mitigations narrow this:
- T-08/T-07 (`check-state.sh`): the failing-first obligation (SC-04, SC-17) is discharged
  structurally, not by commit order — the marker-anchored `inv32-red` mutation inside
  `test-check-state.py` itself proves the assertion reddens against a mutant lacking INV-32
  (verified below, §5).
- T-09/T-10/T-12: dev-ops receipts (`receipt-harness-dev-ops-T09.md`,
  `-T10.md`, `-T-12.md`) claim RED-before-implementation with re-measured evidence
  (`1 of 16 FAILING` for T-12's pre-change state). This is the dev's self-report, not
  independently re-derived by me from history — reasoned, not measured by qa.

## 5. Mutation re-verification of `test-plan-panel.py`'s load-bearing assertions

Method: never edited the tracked target files (bash-write-guard denies `harness-qa` writes
outside its domain, confirmed live). Built a disposable `/tmp/qa-fixture-repo` symlink-mirror
of the worktree with **only the file under mutation materialized as an independent copy**
(different inode, confirmed), mutated via Python (not shell `cp`/redirect), ran
`test-plan-panel.py` with `HARNESS_PROJECT_DIR`/`CLAUDE_PROJECT_DIR` pointed at the fixture,
then reset. Real worktree confirmed clean throughout and after (`git status --porcelain`
empty).

One environmental artifact surfaced and was isolated: routing `check-domain.sh` through the
fixture's `.git` (a symlink to the real repo) makes its own root resolution disagree with
`CLAUDE_PROJECT_DIR`, so **case (2)'s two `check-domain.sh` sub-checks fail on the
UNMUTATED baseline too** — confirmed by a baseline (no-mutation) run before trusting any
result. This is noise from the harness, not a defect in the assertion; case (2) was instead
proven directly (§ below) by reproducing its exact subprocess call against the real repo root
with no relocation.

| Assertion | Mutant | Observed | Verdict |
|---|---|---|---|
| (1a) should-not-exist prompt asks "what here should not be built at all" | reworded the question | RED (`FAIL (1a)...`), no other assertion affected beyond baseline noise | binding |
| (1b) scope prompt asks "which tasks serve no live requirement" | reworded the question | RED (`FAIL (1b)...`) | binding |
| (2) `check-domain.sh --resolve` grant, scope step's output path | direct probe (real repo root, unmutated env): real granted path resolves `code-reviewer` (PASS); a wrong-prefix path resolves only `harness-orchestrator`, no `code-reviewer` (FAIL) | RED on the mutant path, GREEN on the real one | binding, not vacuous |
| (3) scope's `on_fail.loop_back` output carries `{{cycle}}` | replaced `c{{cycle}}` with `c0` | RED (`FAIL (3) scope's loop_back outputs...`) | binding |
| (4a) should-not-exist persona is not a canonical `.omp/agents/` role | changed persona to `harness-code-reviewer` | RED (`FAIL (4a)...`) | binding |
| (8a) panel persona ∈ `harness-validator-lead.md`'s `spawns:` | removed `fable-advisor` from frontmatter list only | RED (`FAIL (8a)...`), (8b) unaffected | binding, independently proven |
| (8b) panel persona ∈ `SPAWNS["harness-validator-lead"]` in `sync-agent-adapters.py` | removed `"fable-advisor"` from the dict only | RED (`FAIL (8b)...`), (8a) unaffected | binding, independently proven |

Every mutant run: exit code 1 (not a crash exit), no Python traceback in stderr, no
`ModuleNotFoundError`/collection error — RED because the targeted assertion caught the
mutant, never because the harness broke. Discovery is non-vacuous: case (2)'s sweep
resolves the scope step's one real (non-empty) output plus the goal-check note path (2
real resolutions, not an empty walk); case (8) discovery confirmed the real `fable-advisor`
entries exist in both places before mutating either away.

`check-state.sh`'s own D-13 mutant (`inv32-red`, read at
`test-check-state.py:3017-3047`) was independently read, not re-executed by me: it brackets
by the exact marker comments T-07 requires, writes the mutant beside the original (never in
a fixture tmpdir, avoiding the import-death trap the file's own docstring records), asserts
`rc in (0,1)` and no `Traceback` in stderr on the mutant (crash-vs-caught discrimination),
and ran green (`ok - INV-32 plan panel fixtures, including inv32-red`) in both suite
invocations above.

## 6. Unasserted REQ/SC sweep

All `verify: automated` SCs (01–08, 13–15, 17) have a locatable assertion:
- SC-01→`test-plan-panel.py` cases 1a/1b/1c · SC-02→case 2 · SC-03→case 3 ·
  SC-04→`check-state.sh` INV-32 check 1 + `test-check-state.py` no-panel/inv32-red ·
  SC-05→`test-check-state.py` ruling-unattributed · SC-06→case 5 · SC-07→INV-32 check 1 ·
  SC-08→`run-unit-tests.sh`'s own drift detector (general mechanism, exits 2 before any
  script if a `test-*.py` is unregistered — not feature-specific but load-bearing) ·
  SC-13→`panel_findings.py` hash + stale-ruling case · SC-14→case 4a/4b ·
  SC-15→case 8a/8b · SC-17→reader-missing/reader-skipped cases + inv32-red.
- `verify: uat`/`verify: inspection` SCs (09, 10, 11, 12, 16) have no automated assertion —
  correctly, per their own declared verification method.

**One real gap, worth surfacing rather than closing quietly:** SC-03's SECOND
falsification direction — *"or by a second run overwriting the first's record"* — has no
dedicated test. `test-plan-panel.py` case (3) only asserts the literal token `{{cycle}}`
is present in re-runnable output paths; nothing simulates two consecutive panel runs and
checks that the first run's file survives the second. The `{{cycle}}` token is a structural
proxy for non-collision (distinct cycle numbers imply distinct filenames), not a direct
behavioral proof. Routed as a coverage gap, not a `must_fix` — the proxy is a reasonable
inference and the underlying mechanism (`{{cycle}}` templating) is the same one DEC-117
already established and tests elsewhere in this suite.

REQ-01..REQ-14: no REQ is left wholly without a tracing SC that itself has coverage per
above, except REQ-02's MODEL-independence half and REQ-11/REQ-12 (`verify: inspection`) —
both already flagged as declared, accepted gaps in BRIEF.md's own "Verification gaps"
section, not new findings.

## Cleanup note

Mutation probes ran against a disposable `/tmp/qa-fixture-repo` (outside the worktree,
never committed). The real worktree's `git status --porcelain` is clean of any change I
made. The scratch fixture directory itself could not be `rm -rf`'d via the `bash` tool
(bash-write-guard treats it as "inside a git worktree" because its `.git` was a symlink to
the real repo's `.git`); it is inert, untracked, and under `/tmp`, so it was left in place
rather than fought with a tool-switch that DEC-151 would flag as evasion.
