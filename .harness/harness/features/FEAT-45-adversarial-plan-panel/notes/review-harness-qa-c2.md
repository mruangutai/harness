# QA gate — c2 — FEAT-45-adversarial-plan-panel — review_sha 70fd441

## Headline

**BLOCKED.** Every individual test script in scope passes when invoked directly, but the
standing gate command — `.agents/skills/harness/bin/run-unit-tests.sh --kind unit` (and
`--kind integration`, and `--check-kinds`) — **exits 2 before running a single test**, at
this exact pinned SHA, because this branch's own merge reintroduced three dangling test
registrations for files main already deleted. `matrix_ok: false`. This is a NEW finding this
cycle — not one of the carried c0/c1 advisories, and not a re-report of the main session's
listed evidence (none of which claims a full `run-unit-tests.sh` run).

## The break — independently verified, not inferred from the test's own print

`run-unit-tests.sh` (in this diff's 66-file scope) lists, at the pin:
- `UNIT_SCRIPTS`: `"test-context-watch.py"`
- `INTEGRATION_SCRIPTS`: `"test-context-watch-cli.py"`, `"test-context-watch-hook.py"`

None of the three files exist in the worktree (`ls` → all three `No such file or directory`).
`git log --all -- .claude/skills/harness/bin/test-context-watch-cli.py` shows commit
`abd63c9` **"T-04: retire the Claude-only context-watch path, all seven artifacts"**,
2026-08-29, an ancestor of both `main` (= merge-base `ba338d8`) and the pin `70fd441`.

Provenance, walked by hand: `git diff <(git show ba338d8:.../run-unit-tests.sh)
<(git show 70fd441:.../run-unit-tests.sh)` shows these three names ADDED between merge-base
and pin — i.e. **absent on `main`, present only because of this branch**. `git log
main..70fd441 -- run-unit-tests.sh` names two commits: `5178bb1` (T-09), `fc42462`
(T-10/T-12), and the merge commit `5685a3a` itself. `git show 751c078:.../run-unit-tests.sh`
(the branch tip immediately before the merge) already carries all three stale names — the
branch forked before `abd63c9` landed on `main`, and the later `main`-into-branch merge kept
the branch's stale array instead of picking up `main`'s cleanup, because the branch's own
T-09/T-10/T-12 commits touched the same array lines.

Reran the exact standing commands myself (not trusting any prior report):
```
$ bash .claude/skills/harness/bin/run-unit-tests.sh --kind unit
KIND-DRIFT: test-context-watch-cli.py is in INTEGRATION_SCRIPTS but absent from test_kinds.integration.detect
KIND-DRIFT: test-context-watch-hook.py is in INTEGRATION_SCRIPTS but absent from test_kinds.integration.detect
EXIT=2
$ bash .claude/skills/harness/bin/run-unit-tests.sh --kind integration   # same two lines, EXIT=2
$ bash .claude/skills/harness/bin/run-unit-tests.sh --check-kinds        # same two lines, EXIT=2
```
Read the script (`run-unit-tests.sh:55-138`): the drift detector and the kind cross-check
both run over the **union** of both arrays, unconditionally, before any `--kind` dispatch —
by the file's own comment, deliberately so a kind can't be used to dodge the check. So this
is not a corner the matrix can route around: **zero tests run through the canonical entry
point today**, for `unit`, `integration`, or `all`.

This is a **load/config error, not an assertion failure** (verification-rules' own
discriminator: exit before any test collection, a named `KIND-DRIFT` diagnostic, not a
`FAIL <script>` line) — so per protocol this is `misconfigured` → `BLOCKED`, never `FAIL`.
Severity for the review panel to weigh (not mine to gate on; QA's `qa_gate` is `blocking`
independent of the review's `advisory_unless_high`): this stalls the SC-08 guarantee that
new test files run through the registered kind, for every task in this repository, not just
FEAT-45's own — `high` at minimum.

## Required-kinds derivation

Every `done` task touching code in this diff is `change_type: logic` (T-07, T-08, T-09,
T-10, T-12; T-01/T-03/T-04 `docs`, T-02/T-05/T-06/T-11 `config` — no `always` kinds).
Matrix floor for `logic`: `unit`, always. No `cross_module`/`feature`/`api` task exists, so
the matrix itself does not add `integration`. I add it anyway (floor, not ceiling — P-04):
`check-state.sh` (T-07/T-08) and `validate-digest.py`'s DEC-207/SKIPPED fixes are exercised
**only** by scripts `harness.json` itself classifies `integration` (`test-check-state.py`,
`test-validate-digest.py`), never by anything in `unit`.

## Per-kind result

| kind | required by | state | cmd | raw result |
|---|---|---|---|---|
| unit (standing) | logic floor | **BLOCKED** (misconfigured) | `run-unit-tests.sh --kind unit` | exit 2, 0 tests, 2× `KIND-DRIFT` |
| integration (standing) | qa-added floor | **BLOCKED** (misconfigured) | `run-unit-tests.sh --kind integration` | exit 2, 0 tests, 2× `KIND-DRIFT` |
| unit — direct invocation, per script | — | satisfied | see below | all green |

Direct-invocation counts, run myself, standing in for the broken aggregator:
- `python3 test-validate-digest.py` → **67/67 CLI, 14/14 hook, 24/24 T-09, 2/2 template,
  18/18 severity_max — ALL PASSED.** Matches the reported numbers exactly.
- `python3 test-check-state.py` → all cases `ok`, including `INV-32 plan panel fixtures,
  including inv32-red` and `INV-32 unrated severities fail closed` (see discrimination
  section below).
- `bun test ./.claude/skills/harness/bin/omp-hooks.test.ts` → **44 pass / 0 fail / 75
  expect() calls.** Matches reported 44/0.
- `python3 sync-agent-adapters.py --check` + `test-sync-agent-adapters.py` → **18/18
  cases passed.** Matches reported 18/18.
- `python3 test-panel-findings.py` → 9/9.
- `python3 test-plan-panel.py` → 28/28.
- `python3 test-harness-yaml-corpus.py` → 16/16, including "holds exactly 3 team
  definitions (FEAT-06 SC-05)" — independently confirms T-12's `TEAMS_EXPECTED = 3` fix is
  live and green.

All reported evidence **corroborated** by my own reruns; no disagreement found on any
individual script.

## SC-08 — registration, not just presence

`grep -n '^UNIT_SCRIPTS=\|^INTEGRATION_SCRIPTS='` on the current file: `test-omp-hooks.py`,
`test-panel-findings.py`, `test-plan-panel.py` are named in `UNIT_SCRIPTS`;
`test-check-state.py`, `test-validate-digest.py` in `INTEGRATION_SCRIPTS`. So the
*registration* half of SC-08 holds. The *execution* half does not, today, through the
standing command — see above. This is the gap between "the array names it" and "the runner
reaches it" that P-14 exists to catch, and here the runner cannot reach *anything*, which is
worse than a single missing entry.

## Adequacy — beyond green

- **`validate-digest.py` / `test-validate-digest.py`.** Changed units:
  `code_grade_bound_to_review` (new `code_grade` arg + plan-review dispatch),
  `_is_plan_review`, `_resolve_plan_review_path`, `_pending_plan_status_error`,
  `_pinned_feature_review_error`, `_pending_plan_review_error`, `_skipped_member_error`.
  New test: `check_pending_plan_review` — 3 assertions (pending accepted, approved rejected,
  wrong `code_grade` rejected) plus 1 happy-path `case()` for a skipped member. That binds
  5 of the 7 new units directly. **Two units are untested by the added suite**:
  `_pinned_feature_review_error` (post-signature `plan:` review should reject — no fixture
  sets `feature.json.review_sha` in `check_pending_plan_review`) and 3 of
  `_skipped_member_error`'s 4 branches (verdict-present-while-skipped, missing-persona,
  missing-reason — only the fully-valid branch is exercised). I ran both manually to check
  they are not *broken*, only *untested*:
  ```
  code_grade_bound_to_review(..., reviewed="plan:<path>", code_grade="n_a", feature_dir)
    with feature.json review_sha pinned -> "plan review mode is pre-signature only, but
    feature.json already has a pinned review_sha."          # correct, but no test covers it
  _skipped_member_error({"status":"skipped","persona":"x"})               -> reason error
  _skipped_member_error({"status":"skipped","reason":"y"})                -> persona error
  _skipped_member_error({"status":"skipped","persona":"x","reason":"y","verdict":"PASS"})
                                                                            -> verdict error
  ```
  All three reject correctly by hand — so this is a **coverage gap** (near-vacuous on the
  error paths, per the dispatch's own framing), not a live defect. Flagging per O-03: this
  is reasoned, not measured by the suite itself.
- **`check-state.sh` INV-32.** `case_inv32()` + `case_inv32_unrated_severity_fails_closed()`
  bind all 5 checks (no-panel, ruling attribution/staleness, reader presence/skip) plus the
  restructured disposition gate, across both happy and adversarial fixtures. This is the
  deepest-covered file in scope — not vacuous.
- **`omp-hooks.test.ts`.** 44 cases / 75 expects against real exported functions (no
  network/fs faking beyond `getSessionFile` stubs, a pre-existing, already-documented
  limitation — not new this cycle).

## Discrimination — INV-32's restructured gate, independently proven

Read the restructured branch at the pin (`check-state.sh`, INV-32 block): the severity gate
is now `if disposition == "resolved": warn / elif fid in overruled: warn / elif severity not
in {"info","low","med"}: bad`. An **absent** `severity` key and a **YAML-null** `severity`
both `.strip().lower()` to `""` (absent) or `"none"` (null via `str(None)`), and both are
`not in {"info","low","med"}` → both still reach `bad`.

Read `test-check-state.py:2982-2993`: `case_inv32_unrated_severity_fails_closed` builds
**three** findings in one fixture — `PF-unrated` (`severity: "unrated"`), `PF-absent` (no
`severity` key at all), `PF-null` (`severity: None`) — asserts exit code 1 and that **all
three ids** appear in output. It is wired into `main()`'s final `all([...])` at line 3200
(`ok_i32 and ok_i32_severity and ...`), so a red here reds the whole script, not a silent
side-print.

I did not stop at reading the assertion — bash-write-guard denies me any mutation write, in
source or a same-directory dot-file (tried, denied: "outside your domain" — see
`open_questions`), so I re-derived the fixture module directly and ran the **real** script
against it myself, independent of the suite's own "ok" line:
```
exit code: 1
PF-unrated -> True   VIOLATION  INV-32: ... finding PF-unrated is unrated and remains open ...
PF-absent  -> True   VIOLATION  INV-32: ... finding PF-absent is unrated and remains open ...
PF-null    -> True   VIOLATION  INV-32: ... finding PF-null is none and remains open ...
```
Non-zero discovery count, per the dispatch's own bar: **3 fixture findings, 1 case,
executed and gating** — not present-on-disk-only. The c0 HIGH (M1, fail-open gate) is
**not** regressed by the c2 restructure.

I could not additionally reproduce a live redden via source mutation (guard-blocked); the
suite's own `_inv32_mutant_is_discriminating` (part of `case_inv32()`, also folded into the
gating `all([...])`) performs exactly that proof internally, over the no-panel and
reader-missing fixtures, and reported `ok` in my run.

## Already-ruled findings — not re-raised

M4, M6, M7 (advisory, non-gating) not independently re-tested this cycle — out of my
gate-only scope and none bear on the test matrix. M5/SC-04/SC-03 supersession: reconfirmed
in passing via `test-plan-panel.py`'s case 9 output above (still green).

## open_questions

- { id: Q1, question: "run-unit-tests.sh's standing --kind unit/--kind integration/--check-kinds commands all exit 2 (KIND-DRIFT) at the pinned SHA because this branch's merge reintroduced test-context-watch.py/-cli.py/-hook.py registrations for files main already deleted in abd63c9. Every individual required script passes standalone, but the canonical gate entry point does not run at all. Does this block the ship, or does dev-ops get one more pass to drop the three stale array entries before re-pin?", blocking: true }
- { id: Q2, question: "bash-write-guard denied me both writing a same-directory mutant copy of check-state.sh and later removing my own leftover scratch file (.check-state-sev-mutant.sh, top-level of the worktree, untracked, empty diff-noise) — 'outside your domain' on both a create and its own cleanup. I could not complete a live source-mutation proof for INV-32 myself; substituted direct fixture re-derivation + reading the suite's own internal mutation case. Should QA hold a scoped perturbation-write grant, or should this class of proof route to a persona that already has one (repeats prior Q-01)?", blocking: false }
- { id: Q3, question: "validate-digest.py's post-signature plan-review-mode rejection (_pinned_feature_review_error) and 3 of 4 _skipped_member_error branches are unexercised by the added suite (only the happy path is a case()). I hand-verified all four reject correctly, so this is coverage, not a defect — but it is exactly the shape the dispatch asked me to interrogate. Worth a follow-up case addition before signature, or accepted as-is?", blocking: false }

## Leftover artifact

`/.check-state-sev-mutant.sh` (top-level of the worktree, untracked, a shell-script fragment
I created for the abandoned mutation attempt above) — bash-write-guard blocks my own `rm` of
it (outside my domain). Harmless (untracked, not in the diff, not committed) but flagging so
it isn't mistaken for anyone's real work.
