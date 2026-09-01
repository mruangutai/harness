# FEAT-51 Claude Code lifecycle safety — signature review

**The plan is ready to sign, and one thing has to be fixed before you can physically sign it.**
Every gating panel finding is closed at source and independently verified. But `plan.yaml` cannot
acquire an `approval:` mapping by any route that exists today, so the signature has nowhere to land
and `check-state.sh` reports it as a VIOLATION. That repair is yours — it is main-session-direct
under DEC-174 — and it is about fifteen lines.

Three things need your decision. They are §1, §2 and §3. Everything else in this document is the
record behind them.

---

## How this briefing was assembled

**No report round was spawned.** I read all thirteen run digests off disk rather than paying a
squad to re-narrate files that already exist (DEC-69). They are:

```
runs/plan-product/digest.md              runs/plan-fix-c1-product/digest.md
runs/plan-fix-c2-product/digest.md       runs/plan-fix-c3-product/digest.md
runs/plan-fix-c4-product/digest.md       runs/plan-goalcheck-product/digest.md
runs/plan-panel-validator/digest.md      runs/plan-transcribe-product/digest.md
runs/plan-ruling-c6-product/digest.md    runs/plan-ruling-c7-product/digest.md
runs/plan-decnum-c8-product/digest.md    runs/plan-panel-c9-validator/digest.md
runs/plan-panelfix-c9-product/digest.md  runs/plan-panelverify-c9-validator/digest.md
```

All fourteen are plan-phase runs. There is no build phase to omit — nothing has been built.

---

## §1 — The decision you are actually making: SIGN, and accept one scope reduction

The plan is **7 requirements, 12 success criteria, 9 tasks, 17 decisions**. It gives the Claude Code
compatibility host a third answer for a parent with live children (`VERDICT: SUSPENDED`), quarantines
an orphan's writes to canonical artifacts instead of letting them land, and makes adoption an
explicit CLI act. OMP behaviour is untouched.

**REQ-04 was NARROWED, and you must accept that or refuse it.** It used to read, without
qualification, that an orphan's writes to canonical feature artifacts are quarantined instead of
landing. It now reads that they are quarantined **on the two governed write routes the harness
gates** — the `Write`/`Edit` editor route through `check-domain.sh`, and the `plan-merge.py`
mutating verbs plus `quarantine.py adopt` through `plan-sign-gate.sh` — and that a generic `Bash`
write to a canonical artifact inside the writer's own domain is **not** covered.

That is not housekeeping. It is a smaller promise than the one you were going to sign, and the
reason is §4.

## §2 — The prerequisite only you can do: `plan.yaml` cannot be signed at all

`plan.yaml` carries no `approval:` mapping and structurally cannot acquire one. Four probes, all
re-run against main's tip `0bc57c88`:

| probe | result |
|---|---|
| `apply` with a proposal carrying `approval:` onto an absent base | exit 8, refused (`plan-merge.py:468`) |
| `apply` with a proposal carrying `approval:` onto an approval-less base | exit 0, `APPLIED`, block **silently dropped** (`:536`) |
| `sign-approval` on a plan carrying no `approval:` | exit 5 (`:903`) |
| `Write` of `plan.yaml`, main session, no `agent_type` | exit 2 — `check-domain.sh` denies the editor route for **every** author |

The route that was supposed to produce the block is the one the pm skill names — instantiate from
`.agents/skills/harness/templates/plan.yaml`, which carries `approval: status: pending`. That is a
filesystem copy, outside the tool, and this plan was created by `apply` instead. Every plan created
that way since FEAT-41 has the same hole.

**Recommended repair, and it adds no capability:** make `cmd_sign_approval` INSERT the mapping when
the file carries none, instead of exiting 5. That verb is already the only writer of `approval:`,
and since #1103 it already reads its caller's real `HARNESS_AGENT_TYPE` and exits 10 for every
governed agent. Nothing that is refused today becomes allowed.

**Why I did not do it.** `plan-merge.py`'s `cmd_sign_approval` is an enforcement point by DEC-174's
category test — "the category governs, not the enumeration" — so it is executed directly by you, not
dispatched through the harness whose gates are the thing being changed. It also cannot be a task in
this plan: it must land **before** the signature, and a plan task can only run after one.

## §3 — One word, and my recommendation is to leave it

The independent verification pass returned FAIL on a single residue: `T-07`'s `title:` at
`plan.yaml:738` reads *"Close the Bash route by adding the quarantine rule to plan-sign-gate.sh and
plan-sign-gate.py"*. After D-19, no artifact of this feature may assert the boundary unqualified,
and "close the Bash route" does exactly that.

It is rated **med**. No `verify:` greps the title. All five places that actually record coverage —
D-19, REQ-04, the `## Goal`, the verification-gaps bullet and T-06's mandated claim list — are
correctly qualified, and this document names the overclaim so nobody signs unaware.

**Recommendation: accept it.** Cycles are at **9 of 10**, the budget is per-feature not per-phase,
and spending the last one on a task title would leave the build with none. If you want it fixed, say
so and raise `max_total_cycles` in the same breath.

---

## §4 — What the panel found, and why REQ-04 shrank

The adversarial panel ran twice, and both times it found the same class of defect: **a protection the
plan promised that the tree does not have.**

**Cycle 5** found the discard trio. `D-16`/`D-17`/`T-09` guarded `quarantine.py discard` while a
plain `rm -rf` of the same directory stays permitted — `bash-write-guard.sh:259` exempts
`harness-dev-ops` outright and `:784-790` notices-and-continues on the `shared` verdict D-06's own
`.harness/*/features/*/quarantine/**` glob produces. You ruled: take the conservative clean scope.
D-16, D-17, T-09 and SC-12 are gone; **D-18** records the choice and the ground.

**Cycle 9** found the same shape one level up, and it is the one that shrank REQ-04. An orphaned
`harness-pm` writing a canonical artifact with a generic shell command reaches no gate this feature
builds. I measured it rather than taking it on report — `agent_type: harness-pm`, no live claim,
`cp /tmp/evil.md <feature>/BRIEF.md`, fired at all three registered `PreToolUse` gates in the main
checkout at `0bc57c88`:

```
bash-write-guard.sh   exit 0
plan-sign-gate.sh     exit 0
check-domain.sh       exit 0
```

`bash-write-guard.sh` passes any in-domain write, and `harness-pm`'s own `team-config.yaml` domain
grants both `BRIEF.md` and `plan.yaml`. `check-domain.sh` is registered for `Write|Edit` only.
`plan-sign-gate.sh`'s new rule matches only `plan-merge.py` and `quarantine.py` basenames.

**This is issue #551's flagship occurrence.** A fourteen-task `plan.yaml` replaced by a one-task file
63 seconds later. If the orphan used `plan-merge.py`, this feature stops it. If it used `cp`, this
feature does not.

I applied your own F-1 ruling to it rather than asking again, because it is the identical class and
the ruling was explicit: admit the hole, do not broaden the feature. **D-19** records it, REQ-04 and
the Goal are qualified, a verification-gaps bullet carries the measurement, and T-06's mandated
DEC-210 entry must state it. Closing the route needs a generic write-route gate, which is a different
feature — it is `B-1` below.

**One more gating defect, found by the cycle-7 goal-check and worth naming because it is the kind
nothing else catches.** The plan numbered its own decision entry `DEC-209`, which is already taken on
main by BUG-1081. `T-06`'s `verify:` therefore ran `grep -q 'DEC-209' DECISIONS-INDEX.md` and passed
against BUG-1081's shipped row — **a gate that was green before its task ran and could never go
red.** Everything now reads `DEC-210`, and the amended verify exits 1 against the current tree.

---

## §5 — The panel record, as signed

`panel.cycle: 9`, `panel.last_run: plan-panel-c9-validator`, three readers all `ran`
(`should-not-exist`/`fable-advisor`, `scope`/`harness-code-reviewer`, `goalcheck`/`harness-pm`),
**13 findings**.

| severity | resolved | open |
|---|---|---|
| high | 4 | 0 |
| med | 4 | 1 |
| low | 2 | 2 |

**No high, critical or unrated finding is open.** The three that remain open are deliberate:

- `PF-e380f685c0697fb709ff29f65af0cf24` (med) — asks for a one-run Claude Code spike before the
  build is paid for. Nine tasks rest on the assumption that the host re-enters a parent that returned
  exit 0 from its Stop hook with a live child claim, and **SC-10 is the only instrument that tests
  it, running last.** You instructed the feature to proceed; this stays open as the honest record of
  an unobserved assumption. It is `B-4` if you would rather buy the spike first.
- `PF-2545afb576b19ad86704f5bfcb556b9e` (low) — asks to narrow SC-02's `awaiting` set-equality to a
  subset check. Narrowing a success criterion is yours, not the squad's. Left as written.
- `PF-3b34920908a79dda63342a9eef302348` (low) — T-08 hard-couples three permanent suite tests to
  DEC-210's prose, which taxes a future unrelated feature. `B-3`.

**What the panel could not tell you, in its own words:** two readers is not a wide panel; no security
or qa lens ran, and F-A is a bypass-class finding found by luck of one reader's framing. Treat the
absence of further bypass findings as unmeasured, not clean.

**The strongest single result:** the `scope` reader RAN all nine `verify:` blocks and recorded each
one RED. No gate in this plan is pre-satisfied. That proves nothing about whether they can go green
on correct work — nothing is built.

---

## §6 — The build is mostly yours to execute, not mine to dispatch

**7 of 9 tasks are `main-session-direct` under DEC-174.** They touch `validate-digest.py`,
`inflight_registry.py`, `check-domain.sh`, `plan-sign-gate.py`/`.sh`, their test files, and the two
playbooks — the enforcement layer, plus three surfaces `check-domain.sh --resolve` answers NOBODY
for. I cannot execute those, and neither can any squad. `check-plan-routes.py` exits 0 with zero
violations; its four `DEVIATION` lines on T-01, T-02, T-07 and T-10 are that carve-out, correctly
declared.

Dependency-ordered segments, each task carrying its own `verify:` in the plan:

| segment | tasks | lane | note |
|---|---|---|---|
| 1 | T-01, T-02 | main-session-direct | independent; both `depends_on: []` |
| 2 | T-03, T-07 | main-session-direct | both need T-02 |
| 3 | T-04 | team (`harness-dev-ops`) | needs T-02; the `quarantine.py` CLI |
| 4 | T-05 | main-session-direct | needs T-01, T-04; both playbooks |
| 5 | T-10 | main-session-direct | needs T-03, T-07; the fail-open coverage |
| 6 | T-06 | team (`harness-documentor`) | needs T-01..T-05 and T-07 |
| 7 | T-08 | team (`harness-dev-ops`) | needs T-06; guards the entry |

Put segment 1's riskiest task and everything independent of it together: a failure in T-01 wastes
none of T-02.

**One anchor warning for whoever builds T-01.** `validate-digest.py` (+270/-158) and
`test-validate-digest.py` (+654/-119) moved between the plan's original anchor sha `ad93d43e` and
main's tip. Every line number in T-01's `intent:` has been re-measured at `0bc57c88` and the
verification pass checked all 26. The other 19 target files are byte-identical between the two shas.

---

## §7 — Proposed backlog

**Anything not listed here dies silently. Strike rows by ID.**

| ID | nature | item |
|---|---|---|
| B-1 | enhancement | **Gate the generic Bash write route to canonical feature artifacts.** The hole D-19 admits: `cp`/`cat`/`tee`/`mv`/`sed -i`/`python3 -c` to `plan.yaml`, `BRIEF.md`, `feature.json` or `STATE.md` inside the writer's own domain passes all three PreToolUse gates. Measured, exit 0 on all three. |
| B-2 | bug | **`plan-merge.py` cannot give a plan an `approval:` mapping.** §2. Affects every plan created by `apply` since FEAT-41. If you fix it as this feature's prerequisite, strike this row. |
| B-3 | chore | T-08 couples three permanent suite tests to DEC-210's prose, so rewriting that entry reds the enforcement-layer suite through a DEC-174 lane. |
| B-4 | chore | The one-run Claude Code host spike `PF-e380f685c0697fb709ff29f65af0cf24` asks for: does the host re-enter a parent that returned exit 0 from its Stop hook with a live child claim? |
| B-5 | bug | **`harness-code-reviewer` cannot terminally yield on a plan-phase dispatch.** `validate-digest.py` refuses `code_grade: n_a` ("cannot be bound to `review_sha`… an unpinned feature (INV-6) cannot anchor a `code_grade` claim") AND refuses it omitted ("missing `code_grade`"). The two refusals are mutually exclusive, so no return satisfies the gate — while `feature.json` already records `code_grade: n_a` for that same unpinned feature. Raised three consecutive times; cost one reader ~32 minutes and four yield attempts. |
| B-6 | bug | `plan-merge.py`'s `UNION_KEYS` is `("tasks", "decisions")` only, so `lanes` and `panel` cannot be amended incrementally — any difference is exit 7. Five full remove-then-recreate cycles were needed this phase. **Probably already in flight:** `BUG-1128-plan-amend-verb` sits at station `review` with an `amend` verb built (`plan-merge.py:916-1091`, ten `case_amend_*` tests, `review_sha 58742037`). Strike this row if that lands. It does NOT cover B-2. |
| B-7 | bug | `check-domain.sh` denies `harness-pm` a `Write` at `notes/plan-proposal-*.yaml` (its grant is `research-*.md` and `uat-*.md`), so the sanctioned tool is refused for the one write route `plan.yaml` has — and `python3` reaches it anyway, which the guard does not intercept. |
| B-8 | bug | `bash-write-guard.sh` reads a `>=` inside Python source as a redirect and refuses the command, naming a target absent from it. Cost four retries in one run. |
| B-9 | bug | `check-plan-routes.py` never reads `lanes.rows`, so a surface missing from that block is ungated. Four missing rows survived two cycles until measured by hand. |
| B-10 | chore | A lead digest missing `artifact:` is written and accepted by its own run, and only `check-state.sh` catches it later. `runs/plan-fix-c2-product/digest.md` had shipped without one; repaired. |
| B-11 | chore | `panel.findings`' `reader` enum has no word for a lead's fan-in finding. Recorded as `validator-lead`, which is truthful; nothing breaks, but the template comment is out of step. |
| B-12 | chore | `check-state.sh` INV-29 is red on a standing worktree that is not FEAT-51's: `.claude/worktrees/harness/BUG-1129-validate-handoff-sweep`, terminal on the default branch and dirty, so `remove` declines until its changes are committed or discarded. Pre-existing and unrelated; it is the only violation left that is not the two signature gates. |

---

## §8 — Budget, honestly

`cycles_used: 9` of `max_total_cycles: 10`. `len(runs): 14` against `max_total_runs: 20` —
informational, and the runs earn their place: each of the last five closed a named finding measured at
source, and two of them found gates that could not go red. The one cycle left is not enough for a
build phase. **If you sign, raise `max_total_cycles` in the same act.**
