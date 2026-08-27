# STATE

## Current

- feature: FEAT-37-lead-stop-and-wake
- run: eng segment, T-04 in flight with harness-eng-lead (slug t04-eng)
- squad: eng
- status: Building — cycles 1/10, runs 9/20

**T-01 IS DONE AND COMMITTED at `79c2a46`.** Verify re-run independently by the orchestrator, not
taken on report: `selfcheck=0 playbook=1 coverage=1 checkkinds=0` then `T01_PASS`. One send-back
inside the run, so cycles is 1, not 0.

**THE EXPECTED-FAIL SET, RECORDED SO A NEW FAILURE IS NOT ABSORBED INTO IT (answers t01-eng Q2).**
`run-unit-tests.sh --kind unit` exits 1 and MUST stay red until T-02, T-05 and T-06 all land. The
red is exactly and only `test-lead-stop-and-wake.py`, and exactly these groups:
  - `--group playbook` exits 1 — turns green when **T-02** writes the lead playbook text
  - `--group coverage` exits 1 — turns green when **T-05** widens DEC-201 to the lead tier
  - `--group bound` exits 1 with FOUR named failures — `case_occurrence_DECISIONS.md_6869_1`,
    `case_occurrence_DECISIONS.md_6870_2`, and two on `inflight_registry.py_339`. The registry pair
    turns green at **T-04**, the DECISIONS.md pair at **T-06**.
`--self-check` and `--check-kinds` exit 0 TODAY and must never go red. **Any failure outside that
enumerated set is NEW and gates.** The qa segment therefore runs AFTER all five tasks, not before —
its matrix cannot be green until the last one lands.

**t01-eng Q1 IS ANSWERED BY MEASUREMENT, AND IT NAMED THE WRONG LINE.** The worry was that D-11
lists three DECISIONS.md sites while the detector matches two, leaving 6872 ungraded. Measured:
`grep -nEi` for the once-only alternation matches DECISIONS.md at **6869 and 6870 only**. Line 6872
is not a separate falsified claim in the way suggested — the clause "the `PreToolUse` hook, whose
refusals have no once-only bound" is TRUE and must not be touched, and it already sits INSIDE the
sentence the 6870 occurrence is graded on. **T-06's scope is not in doubt:** its intent names the
6872 residual sentence explicitly and tells the documentor to correct it.

**BUT THE REAL GAP IS ONE PHRASE OVER, AND IT IS A DETECTOR GAP, NOT A SCOPE GAP.** DECISIONS.md:6872
reads "a second identical return **ships**"; `inflight_registry.py:339` reads "a second identical
return **will ship**". T-01's approved alternation spells only the "will ship" variant, so the
DECISIONS.md sentence is not an occurrence at all. Consequence: after T-06 corrects 6869 and 6870,
`--group bound --only DECISIONS.md` exits 0 **whether or not the documentor also fixed 6872** — so
T-06's own verify cannot see the third correction D-11 mandates. Closing this is an orchestrator
execution-time call, folded into the T-04 run because backend-dev owns that test file; it changes no
requirement, and is disclosed to the operator for overrule.

**DEPENDENCY REALITY — THE CRITICAL PATH IS BLOCKED ON THE OPERATOR.** `T-01 -> {T-02, T-04}`;
`T-02 -> T-05 -> T-06`. T-01 is done, so **T-04 is the ONLY task the squad can run.** T-02 is
main-session-direct, and T-05 and T-06 sit behind it. When T-04 returns there is nothing further to
dispatch until the operator executes T-02.

**BUILD STARTED.** feature.json is `Building`; `gh-sync.py open` created milestone #29, parent issue
**#904**, and sub-issues **#905 (T-01), #906 (T-02), #907 (T-04), #908 (T-05), #909 (T-06)**.
`status Building` and `start-task T-01` are both written. T-01 is `building` in plan.yaml.

**ONE STALE ANCHOR ALREADY CONFIRMED.** T-01's intent calls `UNIT_SCRIPTS` line 17 of
`run-unit-tests.sh`; it is **line 30** at HEAD. Every other number in the plan is orientation only
and must be re-derived — `origin/main` carrying FEAT-42 was merged after the 8fc87f8 measurement.
Two anchors DO still hold at HEAD: `.claude/skills/harness-team/SKILL.md` is 240 lines and
`.harness/harness/docs/DECISIONS.md` is 7276.

**AFTER THE STRIKE, EXACTLY ONE TASK IS main-session-direct: T-02.** The plan's `lanes:` block lists
two NOBODY surfaces, but the second (`.claude/skills/harness/SKILL.md`) was T-03's and T-03 is
struck. Re-measured at HEAD: `check-domain.sh --resolve` returns NOBODY for
`.claude/skills/harness-team/SKILL.md` only; T-01/T-04 resolve to backend-dev and T-05/T-06 to
documentor.

**PLAN AND BRIEF ARE APPROVED, 2026-08-27, by the operator. FIVE tasks: T-01, T-02, T-04, T-05,
T-06. Runs 8 of 20, cycles 0/10.**

**ONE TASK WAS STRUCK AT SIGNATURE, with REQ-08 and SC-09.** It would have restored the
orchestrator tier's own never-wait rule, which `c5e59aa` deleted one tier up. The operator ruled the
lead-tier rule ships sooner without it. **The strike record is `plan.yaml` D-12** — that is the
authority, and the struck id is named there rather than here, because a live STATE.md may not cite a
task its plan no longer holds. The knock-on is applied: T-01 dropped its `orchestrator` group and
that group's line from its verify block. Task numbering is NOT compacted, so every citation to T-04
and later still resolves. The regression is real and returns to the backlog.

**THE FALSE ATTRIBUTION IS CORRECTED.** `plan.yaml` D-12 and `BRIEF.md`'s scope section claimed the
REQ-08 restore was the operator's own scope call. It was not — the operator delegated that call at
re-plan and the orchestrator took it, then labelled its own choice as the operator's. Both documents
now record that plainly, and the operator ruled on it for the first time at this signature.

**`origin/main` WAS MERGED IN BEFORE THE SIGNATURE, and that was not routine.** The worktree sat
**20 commits behind** — FEAT-42 had landed. Signing against a stale tree is exactly what forced the
first withdrawal. Merge was clean, and every anchor was re-measured on the merged tree: the refusal
sentence T-04 rewrites survives verbatim, DEC-174 amendment 4's write grant is at `DECISIONS.md:5011`,
`DECISIONS.md` holds 201 level-two `DEC-` headings against 28 level-three, and the never-wait
paragraph is still absent from the orchestrator playbook.

**TWO PARAGRAPHS WENT FALSE WHEN FEAT-42 LANDED; ONE IS FIXED HERE.** T-04's intent said
`refusal_lines` cites issue 551 where 866 measures 628, held deliberately out of scope. **FEAT-42
already fixed it** — at `origin/main` that function cites 628, and `RELEASE_ALL_CMD` is retired as a
printed remedy in favour of `release_cmd`, which is absolute and single-agent. T-04's paragraph is
rewritten to say so; the instruction not to touch that function is unchanged.

**BUILD ORDER.** T-01 alone first — it is the test file every other task's `verify:` calls, and
nothing can be graded until it exists. T-02, T-04, T-05 and T-06 follow in plan order.

## Open Questions

- Q1 (was: D-02 and D-11 spell the ruling AMEND) — RESOLVED at re-plan. Both now read "corrected IN
  PLACE". The only `AMEND` strings left in `plan.yaml` are T-05's and T-06's own DO NOT ADD AN
  AMENDMENT instructions.
- Q2 (was: DEC-199 amend or STRIKE) — RESOLVED. Corrected in place. D-11 and T-06 carry the reasoning.
- Q3 (was: the #811 split ruling) — RESOLVED by operator ruling of 2026-08-24. D-07 is the strike
  record. Issue #811 stays OPEN and returns to the backlog.
- Q4: `notes/root-cause-*.md` is in no member's domain, so debug reports fall back to receipt paths.
- Q5: engineer DIGESTs carry no `files_touched`, so a member that wrote a receipt reported no files;
  the lead reconstructs it by hand. Schema gap or intended?
- Q6 (the #866 deadlock) — HALF CLOSED BY FEAT-42, and the note that said otherwise is now corrected.
  The dispatch end is fixed: `release_cmd` prints an absolute single-agent command, so a refusal no
  longer tells an agent to wipe every feature's live claims. The RETURN end is what T-04 still
  corrects. This feature does not close #866 and never claimed to.
- Q7: single-flight is keyed per checkout, so several orchestrators' children can share one registry
  when they run from one cwd.
