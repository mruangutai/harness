# FEAT-09 residual backlog — the rationale

Routed out of `feature.yaml` per the DEC-150 shape gate's own advice: *"rationale goes in
notes/; state files carry no history."* `feature.yaml` keeps one line per item; the reasoning is
here. Nothing below is blocking.

## B-1 — a `shared:` file is falsely REJECTED by the checker

**Needs a user ruling; answering it amends DEC-179.** A PLAN task naming a `shared:` file
(`package.json`, `pyproject.toml`, lockfiles) is rejected by `check-plan-routes.py`. Note the
direction: the dispatch predicted this would fail *open*; the truth is the opposite — it fails
**closed** at `:64`. Top of the non-gating list because any dependency work hits it immediately.

## B-2 — SC-08 is weaker than its clause count suggests

Three of SC-08's four clauses are **source greps**, so they are respellable — a reimplementation
that avoids the literal strings passes. Case 17's mid-pattern `*` never crosses a `/`, so an
`fnmatch` reimplementation would pass it too. The design rule is roughly a third as guarded as
"four clauses" implies. **This is issue #74 mode 3 in the wild**: the clauses share one matching
technique, so the set has one blind spot rather than four.

## B-3 — the matcher itself was never verified

`matches()` / `glob_to_re()` are UNMODIFIED, so the panel established only that the matcher was
not *re-implemented* — never that it is *correct*. Separately, the two modes do not share input
normalisation: the hook uses `os.path.abspath` (cwd-relative), `--resolve` uses
`os.path.join(root)`.

## B-4 — the checker has never been observed in use

No reviewer could tell whether a planning agent actually **runs** it; `BRIEF.md:91-93` names this
limitation itself. It has been exercised against synthetic fixtures and FEAT-09's own PLAN only,
so the false-positive rate against the tree's other live PLANs is **unmeasured**.

## B-5 — a stale source anchor, and it is not the builder's

`check-plan-routes.py:16` and `test-check-plan-routes.py:142` cite `check-domain.sh:190-197` for
the prefix-comparison bug; the real record is at `:61-69`. **`PLAN.md:210` carries the same wrong
anchor** — the approved plan is the origin, so this is a planning defect, not a build defect.

## B-6 — the `team` token is not validated

Within the approved intent. `LEGAL_TOKENS` at `:42` is display-only, and `PLAN.md:177-181`
specifies that a granting agent means OK regardless of the token. A design limit, not a defect.

## B-7 — argv-less invocation gives a clean answer from a run that checked nothing

With no argv, `check-plan-routes.py` globs relative to CWD, so from a non-repo-root cwd it prints
0 violations across 0 plans and exits 0. Not reachable via the documented invocation — but it
**becomes blocking if B-8 lands**, because an invariant that silently checks nothing is worse than
no invariant.

## B-8 — promote the route checker to a `check-state.sh` invariant?

Open design question, carried from the plan phase.

## B-9 — the checker copies `check-state.sh`'s task-block regex (D-08)

Two copies of one regex. Consolidate, or accept the duplication deliberately?

## B-10 — two historical plans use a token this feature retires

`squad-dispatched`. Leave them as history, or normalise?

## B-11 — a blank `files:` field is mishandled

Code reviewer's MED finding, unresolved.

## B-12 — INV-17 shape-checks a handoff note too late

The handoff cap **is** enforced at write time. What `check-state.sh` INV-17 adds is a re-check
only once `phase:` moves **past** the seam — so a note that reached disk over-cap sits unflagged
for the whole phase it describes, which is exactly when a successor reads it. `handoff-build.md`
was 63 lines against a 60 cap and surfaced only when the phase advanced.

## B-13 — the state-file cap story, corrected twice

The orchestrator first recorded that `feature.yaml`'s 200-line cap was **not** enforced, then
corrected itself: it **is**, having rejected four successive drafts at 217/208/206/205 lines. The
main session then found the real shape of it — the cap is enforced against **`Write` only, and
`Edit` bypasses it entirely**. Both earlier observations were true and neither was the whole
picture. See `notes/vf2-shape-gate-edit-bypass.md`; that one is a live must-fix, not backlog.
`STATE.md` has no mechanical cap at all.
