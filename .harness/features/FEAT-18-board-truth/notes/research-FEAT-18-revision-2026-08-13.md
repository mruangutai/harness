# FEAT-18 — revision of the UNSIGNED plan, 2026-08-13 — D-08 and SC-08 struck

**BLUF.** All nine sites are revised. The plan stays at **8 REQ, 6 tasks, 8 decisions** (D-08 kept
with a strike record, DEC-188 shape). Both approval blocks are untouched and still `pending`.
Nothing was re-measured: every figure came from `notes/answers-2026-08-13-revision.md`.

## What changed, and where

| # | Site | What it now says |
|---|---|---|
| 1 | `plan.yaml` D-08 | New `struck:` key carrying the strike record; `choice:` prefixed `STRUCK - no longer in force`; `because:` prefixed `RECORDED, NO LONGER LOAD-BEARING` with its original text intact. Both breaks recorded as **measured, not predicted**. |
| 2 | `BRIEF.md` SC-08 | Struck in place, entry kept, `verify: none — struck`. |
| 3 | `BRIEF.md` REQ-07 | **Restated, not deleted**, to the surviving half: no harness-composed text in a PR body closes an issue. T-06's `traces: [REQ-07, REQ-08]` still resolves. |
| 4 | `BRIEF.md` out-of-scope fence | `Closes #N` restated as the operator's standing preference; a second fence added recording that teaching `branch-create-gate.sh` `gh` subcommands is now unnecessary and out. |
| 5 | `plan.yaml` D-03 `because:` | Sole-driver claim now unqualified, with the workflow roster folded in and marked READ, not assumed. Notes that the strike **restores** the Done-exemption premise the linkage had falsified; the exemption itself is unchanged. |
| 6 | `plan.yaml` T-06 title | "plus the linked branch" → "plus how the build branch is created". |
| 7 | `plan.yaml` T-06 `intent:` §3 | Plain `git checkout -b feat/<FEAT-id>`. Keeps the no-composed-closing-text clause. Adds one caution: make the edit with the editor, not by echoing through a shell. |
| 8 | `plan.yaml` T-06 `verify:` | The `gh issue develop` clause replaced by `grep -q "checkout -b feat/"`; the six-subcommand loop and the stderr clause are byte-unchanged. Still a literal `\|` block. |

## The verify trap, and the evidence it is closed

The replacement clause carries **no `git` token**, so `branch-create-gate.sh` cannot match it.
Verified, not reasoned: the task's `verify:` string was loaded from the file, wrapped as a hook
payload and fed to the live gate — **empty output, exit 0, no adjudication**.

It is also **discriminating**: `grep -c "checkout -b feat/" .claude/skills/harness/SKILL.md` returns
**0** at the working tree today, so the clause fails now and can only pass after §7 is executed.
The clause and the intent agree by construction — §7 names the exact substring the verify greps for.

`check-plan-routes.py` on the revised plan: **0 violations, exit 0** (T-04's `DEVIATION` line is
pre-existing and informational, not a violation).

## The item-9 coverage judgement — stated in `BRIEF.md ## Verification gaps`

SC-08 was the **only** criterion in this feature touching the live GitHub API, so after the strike
**no criterion here observes GitHub at all**; the carrier roster drops from three to two, and one of
the two is a human looking at a board. That is the honest loss. It is smaller than it reads: SC-08
read back `linkedBranches` on an issue — a different query surface from the `projectV2` field-set the
automated criteria fake — so it never proved the field name `Status`, the six option names, or the
item-id lookup, which are the three things the gap actually names. No replacement SC was invented:
the behaviour SC-08 graded no longer exists.

## Open, and deliberately untouched

- **Q1 is NOT resolved** and no answer is written anywhere. It rides to the signature.
- **Q2 is moot** — D-08 is struck, so the gap the advisor's ruling accepted cannot occur. Q2 appears
  in **neither** `plan.yaml` nor `BRIEF.md`, so there was nothing for me to restate; its copy in
  `STATE.md` is the orchestrator's.
- Scope was not widened: no new task, no new REQ, no new SC.
