# CEO briefing — FEAT-42 One root resolver — plan phase, BLOCKED

## The one-liner

**FEAT-42 is blocked by the exact bug it was created to fix.** A stranded single-flight claim from an
abandoned run refused the planner's spawn, so `plan.yaml` does not exist. One command from a tier with
an unrestricted shell clears it, and the run resumes from prepared inputs with nothing re-spent.

## How this briefing was assembled

No report round was spawned. I read the run digest from disk:
`.harness/harness/features/FEAT-42-one-root-resolver/runs/2026-08-26-2-plan-product/digest.md` — the
only run this feature has. Everything else here is my own measurement at sha `3952814`, cited inline.

## What you need to do

Run these two, in the **main checkout**, then re-dispatch the plan phase:

```
python3 /Users/molchairuangutai/GitHub/harness/.claude/skills/harness/bin/inflight_registry.py release --agent harness-pm --root /Users/molchairuangutai/GitHub/harness
python3 /Users/molchairuangutai/GitHub/harness/.claude/skills/harness/bin/inflight_registry.py release --agent harness-product-lead --root /Users/molchairuangutai/GitHub/harness
```

**Never `release-all`.** It mutates the registry to `{}` (`inflight_registry.py:238-248`) — every
claim of every agent, including other features' live work. That is REQ-06's defect, and the printed
remedy the tool itself suggests.

I attempted the first command twice. The host permission layer denied both. I did not work around it.

## What blocked it, precisely

`dispatch-guard.sh` refused the `harness-pm` spawn at `PreToolUse` on single-flight, against a claim
left behind when a predecessor orchestrator context ended mid-run (`runs/2026-08-26-1-product/state.yaml`
still records `s1-plan` dispatched, never completed). The claim was ~17 minutes old against a TTL of
3600s, so it had no chance of expiring inside the cycle it was guarding — REQ-06 verbatim.

The same stale entry then refused the lead's *return*, because `validate-digest.py`'s children-in-flight
check reads the same registry. **One stranded claim blocks both ends of a run.**

It then refused **my own return too** — a third consumer, in a single planning attempt. The chain is
now: (1) `dispatch-guard.sh` refused pm's spawn, (2) `validate-digest.py` refused the lead's return
against pm's stranded claim, (3) `validate-digest.py` refused the orchestrator's return against the
lead's stranded claim. **The defect propagates up the tier chain**, each stranded claim creating the
next. That is a materially stronger case than BRIEF's REQ-06 currently makes, and the plan should
say so.

## The feature's own defect, measured live

Both claims were recorded in the **main checkout's** registry with `cwd:
/Users/molchairuangutai/GitHub/harness`, though every agent involved was assigned to the FEAT-42
worktree — which has no registry file at all. A guard was green and watching the wrong tree. This is
#866 reproduced by the attempt to plan its fix, and it is the strongest evidence the feature is worth
building.

## Three findings that change the plan's shape

**1. SC-01 cannot prove REQ-01 — a weak gate, and this repo has been burned there.** REQ-01 says no
site outside the resolver carries its own env fallback chain. The chain occurs **20 times across 15
files**; D-5's map removes 7 definitions covering 6 of them; **14 occurrences in 9 files survive, and
SC-01's file list cannot see one of them.** SC-01 would go green with REQ-01 plainly unmet. Seven
survivors are enforcement layer (`check-plan-routes.py:496` — the model implementation the design was
copied from — plus `check-domain.sh:152/:296`, `bash-write-guard.sh:194/:232`,
`validate-digest.py:821/:913`). Seven are not, and one of those, `inject-expertise.sh:31`, is a
**SubagentStart hook falling back to `$(pwd)`** — #866's defect verbatim in a file nobody scoped.
**This needs your call: widen scope, or narrow REQ-01 to the truth and backlog the rest.** What must
not ship is a broad requirement with a narrow gate.

**2. A test exemption goes stale on delivery.** `test-check-plan-routes.py:1167` carries
`KNOWN_DIRECTORY_PROBE = {"wayfind.py"}`, exempting it from the rule that every root probe names the
manifest. D-5 moves `wayfind.root()` onto the marker file, so the exemption stops being true and
starts hiding future regressions. Enforcement-layer test file, so main-session-direct.
(The analysis note's claim that `wayfind` has zero test coverage is false at HEAD — this is the
coverage, and it is an exemption rather than a test.)

**3. A fourth registry defect, not in BRIEF.** `release(root, agent)` (`:224-232`) pops the **oldest**
claim for a persona, but a returning agent means to release its **own**, newest. Measured live across
the lead's two returns: the stop hook released the abandoned lead's claim (`started_at 1787783953`)
and left the returning lead's own (`1787784855`) stranded. With two live same-persona agents, each
stop releases the other's — the still-running agent loses protection mid-run and the last claim leaks
permanently.

## One correction to the record

The dispatch and the analysis note both state the printed remedy names a path that does not exist in
this checkout. **That is false.** `inflight_registry.py` exists and executes. The real defects are that
`CLI_REL_PATH` (`:42`) is relative, so the remedy only resolves when cwd happens to be the root, and
that `release-all` wipes everything. BRIEF SC-07 already encodes the corrected version; no plan work
rests on the wrong premise.

## Budget

Cycles 0 of 10, runs 1 of 20. No rework has occurred — nothing was produced to rework. The blocked
run cost one spawn and produced usable artifacts (a corrected `send-back-criteria.md` written before
dispatch, so it could not be fitted to the answer). A re-dispatch resumes from those.

## Proposed backlog

| ID | Finding | Nature |
| --- | --- | --- |
| B-1 | The 9 files carrying the env fallback chain that D-5 does not touch, if you choose to narrow REQ-01 rather than widen scope | bug |
| B-2 | `release()` releases the oldest same-persona claim, not the returner's own (`inflight_registry.py:224-232`) | bug |
| B-3 | `validate-digest.py`'s children-in-flight check shares the dispatch guard's registry, so one stranded claim blocks a return as well as a dispatch | bug |
| B-4 | The analysis note's Section 5 item 2 ("wayfind has ZERO test coverage") is false at HEAD; the note is a signed input and carries a wrong fact | chore |
| B-5 | An orchestrator cannot clear a stranded claim — no tier below the main session has both the need and the permission | enhancement |
| B-6 | SC-11 may now be settleable from disk, contrary to BRIEF:104 which calls it operator-only | chore |

Anything you do not strike becomes a backlog issue on acceptance. Anything not listed here dies
silently.
