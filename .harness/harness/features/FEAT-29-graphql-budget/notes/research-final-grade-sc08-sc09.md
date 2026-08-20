# Final independent grade — FEAT-29 SC-08 and SC-09

**SC-08 unmet. SC-09 met.** SC-08 fails on half (b) — its cheapness half (a) is clean, but a live,
in-force file created by this very feature states the corrected number with no condition at all:
`.claude/skills/harness/bin/gh_cost_log.py:4,15,50`. That is genuinely wrong, not merely unproven.
SC-09's rule conjunct is present in the COMMITTED tree at `27b85f2`, verified with `git show`.

Graded on the signed text at `.harness/harness/features/FEAT-29-graphql-budget/BRIEF.md:104-133`,
with the three operator rulings applied as settled: three governing conditions (board, item count,
commit), binding per document, and SC-09's conduct conjunct dropped.

## SC-09 — met

Instrument: `git show 27b85f2:CLAUDE.md` (read-only). Not a working-copy read — the criterion turns
on the committed tree, and `Read` cannot distinguish the two.

`27b85f2:CLAUDE.md:55` reads:

> `- Never write a shell wait loop. A Bash foreground timeout detaches rather than kills, so a loop outlives its own bound. Use Monitor (its timeout_ms terminates) or run_in_background.`

Three conjuncts, each satisfied by that one line: forbids shell wait loops **outright** ("Never
write"), names **Monitor**, names **`run_in_background`**. It is in the committed tree at the pin —
`git rev-parse 27b85f2` → `27b85f29776933af47c56ab3719192980629774a`, `git grep -n ... 27b85f2 --
'*.md'` returns `27b85f2:CLAUDE.md:55`. The dropped conjuncts (the 10-second polling conduct, the
per-poll cost citation) are not graded, per rulings 3 and the signed amendment at BRIEF.md:123-132.

## SC-08 — unmet

### First clause — corrected in place: satisfied

`.harness/notes/grilling-graphql-cost-2026-08-10.md:14-23`. The 31-point exclusion bullet is struck
in place (`~~...~~`) with the text preserved, and the replacement at `:17-21` carries **506 GraphQL
points, on board 3 with 473 items, at commit `6bbd706`**, dated `STRUCK 2026-08-19 (#571)`, quotes
**490 to 506**, and records 608 explicitly as "a contaminated upper bound". Every element the clause
names is present.

### Half (a) — "no in-force document asserts item-list is cheap enough to ignore": satisfied

The only surviving assertion of that shape is `FEAT-11-graphql-field-resolve/BRIEF.md:171`
("stays as it is — 31 points, once per invocation"). `FEAT-11-graphql-field-resolve/feature.json`
reads `status: Done`, so it is frozen dated history and out of scope by the first amendment. I
checked lifecycle status for every feature directly from its own `feature.json`: FEAT-13 (the other
31-point carrier, `BRIEF.md:115`) is also `Done`; FEAT-19 is `Abandoned`; **FEAT-26 and FEAT-28 are
`Plan`** — in force, and they carry no GraphQL cost figure at all. FEAT-29 is `Building`.
`.harness/notes/grilling-board-read-lookups-2026-08-10.md:69` ("~102 points per 100 items; making
that cheaper is GitHub's business") is a scope exclusion about the cost *model*, not a cheapness
claim — the same file measures the call at 203 points. No violation of (a).

### Half (b) — "no such document states a bare corrected number without its condition": VIOLATED

**Violation 1 (decisive) — `.claude/skills/harness/bin/gh_cost_log.py:4-6, :15, :50`.**
Live production code shipped by this feature; committed at the review sha (`git show
27b85f2:.claude/skills/harness/bin/gh_cost_log.py` carries the same lines 4 and 15). It states the
corrected figure three times — ":4 burned **506** GraphQL points", ":15 and :50 costs **5** points
instead of **506**" — and the file contains **none of the three conditions anywhere**:
`grep -nE "board|items|commit|6bbd706|8c2c24d|473|486"` over the file returns nothing. Under ruling 2
a document may state its condition set once and let its figures inherit; this document never states
it. Mitigation, stated honestly: `:5-6` cites
`.harness/harness/features/FEAT-29-graphql-budget/notes/measurement-before.md`, which records
`board_items: 486` and `sha: e1bcdc1` (`:16-17`) — so the figure is one hop from re-derivable. I
judge a pointer to be *delegating* the condition rather than stating it, and the delegate itself
never names the board. This is exactly the rot shape the criterion exists to stop, now sitting in a
source file that outlives every note around it.

**Violation 2 (weaker, but real) — `.harness/notes/grilling-board-read-lookups-2026-08-10.md:73-74,
:77-80, :89-90`.** In force by parity: it is a standing `.harness/notes/` grilling note, not a
feature artifact, and its sibling `grilling-graphql-cost-2026-08-10.md` is the very file SC-08
orders corrected in place — a document class cannot be frozen history and correctable-in-place at
once. `:89-90` makes its numbers explicitly *corrected* ones: "#217's own body cites 31 points…
That figure is stale… **203 supersedes it**." Its condition line `:73-74` gives board 3, 163 items
and the date — **two of three; no commit**. BRIEF.md:119-121 names the missing commit as the
decisive gap ("a figure without its commit cannot be re-derived, and that is precisely how the 31
survived nine days unfalsifiable"), so two-of-three does not discharge the rule as settled. Weaker
than violation 1 because the note pins the exact `gh` command line, which makes the repo commit less
load-bearing for a raw-CLI measurement.

### Repository-tier Expertise — the call nobody owns: IN FORCE, and it complies

I judge `/Users/molchairuangutai/GitHub/harness/.harness/harness/expertise/**` to be documents
**still in force** for SC-08's purposes. Reasoning: a `SubagentStart` hook injects them into every
spawn (the mechanism is stated in the `harness-expertise` rule and I observed my own injection this
run); they carry no date; they are maintained by amendment rather than frozen. A rotted figure there
does not sit waiting to be read — it is pushed into every agent's beliefs on every spawn. If
anything in this tree is in force, this tier is, and exempting it would be the single most
consequential exemption available.

Graded, it complies. `.harness/harness/expertise/harness-orchestrator.md:8-11` (G-01) carries both
figures with **all three conditions each** — "~500 points (board 3, 486 items, `e1bcdc1`)" and "5
(board 3, 473 items, `8c2c24d`)" — and its instruction is to re-measure rather than recall, the
opposite of a cheapness claim. A sweep of both tiers (`.harness/expertise/**` and
`.harness/harness/expertise/**`) for `graphql|item-list|points` finds no other cost figure. So the
awkward area is clean; SC-08 does not fail here.

### Scoping I applied, stated so it can be overturned

I treated as in force: repository code and skills, standing `.harness/notes/` grillings, `docs/`,
`CLAUDE.md`, both Expertise tiers, unshipped features' artifacts (FEAT-26, FEAT-28), and the live
feature's governing trio (`BRIEF.md`, `plan.yaml`, `STATE.md`). I treated dated per-run records —
`runs/*/digest.md`, ship reviews, handoffs, measurement notes — as records of a moment, the same
class the first amendment exempts. Widening to that class would add candidates, not remove violation
1, so the verdict is not sensitive to the scoping.

The governing trio itself passes: `BRIEF.md:11` states board 3, 473 items, `6bbd706`;
`plan.yaml:439` states the same set; `STATE.md:40-42` states it explicitly once ("conditions stated
once for this document") and its figures inherit. That is ruling 2 working as intended.

### Is SC-08 meetable as written?

Yes. Nothing here is a defect in the sentence — the two violations are correctable in place with two
edits (a condition line in `gh_cost_log.py`'s docstring, a commit anchor on the board-read grilling's
condition line). This is a genuine behaviour gap, not an unprovable criterion.

## Comparison with the withheld prior work — written AFTER the verdict above, and not changing it

I read `notes/research-goalcheck-FEAT-29-sc08-sc09-regrade-1f585fc.md` only after writing everything
above. Disclosure: while running `git grep` for the wait-loop rule across the committed tree, two
lines of that note appeared in the results; my SC-09 evidence was already taken from
`git show 27b85f2:CLAUDE.md` directly.

- **SC-09.** The earlier grade (at `1f585fc`) marked the rule conjunct **met** on the same
  `CLAUDE.md:55` line and returned SC-09 unmet solely on the conduct conjunct. Ruling 3 drops that
  conjunct, so the two grades agree on everything still gradable.
- **SC-08 violation 2** (`grilling-board-read-lookups-2026-08-10.md`, no commit) is found
  independently by both grades, unchanged at `27b85f2`.
- **SC-08 violation 1** (`gh_cost_log.py`) is where we differ, and I differ deliberately. The earlier
  grade filed it "borderline; the verdict does not rest on it", because its verdict rested on a third
  violation — repository-tier Expertise G-01, then carrying a bare "roughly 500 points". That one has
  since been fixed: at `27b85f2` G-01 carries both figures with all three conditions. With the
  Expertise violation gone, the borderline file is no longer a spare — it is load-bearing, and I judge
  it a violation. A pointer to where the conditions live is not the document stating them, and
  ruling 2 presumes a document that states its set once.

**Net:** SC-08 was unmet at `1f585fc` on three violations, and is unmet at `27b85f2` on two. Fixing
the highest-blast-radius one did not close the criterion.
