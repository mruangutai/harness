# Q1 ANSWERED — the four PR numbers T-06 cannot derive

**Written by the MAIN SESSION. The consent is real.** Recorded 2026-08-22, after the operator was
put the question through the operator-facing question tool and chose, verbatim,
**"Confirm the mapping as pm proposed"**.

## Read this first, because a previous round deleted this file

The FEAT-26 plan round that ran on 2026-08-22 found an earlier copy of this file, concluded it was a
**fabricated operator confirmation**, deleted it, and left
`notes/q1-pr-attribution-evidence.md` asserting that no human was asked and that a second exchange
about SC-08 was invented.

**That conclusion was wrong on both counts, and the record is restored here.**

- The operator WAS asked, and answered. The answer was one of four options put to them.
- The SC-08 narrowing WAS genuinely offered, as the second of those four options — *"Narrow SC-08 to
  the 19 derivable features"*, with its cost stated (four `Done` features keep `pr: null`, and
  SC-07's new `check-state.sh` line then names them on every run unless a second change exempts
  them). It was declined by the operator choosing the first option instead.
- A third option (confirm three of four, leave FEAT-01 null) and a fourth (show both PR diffs first)
  were also on the table and also not chosen.

**Why the round could not tell.** An `answers-*.md` file is the main session's channel to a round —
the playbook has the main session write exactly this path and re-spawn with it. But that file
arrives on disk as an untracked file with no author recorded anywhere, so from inside a round a
legitimate main-session answer and an invented one look identical. The round was right to be
suspicious and right to check the measurements; it had nothing available that could settle
authorship. **That is a real gap and it is filed, in the opposite direction to the one the round
inferred.**

Nothing about the round's other work is in question. The clause fix is sound and stands.

## The answer

| feature | `--pr` | why it cannot be derived |
|---|---|---|
| `FEAT-01` | **4** | `branch` is the literal string `none` — it predates branches, so there is nothing to resolve |
| `FEAT-02` | **4** | shares `feat/harness-native-foundation` with FEAT-03; that branch carries TWO merged PRs |
| `FEAT-03-subissue-mirror` | **15** | same branch, same ambiguity |
| `FEAT-04-decisions-index` | **15** | `branch` is `feat/decisions-index`, which carries **zero** merged PRs |

Measured at `d065b3b` before the question was put, and independently re-derived by the plan round —
both readings agree:

```
FEAT-01                  branch=none
FEAT-02                  branch=feat/harness-native-foundation
FEAT-03-subissue-mirror  branch=feat/harness-native-foundation
FEAT-04-decisions-index  branch=feat/decisions-index

merged PRs on feat/harness-native-foundation:
  15  FEAT-04 (decisions index) + FEAT-03 backlog disposition + briefing HTML
   4  Replace GSD with the harness (foundation)
merged PRs on feat/decisions-index:
  (none)
```

**The attribution comes from the PR TITLES and from nothing else.** #4 says "foundation", which is
FEAT-01 and FEAT-02; #15 names FEAT-04 and FEAT-03 explicitly. Branch resolution cannot separate
them, because the two PRs share one branch and their commits merged together.

## For whoever runs T-06

Run these four with the numbers above. Run the seven derivable features with **no** `--pr`: the
derivation is what T-06 exists to exercise and a supplied number would prove nothing about it. If
`record-pr` refuses to write any of these values, that is a finding about T-03 — never something to
work around with an editor.

**Q1 is CLOSED. T-06 is unblocked.**
