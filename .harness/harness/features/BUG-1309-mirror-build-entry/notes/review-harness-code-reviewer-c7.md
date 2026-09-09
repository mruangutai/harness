# Code review c7 — BUG-1309 mirror build entry — whole-feature diff @ 894adc0f

Re-derived from source at the pin; c6 (interrupted before a lead verdict, treated ABSENT) read only
as a hypothesis set. Range graded: `6ad7233f (merge-base origin/main)..894adc0f` — the WHOLE feature
diff, 17 files, +1295/-102, not only the last commit.

## Verdict: PASS, severity_max med, no must_fix

## Stage 1 — spec compliance: PASS

Traced every task (T-01..T-13) in `plan.yaml` against its `files:` list and the diff --stat; no file
touched by the diff is untraced to a task, no task's declared file is absent from the diff. One file
outside the batch's named "code surfaces" list is genuinely in scope and was checked:
`.claude/skills/harness/bin/merge-settings.py` (T-05's `files:` names it explicitly; HOOK_SPECS gained
exactly one entry, appended last, matching T-05's registration spec verbatim — confirmed by diff).

The last commit (894adc0f, merge-gate.py `feature_for` + `main`'s `document is None` branch, +7/-11)
is the decision-table fix scoped by the c5 FAIL. Re-verified against T-05's own intent text
(plan.yaml:886-891, "LOCATE THE FEATURE ... No match: exit 0"): the ORIGINAL T-05 spec never asked
for an `unusable` scan-wide sentinel at all — the c5-era code invented that behaviour, and this pin's
fix removes it, restoring the code to what T-05 actually specified. This is a correction to spec, not
new scope. `tests/integration/test-merge-gate.py`'s own diff at this commit deletes the assertion
"T-05 unusable target record fails closed" (which asserted DENY + "malformed feature record") and
replaces it with "T-05 no-record branch ignores unrelated malformed record" (asserts ALLOW) — the
test suite itself flipped polarity in the same commit, not left stale. Ran the whole file at the pin:
`python3 tests/integration/test-merge-gate.py` → 19/19 `ok`, `ALL PASSED`, exit 0 (executed this run).

No scope creep found: `merge-settings.py`'s HOOK_SPECS addition, the three hook-array registrations,
`feature_schema.BUILD_ENTRY_ERA_EXEMPT`/`recovery_command_for`, `gh-sync.py`'s `record_build_entry`/
`_build_entry_preflight`/`recover-terminal` family, and `check-state.sh` INV-37 all trace cleanly to
REQ-01..REQ-10 and D-01..D-12 with no unrequested behaviour added. No omission found in the surfaces
read (below). SC-09 (doc naming) not independently re-read word-for-word this cycle — no code change
in this diff touches `github-mirror.md`/`SKILL.md` beyond what six prior cycles already inspected at
this same pin (unchanged since); not re-litigated.

## Stage 2 — code quality

**Files actually read this cycle, beyond merge-gate.py**: `gh-sync.py` full diff (`skip`,
`record_build_entry`, `_build_entry_preflight`, `_build_entry_recovery_notice`,
`cmd_recover_terminal` + its three helpers, `main`'s `_BUILD_ENTRY` arming, `cmd_ship`'s new skip
text); `feature_schema.py` full diff (`BUILD_ENTRY_ERA_EXEMPT`, `recovery_command_for`);
`check-state.sh` INV-37 block in full; `post-merge-sweep.sh`'s new retention block in full;
`.claude/settings.json`, `templates/settings.snippet.json`, `.omp/extensions/harness-hooks.ts`,
`merge-settings.py` HOOK_SPECS diffs. Not re-read line-by-line this cycle: `feature-schema.json`,
the four test files beyond spot-checking case names/counts, and the two doc files (six prior cycles
already covered these; nothing in this pin's diff touches them).

**Fail-open hunt, whole-feature scope:**
- `feature_for` (merge-gate.py:100-108): a non-dict/unparseable record can no longer be "matched" by
  construction (`isinstance(document, dict) and ...` short-circuits) — confirmed by test suite's own
  new negative-control case above. No fail-open here; this is the fix, not a gap.
- `recovery_command_for` (feature_schema.py): `except Exception: return "recover-terminal"` on an
  unreadable/absent plan.yaml. This fails toward the SAFER command — recover-terminal creates zero
  task sub-issues, `open` on an actually-finished feature would recreate the exact historical-issue
  bug this feature exists to close (FEAT-55). Correct fail direction, not a gap.
- `check-state.sh` INV-37 (:1993-1996): `_sync37 = bool(...) except Exception: False` — a malformed
  `harness.json` silently disables the INV-37 loop with no dedicated diagnostic. NOT a coverage hole
  in practice: `cj`/`cfg` parsing at :995-1002 (unconditional, earlier in the same file) already
  appends `".harness/harness.json is not valid JSON."` to `bad` for the identical failure mode, so
  the operator is never left without a violation. **[info]** — INV-37 re-parses `harness.json`
  independently instead of reusing the already-validated `cj`, which is pure duplication risk (a
  future edit to the earlier parse's error handling would silently uncouple from this one) rather
  than a live gap. Introduced at this pin (new code, `git show 894adc0f^:.../check-state.sh` has no
  INV-37 block at all — confirmed, entire block is new). Non-gating.
- `post-merge-sweep.sh`'s new retention block (:213-232): `except (OSError, json.JSONDecodeError):
  SKIP removal ... return` on failure to read either config file — fails toward RETAINING the
  worktree (the safe direction: an operator can always remove a wrongly-kept worktree by hand, but a
  wrongly-removed one loses the evidence this whole feature exists to preserve). Correct direction.
- `gh-sync.py`'s `skip()` (:163-196): the Build-entry write only fires when
  `_BUILD_ENTRY["feat_dir"] is not None` (armed only for `cmd == "open"`, `main()`:2283-2286) AND
  `not _BUILD_ENTRY["remote_written"]` AND the target `feature.json` file exists. Traced all three
  guards: `remote_written` is set exactly at the three remote-mutating call sites
  (`_open_ensure_milestone`, `_open_ensure_parent`, `_open_sync_task`) each immediately after their
  `gh` create call returns success — matches D-04's "records nothing after a partial write" exactly.
  For `recover-terminal`, `_BUILD_ENTRY` stays unarmed (no `feat_dir`), so a `load_config` skip
  (e.g. gh outage) during recovery writes nothing at all, leaving the record exactly as it was
  (absent or `recovery-required`) — satisfies REQ-09's "leaves the feature non-terminal"; the
  worktree-keeps half of REQ-09 is already decided earlier by `post-merge-sweep.sh` at the original
  merge event and is not re-evaluated by a later `recover-terminal` invocation, so there is nothing
  here to re-derive dynamically. No gap found on this path.

### c6 finding (a) — unresolvable git/gh denies naming "this feature"

**REPRODUCED live**, current code, this pin. Built a fixture root (`.harness/harness.json` with
`github.sync: true`, `github.repo: "org/repo"`; one feature dir with `branch: "somebranch"`,
`github.build_entry: "recovery-required"`). Control run (`git merge somebranch`, explicit branch,
normal `PATH`) correctly denies naming the feature and the `recover-terminal` command. Repro run
(bare `git merge`, no branch arg, `PATH` pointed at an empty directory so the `git` binary cannot be
found) produces: `{"...": "merge-gate: could not evaluate this feature's Build-entry receipt, so
this merge is denied. Repair the feature record and re-run the merge."}` — the generic seed string,
naming no feature and no actionable command. Mechanism: `local_branch()` (merge-gate.py:69-72) calls
`subprocess.run(["git", ...])` unguarded; when `git` is not resolvable via `PATH` this raises
`FileNotFoundError` from inside `head_branch()`, called before `feat_dir` is ever assigned in
`main()`, caught only by the terminal `except Exception: deny(f"...{feat}'s...")` with `feat` still
the `"this feature"` seed (merge-gate.py:132).

**Pre-existence, established, not assumed.** `git -C <worktree> show 894adc0f^:.claude/skills/harness/bin/merge-gate.py`
— `local_branch`, `head_branch`, the `feat = "this feature"` seed line, and the terminal `except
Exception` are byte-identical to the pin; unaffected by this pin's diff (which touched only
`feature_for` and the `document is None` branch). Traced further: `git log --oneline -S"def
local_branch" 6ad7233f..894adc0f -- .../merge-gate.py` shows this pattern originates at `4338ee44`
("[harness:t-05] gate merges on Build-entry receipt") — i.e. it is part of this FEATURE's own new
code (merge-gate.py did not exist before this feature), not legacy code from outside the diff. It has
been unchanged across every one of this feature's 7+ cycles, including this one. Framing: **not
pre-existing outside this feature's scope**, but also **not introduced or touched by 894adc0f
specifically** — it is inherited, unmodified, from an earlier cycle of the same feature's own build.

**Disposition: unchanged from c6, med, non-gating.** The failure direction is safe (deny, not
allow) — no security regression. T-05's own spec (plan.yaml step 3) contemplates the `gh` ROUTE
failing (absent/unauthenticated/unreachable) and falling back to local `git`, but never contemplates
`git` itself being unresolvable — a materially more broken host (nothing else in the hook chain would
function either) than the spec's stated failure modes. A `high` bar requires "wrong behaviour in a
realistic case"; an environment missing `git` on `PATH` while still invoking Bash-gated hooks is not
realistic enough to gate this ship, and the merge is still correctly refused. Advisory.

### c6 finding (b) — duplicated DEC-138 f-string, inaccurate at the second site

**Re-verified.** Both call sites still present verbatim: merge-gate.py's `document is None` branch
(the "no record found" ALLOW-with-note) and the `entry in {"opened","not-applicable",
"recovered-terminal"}` branch (the "record found and compliant" ALLOW-with-note) print the identical
f-string ending "...owes no build-entry receipt; allowing it...". At the second site a matching
record WAS found and IS compliant (held, not owed) when this text fires (only reachable there when
the `gh` remote read also failed) — "owes no build-entry receipt" is inaccurate; the correct
statement would be "already records `<entry>`". Cosmetic wording only; the ALLOW decision itself is
correct in both branches.

**Pre-existence, established.** `git show 894adc0f^:.../merge-gate.py | grep -n "owes no
build-entry receipt"` returns both call sites unchanged. Same `git log -S` trace: introduced at
`4338ee44`, unchanged across all cycles including this one and this pin.

**Disposition: unchanged from c6, low, non-gating.**

## Code grade

`python3 .claude/skills/harness/bin/code-grade.py --base 6ad7233f --head 894adc0f`: exit 0, 50 PASS.
Four `RESULT: FAIL` / `GRADE: 2` records, each with a `REASON REQUIRED:` line and each already
carrying an in-source `GRADE-2 REASON:` comment (verified all four are new-in-this-diff via
`git diff <base>..894adc0f`, not inherited debt):
- `merge-gate.py:main` (cyclomatic 17, cognitive 21, ABC 38.7) — "this is the gate's orchestration
  boundary; helpers own parsing, resolution and rendering, while this function preserves the
  policy's ordered exits." Reasoned, accepted.
- `tests/integration/test-check-state.py:case_t06_build_entry_invariant` (ABC 45.0) — "the test
  intentionally drives each independent invariant state through the external checker; splitting it
  would hide the fixture-to-checker contract." Reasoned, accepted.
- `tests/integration/test-hooks-install.py:_run_merge_and_check` (ABC-driven) — "This SC-14 fixture
  deliberately keeps the setup, commit, linked-worktree, real-merge, hook-observation, and retention
  assertions in one routine. Splitting those steps would hide the shared clone/worktree state that
  the end-to-end contract must prove." Reasoned, accepted.
- `tests/integration/test-post-merge-sweep.py:case_t07_build_entry_receipt` (ABC-driven) — "the
  table-driven test keeps all eight retention states in one visible matrix, so the era pair and
  no-mirror contrast cannot drift apart." Reasoned, accepted.

No grade-1 and no below-bar non-grade-2 function in range → `code_grade: grade_2`, matching the
mechanical result exactly (not my own reading of it).

## Findings

1. **[med, inherited from feature cycle 1 (4338ee44), unmodified by 894adc0f]**
   `merge-gate.py:69-72,132,155-156` — an unresolvable `git`/`gh` binary raises before `feat_dir` is
   set, producing a DENY naming literally "this feature", no path, no re-run command. Reproduced live
   this cycle (see above). Fails closed (no bypass); unactionable message only. Non-gating.
2. **[low, inherited from feature cycle 1 (4338ee44), unmodified by 894adc0f]**
   `merge-gate.py:136-137,145-146` — the DEC-138 stderr message is duplicated verbatim; at the second
   site "owes no build-entry receipt" misdescribes a record that is actually held/compliant.
   Cosmetic. Non-gating.
3. **[info, new at this pin]** `check-state.sh:1993-1996` (INV-37) — re-parses `harness.json`
   independently of the file's own already-validated `cj`/`cfg` (set at :995-1002, which already
   flags invalid JSON as a `bad` finding). Currently harmless — no live coverage gap — but is
   duplicated parsing that could silently drift from the primary parse in a future edit. Non-gating.

## Not re-litigated

Cycle-5 sentinel removal (Contract item 1): no executed scenario found showing harm the signed trade
does not already cover — the new negative-control tests in `test-merge-gate.py` (verified running,
19/19 pass) demonstrate the intended symmetry (a healthy same-branch record still wins over an
earlier malformed hit in the same glob scan; an unrelated malformed record never blocks a no-record
branch). Not re-opened.

## DIGEST-relevant summary

Stage 1: PASS. Stage 2: two advisory findings carried forward from c6 and independently reproduced/
re-derived at this pin (both inherited from this feature's own first cycle, neither touched by
894adc0f), one new info-level nit. `code_grade: grade_2` (mechanical, matches tool output exactly).
No must_fix. `severity_max: med`.
