# Close-out spawn baseline — taken BEFORE #80 lands

Recorded so #80 can be validated later. Without this, the change is unfalsifiable: nothing in the
tree measures close-out cost, and after the merge there is no pre-state left to compare against.

## Method

Count agent spawns per feature from `runs/*/digest.md` — each digest is one lead spawn plus
`len(DIGEST.members)` member spawns. A run counts as close-out when its dir name contains
`distill`, `goalcheck`, `ship` or `close`.

Sample is FEAT-06/07/08 only: earlier features use a pre-current digest format that does not parse,
so including them would silently undercount rather than fail.

```
FEAT-06-team-layer-inv6              close-out   2 /  26 spawns    8%
FEAT-07-verify-teeth-batch-probe     close-out  10 /  31 spawns   32%
FEAT-08-remove-cost-tracking         close-out  11 /  34 spawns   32%
TOTAL                                close-out  23 /  91 spawns   25%
```

**Which runs counted, so this is auditable rather than trusted.** PR #141's reviewer ran their own
parser and got 7 / 29 / 40%, so the classification is written out here in full — a later
measurement must use the same rule or it is comparing different things:

| Feature | close-out runs counted (spawns) |
|---|---|
| FEAT-06 | `goalcheck-product`(2) |
| FEAT-07 | `close-eng`(2), `close-product`(3), `close-validator`(3), `goalcheck-product`(2) |
| FEAT-08 | `distill-apply-product`(2), `distill-apply-validator`(1), `distill-eng`(2), `distill-product`(3), `distill-validator`(1), `goalcheck-product`(2) |

Spawns per run = 1 lead + `len(DIGEST.members)`. The divergence is almost certainly the
classification rule, not the arithmetic: FEAT-06 has exactly one close-out run under this rule, and
whether `goalcheck` counts as close-out at all is a judgment a different parser may make
differently. **That is itself a reason to prefer the binary measure below.**

## The caveat that decides how to read a follow-up measurement

**The variance is larger than the effect being chased.** FEAT-06's close-out was 8% and FEAT-07's
was 32% — a 4× spread across three features under the SAME playbook. So a single post-change
feature landing at, say, 20% proves nothing: it is inside the existing spread.

Validating #80 honestly needs **two or three features**, or a direct count of the specific thing
removed rather than the aggregate: **did a close-out spawn a three-lead report round, yes or no.**
That second measure is binary, has no variance, and is the one worth taking.

## What #80 actually changed, stated as a testable prediction

1. **No close-out run should exist whose purpose is a lead reporting its domain.** Directly
   checkable from run-dir names and digests.
2. **Ship-refresh and distillation should appear as one dispatch turn**, not two rounds. Checkable
   from `dispatched_at` timestamps in the leads' `state.yaml`, which are written before each spawn.

## Honest limit

Nothing enforces either prediction. `check-docs.sh` checks wording, `run-unit-tests.sh` touches no
file this change edited, and no hook or invariant inspects close-out shape. An orchestrator that
spawns the report round anyway produces a green tree.

Issue #79 (count and budget RUNS) is the instrument that would make prediction 1 automatic. It is
currently ranked *after* #80, which means #80 ships unmeasured — see the note on ordering in the PR.
