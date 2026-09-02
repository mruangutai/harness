# FEAT-53 metrics dashboard — plan signature review

**The plan is finished and ready for your signature, and it is not ready to be signed as-is.**
Five things need your decision. Three are choices the factory deliberately refused to make for you;
two are defects a panel found that neither I nor the product manager is permitted to overrule.

Everything below is on disk in `.harness/harness/features/FEAT-53-metrics-dashboard/` on branch
`feat/FEAT-53`. `BRIEF.md` (14 requirements, 16 success criteria), `DESIGN.md` (518 lines),
`plan.yaml` (20 tasks, 20 decisions, panel result recorded). All three read `approval: pending` and
will keep reading pending until you sign — only you can.

**How this briefing was assembled.** I spawned no reporting round. I read the nine run digests off
disk and assembled from those, which is why this costs one document rather than three re-narrations:
`runs/2026-09-01-01-product/`, `-02-product/`, `-03-product/`, `-04-product/`, `-05-product/`,
`-01-eng/`, `-01-validator/`, `-05-validator/` (superseded) and `-06-validator/` (canonical panel),
each `digest.md`. Where I state something as measured, I re-measured it myself; where a squad
measured it, I say whose finding it is.

---

## What you are being asked to decide

### DEC-1 — The plan reverses something you settled, and nobody told you until now

You settled at the grilling that **"a real web framework (backend + a JS charting lib) is
justified for this feature."** The plan ships a **python3 stdlib `ThreadingHTTPServer`** with a
hand-written route table, and rejects FastAPI, Flask and a Node server outright (`D-03`).

Engineering reviewed that choice **on its merits and endorsed it**: three read-only loopback GET
routes do not repay a framework, and every added runtime import becomes a hard prerequisite gate in
the Harness distribution itself — not in one application. It is, in my read, the better engineering
call.

That is not the problem. The problem is that the reversal was recorded inside a decision's
`because:` clause where you would never have seen it. pm's goal-check against your own words caught
it (`notes/research-FEAT-53-goalcheck-plan-c1.md`). **Confirm the stdlib server, or hold the
framework you settled on.**

### DEC-2 — Keep the client build at all?

`D-20` writes down, for the first time, a decision the plan had been resting on without stating:
React + TanStack Router/Query on the Astryx substrate, an npm package under
`bin/dashboard/client/`, and a committed `dist/` bundle.

You settled React + TanStack at the grilling, so **this is not being reopened** — it reaches you
because engineering's review surfaced information you did not have then. A server-rendered HTML
surface with no npm would delete the frontend framework, the first `package.json`, the committed
bundle and the entire alpha-charting risk in one stroke. pm measured the blast radius of switching:
it voids `D-02`, `D-04`, `D-07`, `D-08` and tasks `T-01`, `T-02`, `T-04`, `T-13`, `T-14`, `T-15`,
`T-16`, `T-18` — **over a third of the plan.**

pm and both leads recommend keeping the client build. I agree, with one caveat: see DEC-3.

### DEC-3 — The charting library has no working fallback

`D-08` pins **TanStack Charts at alpha**, which you accepted knowingly. Its named fallback was
`react-charts`. Engineering checked the package: **it is dead** — React 16 peer dependency, last
published 2023-11-02, against a React ≥19 substrate. The fallback trigger currently fires into
nothing. The dead reference has been struck; no replacement was invented in its place.

Two further facts bear on this. The fallback trigger reads "any of CAP-01, CAP-05, CAP-07 or CAP-11
unmet", but `T-18`'s own instructions make **CAP-05 inert**, so the net is three live triggers, not
four. And the panel observed that two of those three (CAP-07, CAP-11) belong to trend charts that
**render nothing but empty states for roughly a month to a quarter after launch**, because the trend
record starts the day this ships.

**Accept the alpha with a documented rollback, or name a second live charting library now.** pm and
I recommend accepting: `T-18` now probes all 13 chart capabilities *before* any client UI is built,
so a STOP verdict arrives while it is still cheap. That reordering was itself a review finding.

### DEC-4 — Two high panel findings must be resolved, and I may not overrule them

The adversarial panel ran with **both readers, neither skipped** — the external adversarial reader
resolved and returned five findings, the scope reader three. It returned `FAIL` at `severity_max:
high`. All eight findings are recorded in `plan.yaml`'s `panel:` key with content-hash ids, all
`disposition: open`.

- **`PF-328f8f3c` (high).** KPI 4 — autonomy — treats an absent touchpoint file as a measured zero.
  On launch day that **publishes ~50 pre-instrument features as having required zero human
  touchpoints**, 41 of which carry a signed approval date. That is a fabricated autonomy record, and
  it is precisely the failure the plan's own `D-19` forbids. Remedy: scope absent-file-is-zero to
  post-instrument features and mark the rest unavailable-with-reason — or KPI 4 does not ship this
  increment.
- **`PF-7408d83a` (high).** `T-15` creates `charts.tsx` *after* `T-14` creates the panel that must
  render it, and **no task ever touches the panel again** — so the grading panel would ship with no
  chart wired, and both tasks' verify blocks stay green throughout. Remedy: add the wiring step and
  assert the chart is actually rendered rather than that the file matches design tokens.

**Order matters here.** Settle DEC-3's Shape-B question *before* anyone remediates `PF-7408d83a`:
deferring the trend charts changes or removes `T-15`, so fixing it first may spend a cycle on a task
your signature deletes.

Both readers noted a shared root cause worth one sweep rather than two point fixes: several verify
blocks check the wrong object — token content rather than composition, instruction text rather than
behaviour. A clean 14/14 requirement census passed over both high findings, because both live in the
gap between "every requirement has a task" and "the tasks compose into the thing".

### DEC-5 — The prototype has never been seen by anyone

The design gate calls for a prototype and one exists — 24 files, Astryx + React, it builds and
server-renders. **Nobody has ever looked at it.** The designer who wrote it had no browser; the
reviewer who audited it read it as source. The design contract has since moved on, so the prototype
is now also stale against it (no tables, no fifth gap state, no focus clauses).

The product lead recommends **waiving** rather than commissioning a rebuild: no agent here has a
browser, so a rebuilt-but-unrendered prototype buys the letter of the gate and none of its purpose.
The alternative is that you open it yourself before signing. Either way the staleness is on the
record in `DESIGN.md`.

---

## Proposed backlog

Residual findings that survived review but do not gate the signature. **Strike any row by ID and it
dies; anything not struck becomes a backlog issue on acceptance. Nothing here is carried anywhere
else, so an unstruck row is the only way these survive.**

| ID | Nature | Finding |
|---|---|---|
| B-1 | bug | `PF-04c95fd6` — the committed `dist/` bundle has no source-to-bundle freshness guard, and is unmergeable across worktrees. This is the same argument the grilling used to reject a binary database, applied to one artifact and not the other. |
| B-2 | enhancement | `PF-3713534d` — the escaped-defect rule counts ~8 items in 5 months while excluding 32 `fix:` commits unexamined. It is gameable in one direction: a `fix:` commit instead of a BUG unit holds the number at zero. |
| B-3 | enhancement | `PF-55e28a6e` — KPI 6's four-hop attribution join powers a tile that is ~77% unattributed, whose ~6% resolvable remainder is already knowable from the 16 static agent files. |
| B-4 | bug | `PF-d2fc9563` — SC-07 declares `evidence: unit`, but its only asserting test is registered as an integration script. |
| B-5 | bug | `PF-ce8b018f` — the forbidden theme-token check covers 4 of the 9 client source files that exist at ship. |
| B-6 | chore | Cycle-time start is `plan.yaml`'s approval date — i.e. **plan** approval — while the grilling and REQ-03 both say **brief** approval. Forced and sound, but undisclosed until now. Confirm, or REQ-03 is wrong. |
| B-7 | bug | KPI 1's change-size half reads `git diff default...branch`, which nulls once a merged branch is pruned. Most onboarded projects prune, so half of KPI 1 would be permanently empty off this repo. `review_sha` survives the prune and is already read by the same task. |
| B-8 | chore | The KPI 6 tile is labelled "by agent/model tier" but its payload keys by model name only; the resolved agent is discarded. Keep the agent name, or relabel the tile. |
| B-9 | chore | The start command is documented under `.agents/skills/...` while the source is pinned under `.claude/skills/...`. Both resolve — `.agents/skills` is a symlink — but the README should state one. I ruled `.claude/skills/...` for internal consistency with `D-01`/`D-17`; overridable. |
| B-10 | chore | A design clause pins focus to the originating control on browser Back, which needs router behaviour that cannot be verified until TanStack Router is installed. If it cannot hold, the fallback is the page heading and the clause needs one sentence. |

---

## Harness defects found while doing this work

These are about the factory, not this feature. They cost real time here and will cost it again.

1. **A plan's first panel cannot produce a valid digest.** `plan-merge.py` **refuses** a proposal
   carrying an `approval:` key when creating a plan (exit 8), so a first-draft `plan.yaml` has no
   approval key at all — while `validate-digest.py`'s plan-review path **requires**
   `approval.status == "pending"` (`validate-digest.py:1001-1006`). I confirmed both at source. The
   scope reader was stuck in an unwinnable retry loop until the main session hand-added the stub.
   Every new feature's first panel hits this.
2. **A read-only documentation lookup was refused by the *write* domain guard**, forcing library
   facts to be gathered from `registry.npmjs.org` and `unpkg.com` instead. Raised independently by
   two squads.
3. **A run's `digest.md` is immutable after its first write**, so a digest that fails validation can
   only be repaired by opening a successor run directory. That is why run `05-validator` holds a
   superseded copy and `06-validator` is canonical.
4. **`plan-merge.py` `safe_load`s a proposal file whole**, so an artifact doubling as a proposal can
   carry a human-readable preamble only as `#`-prefixed lines. Any plain prose paragraph above the
   YAML exits 5.

---

## Budgets and honesty about this run

Seven runs against an informational budget of 20; **3 rework cycles against a hard 10**. The runs
earn their place: each of the three review segments changed the plan materially, and the two high
panel findings were invisible to every prior reader. Nothing here is close to a runaway.

One thing I will not dress up: this feature began as FEAT-51, collided with an existing in-flight
feature of that number, and was renumbered mid-run. No work was lost — every artifact was carried
across — but roughly one product segment was spent twice, and the first plan draft died with the
context that held it. Two of the three rework cycles trace to that and to the write-route defect
above, not to anything wrong with the plan.

**The prototype has never been rendered by anyone.** I state that plainly because three separate
artifacts now assert what this dashboard will look like, and not one of those assertions has been
checked against a screen.
