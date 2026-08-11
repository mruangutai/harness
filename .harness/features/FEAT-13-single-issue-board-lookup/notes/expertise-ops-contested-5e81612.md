# FEAT-13 — contested Expertise ops, verbatim

**Why this file exists.** FEAT-12 was distilling into the same shared `.harness/expertise/` files
while FEAT-13 closed, so six files are contested and were deliberately **not committed**. They sit
modified-but-uncommitted in the worktree
`.claude/worktrees/FEAT-13-single-issue-board-lookup`. The run digests that hold these ops are
gitignored (`.harness/features/*/runs/**`) and the worktree is disposable, so **this committed file
is the only durable copy.** Apply these against the settled tree once FEAT-12 lands.

**Do not merge the six files textually.** `harness-backend-dev.md` in particular is a full-file
**renumber**, so a three-way merge conflicts broadly and a careless hunk-by-hunk resolution can
silently reproduce the very revert this was avoided to prevent.

Uncontested and already committed: `harness-product-lead.md`, `harness-ui-reviewer.md`,
`harness-validator-lead.md` (at `2c9ccf6`) and `harness-orchestrator.md` (at `e4be554`).

---

## harness-backend-dev.md — RENUMBERED, read the deletions first

**Two entries were DELETED** by its own judgement, and the renumber cascades from them:

- old `P-04` — diffing a byte-identical claim against the deployed copy under
  `~/.claude/skills/harness/bin/`.
- old `P-09` — asserting an exception's VALUE slot with a value absent from every compared message.
  Dropped as subsumed by the surviving pairwise-distinctness rule (now `P-08`). The lead recorded a
  mild reservation: the two are adjacent, not identical.

Old `P-05`–`P-08` shift down to `P-04`–`P-07`; old `P-10`–`P-11` become `P-08`–`P-09`. **Added:**

- `P-10: WHEN a task's verify pins a claim to a specific section via a presence grep DO scope the grep to the extracted section text, not the whole file — a substring present elsewhere in the file lets the check pass while asserting nothing about the section it names.`
- `P-11: WHEN a task's intent cites a specific line as an existing assertion of old wording to update DO read that line first — it may be a docstring or unexecuted comment, not a check. If no executable path exercises it, add new RED-then-GREEN tests instead of a rewrite.`
- `P-12: WHEN naming a test assertion for a property DO name it only for what the assertion can actually distinguish — a call-tuple equality check named "no state scoping" asserts nothing about state and passes vacuously even after the real state-scoping property breaks.`
- `P-13: WHEN production code was edited before RED was watched DO disclose the lapse, then reconstruct RED as evidence: hash the edited file, swap in `git show HEAD:<path>` over it, confirm the expected failures, restore, and re-verify the hash — never treat it as harmless.`
- `P-14: WHEN asserting on recorded subprocess argv against this repo's gh-call fakes DO scope comparisons to argv[1:3], not argv[0:2] — argv[0] is always the gh binary, so a [0:2]-anchored assertion against a subcommand pair can never match and passes vacuously.`
- `P-15: WHEN measuring a live call's cost or side effects DO bracket it with a null-control read taken before the window and derive any independent reference value only after the window closes — deriving the reference inside the window risks contaminating the number being measured.`
- `G-09: WHEN validating a live or side-effecting measurement against changed code DO confirm the loaded module's `__file__` resolves under the worktree being tested, not a stale main-checkout copy — a silently wrong root produces a plausible but false measurement.`

## harness-code-reviewer.md — Patterns now AT cap 15/15

- `P-15: WHEN you dismiss a candidate finding as a non-issue DO record it explicitly with the reason rather than omit it silently — the record stops a downstream reader (a lead, a panel digest) from re-raising the same question.`
- `G-03: WHEN a test double is the only thing exercising a production call's arguments DO check whether the double actually reads them — a fake returning fixed values regardless of its `fields`/`args` parameter leaves that argument list unpinned, so deleting a required field stays fully green.`

## harness-eng-lead.md

- `G-04: WHEN a receipt path is named both by the team file's `outputs:` template and by the approved plan's `files:` list DO write the plan's literal path — a `verify:` clause greps the plan's string, so the rendered template leaves the gate red on correct work.`
- `G-05: WHEN dispatching a distillation from a worktree DO grep the entry IDs from both that copy and the main checkout's and compare — a worktree branched before the last distillation carries a stale copy whose write reverts the prior feature's entries, every format check still green.`

## harness-pm.md — two REPLACEMENTS, one addition

`P-07` **replaced** (the incumbent was about presupposition between criteria):

- `P-07: WHEN judging whether an unmet criterion is undischargeable DO read the signed proof standard. If it forbids the only technique that could instantiate the condition, it cannot also demand it: the strongest proof permitted inside the standard is the proof, and the route is a fix cycle.`

`P-10` **replaced** — and this one is a **merge, not a kill**: both sides widened the same incumbent
in different directions, so re-judge rather than overwrite.

- `P-10: WHEN a criterion, a task step, or a carried-forward evidence pointer cites a location DO anchor it on content text, never a line number. Any edit above shifts the rows below, so anchors rot within one cycle: the verdicts still stand while every pointer under them lands wrong.`

Added:

- `G-12: WHEN citing a file:line as evidence DO confirm which checkout the path resolved in. A sibling checkout on another branch holds a different copy at the same path, returns unrelated content at the cited lines, and nothing errors — the read succeeds and reads as proof.`

**Caution:** the main checkout's Gotchas may already be at 15/15 and its `G-12` slot taken, so this
entry needs both a free id and a displacement target chosen by pm.

## harness-qa.md

- `P-11: WHEN a fake/stub returns canned data regardless of arguments passed (e.g. ignoring a `fields` param) DO assert the literal argument value at each call site — an argument-blind fake keeps call-count-only assertions green even when the caller silently narrows what it requests, hiding a fail-closed defect.`

## harness-security-reviewer.md — opens its empty Outcomes section

- `P-10: WHEN a diff synthesizes a sparse object standing in for a fuller one DO trace every consumer field-by-field to its write or auth check — a permissive `.get()` reading an omitted key as absence-equals-permission is the fail-open shape to rule out.`
- `P-11: WHEN a security-relevant detail is observed but pre-existing/unchanged by the diff DO record it in the review as assessed-and-dismissed rather than omitting it — a recorded non-finding stops a later reviewer re-raising it; a silent drop does not.`
- `G-06: WHEN a diff is scoped IN and returns zero findings DO set severity_max to info, not n/a — n/a is reserved for scoped-out diffs; conflating them misreports whether the surface was actually assessed.`
- `O-01: WHEN a surface looks clean on first read DO close with identity-level evidence (assertions proving equality, consumers traced to their actual write) not a read-and-conclude — a zero-finding review is otherwise indistinguishable from a shallow pass to anyone downstream.`
