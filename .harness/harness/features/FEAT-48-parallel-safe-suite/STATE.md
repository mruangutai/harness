# STATE

## Current

- feature: FEAT-48-parallel-safe-suite
- run: none — no squad ran this session
- squad: none
- status: blocked — routing

**The build phase did not start, and the reason is structural, not a failure.** All six executable
tasks (and abandoned T-07) carry `execution_mode: main-session-direct` under DEC-174's
enforcement-layer carve-out. `references/github-mirror.md:32-34` assigns those to the **main
session**: *"Phases the main session holds itself: plan, ship acceptance, and any
main-session-direct segment."* There is no `team` task in this plan, so an orchestrator has nothing
to sequence and no lead has anything to route. Measured, not inferred: `check-domain.sh` exits 2
for `harness-orchestrator` on `.claude/skills/harness/bin/**`, `.harness/harness.json` and
`DECISIONS.md` — 8 of the 9 task surfaces. Dispatching a lead anyway would be the team run DEC-174
forbids, against a signed `lanes:` block that declares the carve-out. Handed back for direct
execution: `notes/handoff-build.md`.

Station stays `ready`; no task was moved to `building`, no `gh-sync.py start-task` was run,
`review_sha` stays `none`, `cycles_used` stays 6 (no rework occurred), and no run was recorded
because none happened. Worktree clean at `cd8a0c34`, branch `feat/FEAT-48-parallel-safe-suite`.

Work banked this session, so the direct build starts ahead rather than level:
- **D-10's census scan was executed** — the first time anyone has run it (257s, 61 test files).
  It reports **13 sites in 6 files** against D-10's dated 8-in-4, and it found
  `test-validate-digest.py` (3 sites), which no artifact had flagged. `notes/census-d10-2026-09-02.md`.
- **A standing blocker was disproved.** `gh-sync.py`'s review-station gate already accepts
  `abandoned`; the open question below that predicted a refusal was stale.
- FEAT-48 still carries **zero** `check-state.sh` violations.

Previously: plan phase COMPLETE and SIGNED (Mike Ruangutai, 2026-09-02, `85900e7f`), both
`plan.yaml`'s `approval:` and `BRIEF.md`'s `## Approval`. Mirror OPEN: milestone #40, parent #1191,
sub-issues #1192-#1197 at `ready`, T-07 correctly absent. `panel:` cycle 6 `verdict: PASS`,
`severity_max: med`, `must_fix: []`, 0 unsatisfiable / 0 under-specified. `fable-advisor` returned
`approve: "yes"` over nine named residual risks, which the operator accepted. 15 runs against an
informational `max_total_runs` of 20.

## Open Questions

- **RESOLVED, and it was stale.** The prior entry predicted `gh-sync.py` would refuse the
  review-station write while T-07 stands, and called for a one-line fix to land first. It is
  already fixed: `gh-sync.py:1158-1161` tests membership in `finished_stations()`, which returns
  `('done', 'abandoned')` (`factory_config.TERMINAL_MARKER`, read live), and the refusal text reads
  "not every task in plan.yaml is done or abandoned". **No fix needs to land and no hand-sync is
  needed.**

- **NEW, from the census, and NOT a plan defect.** `test-validate-digest.py` writes three
  `<pid>`-suffixed files into the live `bin/` and was flagged in no prior artifact.
  `test-check-fixture-secrets.py` (2 sites) was already flagged. Both sit under the lanes glob, so
  neither is a D-10 boundary escalation, and the operator's ruling on the first covers the second
  identically. **T-02's derived run set does not reach either file; T-03's repository-wide walk
  does, so T-03 cannot ship green until all five are fixed.** The doer names them in its receipt;
  no plan edit is needed, which is D-10 passing its fourth real test.

- `test-check-domain.py` exited 1 once in 5 runs at `cd8a0c34`, and I could not reproduce it —
  including under a deliberately concurrent `check-state.sh`. The census discarded the failing
  output, so the mechanism is **UNVERIFIED and the instrument gap is mine**. T-01's `verify:`
  demands exit 0 plus an empty `appeared` set, so a doer may read a spurious red; run it on a quiet
  tree and re-run before concluding failure.

- Whether issue #1053 CLOSES on FEAT-48's ship is a product call the Advisor declined to settle. It
  settled the evidence question (SC-05's ten `--kind all` runs do exercise `test-gh-sync.py`) and
  left disposition to the operator; its own recommendation is close on ship, stating the evidence
  honestly.
- Issue #1053's `## Scope` still reads "Folded into FEAT-47". No plan task can write an issue body;
  only the operator's hand fixes it.
- T-07's exclusion from any expansion rests on prose, not a mechanical guard. It is moot while the
  build is main-session-direct, and it returns the moment anything expands a task list here.
- SEC-01, sixth consecutive cycle: `validate-digest.py harness-code-reviewer` refuses every
  `code_grade` value — `n_a` included — and refuses the key's omission, while `feature.json` has no
  pinned `review_sha`. Harness defect, no FEAT-48 owner; it binds until `review_sha` pins.
- `plan-sign-gate.py` does not read the `panel:` key, so a signature can land on a plan whose own
  last panel word is FAIL. Closed for FEAT-48 by the cycle-6 write; the guard gap is untracked.
- `{{cycle}}` resolves from no `plan-panel` team input; hand-supplied six cycles running, and the
  team file's `outputs:` template interpolates it, so a run without it overwrites a prior artifact.
