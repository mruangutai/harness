# FEAT-29 — GraphQL budget · final ship review

**Supersedes both earlier reviews. Ready for your ship decision.**

## The result

**`check-state.sh` costs 5 GraphQL points. It cost 506.** Both numbers are differenced measurements
across a real run, not inferences from a changed call shape.

**The saving is the query shape, and the competing explanation is ruled out.** Board 6 — four items —
read **102 points on the old shape and 1 on the new**, with `board_items: 4` on *both* sides. Identical
item count, so item count cannot account for a 102-versus-1 difference.

**The cheap read still discovers what the expensive one did.** This was the real risk, not the saving:
issue #588 records that INV-26 prints nothing both when the board agrees *and* when the read fails, so
a silent break and a working read were indistinguishable. Three independent instruments close it — the
positive control's seven expected lines reappearing verbatim at 5 points; the live run returning **two
different station values across nine cards**, which no truncating read can do; and a fixture case
covering the failure mode the live run does not reach.

**Nine of nine tasks done. Both suites green.** `--kind unit` exit 0, 18 of 18 scripts, 0 FAIL;
`--kind integration` exit 0, 12 of 12, 0 FAIL. `matrix_ok: true`, panel PASS, `must_fix` empty,
SIMPLIFY four angles and zero applies.

## Success criteria — and exactly how each was graded

**Eight of ten were graded met by pm's goal-check** against evidence cited by path.

**SC-08 and SC-09 were graded UNMET by that goal-check**, then amended by you afterwards — SC-08 scoped
to documents still in force, SC-09's cost-citation clause struck. **No agent has re-graded them since
the amendment.** I verified both mechanically: `git show 444c611:CLAUDE.md | grep -c "wait loop"`
returns 1, and the grilling note carries its strikes. That is the honest provenance — a mechanical
check by me and by you, not an independent re-grade — and you should weigh it as such.

SC-09 is the one that nearly shipped broken. T-08's rule existed only in the working tree; its
`verify:` read the working tree rather than the tree under review, so the gate passed on a deliverable
that was never committed. pm found it, could not confirm it — leads and members hold no `Bash` — and
escalated rather than guessing. That generalises well past this feature and is B-18.

## Cost, cycles, runs

**46 GraphQL points spent by me across the entire feature** — against a subject that leaked 506 per
run. Every pre-commit gate ran at **zero** cost under `FACTORY_GH=/nonexistent/gh`, which skips only
INV-26's board read.

**9 cycles of 10. 17 runs of 20** — both inside budget. The runs earned their place: each resolved
something and the SCs advanced monotonically. **The one real waste was seven premature lead closes**
under the `SubagentStop` hook. Three bought no artifact, one built a digest from a member's mid-write
file, one became a false premise in a brief I then wrote. That single harness defect cost more than
every other inefficiency here combined, and it is B-16.

## Close-out

**Distillation: 34 entries across 14 Expertise files, `check-expertise.sh` exit 0 on 16 of 16.** Every
capped section held at cap by displacement. The rejections are the signal: pm rejected a candidate
because a preloaded rule skill already carries it verbatim — which grades the lead's relay, not pm, and
the lead recorded that against itself. The eng lead reported the digest-skim's honest yield as **one**
entry rather than the eleven the raw count suggests, because two of its three members kept no log, so
acceptance there grades the dispatch. That is the metric DEC-145 put the skim on trial for, reported
against its own interest.

**Ship-refresh: SKIPPED, and disclosed.** No map exists in this repository — `render-map.py` expects
`INDEX.md`, `architecture.md` and `domains/`, none of which are present. A skip with a reason, not an
omission, and it cost no spawn.

## Proposed backlog

Unstruck rows become issues on your ship acceptance; anything not listed dies silently.

| ID | Finding | Nature |
|---|---|---|
| B-1 | `test-factory-gh.py` aborts instead of reddening under any mutant adding a subprocess call | bug |
| B-2 | `gh_board.py:142`'s `or {}` guard is unreachable from its only producer | chore |
| B-3 | Four T-04 fixtures tolerate an extra `gh` call; only `ensure_labels` asserts a count | chore |
| B-5 | T-03's `intent:` still carries text amendment 5 superseded | chore |
| B-6 | `test-gh-sync.py` is in `INTEGRATION_SCRIPTS`, so `--kind unit` never exercises T-03's `gh-sync.py` half | enhancement |
| B-7 | The cost log cannot see `gh` typed straight into Bash — where #571's own traffic lived | enhancement |
| B-8 | `.harness/logs/gh-cost-*.jsonl` has no ignore rule and is written `0644` — the **narrow** pattern, never blanket `.harness/logs/` | chore |
| B-9 | `factory_claim.py:304` calls `project_items` per served repo at ~102 points, unmeasured for fleet size | enhancement |
| B-10 | gh-sync's sync points and a board-derived positive control silently destroy each other | bug |
| B-11 | Nothing serialises two leads' members against one checkout; `mutates_repo` is per-lead-DAG | bug |
| B-12 | `integration.detect` names 4 files while `INTEGRATION_SCRIPTS` runs 12; `unit.detect` matches all 30 | bug |
| B-13 | `factory_gh.py:359-363` spins forever on `hasNextPage: true` with a null `endCursor` | bug |
| B-15 | `check-domain.sh` binds Edit/Write but not Bash (DEC-85) | bug |
| B-16 | `SubagentStop` forces a digest from a lead with a member in flight — **seven occurrences here**, the largest single source of waste | bug |
| B-17 | `factory_config.harness_root()` falls back to the real checkout when `CLAUDE_PROJECT_DIR` lacks `SPEC.md` | bug |
| B-18 | A task `verify:` reading the working tree cannot distinguish committed from uncommitted work | bug |
| B-19 | Issue #588 survives: `check-state.sh:1172-1176` still swallows a failed board read into silence | bug |
| B-20 | Leads hold no `SendMessage`, so a lead cannot course-correct an in-flight member | bug |
| B-21 | `check-expertise.sh` has no notion of prior state, so it cannot detect a DEC-125 wipe — proving zero drops took a separate git audit | bug |
| B-22 | backend-dev's craft `P-07` was replaced with a version adding an escape hatch to a previously absolute rule — the one entry that got weaker | chore |
| B-23 | Nothing at plan time compares a criterion's quantified scope against the union of `files:` across its tasks — the SC-08 root cause | enhancement |
| B-24 | pm displaced a `P-11` whose original purpose was anti-over-harsh grading; flagged for a curation pass | chore |
| B-25 | Observation logs are Write-not-Edit, so two concurrent contexts silently last-writer-wins | bug |
| B-26 | `dispatch-guard.sh` refused a `model:` parameter in three independent lead contexts; the Expertise entry covering it is injected every spawn and fired for none | bug |
| B-27 | `harness-security-reviewer.md` is at **147 of its 150-line budget**; the spawn hook hard-truncates, so the next distillation silently loses entries off the tail and `check-expertise.sh` warns nothing | bug |
| B-28 | Run-id sequence numbers no longer order runs — three squads each took seq `14` on one date. Nothing collides on disk, but a reader cannot order concurrent segments | chore |
| B-29 | The directory-wide `check-expertise.sh` is dispatched per-lead while sibling leads are still writing; the prescribed single re-run does not settle it. Proposal: the orchestrator owns one gate run after all squads close, leads gate only their own members' files | bug |

B-4 and B-14 remain struck — you fixed both in amendments 4 and 1.

## How this was assembled

**No report round was spawned.** Read from disk: `runs/plan-product/` and all sixteen
`runs/2026-08-*/` digests, `notes/research-goalcheck-FEAT-29.md`,
`notes/qa-matrix-gate-final-c472a02.md`, the three `measurement-*.md` files, and the T-03 receipts.
Every measurement attributed to me I ran myself — the corpus sweep, `git show` on the committed
`CLAUDE.md`, the `8c2c24d..4f2e5d0` diff, the worktree bisect, and both suites.

**Not independently reviewed:** no UI reviewer ran, correctly — no UI surface. The security reviewer's
single pass covered the cost log only. SC-08 and SC-09 carry the grading provenance noted above.
