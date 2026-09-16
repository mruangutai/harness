# D-14 — the operator's pre-merge manifest-deviation acceptance

**BLUF.** The operator's ruling of 2026-09-09 is recorded as **D-14** in `plan.yaml:175-208`, and the
known-red gate is now disclosed in `BRIEF.md:324-335` under `## Verification gaps`. The qa gate may
pass with the single `check-plan-routes.py` manifest-deviation violation outstanding, provided its
report cites D-14. Nothing else changed: 20 tasks, `approval:` bytes verbatim, no gate edit, no T-19
revert, no commit.

## What was decided

Route (a)-accept: the one violation is an expected pre-merge condition and expires at merge. Scope is
exactly one violation — the `.harness/team-config.yaml` owner-manifest deviation. A second violation
of any kind, or this one surviving the merge, is a failure and is not covered.

## Rejected, and why (both named in D-14 because the operator rejected both)

1. **Alter `check-plan-routes.py` so a key removal stops counting as a deviation.** Rejected: it
   amends a gate so this feature's own change passes — the gate-weakening the factory forbids. The
   tool's tolerance boundary is deliberate:
   `case_41_t09_comment_only_manifest_difference_is_NOT_a_deviation` PASSES, so comment-only branch
   edits were tolerated by design and semantic ones were not; a removed key is semantic.
2. **Revert T-19 and defer the removal to a post-merge chore.** Rejected: it contradicts the
   operator's own D-13, which ordered `cli_min_version` removed from all five sites.

The product lead independently recommended (a). D-14 names the OPERATOR as the ruler, and says so —
this feature already had to correct one entry that read as its recommender's (D-12/D-13).

## Verification — raw output

Plan invariants after the merge (`plan-merge.py apply` printed `ADDED D-14` / `APPLIED …`):

```
20 ['D-01', 'D-02', 'D-03', 'D-04', 'D-05', 'D-06', 'D-07', 'D-08', 'D-09', 'D-10', 'D-11', 'D-12', 'D-13', 'D-14'] {'date': '2026-09-09', 'approved_by': 'molchairuangutai', 'status': 'approved'}
```

20 tasks unchanged; exactly one more decision; `approval:` unchanged (`approved`, `molchairuangutai`,
`2026-09-09`).

Gate, run from the worktree with the worktree's own copy of the script (root resolution reads the
script's location — the main checkout's copy scans main's four plans and reports 0):

```
1 violation(s) across 5 plan(s)
examined 85 feature dir(s); 80 skipped as shipped
EXIT=1
```

The single violation, unchanged in kind and count from before this write (grep of
`^(VIOLATION|DEVIATION)` returns exactly 1 line; every per-task line is `OK`):

```
DEVIATION /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-56-central-onboarding-model/.harness/team-config.yaml differs from /Users/molchairuangutai/GitHub/harness/.harness/team-config.yaml; routes were resolved against the owner manifest because that is what the hook consults
```

The landed D-14 entry is `plan.yaml:175-208` (`choice:` 176-190, `because:` 192-207, `dec: none` at
208). The new BRIEF bullet is `BRIEF.md:324-335`.

## `dec:` judgement

`dec: none`. D-14 is bounded to this branch and self-expires at merge, so it fails the DEC bar on
durability — a `DECISIONS.md` entry would outlive the condition it describes and read as standing
licence. The durable, repo-general statement it hints at — *any feature editing the shared owner
manifest reddens `check-plan-routes.py` from every worktree of its branch until merge* — is worth a
DEC entry, but it is not this ruling and not this dispatch (T-16 and T-20, the doc tasks, are closed).

## Open questions

- Q1 (non-blocking): should the structural property above be raised as a separate backlog item, so a
  later feature editing `.harness/team-config.yaml` does not rediscover the red gate as a defect?
