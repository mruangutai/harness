# STATE

## Current

- feature: FEAT-09-plan-time-route-check
- phase: validate
- worktree: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/FEAT-09 (branch feat/FEAT-09-plan-time-route-check)
- head: 4918d06 — also the pinned `review_sha`
- base: 47ed11f (`git merge-base main HEAD`)
- run: none open
- status: **awaiting_user** — one BLOCKING finding, in a lane no agent here may enter

**Segment 2 delivered everything it was asked to, and the panel then found a HIGH.** T-02 landed
clean at `ae28daf` — `check-plan-routes.py`, a 17-case test, and one appended `SCRIPTS` element.
DEC-179 landed at `4918d06` with the index regenerated. `review_sha` was pinned ONCE, after both,
against a complete diff. The four-wide panel ran with no skips.

**The blocking finding — VF-1.** If `HARNESS_RESOLVE_PATH` is present in the environment, every
agent can write every path: exit 0, no stderr, nothing logged. `check-domain.sh:38` exports it in
the `--resolve` branch and the `else` branch at `:39-41` never unsets it; `:133-134` selects mode on
`is not None`, so even an empty string qualifies. **I reproduced this myself with payload FILES,**
not inline: the same documentor-writes-`bin/` payload exits 2 on a clean env and exits 0 with the
variable set. Full write-up at `notes/vf1-guard-bypass.md`.

**SC-04 is false as written, not under-tested.** `BRIEF.md:48-49` states it in argv terms — "no
`--resolve` in argv → still exits 2" — and the implementation does not branch on argv at all. The
existing cases (g)/(h) pass only because the environment happens to be clean. That is what makes
this gate rather than sit as a `med`.

**It is a DECLARED main-session step, which is this feature's own thesis applied to itself.** The
manifest grants `check-domain.sh` to backend-dev and dev-ops — measured, not assumed — but DEC-174
forbids dispatching a change to it through a team run whose gates are the thing being changed, and
the domain hook separately blocks me. I may neither perform this fix nor delegate it. It is exactly
the `DEVIATION` shape `check-plan-routes.py` was built to surface.

**The no-pre-emptive-skips ruling earned its keep.** No single reviewer could have produced this.
Security found the mechanism without checking it against SC-04; code checked SC-04 correctly, under
a clean environment. The defect lived in the *union* of the scopes. The ui reviewer declined on
measurement, not prediction — a reviewed finding.

**Goal-check, distillation and the briefing are deliberately NOT run.** SC-04 is already known
false, and the fix changes the guard, so a goal-check now would be invalidated by the fix and a
briefing would be addressed to a decision the user has not yet made.

## Open Questions

- **Q-VF1 BLOCKING** — apply the one-line `unset` plus the env-explicit test case to
  `check-domain.sh`? It is main-session-direct by DEC-174. Nothing else in the feature is
  outstanding. See `notes/vf1-guard-bypass.md`.
- Q-VF2 NON-BLOCKING — a task naming a `shared:` file (package.json, pyproject.toml) is falsely
  REJECTED by the checker. It fails closed, not open. Ruling on it amends DEC-179.
- Q-SC08 NON-BLOCKING — three of SC-08's four clauses are respellable source greps, and case 17's
  mid-pattern `*` never crosses a `/`, so an `fnmatch` reimplementation would pass it. The design
  rule is weaker than its clause count suggests.
- Q3 NON-BLOCKING — promote the route checker to a `check-state.sh` invariant?
- Q4 NON-BLOCKING — the checker copies the state checker's task-block regex. Consolidate?
- Q5 NON-BLOCKING — two historical plans use a token this feature retires. Normalise?
- Q-INV17 NON-BLOCKING, HARNESS DEFECT — `check-state.sh` shape-checks a handoff note only once
  `phase:` moves PAST the seam, so an over-cap note sits unflagged for the whole phase it
  describes — exactly when a successor reads it. `handoff-build.md` was 63 lines against a 60 cap
  and went undetected until I advanced the phase.
- Q-STATECAP NON-BLOCKING — corrected against myself: `feature.yaml`'s 200-line cap IS
  mechanically enforced (it blocked me three times and routed the rationale to `notes/`). The
  unenforced one is this file, where a 205-line write once succeeded.
