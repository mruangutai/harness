# Goal-check — delivery — BUG-1309-mirror-build-entry

**Verdict: 7 met, 2 partial, 1 not met.** The feature's mechanism is delivered and measured. Two
criteria (SC-03, SC-07) are partial on **one procedural clause each** — the required red-state
demonstration — for which there is **no record**, because both owning tasks are
`execution_mode: main-session-direct` and DEC-174's carve-out writes no receipt. **That clause
cannot be met as written and is a RE-PLAN for the operator, not a retry.** SC-10 is not met because
the operator has not run the UAT yet; the script is written and proven executable.

Graded at `review_sha d80a7b12404f882f638d0cd714a5f372e38af926`, read via `git archive <sha>`
into `/tmp/bug1309-pin` and `git show <sha>:<path>` — never a plain worktree read. Branch tip
`23f0b9d8`; the pin→tip diff touches only this feature's `feature.json`, no code.

## The ten criteria

| SC | Declared | Evidence obtained at the pin | Verdict |
|---|---|---|---|
| SC-01 build-entry outcome per state | automated / integration | `test-gh-sync.py`: `T-02 open records opened`, `T-02 sync false records not-applicable`, `T-02 unpinned repo records nothing` (asserts `"build_entry" not in ghT2c` — **key absence**, `:3430-3432`), `T-02 first-call failure records recovery-required`, `T-02 second open stays opened` (`opened` **and** no new create call). Suite exit 0, 322 ok, 0 FAIL. "sync false **or absent**" is one branch, not two: `gh-sync.py:283-285` reads `cfg.get("github") or {}` then `if not g.get("sync")` — absent and false converge on that falsy test, so the one case discharges both | **met** |
| SC-02 partial write / caller error record nothing | automated / integration | `T-02 partial remote write records nothing` (`:3450-3453`) asserts **key absent** *and* `milestone == 7`, i.e. a remote object was genuinely created first; `T-02 contract error records nothing` (`:3492-3494`) asserts `rc == 1` and key absent. Both `ok` | **met** |
| SC-03 Build refuses, station picks the command, era-exempt continues | automated / integration | Behaviour clauses all `ok`: `T-04 non-era absent refuses` (`rc==2` + `gh-sync.py open`), `T-04 BUG-named non-era absent refuses`, `T-04 station discriminator` (`rc==2` + `recover-terminal` + no `open` token), `T-04 era-exempt continues` (`rc==0` + `predates`). **The red-state clause has no record** — see below. Secondary: the *non-era* `recovery-required` proceed branch (`gh-sync.py:1387-1389`) is asserted by nothing; I observed it directly (no `SystemExit`, its own distinct message) | **partially met** |
| SC-04 merge deny / allow matrix | automated / integration | `test-merge-gate.py` 16/16 `ok`, exit 0. Deny: `T-05 recovery-required denies`, `T-05 non-era absent build_entry denies`, `T-05 unpinned repo … naming the configuration fix`. Reason names the feature, the recorded value and the exact remedy (`merge-gate.py:151`). Allow ×3: `T-05 opened/not-applicable/recovered-terminal allows` (`rc==0`, `d is None`). Era-exempt: `T-05 era-exempt absent build_entry allows` + `T-05 era-exempt recovery-required allows` (`rc==0`, no decision; `merge-gate.py:138-140` returns before any entry check). `gh` unavailable: `T-05 gh outage with no matching feature allows` (`could not verify` on stderr) beside `T-05 gh outage with a feature owing a receipt denies` | **met** |
| SC-05 recovery creates zero task sub-issues | automated / integration | `T-03 recover-terminal creates milestone and parent only` asserts `issues == {}` (**exact map**) and `len([l for l in log if "issue create" in l]) == 1` (**exact count**); `T-03 FEAT-55 shape adopts and creates nothing` asserts `issues == _FEAT55_ISSUES` and `len(create_calls(...)) == 0`. No substring search anywhere. Both `ok` | **met** |
| SC-06 sweep retention keys on the recorded value | automated / integration | `test-post-merge-sweep.py` exit 0, 61 PASS, 0 FAIL. Both named cases present **verbatim**: `T-07 era-exempt recovery-required keeps the worktree` and `T-07 era-exempt absent build_entry is swept`. Retention keys on the value, never era: `post-merge-sweep.sh:222-232` tests `entry is None and feature_id in ERA_EXEMPT` first, then `elif entry not in {opened, not-applicable, recovered-terminal}` — so era + `recovery-required` falls to the retain arm. Announcement text exists at `:224` (predates) and `:229-232` (names `github.build_entry=<value>`) | **met** (see advisory A2) |
| SC-07 INV-37 on the FEAT-55 shape | automated / integration | `test-check-state.py` exit 0, 225 ok, 0 FAIL. `T-06 INV-37 fires at a done station with no task statuses` — fixture is `station="done"`, `task_status=None` (no `status` key at all: `:4644-4645`), sync true, repo pinned; asserts the line names the feature **and** `recover-terminal`, plus `T-06 INV-37 message discriminator names recover-terminal only`. Silent once recorded: `T-06 INV-37 silent on build_entry opened` / `recovered-terminal`, same fixture. **The red-state clause has no record** — see below | **partially met** |
| SC-08 schema declares the closed value set | automated / integration | `test-validate-feature-json.py` exit 0. `accepted_github_build_entry_{opened,recovery-required,not-applicable,recovered-terminal}` PASS; `rejected_github_build_entry_illegal_value_'opened '` and `_'reopened'` PASS asserting the message contains `is not one of` **and** `recovered-terminal` (the enum, not a bare non-empty check); `rejected_github_build_entry_hyphen_misspelling` PASS asserting `'build-entry'` is named plus the redirect sentence | **met** |
| SC-09 the two docs name Build entry | inspection | Exactly the two reads the criterion specifies. `git show <sha>:.claude/skills/harness/references/github-mirror.md` — `:41` "Build entry — immediately after the plan's signed approval, before the first task starts \| **orchestrator** \| `gh-sync.py open`"; `:51-54` defines the four values and states "Ship is post-merge terminal finalization only". `git show <sha>:.claude/skills/harness/SKILL.md` — `:141-144`, **build-phase segment 1 of five**, "**Build entry.** Immediately after signed approval and before dispatching any task, run `gh-sync.py open <feature-dir>`". Grepped both at the sha for `mission ship` / `mirror.*at ship` / `right after the approval`: **zero hits**, so the originating `ab4d2fdc` framing is gone, not left beside | **met** |
| SC-10 operator sees an actionable refusal, `open` clears it | uat | UAT authored at `notes/uat-BUG-1309-mirror-build-entry.md` and proven executable end to end by me against the pinned scripts on a throwaway `/tmp` root. **It stays not met until the operator executes it.** Recording it met would be a false record | **not met** |

## The two partials — one clause, one cause, one owner

SC-03: *"The refusing assertion must be demonstrated failing against the pre-change copy of the
script before the fix is accepted."*
SC-07: *"The violating fixture must be shown passing `check-state.sh` before the invariant lands."*

Both are claims about **ordering of conduct**, and both declare `verify: automated`. No test can
observe that a demonstration happened *before* a fix — a green suite proves presence and passing,
never order. The record confirms it was not captured:

- `notes/qa-matrix-gate-BUG-1309.md:131-135` — "**T-04, T-05, T-06, T-07, T-08: could not
  establish.** These are `execution_mode: main-session-direct` (DEC-174 enforcement carve-out); the
  main session does not write receipts, and I found no observations-log entry … establishing
  red-before-green for these five tasks specifically. All of their named `verify:` cases pass at
  HEAD, which proves presence and passing, not ordering. **I am not upgrading this silence into
  compliance.**"
- `notes/qa-matrix-gate-BUG-1309-rerun.md:182-188` — the set is restated as still open and
  **structural**, not a defect a re-run can close.
- The cycle-1 panel's two executed reconstructions (`notes/review-harness-security-reviewer-c1.md:6-11`,
  `notes/review-harness-code-reviewer-c1.md:15`) close the `gh_head` fail-open and the era branch.
  Neither is a red-before-green record for T-04 or T-06. I checked; it is not hiding there.

**What would close them.** Nothing a squad can do. Either (a) the operator amends the clause —
e.g. "the shipped assertion is discriminating" (checkable) instead of "was demonstrated failing"
(conduct) — or (b) the operator accepts the clause unmet on the record. Manufacturing the
demonstration now and calling it prior evidence would falsify the record. **Fault: COVERAGE, and
specifically the record; not code.** The mechanism both criteria exist to protect is delivered and
measured, and the assertions are discriminating in shape (SC-03's refusal asserts `rc==2` *and* the
command token; SC-07's asserts INV-37 names the feature *and* `recover-terminal` *and* excludes
`open`).

**This is the same structural hole in two places, and the honest fix is upstream:** a criterion may
not declare `verify: automated` over an ordering claim on a `main-session-direct` task, because
that combination is unobservable by construction.

## Advisories — not criteria, not gating

- **A1 (coverage, SC-03).** `gh-sync.py:1387-1389`, the *non-era* `recovery-required` "Build
  proceeds, the MERGE is refused until …" branch, is defended by no case. Both existing cases
  (`T-04 era recovery-required does not claim a refusal`, unit `BE-23`) exercise the **era** branch
  at `:1381-1385`. I confirmed the non-era branch works by direct in-process observation. A future
  edit to that message or to that arm reddens nothing. Ship backlog, one case.
- **A2 (coverage, SC-06).** The two named cases assert `returncode == 0` and worktree
  presence/absence only (`test-post-merge-sweep.py:938-940`); neither asserts the announcement text
  the criterion describes. The text exists at the sha and is on exactly those two branches, and
  `test-hooks-install.py:427-430` pins the negative discriminator, so the clause is **true but
  undefended**. Backlog chore, not a downgrade.
- **A3 (coverage, SC-04).** `T-05 era-exempt absent build_entry allows` asserts `d is None` but not
  `returncode == 0`; the sibling era case does assert it, and I observed `rc=0` directly. Cosmetic.
- **A4 (hygiene).** The worktree carries one uncommitted edit — a `GRADE-2 REASON:` comment in
  `tests/integration/test-hooks-install.py:392`, the very file the cycle-1 panel noted as lacking
  one (`runs/2026-09-07-04-validator/digest.md:79-81`). It is **not in the reviewed tree**. Commit
  it or discard it before the pin is treated as the shipped state.

## Method notes

Suites re-run by me from the pinned tree with `HARNESS_AGENT_TYPE` unset: `test-gh-sync.py` 322 ok
/ 0 FAIL, `test-merge-gate.py` 16/16, `test-check-state.py` 225 ok, `test-post-merge-sweep.py` 61
PASS, `test-validate-feature-json.py`, `tests/unit/test-feature-schema-build-entry.py`,
`tests/unit/test-gh-sync-build-entry.py` — every one exit 0, and I grepped `^FAIL`/`^not ok` on each
rather than trusting the exit code alone. No gate script, test file or source file was edited; no
mutation was re-run. The three branch observations (SC-03 non-era, SC-04 era-absent exit code,
SC-04 `gh`-outage allow) were taken by invoking the shipped code unmodified.

## Open questions for the operator

- **Q1 (blocking the ship, not the build).** SC-03's and SC-07's red-state clauses: amend to a
  checkable property, or accept unmet? Nothing downstream can close them.
- **Q2 (not blocking).** Should the SC-authoring rule forbid `verify: automated` on an ordering
  claim whose owning task is `main-session-direct`? This feature hit it twice.
