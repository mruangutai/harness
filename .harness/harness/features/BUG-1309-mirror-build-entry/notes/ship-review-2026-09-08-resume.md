# Ship review — BUG-1309-mirror-build-entry — 2026-09-08

## The decision in one paragraph

**Do not ship yet, and nothing is left for a squad to build.** The feature is code-complete and
measured: all thirteen tasks are done, the blocking test-matrix gate is green, and nine of the ten
success criteria are met with executed evidence at the pinned commit `894adc0f`. Four things now
need **you**, and only you — they are batched here so one sitting closes them. A fresh review panel,
run today because the previous one was lost to a provider interruption, found **three high-severity
defects in code this feature itself introduces**, and every remedy sits in a lane the harness is
forbidden to execute in. That is the whole of what stands between here and a merge.

## What you must do — four items

| # | Item | Why it is yours |
|---|---|---|
| **1** | Rule on **F-01** and **F-02**, two fail-open/misfire defects in `merge-gate.py` | The remedy edits a registered PreToolUse gate script. DEC-174 forbids the harness executing changes to its own gate scripts, whatever `check-domain.sh` resolves |
| **2** | Rule on **F-03**, a wrong remedy command in `gh-sync.py` | The code **matches** the approved spec — `plan.yaml:779-791` dictates the string verbatim. Fixing it amends a signed plan, which needs your signature, not a fix cycle |
| **3** | **Re-sign** `BRIEF.md ## Approval` | SC-03 and SC-07 were amended today on your ruling. The 2026-09-06 signature no longer covers the file on disk |
| **4** | Run the **SC-10 hand test** — `notes/uat-BUG-1309-mirror-build-entry.md`, 8 steps, ~10 minutes | SC-10 is `verify: uat`. No agent may grade it. The script was verified drift-free against the pinned code today |

Item 4 does **not** depend on items 1–3: pm confirmed at its own tier that no UAT step reaches the
`gh-sync.py` line F-03 concerns, so your ten minutes are not wasted by ruling later. Run it whenever
suits. It must be run **before the worktree is released** — the script points at that checkout.

## The three gating findings

**F-01 — `merge-gate.py:98-109`, high, security-reviewer.** `feature_for` returns the FIRST
`glob.glob` match and `glob.glob` guarantees no ordering, so when two well-formed records carry the
same `branch` value the merge is decided nondeterministically — in one direction a feature that owes
a receipt merges silently (the gate defeats itself), in the other a healthy merge is DENIED naming
an unrelated feature. Reproduced 5/5 in both directions. No committed test binds a duplicate-branch
fixture. *Options:* order the glob and refuse on ambiguity; or accept and record.

**F-02 — `merge-gate.py:44-48`, high, security-reviewer.** `git_merge` strips every `-`-prefixed
token and then reads `args[0]`, so the VALUE of a value-taking global flag lands in that slot:
`git -C <dir> merge X`, `git -c k=v merge X` and `git --work-tree <d> merge X` all fall straight
through and the gate allows the merge silently, whatever the receipt says. I re-ran this myself
against the pinned script: `merge_ref` returns `None` for all three, and `git -C` is the idiom
`merge-gate.py`'s own `local_branch()` uses. *Options:* teach the parser the value-taking flags; or
accept a gate that ordinary git usage walks past.

**F-03 — `gh-sync.py:1387-1389`, high, ui-reviewer.** The non-era `recovery-required` notice tells
you to run `gh-sync.py open`, while `feature_schema.recovery_command_for` and `merge-gate.py`'s own
deny both say `recover-terminal` for the same feature in the same state. Following the notice runs
`cmd_open`, which creates real GitHub sub-issues for already-finished work. **The plan signs that
string deliberately** — it reasons the non-era line "keeps its `open` clause". *Options:* amend the
plan so the notice derives its command like every sibling site; or keep the signed wording and
record the contradiction under `BRIEF.md ## Verification gaps`.

## Where the feature stands

- **Goal-check at `894adc0f`:** SC-01 … SC-09 **met**, each with executed evidence — see the
  `sc_status` table in `runs/2026-09-08-amend-gc-product/digest.md`. SC-10 **user-gated**.
- **Test-matrix gate:** PASS. Unit 33 files exit 0, integration 50 files exit 0, `test-merge-gate.py`
  19/19, no cell missing; T-07's unit cell is not-applicable per D-12.
- **The SC amendment you ruled on:** both criteria kept their teeth. The unevidenceable "must be
  shown red before the fix landed" became "is DISCRIMINATING at `review_sha`" — and pm then *ran*
  both: the pre-change `gh-sync.py` fails all five SC-03 cases, the pre-change `check-state.sh`
  fails the SC-07 violation case.
- **Cycles:** 12 of 14. Neither of today's two runs sent anything back, so neither cost a cycle.
- **Runs: 37 against a 20-run budget (INV-22, informational).** My read: the count is honest, not
  waste — this feature absorbed eleven adversarial panel cycles and each closed something real, and
  today's two runs found three highs six earlier cycles had misfiled. It is a long feature that has
  been earning its length, but F-01/F-02 show the panel is still finding gate-integrity defects, so
  do not read the count as evidence of convergence.

## The one thing that changed how this run was judged

Six review cycles established "is this new?" against the **pin's parent commit** and therefore
reported F-01 and F-03 as pre-existing carry-forwards, out of scope. The panel lead ordered the
measurement against the true merge-base instead, and I re-ran it myself: `merge-gate.py` and
`merge-gate.sh` **do not exist** at `6ad7233f` and arrive at `4338ee44`, inside this feature's own
range. They are this feature's code. That single measurement is what promoted two advisories into
gating findings.

## Proposed backlog — strike any row by ID; anything not listed here dies silently

| ID | Item | Nature |
|---|---|---|
| B-1 | Gate-dispatcher consolidation plus the `HOOK_SPECS` gaps (operator already accepted the fifth standalone gate) | enhancement |
| B-2 | `gh-sync.py:247`'s no-op remedy string | bug |
| B-3 | The 17 unrecovered sync-enabled features | chore |
| B-4 | The nonexistent `gen-decisions-index --check` clause in four features' plans | chore |
| B-5 | `gh-sync.py:1234`'s unguarded `int()` | bug |
| B-6 | `merge-gate.py:11` imports `feature_schema` at module scope, ~50-60 ms on every Bash call | enhancement |
| B-7 | `merge-gate.py` DENY interpolates the literal `this feature` when the git binary is unresolvable — fails closed, med | bug |
| B-8 | The DEC-138 stderr line says "owes no build-entry receipt" where the record is HELD — diagnostics only, low | bug |
| B-9 | Three different spellings of "Build entry receipt" across the messages | chore |
| B-10 | `test-check-state.py`'s "INV-37 message discriminator" case is vacuously green — asserts a token absent from an empty line | chore |
| B-11 | `test-merge-gate.py`'s "gh outage with no matching feature allows" does not itself discriminate a cycle-5 sentinel reintroduction | chore |
| B-12 | Handoff `Authority:` pointers `plan-task:` and `brief-sc:` cannot resolve for a feature living only in a worktree — the checker joins the feature path to the main checkout root | bug |
| B-13 | The reviewer dispatch template does not state the canonical novelty range, which is how six cycles read "pre-existing" as "pre-existing since two commits ago" | enhancement |

## How this briefing was assembled — disclosure

**No report round was spawned.** I read the digests and notes on disk. The load-bearing ones:
`runs/2026-09-08-panelc7-validator/digest.md` (today's panel), `runs/2026-09-08-amend-gc-product/digest.md`
(today's amendment and goal-check), `notes/review-harness-{code-reviewer,qa,security-reviewer,ui-reviewer}-c7.md`,
`notes/qa-matrix-gate-BUG-1309-rerun.md` (the gate), `notes/research-BUG-1309-goalcheck-amend-c13.md`,
`notes/uat-BUG-1309-mirror-build-entry.md`, and the `headline:` line of every one of the 30 run
digests on disk for plan- and build-phase coverage. I did not read the plan- and build-phase digests
in full — their headlines plus `STATE.md` and `feature.json` carried what this decision needs. I
re-verified four claims myself rather than relaying them: the merge-base novelty of `merge-gate.py`,
F-02's parser miss (executed), F-03's source contradiction, and that `894adc0f..HEAD` touches
`feature.json` alone, so the pin still covers all code.
