# Re-grade — SC-08 and SC-09 at `review_sha = 1f585fc`

**SC-08 unmet (genuinely wrong). SC-09 unmet (merely unproven, and one conjunct is ungradable as written).**
Scope: SC-08 and SC-09 only. Graded against the committed tree at `1f585fc`. I did not read the prior
digest, state.yaml or the earlier goalcheck notes before writing the verdicts below.

---

## SC-09 — unmet (merely unproven)

Instrument: `git show 1f585fc:CLAUDE.md`. Not a working-copy read.

**Conjunct (b), the recorded rule — MET.** `git show 1f585fc:CLAUDE.md` line 55:

> `- Never write a shell wait loop. A Bash foreground timeout detaches rather than kills, so a loop outlives its own bound. Use Monitor (its timeout_ms terminates) or run_in_background.`

"Never" is an outright prohibition, not an interval bound. Both replacements are named: **Monitor** and
**`run_in_background`**. It is in the COMMITTED tree at the pin, which is what the amendment requires.
The struck cost-citation clause is dropped and not graded.

**Conjunct (a), the behaviour — NOT ESTABLISHED.** The subject is what the main session *runs*, not what
a file says. What I can show from files:

- `git grep -n "pr checks" 1f585fc --` returns hits in FEAT-29's own artifacts only (`BRIEF.md:46`,
  `BRIEF.md:117`, `plan.yaml:67`, `plan.yaml:631`, `notes/research-plan-product.md:15,64`, prior grading
  notes). The same grep filtered to non-FEAT-29 paths returns nothing. No file at the pin instructs,
  schedules or configures a 10-second `gh pr checks` poll.
- `git grep -nE "sleep 10|--interval|10-second" 1f585fc --` surfaces only FEAT-09/FEAT-16 `--resolve`
  timeout probes, unrelated to polling.

That is absence of an *instruction*, not absence of the *behaviour*. The behaviour was `gh` typed
straight into Bash by the main session, and nothing at the pin records those invocations:
`.claude/skills/harness/bin/gh_cost_log.py:12-15` states the recorder is opt-in, default off, and
**blind to `gh` invoked directly from Bash** — the exact path the ~360-point burn lived on. Consistent
with that, `.harness/logs/` contains no `gh-cost-*.jsonl` file at all (`ls .harness/logs/` — only daily
`.md` session logs). No artifact in the tree could record either an occurrence or a clean absence.

Inferring (a) from (b) is inferring compliance from a rule, which is accepting an assertion — the one
thing `verify: inspection` forbids. It would also make (a) redundant of (b), and the amendment wrote them
as two clauses.

**Verdict: unmet.** A conjunction with one conjunct unestablished is not met. **Classification: merely
unproven** — no evidence the polling still happens, none that it stopped.

**Plan-level finding (not a fix):** conjunct (a) cannot be met as written under `verify: inspection` at
this pin, and no retry of the *work* changes that. Main-session Bash `gh` calls leave no inspectable
trace; the only recorder that could leave one is off by default and blind to that path anyway. Either
the clause is rewritten to grade the recorded rule (which (b) already does, making (a) redundant), or its
method changes to something with an instrument — e.g. an always-on wrapper covering direct Bash `gh`,
which the feature deliberately did not build. Operator's call, not mine.

---

## SC-08 — unmet (genuinely wrong)

### Part 1 — the 2026-08-10 grilling note corrected in place: MET

`.harness/notes/grilling-graphql-cost-2026-08-10.md`:

- `:14-16` the 31-point exclusion bullet is struck through in place, text preserved.
- `:17-21` the correction carries the measured figure and its full condition: "506 GraphQL points, on
  board 3 with 473 items, at commit `6bbd706`", struck-date `2026-08-19 (#571)`, and "quote **490 to
  506** and treat 608 as a contaminated upper bound" with the containment argument stated.
- `:22` reverses the conclusion outright: "**It IS the burn.**"
- `:61-65` the second 31 ("`gh project item-list --limit 500` costs **31**") is struck and recorded as
  unreconciled rather than back-fitted.
- `:87-90` records the three-condition rule (board, item count, commit) as the lesson.

Every element Part 1 names is present. Met.

### Part 2 — "no document THAT IS STILL IN FORCE …": UNMET

In-force test applied per the operator's ruling: the owning feature's `feature.json` `status`. Files with
no owning feature (repo-level notes, `.harness/harness/expertise/`, `.claude/`, `docs/`) have no Done
status to freeze them and are in force. Consistency check on that reading: Part 1 of this same criterion
*requires* a repo-level 2026-08-10 grilling note to be corrected, so repo-level notes are in force by the
criterion's own construction.

Statuses read directly from each `feature.json`:

| Feature | status | Effect |
|---|---|---|
| `FEAT-11-graphql-field-resolve` | `Done` | frozen history, out of scope — confirmed, not taken on the criterion's word |
| `FEAT-13-single-issue-board-lookup` | `Done` | frozen history, out of scope |
| `FEAT-29-graphql-budget` | `Building` | **in force** |
| `FEAT-26`, `FEAT-28` | `Plan` | in force; no cost claim about this read (no grep hits) |
| `FEAT-19-central-product-config` | `Abandoned` | no cost claim about this read |
| FEAT-01..FEAT-27 (all others) | `Done` | frozen history |

**Enumeration — every in-force document I found making a claim about the read's COST**, and whether each
cost figure carries board + item count + commit:

| # | Document | Figure(s) | board | items | commit | Cheapness claim? |
|---|---|---|---|---|---|---|
| 1 | `.harness/harness/expertise/harness-orchestrator.md:9-12` | "roughly 500 GraphQL points from INV-26's whole-board read" | no | no | no | no |
| 2 | `.harness/notes/grilling-board-read-lookups-2026-08-10.md:73-79`, `:69` | 203, 102, "~102 points per 100 items" | yes (3) | yes (163) | **no** | no |
| 3 | `.claude/skills/harness/bin/gh_cost_log.py:4-5`, `:15`, `:50` | 506, "5 points instead of 506" | no | no | no (cites `notes/measurement-before.md`) | no |
| 4 | `.harness/notes/grilling-graphql-cost-2026-08-10.md:17-21`, `:61-65` | 490-506, 506, 608, 31 (struck) | yes (3) | yes (473) | yes (`6bbd706`) | no — reversed at `:22` |
| 5 | `FEAT-29/BRIEF.md:9-17` | 490-506, 608, 102 | yes (3, 6) | yes (473, four) | yes (`6bbd706`, `:10`) | no |
| 6 | `FEAT-29/notes/research-plan-product.md:4`, `:59`, `:95-99` | 506, 608, 490-506 | yes (3) | yes (473) | yes (`6bbd706`, `:95`) | no |
| 7 | `FEAT-29/STATE.md:28-31` | 5, 506, 102, 1 | yes (3, 6) | yes (473, 486, 4) | yes (`8c2c24d`, `e1bcdc1`) | no |
| 8 | `.harness/harness/docs/DECISIONS.md:4755` | "returns **30 items**" | — | — | — | not a cost figure — out of subject |
| 9 | `.claude/skills/harness/bin/factory_gh.py:375-376` | field-list 102, `project view` 2 | no | n/a | no | different call (`field-list`), not this read |

**Clause (a), "asserts that `project item-list` is cheap enough to ignore": satisfied.** No document in
rows 1-9 makes that claim. The original assertion is struck and reversed (row 4, `:14-22`). Row 2's `:19`
("keeps `project_items` and keeps costing what it costs") and `:68-69` are scope declinations that
*acknowledge* the cost; neither calls it cheap. Row 1 asserts the read is expensive, not cheap.

**Clause (b), "no such document states a bare corrected number without its condition": VIOLATED, twice.**

**The load-bearing failure — row 1, `.harness/harness/expertise/harness-orchestrator.md:9-12`:**

> `- G-01: WHEN running check-state.sh DO expect roughly 500 GraphQL points from INV-26's whole-board`
> `  read against a 5,000-point budget — …`

A claim about this exact read's cost, carrying **zero of the three condition tokens** — no board, no item
count, no commit. It is the precise defect the criterion exists to close, in a file with no owning
feature. And it is worse than unconditioned: it is **false at the pin**. T-01/T-02 took that read to 5
points (`.claude/skills/harness/bin/gh_cost_log.py:15`; `FEAT-29/STATE.md:28-29` — board 3, 473 items,
`8c2c24d`). This file is the repository-tier Expertise injected into every `harness-orchestrator` spawn,
so the stale figure is not dormant — it is handed to the orchestrator on every run, telling it to expect
roughly 100x the real cost of a gate it runs constantly.

**Second violation — row 2, `.harness/notes/grilling-board-read-lookups-2026-08-10.md`.** `:73-74`
conditions its figures on "measured on 2026-08-10 against board 3 (163 items)" — board and item count,
but **no commit**; a grep for a backticked 7-40 hex sha or the word "commit" over the file at the pin
returns nothing. Its 203 is explicitly a *corrected* number: `:89-90` — "#217's own body cites 31 points
for this call. That figure is stale … 203 supersedes it." A corrected number missing one of the three
conditions the criterion demands.

Row 3 (`gh_cost_log.py`) states 506 and 5 bare but points at `notes/measurement-before.md` for the
conditioned measurement. Recorded as borderline; the verdict does not rest on it.

### STATE.md — graded on what it does

Requested explicitly, and it passes on its own conduct. Every read-cost figure it states at
`FEAT-29/STATE.md:28-31` carries all three conditions: 5 points (board 3, 473 items, `8c2c24d`), 506
before (board 3, 486 items, `e1bcdc1`), board 6 old 102 / new 1 (four items, `8c2c24d`). `:32`'s "46
GraphQL points" of orchestrator spend is an aggregate of mixed calls, not a claim about this read — out
of subject, and board/item count are inapplicable to it. Its `:19-26` assertions about prior rounds and
prior remedies are narrative and carried **no** weight in this verdict in either direction; I graded only
the figures. STATE.md is not the reason SC-08 fails.

### Verdict and classification

**SC-08: unmet. Genuinely wrong, not merely unproven.** The failing document exists, I read it, and its
figure is both unconditioned and falsified by this feature's own shipped change. A retry can fix it: one
edit to `.harness/harness/expertise/harness-orchestrator.md` G-01 (restate at 5 points with board 3 / 473
items / `8c2c24d`, or strike it), plus a commit token added to
`.harness/notes/grilling-board-read-lookups-2026-08-10.md:73-74`. **That routes to a fix cycle, not to
the user, and not to me — I mark nothing met, waived or edited.**

---

## Open questions

- **Q1 (blocking):** SC-09 conjunct (a) is ungradable by inspection at this pin. Rewrite the clause or
  change its method — operator's call.
- **Q2 (non-blocking):** `506` appears with two different conditions — board 3 / **473** items /
  `6bbd706` (`grilling-graphql-cost-2026-08-10.md:18`, `BRIEF.md:10`) and board 3 / **486** items /
  `e1bcdc1` (`STATE.md:29`). Both are conditioned, so clause (b) is satisfied by each; but one number
  under two item counts is either two measurements or one transcription error. Worth resolving.
- **Q3 (non-blocking, harness defect):** repository-tier Expertise files under
  `.harness/harness/expertise/` are injected into every spawn and have no owning feature, so nothing in
  the feature lifecycle re-checks their factual claims when a feature falsifies one. That is how a stale
  cost figure two orders of magnitude out survived the change that invalidated it.

---

## Comparison with the prior round — written after the verdicts above

Deliberately not read before forming the verdicts, per the dispatch, and nothing above was reconciled to
it. From `notes/research-goalcheck-FEAT-29-sc08-sc09-regrade.md` at the pin, the earlier round recorded
SC-09 limb 1 as **NOT-ASSESSED** ("not assessable from files", `:79-85`) and SC-08 limb 2 as **MET** ("no
in-force document asserts item-list is cheap enough to ignore", `:28`).

Where I differ, stated plainly and not softened:

1. **SC-09.** Same finding about assessability, different verdict: **unmet**, not not-assessed. Conjunct
   (b) is now met at `1f585fc` and was not at `4f2e5d0` — `git show 4f2e5d0:CLAUDE.md | grep -c "wait
   loop"` returns `0`, run by me. A conjunction whose other conjunct cannot be established is not met.
   Not-assessed leaves a criterion neither passed nor failed; unmet plus an explicit plan-level finding
   routes it somewhere.
2. **SC-08.** The earlier round graded the cheapness clause, which I also find satisfied. I find the
   criterion fails on its **second** clause — bare number without condition — on a document its search
   set did not reach: `.harness/harness/expertise/harness-orchestrator.md:9`. A `.md`-scoped grep for
   `item-list|item_list|project_items` (`:36`) cannot match it, because G-01 names the read as "INV-26's
   whole-board read" and never uses those tokens. That is the gap: the enumeration has to be built from
   the cost *claim*, not from the call's spelling.
