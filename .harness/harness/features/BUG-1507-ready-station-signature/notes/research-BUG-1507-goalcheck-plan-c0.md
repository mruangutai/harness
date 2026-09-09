# Goal-check — BUG-1507 plan against the operator's stated intent (cycle 0)

**Does this plan deliver the operator's stated intent? NO — not as drafted. Three of the five
Definition-of-Done bullets are fully discharged; DoD bullet 1's actual observable (a card visibly at
Ready) is asserted by no criterion, and DoD bullet 2 (Ready means signed, and nothing else puts a
card there) has no REQ, no SC and no disclosure anywhere in the BRIEF — while being measurably false
for task cards today.** Both gaps are repairable pre-signature by editing `BRIEF.md` (one SC plus one
`## Constraints` disclosure). Everything else — task specification, verify discrimination, lane
resolution, REQ traceability, D-02's premise, the scope calls on T-05 and D-06 — holds up under
execution.

Graded against `notes/intent-BUG-1507.md` (the operator's words), not the BRIEF. Worktree at
`4b5dbb23`; no file was modified by this run.

## (a) Definition-of-Done coverage, bullet by bullet

| # | DoD bullet (intent-BUG-1507.md:12-24) | Discharge | Verdict |
|---|---|---|---|
| 1 | Signing moves the ticket to **Ready** automatically, no extra manual command | REQ-01 → T-01 (`harness-plan.md:24` `Ready`→`ready`); D-01 takes reading (a); SC-01 grades the run | **PARTIAL** — see F-01. SC-01 grades `plan.yaml` + one print line, never a card |
| 2 | Ready **always** means signed; nothing else puts a card there | **nothing.** No REQ, no SC, no constraint line | **NO DISCHARGE** — see F-02 |
| 3 | Build dispatch advances the **feature's own** plan record to Building | REQ-02 → T-03 (`SKILL.md` build phase, segment 1); REQ-04 → T-02 change 4; SC-04, SC-06, SC-05 | **MET as a deliverable** (F-03 threatens SC-05's execution, not the deliverable) |
| 4 | Grep `features/*/plan.yaml` and see `ready` and `building` in the history | BRIEF:119-124 declares this is SC-01 + SC-05 and nothing more, and says why a standing-corpus SC is unmeetable | **MET, narrowed honestly** — see (c) |
| 5 | No new stations, no schema change, no change to the frozen six | REQ-06 → T-04; SC-08, SC-10 (byte-level `git diff` pins) | **MET** |

## (b) The two criteria the plan cannot itself close

- **SC-01** (BRIEF:71-75) — actor and moment: the **main session**, immediately after it writes the
  signature. Written as `Graded POST-SIGNATURE, on this feature's own run`; the **actor** appears
  only in `## Verification notes and gaps` (BRIEF:125-128), not in the criterion (F-04). Executable:
  yes — the command exists, the pinned output string is real (`gh-sync.py:649`), and the ready path
  refuses unless `approval.status == "approved"` (`gh-sync.py:1327-1331`), which post-signature
  satisfies. **But it can pass while moving nothing (F-01).**
- **SC-05** (BRIEF:93-95) — actor and moment: the **orchestrator**, when the eng segment starts
  dispatching. Same split: the actor is in the notes block, not the criterion. Executable: yes
  (`plan-merge.py set-feature-station --station building`), **subject to F-03**.
- The BRIEF does record both post-signature gradings where the operator reads them (BRIEF:125-128,
  above `## Approval`). Neither is an ungradeable SC.

## (c) The DoD grep bullet — measured, not asserted

Ran over the real corpus (main checkout, not the worktree):

```
grep -h '^status:' /Users/molchairuangutai/GitHub/harness/.harness/harness/features/*/plan.yaml | sort | uniq -c
  →  69 done   4 review   2 abandoned      (75 plan.yaml files; 10 further feature dirs are pre-DEC-182 PLAN.md and have none)
```

`ready`: **0**. `building`: **0**. `plan`: **0**. The operator's bullet is therefore true today for
neither station — consistent with the BRIEF's Problem statement.

The plan's discharge is SC-01 + SC-05 (BRIEF:119-124): two moment-in-time observations on **this
feature only**, recorded under `notes/`, performed by the main session and the orchestrator
respectively. That is **achievable**. What is *not* achievable, and the BRIEF says so plainly, is the
bullet's literal "recorded in their **history**": `plan.yaml` holds only the current station, so a
finished feature's file reads `done` and the two intermediate stations leave no trace there. Going
forward the grep will find `ready`/`building` on **in-flight** features once the instructions are
merged; it will never show them for a completed one. The operator should sign knowing that.

## (d) Scope, both directions

**Under-delivery:** F-01 and F-02 (above). Nothing else the operator asked for is uncovered — the
issue's four enumerated items map to T-01 (item 1), T-02 (items 2 and 3b), T-03 (item 3a), T-04
(item 4).

**T-05 (the witness) vs "documentation/instruction only — no station enum work, no schema change, no
new decision": PASSES.** Verified on disk: `harness.json` `test_matrix.bugfix.when` carries
`{kind: integration, if: fix_confined_to_tests_and_contract_docs}`. T-01/T-02/T-05 are typed
`bugfix`, so `integration` evidence is the matrix's **own requirement** for this change, not added
scope. T-05 touches no production surface, no enum, no schema. D-03's premise is sound.

**D-06 (`harness-plan.md:11` `board-station.py <n> Plan`) vs the same line: PASSES on substance,
exceeds the enumeration.** It is one token in the same instruction file — documentation only, no
enum work, no schema. It is a live fifth instance of the same defect (orchestrator-measured exit 2),
and it sits inside the swept scope, so leaving it makes T-05 red. Correctly disclosed as strikeable
(BRIEF:63-67). See F-07 for what the strike note omits.

"No new decision" is honoured in the DECISIONS.md sense: every D-01..D-06 carries `dec: none`.

## (e) Task quality — every `verify:` executed, from the worktree root, against the unfixed tree

| T | What I ran (verbatim from `plan.yaml`) | Observed | Discriminating? |
|---|---|---|---|
| T-01 | the `re.sub`/`re.findall` one-liner over `harness-plan.md` | printed `['Plan', 'Ready']`, **exit 1** | **yes** — post-fix it becomes `['plan','ready']` → exit 0 |
| T-02 | same one-liner over `github-mirror.md` + the `set-feature-station --station building` substring | printed `['Review', 'Ready', 'Review']`, **exit 1** | **yes**, both conjuncts red today; count 3 matches the three named changes |
| T-03 | the `SKILL.md` build-phase slice test | **exit 1** | **yes**. Slice is safe: `## The build phase` occurs exactly once (`:136`) and `## Routing a lead` bounds it at `:163` |
| T-04 | the `ast.parse` + docstring-bullet one-liner, `&&` the tuple grep | **exit 1** (first conjunct). Ran the second conjunct separately: `grep -nF` matched `gh-sync.py:1347` byte-exact, **exit 0** | **yes** for the docstring conjunct; the tuple conjunct is a no-change pin and correctly green today |
| T-05 | `python3 tests/integration/test-station-argument-spelling.py` (×3, `&&`-chained) | `can't open file … No such file or directory`, **exit 2** | file absent; red for the trivial reason, and the intent's own §5 negative control is what makes it discriminating once written |

**`intent:` blocks specify the change rather than deferring judgement.** D-04 gives the
discriminating rule in one sentence — a capitalized station word is a command argument exactly when
it is the token after a tool name and that tool's first argument — and T-01 and T-02 both restate it
and carry an explicit **LEAVE list** (T-01 lines 91-96; T-02 change-by-change). I re-ran the sweep
the rule implies: 6 occurrences across 37 scope files, exactly `MIN_OCCURRENCES = 6`
(`plan.yaml:298`), in the three `EXPECTED_FILES`. The doer re-judges nothing.

## (f) Internal consistency

Clean. REQ-01..06 all traced (T-01→01; T-02→01,04; T-03→02; T-04→03,06; T-05→05); no orphan REQ, no
task citing a REQ that does not exist. `depends_on` is topological (only T-05→T-01,T-02). Every task
carries `change_type`. No `verify:` asserts anything another task removes.
`check-plan-routes.py <plan>` → **0 violations, exit 0**; three `main-session-direct` rows are the
DEC-174 carve-out and match the recorded `check-domain.sh --resolve` NOBODY results.

## (g) D-02's premise

Premise not re-litigated (`SystemExit` confirmed by the orchestrator at `gh-sync.py:522-539`).

- **(i) The conclusion follows for the operator's purposes.** The operator's bullet 3 wants the
  *feature's plan record* to advance, and T-03 delivers that through
  `plan-merge.py set-feature-station`, not through `gh-sync.py status`. The parent CARD reaches the
  Building column by derivation from task statuses (`gh_board.derive_station`, `gh_board.py:120-121`),
  so no card write belongs in `cmd_status`. Nothing the operator asked for requires touching the
  line-1347 tuple, and the issue's scope line forbids code change.
- **(ii) The docstring-only remedy does satisfy "a stated decision, not silent fallthrough"** —
  literally, that is what item 4 of the scope line asks for. T-04's intent enumerates the four facts
  the bullet must state and they match the code. See F-08 for the residue worth one sentence.

## Findings

- **F-01 · med** — SC-01 (BRIEF:71-73) grades `exit 0` + the `plan.yaml station -> ready` print +
  `status: ready`. It never observes a card. `gh-sync.py:1353-1356`: with no recorded sub-issues the
  ready branch prints `no sub-issues recorded, nothing to move` and **returns 0**. This feature's
  `feature.json` carries **no `github` key at all** at `4b5dbb23`. *Consequence:* SC-01 can be
  graded `met` with zero cards at Ready — precisely DoD bullet 1's observable. Fix: add to SC-01
  that the recorded T-NN sub-issues are observed in the Ready column (or that zero were recorded,
  stated as such).
- **F-02 · med** — DoD bullet 2 appears in no REQ, no SC and no `## Constraints` line, and half of it
  is false today: `gh_board._task_statuses` reads an absent-or-`ready` task status as `ready`
  (`gh_board.py:192-202`) and `project()` places those cards, so a reconcile
  (`board_lifecycle.py:1080-1083`) can put a **task** card at Ready with no signature. The **parent**
  is protected — `derive_station` never returns `ready` (`gh_board.py:120-124`), D-18. *Consequence:*
  the operator signs a DoD believing an exclusivity guarantee the fix does not deliver, and no gate
  would ever notice. Enforcing it is code work and out of the issue's stated scope, so the honest
  repair is a disclosure line in `## Constraints`, not a new task.
- **F-03 · med** — SC-01 and SC-05 are graded on **this feature's own run**, but the actors read the
  unpatched files: the main session runs `/harness-plan` from the control-plane checkout, whose
  `harness-plan.md:24` still says `Ready` until merge, and the orchestrator loads `SKILL.md` from the
  same place, so T-03's new instruction is invisible on this very build. Nothing in the plan records
  a compensating hand instruction. *Consequence:* both SCs go `not_met` for a reason unrelated to the
  fix. Fix: state in each SC which copy is followed (the worktree file, or `git show <review_sha>:`).
- **F-06 · med** — the T-05 strike note (BRIEF:157) lists SC-02, SC-03 and REQ-05 as the casualties.
  It omits that T-01, T-02 and T-05 are typed `bugfix`, whose matrix row demands `integration` (and
  `__bug_class__`). *Consequence:* striking T-05 leaves three `bugfix` tasks with no matrix evidence
  and the qa gate should FAIL; the strike therefore also requires retyping T-01/T-02 as `docs`. Say
  so where the operator strikes.
- **F-04 · low** — SC-01/SC-05 name the moment but not the **actor** in the criterion text; the actor
  is only in BRIEF:125-128. *Consequence:* whoever executes the criterion in isolation cannot tell
  whose job it is.
- **F-05 · low** — T-02 change 4 says "Wrap each command name in backticks", while T-02's `verify:`
  requires the contiguous literal `set-feature-station --station building`. Backticking
  `` `plan-merge.py set-feature-station` `` and leaving `--station building` outside is a
  correct-looking edit that reddens the verify. Fix: one clause — keep `--station building` inside the
  same backtick span. (T-03 is not exposed: segment 4's existing style, `SKILL.md:156`, backticks the
  whole command.)
- **F-07 · low** — the D-06 strike note (BRIEF:63-67) names SC-02/SC-03 as the casualties but not
  **T-01's own `verify:`**, which requires `len(m)==2 and all lower`; leaving `Plan` at line 11 makes
  T-01 unable to go green as written.
- **F-08 · info** — after the fix, `gh-sync.py status <dir> building` is *documented* (T-04) but
  *called by nothing*: T-03 routes the feature-station write through `plan-merge.py`. That satisfies
  the issue's item 4, but the asymmetry invites a future reader to "complete" it by adding `building`
  to the line-1347 tuple — exactly what D-02 forbids. One clause in T-04's bullet naming
  `plan-merge.py set-feature-station` as the route actually used would close it.
- **F-09 · info** — T-04 is typed `docs` while editing a `.py` file, which sidesteps `bugfix`'s
  `unit if touches_runtime_code`. Legitimate here: SC-08 pins the executable lines byte-identical at
  `review_sha`, which is a stronger control than a unit test.

## Open questions

- **Q1 (blocking, operator):** DoD bullet 2's exclusivity — accept as out of scope with a disclosure
  line, or widen (code work, contradicting the issue's scope line)? Not the planner's to decide.
- **Q2 (non-blocking):** should SC-01 assert the card position, given this feature currently records
  no sub-issues (F-01)?

## What this run did not do

No file other than this note was written. `plan.yaml`, `BRIEF.md`, `feature.json`, `STATE.md` and
everything under `.claude/` are untouched; `git status --porcelain` shows only the untracked feature
directory. Every `verify:` run was a read-only probe against the unfixed tree. No defect was repaired.
