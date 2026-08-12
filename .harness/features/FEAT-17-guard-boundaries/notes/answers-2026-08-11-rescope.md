# Operator answers — FEAT-17 — the rooted case is already governed — 2026-08-11

## The measurement that forces this re-scope

**#103's founding evidence has been overtaken and nobody checked.** The ticket's most-cited damage
is FEAT-09's: an orchestrator wrote a 205-line `feature.yaml` and a 63-line handoff note from a
sibling worktree, both over DEC-150's caps, both unblocked, and reported the caps as "prose-only,
not mechanically enforced". That happened on 2026-08-05.

**Re-measured at `a29ad06` by rebuilding the exact damage** — a 211-line `feature.yaml` against the
200 cap and a 70-line handoff note against the 60 cap, fired from a session ROOTED in a stray
sibling worktree:

| Payload | Rooted in stray worktree | Real checkout |
|---|---|---|
| `feature.yaml`, 211 lines | **exit 2** | exit 2 |
| handoff note, 70 lines | **exit 2** | exit 2 |

**Identical. The FEAT-09 scenario is no longer possible.** DEC-180 and issue #132 made SHAPE
independent of DOMAIN and bound it to every author, so the caps fire relative to whatever root the
session is standing in.

**The domain guard works there too.** `harness-documentor` writing a `bin/` script from inside the
stray worktree exits **2**. Because the root IS that worktree, every domain rule resolves against it
correctly.

## What this changes

| Concern | Status at `a29ad06` |
|---|---|
| An agent writes outside its domain from a rooted stray worktree | **GUARDED** — exit 2 |
| DEC-150 shape caps go dark in a rooted stray worktree | **GUARDED** — exit 2 |
| A harness-rooted session writes INTO a stray worktree | **UNGOVERNED** — exit 0 |
| Creating a stray worktree | **UNGOVERNED** — exit 0 on both hooks |
| Work lands in a checkout nobody merges | not guarded, and **not an enforcement hole** |

**The distinction the plan must be re-scoped around.** When the session is rooted IN the stray
worktree, everything is enforced — it is merely enforced in the wrong place, which is a lost-work
risk, not an ungoverned-write risk. When the session is rooted in harness and writes INTO a stray
worktree, nothing is enforced at all. **Only the second is an enforcement gap.**

## The ruling

**Re-scope FEAT-17 on what is actually ungoverned.** The two real holes are unchanged and both
remain confirmed at `a29ad06`:

1. **#261 — the shell route.** With `src/**` granted, `<root>/src/main.py` is Write **2**, Bash
   **0**. `bash-write-guard.sh` holds zero references to `fleet`, `workspace_root` or
   `factory_config` and carries its own worktree rule at `:405`. This is the DEC-151 failure shape
   and it is the sharpest thing in the feature.
2. **#103's surviving half — writes INTO a stray worktree, and creating one.** Three payloads into
   a real sibling worktree from a harness-rooted session all exit 0 while exiting 2 in the real
   checkout. `git worktree add --detach ~/GitHub/harness-SIBLING HEAD` passes both hooks at exit 0.

**SC-03's rooted-session refusal drops to a much weaker justification.** It is no longer closing an
enforcement hole; it is refusing a location the architecture says should not exist, whose work would
never merge. That may still be worth doing — the earlier ruling that a stray worktree is a MISTAKE
stands — but it must be justified on those terms and sized accordingly, not on FEAT-09's evidence.

**The BRIEF must stop citing FEAT-09's shape-cap failure as live.** State it as overtaken by
DEC-180, with the re-measurement above, so the next reader does not re-derive a closed hole.

## What is NOT re-opened

- The two legitimate locations — `.claude/worktrees/<id>/` and `workspace_root/<product>` — are
  correct and untouched.
- A stray worktree remains a MISTAKE, not a supported shape. `git worktree list` resolution stays
  declined.
- `bash-write-guard.sh` still learns the boundary rule from the SAME source, never a fourth copy.
- INV-25 remains a **FAILURE**, not a warning (operator, 2026-08-11). A warning is precisely what
  failed for #103 — INV-20 is a warn and warning is what let it sit.
- One out-of-place worktree exists today (`…/scratchpad/r6`) and is **clean**, plus one prunable
  entry (`…/scratchpad/wt140`, directory already gone). Refusing writes strands nothing.

## The lesson worth recording

**A ticket's founding evidence can be silently repaired by an unrelated feature.** Nobody re-ran
FEAT-09's case before planning against it, including me when I wrote the grilling artifact. The
check that settles it costs one command. This is the same class as verifying a ticket's premise
before acting on it, applied to evidence that was true when written.

---

# SIGNATURE — 2026-08-11

BRIEF and plan.yaml both `approved`, operator. Seven tasks, nine decisions, nine REQs, ten SCs.
Six tasks `main-session-direct` (all four DEC-174 carve-outs plus the new shared module), one team
task.

**D-09 is ACCEPTED as recorded.** In a PyYAML bootstrap-grant session the Bash route refuses an
out-of-place session root and the Write route does not. Two routes disagree in exactly one session
shape, in a feature whose goal was that they cannot drift apart.

Accepted on the argument the orchestrator verified rather than asserted: **the Write route's
target-side refusal is ALREADY parser-contingent** — it is wired into `classify`, and only
`domain_check` calls `classify` — so siting the root-side check there is symmetric with what the
plan had already accepted, not a new weakness singled out. Supporting: the bootstrap grant skips
`domain_check` in the real checkout too (`check-domain.sh:675`, `if _run_domain and not
_no_parser:`), so a stray-worktree session under the grant is no worse off than a sanctioned one.

**Reversible at signature and only as a pair.** Restoring the module-level hoist restores SC-03's
no-PyYAML cluster and REQ-02's bootstrap clause with it; they were cut together because one
premise carried all three.

**No ticket filed.** The divergence lives in D-09 where a reader of the decision record finds it.
Filing it would put a fourteenth item on a board already carrying thirteen, for a gap that is
recorded, bounded to one session shape, and fails toward refusal on the route that still fires.

**The SC-03 split question is MOOTED, not deferred** — the no-PyYAML cluster it referred to no
longer exists.

**Build ordering, held by the main session.** FEAT-17 does NOT build next. FEAT-14's migration
rewrites all 17 `feature.yaml` files and needs every other flow idle; a signed, undispatched plan is
idle, so this signature does not block it. FEAT-16 and FEAT-17 build AFTER the migration, once, on
the settled `feature.json` format.

**Carried forward unverified, for whichever feature lands second:** FEAT-16 and FEAT-17 share three
files — `test-check-domain.py`, `docs/harness/DECISIONS.md`, `docs/harness/DECISIONS-INDEX.md`. The
second to land rebases in all three.
