# Goal-check (plan exit) — FEAT-2423-retire-state-md

**Verdict: FAIL, narrowly.** The plan delivers the operator's stated intent (grilling
`.harness/notes/grilling-retire-state-md-2026-11-28.md`) on every substantive axis. It still breaks one of the
orchestrator's goal constraints: T-01 leaves INV-5 named in live prose in files it already owns, and no verify
catches it. The fix is one T-01 amend (below). Two operator-level partials are signature rulings, not plan defects.

Evidence base: plan.yaml and BRIEF.md in this feature dir (pending approval). Inventory: `git grep` at base
`3c49011652cc396e7717e799c49173ed8f452edb` over every tracked path outside `.harness/*/features/**`,
`.harness/logs/**` and `council/**`. `plan-merge.py check --root <main checkout>` gives 7 tasks, 77 anchors and
0 failures.

## Does the plan deliver the stated intent?

Yes, with the exceptions graded below. The grilling's Settled items all land:

- Full retirement: T-01 to T-04 and T-07.
- The orchestrator's read and write switch to plan.yaml, feature.json and the latest digest: T-03 SKILL.md steps 1, 4 and 6, plus succession.md.
- Open questions stay in the run digest and answers notes, with no new field: D-01.
- All tracked copies are deleted: T-06 and T-07.
- DEC-45 is struck, and DEC-129 and DEC-150 are rewritten in place: T-05.

Both "Not yet specified" items are resolved. FEAT-2643 timing goes to Q-01 with a recommendation. The state-tagged
DECs each get a decisions_affected row: DEC-131, DEC-171, DEC-191 and DEC-193 are keep; DEC-159 is amend; DEC-180
is amend plus keep.

The base-tree live-mention census found 39 files naming the file outside feature directories. Each falls in one
of three groups:

- 35 sit in a task's `files:`.
- BUILD.md and the two `prior-*` fixtures are declared byte-identical history.
- The two Expertise files are Q-04.

The BUG-2423 housekeeping item is already satisfied on disk:

- `git worktree list` shows no BUG-2423 worktree.
- No `BUG-2423-state-md-derived` feature dir exists on main.

## Perspectives (`## Done when — by perspective`)

| Perspective | Grade | Carried by |
|---|---|---|
| operator | **partial** | SC-01, SC-10 (SC-02 supports); T-03, T-04, T-06, T-07. All 40 tracked copies and the template are deleted, and SPEC, README and org.html are rewritten. Two items stay open. (1) `.harness/harness/expertise/harness-validator-lead.md` G-01 still tells a validator to "check `STATE.md` against `feature.json`" as "the live human pointer a resuming context reads". DEC-145/253 rightly bar a build task from editing it, but no SC or task guarantees the Q-04 distillation `drop` lands, so "nothing on main still tells anyone" rests on a recommendation. (2) The grilling's Destination says no decision or existing feature directory *mentions* the file. The plan keeps dated mentions in DEC-121, DEC-160, DEC-173 and DEC-180, plus shipped runs, notes and plan.yaml (BRIEF Constraints, "Stays byte-identical"). That is defensible under DEC-205, but it narrows the literal intent, so the operator should acknowledge it at signature. The kaya copy, which the grilling's Out of scope arguably covers, defaults to deletion and is correctly put to the operator as Q-03, with a pre-specified amend path in T-07. |
| orchestrator | **pass** | SC-02; T-03. Step 1 reads `plan.yaml` status and approval.status, `feature.json` runs (the open run is the PENDING entry) and the latest accepted digest's open_questions, and it handles the no-accepted-digest case explicitly. Step 4 re-reads at wake, and the digest is read only after verification. Step 6 drops the status-file write. succession.md's disk-only path names the same records. Base `ctx.states` is consumed only by inv_2 and inv_5 (`git grep '\.states\b'`), so removing it orphans nothing. |
| code maintainer | **partial** | SC-03 to SC-08; T-01, T-02, T-03 and T-07. INV-2 and INV-5 go into `table.py#RETIRED` with DEC reasons, and INV-23 is narrowed (SC-04). Stray-file inertness is covered for check-state (SC-05) and check-domain (SC-06). Every catalogue row, the `structure_audit.py#ROW_FAMILIES` entries and the structure-lock mutants are covered. **Gap:** three references stay "dangling" in live prose, contrary to this perspective's wording. They are in `check_state/plan.py` (module docstring `INV-35/3/4/5/34/32/44` and the `_inv32_shape` comment `INV-3/4/5 check approval.status only`) and in the `tests/integration/test-check-state-plans.py` docstrings (file header `INV-3/4/5` twice, case (q) `INV-3/4/5`). T-01's intent names only the INV-3/4/5 *note*, the parse-guard message and ctx.py's load message. Its verify greps only the file name. |
| reader | **pass** | SC-09; T-05. Every amend and strike row has a concrete replacement text. The DEC-45 heading `## DEC-45 — STRUCK 2026-11-28` matches the existing DEC-90 and DEC-207 convention, and its body names DEC-188 and its successor. DEC-129 and DEC-150 are barred from Amended-by text in the verify. The index regenerates and diffs clean, with hand-written tails of 30 words or fewer (DECISIONS-INDEX G-13 handled). |

## Orchestrator's added goal constraints

| Constraint | Grade | Evidence |
|---|---|---|
| No new feature.json field and no replacement status file | **pass** | D-01 and the BRIEF Out of scope. The only feature_record edit is the `_REDIRECT` sentence text (T-03). No task adds a key or a file. DEC-191 is a keep row that supplies the rule. |
| check-state and check-domain green over features with and without the file | **pass** | Coverage by case: <br>• With the file: SC-05 and SC-06 show identical exit and stdout with and without a 200-line, illegal-section, dangling-T-99 copy, plus PreToolUse and PostToolUse exit 0. <br>• Without the file: SC-07 and SC-08 cover the suites, and the SC-06 controls still deny. <br>• No surviving check reads the file: ctx.states has no consumer after T-01. <br>FEAT-2641, FEAT-2688 and BUG-2524, which keep copies in flight, therefore stay green (Q-02). |
| No orphan INV ids or rule-table rows | **partial** | The rows are clean (SC-04). The live prose orphans of INV-5 listed under "code maintainer" are unaddressed, and so would survive the build unless the executor happens to fix them. DEC-182's `check-state.py (INV-3/4/5)` and "verified: INV-3/4/5 report 0 findings … today" are dated narrative and acceptable, but they have no decisions_affected keep row. |
| No live text telling anyone to write or read STATE.md | **partial** | SC-03 covers `.claude/skills`, `.omp` and team-config, and its T-07 verify greps at the terminal task. SC-10 covers SPEC, README and org.html, and SC-09 covers DECISIONS. The residual is validator-lead G-01 and code-reviewer G-05, left to distillation (Q-04). No gate covers `.harness/harness/expertise/`. |
| Every task main-session-direct | **pass** | T-01 to T-07 are all `execution_mode: main-session-direct` with `execution_reason` and no `execution_agent` (parsed plan.yaml). The lanes are all main-session-direct. |
| DEC-45 struck with strike record; DEC-129 and DEC-150 rewritten in place | **pass** | T-05 intent and verify: the `^## DEC-45 — STRUCK 2026-` grep, the no-Amended-by check on DEC-129 and DEC-150, the STATE-token check over 11 amended DECs, and the index diff. SC-09 is graded at `git show <review_sha>`. |

## Remediation (one amend, T-01)

Make two changes to T-01:

1. Add these bullets to T-01's intent:
   - check_state/plan.py module docstring becomes `INV-35/3/4/34/32/44`.
   - The `_inv32_shape` comment becomes "INV-3/4 check `approval.status` only".
   - The tests/integration/test-check-state-plans.py docstrings (file header and case (q)) say INV-3/4.
2. Add a verify line:
   `rc=0; git grep -n -I -E 'INV-(2|5)([^0-9]|$)|INV-[0-9/]*/5([^0-9]|$)|INV-1\.\.5' -- .claude/skills/harness/bin tests ':(exclude)tests/integration/fixtures/prior-*' ':(exclude)tests/integration/test-check-state-table.py' || rc=$?; test "$rc" -eq 1`.
   test-check-state-table.py is excluded because it legitimately asserts the retired INV-2 and INV-5 lines. Before signature, check that the pattern does not catch a surviving INV-23 or INV-25 line. `([^0-9]|$)` already excludes them.

## Open at signature

These are the operator's calls, not pm defects:

- **Q-04:** accept that validator-lead G-01 stays live until this feature's distillation, or require that distillation as a ship gate.
- **Destination wording:** acknowledge that historical records (DEC-121, DEC-160, DEC-173, the DEC-180 narrative, and shipped runs, notes and plans) keep mentioning the file.
- **Q-03 kaya default.**
- **Q-01 and Q-02:** as in the BRIEF.

## Principles applied

- **Outcome-Oriented Execution** was not read this run, so it is not cited. Grading used pm Expertise P-04 (per-item assertion: the per-file census rather than a pass on a file-global grep) and P-16 (affirmative prose: the plan.py docstring and comments left out of T-01's intent).

## Remediation applied — 2026-11-28 (apply-r1, GC-01)

GC-01 is closed by amending T-01 only (`plan-merge.py apply`, `REPLACED T-01.files/verify/intent`, then
`REPLACED T-01.verify/intent` to fit the 50-line machine-field budget). Neither run printed an `APPROVAL-RESET:`
line: the plan was pending. No `gh-sync.py` call was made. `panel:` and `approval:` are untouched.

**Wider than GC-01 listed.** A census at base `3c490116` (`git grep` over `.claude/skills/harness/bin` and
`tests`, excluding `fixtures/prior-*` and `test-check-state-table.py`) finds 25 live INV-2/INV-5 mentions in
9 files. They are bare, in slash lists, or in ranges. T-01's intent now names each site that its existing
bullets did not already cover:

- `check_state/plan.py`:
  - The module docstring `INV-35/3/4/5/34/32/44`.
  - The section comment `INV-3/4/5 on plan.yaml … Same three invariants`.
  - The f-string `INV-4/5 would be vacuous`.
  - The `_inv5_plan_yaml` pointer `see the INV-3/4/5 note above`.
  - The `inv_5` docstring.
  - The `_inv32_shape` comment `INV-3/4/5 check approval.status only`.
- `check_state/feature_record.py`: the `inv_2` docstring, and the target module-docstring list
  `INV-1/6/7/8/12/18/22/23/33`.
- `check_state/brief.py` is **new to T-01**. It holds `INV-1/2's reason` ×3 and `INV-1/2 (the ## Approval block)` ×2,
  spread across the duplicated INV-38 block and the INV-49 comment. Its anchor is
  `{path: …/check_state/brief.py, quote: "is skipped for INV-1/2's reason"}`.
- `tests/integration/test-check-state-plans.py`: two mentions in the file-header docstring, the `case_q` docstring,
  and the `# INV-5 across the yaml path` comment.
- Already covered: `ctx.py` `INV-3/4/5 cannot be checked`; `harness_yaml.py` `INV-5's membership test`;
  the `structure_audit.py` ROW_FAMILIES entries; the `table.py` rows; and the `"INV-2 "` assertions in
  `test-checker-structure-locks.py`.

**New verify conjunct.** It is merged into T-01's final python block. The block runs a `git grep` for bare,
slash-list and range forms. It returns exit 2 on any git grep exit other than 0 or 1. Exit 1, meaning no hits,
is also red, because the two new `table.py` RETIRED entries (`"INV-2": "DEC-129 …`, `"INV-5": "DEC-129 …`) are
the required positive control. Any other hit is red. Measured at base, the block exits 1 and lists 25 live
mentions. The green path was not executed: bash-write-guard refuses fixture paths under `.claude/skills/...`,
even in a temp repo. The classifier regexes were exercised on synthetic lines instead: INV-23/25/52, INV-6..8,
INV-38..41, INV-3/4 and INV-35/3/4/34/32/44 do not match, while INV-1..5, INV-3/4/5 and INV-1/2/6 do.
[INFERENCE] the block goes green once T-01 lands as specified.

**Re-graded:**

| Item | Was | Now | Why |
|---|---|---|---|
| code maintainer perspective | partial | **pass** | T-01 now names every live INV-2/INV-5 site under bin and tests, and its verify fails on any survivor (PRIOR exemptions are named). |
| No orphan INV ids or rule-table rows | partial | **pass** for bin and tests | The rows are clean (SC-04). Prose orphans under `.claude/skills/harness/bin` and `tests` are now gated. Residual: DEC-182's dated `INV-3/4/5` narrative in DECISIONS.md is history and is not gated. It still has no decisions_affected keep row (unchanged, non-blocking). |

`plan-merge.py check`:

- `--root <worktree>`: 7 tasks, 38 anchors resolved, 40 failures. All 40 are the sparse-checkout STATE.md
  anchors in T-06 and T-07 (Q-05), and there is no budget VIOLATION.
- `--root /Users/molchairuangutai/GitHub/harness`: 7 tasks, 78 anchors resolved, 0 failures.

## Re-grade after c1 rulings (run 2026-11-28-02-plan-product)

**Verdict: PASS.** The plan delivers the operator's stated intent (the grilling `## Destination` and `## Settled`) as
narrowed by `notes/answers-2026-11-28-plan-c1.md`. All four perspectives pass. Every narrowing still standing is one
the operator ruled, and no unruled narrowing was found.

**Evidence base.** plan.yaml and BRIEF.md (approval `pending`). A fresh census at main `260742cd` (the earlier
grades were at `3c490116`) ran `git grep -l -I -E 'STATE\.md|STATE_MD|state_md' HEAD` outside `.harness/*/features/**`,
`.harness/logs/**` and `council/**`. It found 39 live files:

- 36 are in a task's `files:`.
- `BUILD.md` is history (GC-03).
- The two Expertise files are SC-11 (Q-04).

`git ls-tree` at HEAD lists 40 tracked `features/*/STATE.md`. The `files:` of T-06 (19) and T-07 (21, including
kaya) match that set exactly in both directions. The live in-flight branches that add a copy are FEAT-2641,
FEAT-2688 and BUG-2524, all three under Q-02. FEAT-2643's branch adds none. The other branches that carry copies
are stale pre-deletion branches, not in-flight features.

`git grep 'org\.html'` outside feature records and logs prints nothing, so T-04 deletes no live link target.
`plan-merge.py check --root <main checkout>` gives 7 tasks, 80 anchors and 0 failures.

| Perspective | Grade | Carried by |
|---|---|---|
| operator | **pass** | SC-01 (T-03 deletes the template; T-06 and T-07 delete all 40 tracked copies, the kaya one under Q-03), SC-10 (T-04 rewrites SPEC and README and deletes org.html by operator direction), SC-11 (Expertise G-01 and G-05 are dropped at distillation as a ship condition, under Q-04, so a task is deliberately not the carrier), and SC-02 in support (T-03 points open questions at the latest accepted run digest, D-01). "Nothing on main still tells anyone": every live mention in the census is owned. Historical mentions stay under GC-03 (DEC-205). Run-01's two partials are closed by ruling, not by a plan change. |
| orchestrator | **pass** | SC-02; T-03. Unchanged from run 01: step 1 reads the plan.yaml station and approval, the feature.json runs (the PENDING entry) and the latest accepted digest's open_questions using D-01's verbatim definition. Step 4 re-reads at wake, step 6 drops the status-file write, and succession.md's disk-only path names the same records. T-04 SPEC §10.1 and T-05 DEC-129 carry the same definition. |
| code maintainer | **pass** | SC-03 to SC-08; T-01, T-02, T-03 and T-07. The retired numbers go to `RETIRED` (SC-04, T-01), and the live INV-2/INV-5 prose is gated (T-01 verify, run-01 remediation). Under Q-06, T-02 now removes the name from both `prior-*` fixtures, and T-07's terminal verify greps all of `tests/` for the name and for a quoted bare `STATE` with no exclusion. Neither stray-file test remains in the plan. One narrowing is ruled: "behave the same with a stray copy" is now proven only by deleting the rules (SC-05, inspection). The generic INV-7/15/37/46 reads are not shown to ignore a stray copy. BRIEF `## Verification gaps` declares this as the direct consequence of Q-06, so it is a ruled narrowing, not a gap. |
| reader | **pass** | SC-09; T-05. Unchanged: each amend and strike row in `decisions_affected` (DEC-45 strike; DEC-71, 95, 120, 129, 138, 150, 159, 180, 181, 182, 199, 201 amends) has replacement text in T-05's intent. The verify checks the DEC-45 STRUCK heading, the absence of Amended-by in DEC-129 and DEC-150, the D-01 definition in DEC-129, an index tail of 30 words or fewer, and a clean index diff. |

**Advisory (not a gap, no question):** T-07's verify fails closed if a merge adds a tracked copy before this feature
builds. That is the right behaviour under Q-02, but the executor must then `git rm` the copy rather than read the
failure as a T-07 defect.

## Principles applied (re-grade)

- No craft leaf was read this run, so none is cited. Grading used pm Expertise P-03: the ownership census is
  re-based on the tree at HEAD, not on the plan's own `files:` lists. It also used P-04: each tracked copy is
  matched one by one against T-06 and T-07, not by count.
