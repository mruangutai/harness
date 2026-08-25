# T-10 acceptance — #728 closes itself

The operator named #728 as the end-to-end acceptance test: this change must close it and land its
card at `Done` with nobody touching GitHub. It did.

**It was the hard case, not the easy one.** #728 is FEAT-34's recorded parent and carries THIRTEEN
children, #818 through #830. Before the run all thirteen were CLOSED on GitHub and all thirteen of
their cards read `Review` — so under the new rule every one of them was OPEN, and the run had to
exercise the children-first ordering (D-04) and the open-child skip (D-03) together. A single-pass
implementation would have skipped #728 and printed a held line.

## The command

    python3 .claude/skills/harness/bin/gh-sync.py ship \
      /Users/molchairuangutai/GitHub/harness/.harness/harness/features/FEAT-34-worktree-act3-enforced

Exit status **0**. Empty stderr. **No `gh` command was typed by hand**; the only hand-run `gh` calls
in this task were the `gh issue view` reads recorded below.

## What must hold — each recorded as its own line

```
#728 CLOSED Done
#806 CLOSED Done
#818 CLOSED Done
#819 CLOSED Done
#820 CLOSED Done
#821 CLOSED Done
#822 CLOSED Done
#823 CLOSED Done
#824 CLOSED Done
#825 CLOSED Done
#826 CLOSED Done
#827 CLOSED Done
#828 CLOSED Done
#829 CLOSED Done
#830 CLOSED Done
```

Asserted **per number**, never as a count.

- the output carries **no** `gh-sync: HELD` line naming #728 — no held line of any kind;
- the output carries **no** `gh-sync: FAILED` line at all;
- it carries the single line `gh-sync: every recorded card is at Done`;
- it contains **no** occurrence of the substring `gh-sync: SKIP`;
- **no line shows an issue close call.** Every one of the fifteen cards reached `Done` by a station
  write, and GitHub's `Auto-close issue` workflow did the closing.

## The captured output, verbatim

```
gh-sync: issue #818 -> Done
gh-sync: issue #819 -> Done
gh-sync: issue #820 -> Done
gh-sync: issue #821 -> Done
gh-sync: issue #822 -> Done
gh-sync: issue #823 -> Done
gh-sync: issue #824 -> Done
gh-sync: issue #825 -> Done
gh-sync: issue #826 -> Done
gh-sync: issue #827 -> Done
gh-sync: issue #828 -> Done
gh-sync: issue #829 -> Done
gh-sync: issue #830 -> Done
gh-sync: issue #728 -> Done
gh-sync: issue #806 -> Done
gh-sync: issue #728 -> Done
gh-sync: every recorded card is at Done
gh-sync: audit — LABEL: issue #860 is not_planned and carries no 'abandoned' label
gh-sync: audit — LABEL: issue #610 is not_planned and carries no 'abandoned' label
gh-sync: audit — LABEL: issue #552 is not_planned and carries no 'abandoned' label
gh-sync: audit — STATUS: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-40-harness-writes-done/.harness/harness/features/FEAT-12-end-copy-distribution records status 'Done' (column 'Done') but its parent #223 reads None
gh-sync: audit — STATUS: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-40-harness-writes-done/.harness/harness/features/FEAT-40-harness-writes-done records status 'Ready' (column 'Ready') but its parent #842 reads 'Plan'
gh-sync: audit — 5 finding(s)
gh-sync: milestone #26 closed
gh-sync: pr already recorded as #837 — not overwritten
gh-sync: feature.json status -> Done
```

stderr was empty.

## Two things in that output worth naming rather than leaving to be rediscovered

**#728 is written twice** — once as a `source_issues` entry and once as the parent, because FEAT-34
records it in both places. The second write is a harmless no-op against a card already at `Done`, and
the run is idempotent, so this is a cosmetic duplicate rather than a defect. It is recorded here so a
later reader does not mistake it for two different cards.

**The audit found five things, and it was supposed to.** This is REQ-06's compensating control
working on its first real run:

- three `LABEL` findings — #860, #610 and #552 are `not_planned` and carry no `abandoned` label.
  #860 is my own T-01/T-02 probe, closed by hand through `board-station.py` before `abandon` learned
  to label. The other two predate this feature.
- two `STATUS` findings — FEAT-12's parent #223 has no station at all, and FEAT-40's own parent #842
  reads `Plan` while the feature records `Ready`.

None of them is caused by this run. All five are exactly the class of drift the audit exists to
surface, and it surfaced them at ship, which is where the decision is made.
