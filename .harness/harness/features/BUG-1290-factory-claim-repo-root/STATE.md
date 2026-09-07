# STATE

## Current

- feature: BUG-1290-factory-claim-repo-root
- run: none in flight — feature-close distillation complete
- squad: none
- status: shipped, distilled

The operator accepted ship; the merge landed on `main` at `7a3640f1` and the worktree was removed by
the `post-merge` hook. `gh-sync.py ship` posted the fourth-pass review on parent #1359, put
#1360–#1364, source #1290 and parent #1359 at Done, and closed milestone #51. Accepted briefing rows
were filed as #1420–#1454.

**Feature-close distillation (DEC-145) ran once, three leads, one dispatch each** — runs
`2026-09-06-19-eng`, `-20-product`, `-21-validator`, all PASS. The `runs/` tree is gitignored and
died with the worktree, so every lead worked from the surviving material only: `observations/`
(two logs — `harness-pm.md`, `harness-backend-dev.md`) and `notes/` (receipts, review notes, qa
notes, research notes), with `notes/ship-review-2026-09-06-19-ship.md` standing in for the vanished
run digests at the skim step.

**Result, measured from the working diff: 35 entry-level ops across 15 Expertise files — 17 adds,
16 replaces, 2 drops.** Eight members distilled (backend-dev, dev-ops, data-engineer, pm, qa,
code-reviewer, security-reviewer, ui-reviewer) plus the orchestrator's own file; the per-member
digest counts sum higher than 35 because the ui reviewer's repository `O-01` was added and then
dropped inside the same run. Every op went through `expertise-merge.py`; no file was written whole,
so no DEC-125 wipe. Sections already at cap took entries only by displacement, and candidates with
nothing weaker to displace died — the healthy outcome, not `expertise_full`. `check-expertise.sh`
exits 0 over both `.harness/expertise/` and `.harness/harness/expertise/`; the three surviving
ADVISORY lines are pre-existing issue-340 layer flags on entries nobody touched this run.

Two corrections landed alongside the additions: pm dropped a repository gotcha that instructed a
direct `plan.yaml` write (false since D-04), and the orchestrator replaced a craft gotcha governing
worktree creation — an act it never performs — with the concurrency rule that closes OQ-02. One
cosmetic drift: dev-ops wrote its new Outcomes as `O-1`/`O-2`/`O-3` where the rest of the corpus
zero-pads; the checker accepts it and it is not worth a cycle, but a later op must target the
unpadded id.

Lead-relayed skim candidates were mostly rejected as already covered, which is the expected shape:
the skim's measured yield was roughly one accepted entry per squad, everything else self-derived.

**Budgets.** 10 rework cycles of the operator-raised hard **11** — one send-back this run (the
validation lead returned a duplicate repository entry to the ui reviewer, which dropped it). 33 runs
of an informational 20; my read is unchanged — the count records a long, honestly-worked bug, not a
loop that failed to converge.

Nothing else moved: no code, test, plan, brief, GitHub or ship-state change in this run.

## Open Questions

- Q1 (**new, non-blocking, harness defect**): `validate-digest.py` cannot accept a truthful
  distillation return from two personas at feature close. For `harness-code-reviewer` the
  code-grade binding runs unconditionally and compares `feature.json`'s recorded branch against the
  current checkout, which after the merge is `main` — it can never match. For `harness-qa`,
  `GATE_FIELDS` binds `suite`/`matrix_ok` and DEC-173 rejects `n/a` + PASS, but a distillation
  dispatch runs no suite and grades no matrix. Both members' ops are applied and verified on disk
  regardless. A distillation/post-merge path is missing. (qa also spelled `matrix_ok: none` rather
  than `n/a` — a real member slip, independent of the defect above.)
- Q2 (**new, non-blocking, harness defect**): `check-domain.sh` resolved the fleet declaration from
  the main checkout's `factory_gh.py`, which imported a module existing only in an unrelated
  in-flight edit, and denied every write factory-wide — including `/tmp` — until that tree settled.
  A guard whose availability depends on another feature's uncommitted tree fails closed globally.
- Q3 (**new, non-blocking**): the hardlink edit-desync report had no durable channel — `check-domain`
  blocked `xd://report_issue` from the worktree, so a build-time-only agent could not file it.
  Backlog row B-13 covers the desync itself; the unfilable half has no row.
- Q4 (carried, non-blocking, operator only, row B-10): the REQ-05 wording correction. The operator
  has declined to rule three times and directed that approved artifacts stay unchanged.
- Q5 (carried, pre-existing, row B-24): no `notes/handoff-build.md`. The build seam was crossed
  without one by a predecessor; writing one now for a phase nobody ran would falsify the record.
- Q6 (carried, harness defects already filed as backlog rows B-11..B-15, B-18..B-22, B-26, B-31,
  B-38): claim scoping, lead digest clobber, hardlink edit desync, null-yield returns, the matrix
  keying a required kind on a directory label, the write-guard's two routes disagreeing, reviewer
  `files_touched` under-reporting, the inert `match_bug_class` leg, and the reviewer
  digest-contract violation.
- Q7 (**closed this run**): the previous close-out's open question on concurrent distillation racing
  the shared Expertise corpus. Three squads ran concurrently with each member's checker scoped to
  its own file and one corpus-wide check after all returned; both tiers exit 0 with no false
  failure. The remedy is now a craft rule.
