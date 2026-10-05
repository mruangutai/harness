# Disposable checkout at the review pin

Reviewers and QA MUST read this before creating a checkout at `review_sha`, including for a
perturbation proof. The resident isolation and cleanup rules live in `harness-code-review` and
`harness-verification-rules`; this is their shared procedure (DEC-238, #1994).

Use only the managed helper, never a bare `git worktree add --detach` into a path nobody sweeps —
sixteen of those, at ~800 MB each with `node_modules`, leaked from one feature. Do not alter the
primary checkout or its dirty changes to reach the pin.

From the feature worktree, with the authoritative full `review_sha` and your own feature, run and
persona identifiers:

```sh
python3 <HARNESS_CONTROL_PLANE_ROOT>/.agents/skills/harness/bin/pinned-checkout.py add --feature <FEAT> --run-id <run-id> --persona <persona> --sha "$review_sha"   # prints the path
python3 <HARNESS_CONTROL_PLANE_ROOT>/.agents/skills/harness/bin/pinned-checkout.py remove --feature <FEAT> --run-id <run-id> --persona <persona>                    # on return, always
```

The helper refuses an abbreviated or unknown SHA. It creates
`<HARNESS_CONTROL_PLANE_ROOT>/.claude/worktrees/.pins/<FEAT>--<run-id>--<persona>/`, keyed to one
reader so your return never deletes a sibling reader's tree. Use the printed path; install and
build inside it, not in the primary checkout.

Before removal, copy evidence out to the feature's `runs/<run-id>/`. Remove your checkout with the
same feature/run/persona key on **every return**, including `FAIL` and `BLOCKED`, and including
external fleet repositories. The control-plane post-merge sweep removes anything a dead run leaves
behind after a day; a fleet repository has no hook, so `remove` on return is its only cleanup.
