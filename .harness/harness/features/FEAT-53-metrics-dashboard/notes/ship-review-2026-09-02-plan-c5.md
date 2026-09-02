# FEAT-53 metrics dashboard — plan signature review, pass 5

**The plan is ready for your signature.** All five fixes you ordered are applied and verified at
source. The cycle budget is raised to 20 and 11 are used, so the build starts with nine rework
cycles instead of one. The cycle-5 panel returned `must_fix: []` at `severity_max: med` with both
readers running — the second consecutive panel that gates nothing. B-23 and B-25 are accepted as
backlog labelled `Dashboard` alongside the rest.

**One thing you should know before you sign, and it is not a defect.** The panel found three new
single-clause findings, and **all three were residue of the fix pass itself** — text written this
cycle that was false or unsatisfiable. I closed all three rather than carrying them, because two
were a false statement and an impossible test instruction introduced by my own dispatch, and
shipping those for signature while reporting "clean" would repeat exactly the defect B-24 was about.
**Those three closures are verified by me at source, not by a sixth panel.** That is the one place
this briefing is weaker than pass 4's.

**How this briefing was assembled.** I spawned no reporting round. I read three run digests off
disk — `runs/2026-09-02-07-product/digest.md` (the fix pass), `runs/2026-09-02-08-validator/digest.md`
plus its `digest-corrigendum.md` (the cycle-5 panel) and `runs/2026-09-02-09-product/digest.md` (the
residue closure) — plus `notes/research-FEAT-53-goalcheck-plan-c5.md` and
`notes/review-harness-code-reviewer-planpanel-c5.md`. Passes 1–4 stand as written in their own four
briefings and are not re-narrated. Everything below that I state as measured, I measured against
disk myself: I re-read every amended field, and I ran the `git init` probe under B-19 rather than
reasoning about it.

---

## Your two rulings, applied

**Q1 — the cycle budget.** `max_total_cycles` is **20** in `feature.json`, recorded as a budget
change per DEC-157 and not itself a cycle. **11 used.** The accounting, so you can audit it: 9 stood
before this pass; the fix run cost 1 (one send-back the lead reported inside it); the residue-closure
run cost 1 — it had no send-back, but it reworked defective output from the run before it, and
counting that only when a lead happens to catch it internally would make the number gameable. The
build phase therefore opens with **9 rework cycles**, which is what you bought.

**Q2 — the five fixes.** Each verified by reading the field, not by accepting a report.

| | What changed | Where I read it |
|---|---|---|
| **B-19** | `T-19`'s simulated ship now `git init`s the copytree copy, sets a local identity, **makes one baseline commit of the copied tree**, and only then ships — so `record_ship`'s commit is observed **succeeding**. Asserts the copy's tree clean and `trend.jsonl` **tracked** (`ls-files --error-unmatch`), not merely present. The non-git case stays as the labelled failure-branch case | `plan.yaml` T-19.intent :1306-1317 |
| **B-20** | `T-10` defines the week: **UTC ISO-8601**, Monday `00:00:00Z` to the next Monday exclusive, each bucket labelled by its own Monday; `30d`/`90d` derive first and last bucket from `resolve_window`; **`all` anchors at the ISO week of the earliest record's `shipped_at`**; no records at all → empty series with its own reason, never a run of nulls | `plan.yaml` T-10.intent :743-781 |
| **B-21** | The record no longer presents your own rulings as open. `D-08` records the alpha **ACCEPTED (2026-09-01)** with the trigger unchanged and **the rollback named for the first time** — see below. `D-20` records the client build **KEPT** and the server-rendered alternative weighed and rejected. Both BRIEF `## Constraints` bullets match. DESIGN C-2 restates the fallback and the dead `react-charts` is gone — **zero occurrences file-wide** | `plan.yaml` D-08, D-20; `BRIEF.md` :73-92; `DESIGN.md` :249-252 |
| **B-22** | New decision **`D-23`** is the single carrier for all fourteen accepted backlog rows, with a one-line subject for the six that carry no panel disposition, and a `because` recording that B-6 was struck and B-11/B-15..B-22/B-24 were fixed — so the list is provably the complete set | `plan.yaml` D-23 |
| **B-24** | `1024` and `ES2022` are **deleted** as carriers of the token `12` in both artifacts. The true carriers are named: `12` in `127.0.0.1` (D-05's loopback bind, shipped in `serve.py`, required in `METRICS.md` by T-17's own verify) and in `122` itself, one of the literals the sweep hunts; `3` in `3x3` and `python3`. **The conclusion is unchanged** — both tokens genuinely cannot be grepped bare and stay carried by SC-15's inspection | `BRIEF.md` :157-166; `plan.yaml` T-07.intent :578-585 |

**The rollback you accepted, now written down** (`D-08.because`), composed only of things already
approved — no new library is named anywhere: **(a)** the alpha is pinned to an exact version in the
client `package.json` and the bundle is committed, so an upstream alpha change cannot reach a user
without an explicit version bump made by a task; **(b)** where a capability is unmet and DESIGN C-2's
`If absent` cell names a workaround, **that workaround is the rollback**, applied in place with no
library change — CAP-02, CAP-03, CAP-04, CAP-06, CAP-09, CAP-10, CAP-12 and CAP-13 each carry one,
enumerated in the decision; **(c)** where the cell reads *hard requirement* — CAP-01, CAP-05, CAP-07,
CAP-11, exactly the four in the trigger — `T-18` records `VERDICT: STOP`, the chart tasks do not
start, and choosing a replacement library becomes your decision **taken then, with the probe in
hand**, rather than now on speculation. `T-18` probes all thirteen before one line of client UI
exists, so a STOP costs only the toolchain task.

**B-23 and B-25 are accepted as backlog** labelled `Dashboard`, carried both by `D-23` and by their
own panel dispositions `C4-05` and `C4-07`.

---

## The cycle-5 panel, and what I did with it

`PASS` · `severity_max: med` · `must_fix: []` · both readers **ran**, neither skipped · 0 send-backs.

Both readers independently verified all six fix-pass claims landed **at source**, deriving from the
fields rather than accepting the summary — including recomputing the `12` substrings themselves and
grepping `react-charts` independently. `D-23`'s fourteen-row set was reconstructed by both readers by
**different routes** — one from the four answers files and briefings, one from the panel entries —
and both arrived at the same fourteen.

Then it found three new things, and this is the part worth your attention:

| # | Sev | What it found | Closed by |
|---|---|---|---|
| 1 | **med** | **`T-10`'s window-boundary bucket was undefined**, and the two readings disagree. The first bucket of a `30d` window is a partial week ~6 days in 7; counting only in-window ships made D-19's verbatim empty-week sentence *literally false* about the rest of that week, while counting the whole ISO week made the buckets sum **above** tile 7's own headline. Every gate stayed green either way | `T-10` now pins the windowed reading REQ-15 forces, states **the bucket values sum exactly to the headline** as an invariant and asserts it as its own test case — the cheapest gate that tells the two readings apart — marks which buckets are partial, and gives a partial empty bucket **its own distinct verbatim reason** so no sentence asserts something false. Fixtured with a window starting mid-week |
| 2 | low | **`T-19`'s new case could not pass as written.** `git init` leaves the whole fixture tree untracked, `record_ship` commits only `trend.jsonl`, so `status --porcelain` prints `??` lines and the case fails for a reason unrelated to the commit under test. **I measured this**, rather than reasoning about it: after `git init`, add, commit of one file, `--porcelain` prints `?? a.txt` | one baseline commit of the copied tree added to the setup |
| 3 | low | **`D-23` asserted something its own plan contradicts** — "B-7..B-10, B-23 and B-25 have no panel disposition of their own", when `C4-05` and `C4-07` are exactly that for B-23 and B-25. The reader's lead extended it: the identical false clause was in `C4-04`'s note too | both sites corrected; only B-7..B-10 are genuinely carrier-less, and the plan now says so |

**Why I closed them instead of bringing them to you as B-26..B-28.** You told me not to manufacture
further scope, and I have not: no new work was invented here. Two of the three were a false statement
and an unsatisfiable instruction that *my own fix dispatch* put into the record this cycle, and the
third was an ambiguity that same dispatch left behind. Finishing an ordered fix correctly is not new
scope. **The honest caveat is that no panel re-read them.** Each is one clause, each is inside a
field the panel had just named, and I verified all three at source; if you want a sixth panel it
costs one run, but my read is that it would find the residue of this pass and the sequence does not
obviously terminate.

`plan.yaml`'s panel key now reads cycle 5, `last_run 2026-09-02-08-validator`, **28 findings** — the
25 earlier ones carried with their summaries immutable, the three new ones `resolved` with citations.
The panel's own note that its lead considered `high` for finding 1 and settled on `med` is recorded
rather than reconciled away.

**What the panel could not tell you, in its own words.** Nothing here was falsifiable, because
nothing is built — every grading is a document-consistency judgement. Both readers agreeing on the
six claims is weaker evidence than it looks: they read the same six fields, written to close exactly
those six findings. The independent signal is the new findings, where **the two readers overlapped on
zero of three**. And a count trending 7 → 3 across two passes cannot distinguish a converged plan
from a tiring panel; no reading of that trend is available from inside the run.

---

## The run count, for the record

**20 runs of an informational `max_total_runs` of 20.** That budget notices a long feature; it never
stops one, and I am not asking you to move it. My one-line read: the runs still earn their place —
every plan cycle closed findings the next cycle independently confirmed closed, and the panel found
genuinely new defects each time rather than re-finding old ones. What the count really says is that
**this plan was reviewed five times and changed materially every time**, which is the argument for
the review, not against it.

---

## Backlog — nothing new is proposed this pass

All three cycle-5 findings were fixed, so no new row is added. The standing accepted set is below,
carried by `D-23` and filed at ship as one issue per row, labelled `Dashboard`. **Strike any row by
ID and it dies. Anything not listed here is not filed.** This is your last look before signature.

| ID | Nature | Row |
|---|---|---|
| B-1 | bug | The committed `dist/` bundle has no source-to-bundle freshness guard and is unmergeable across worktrees |
| B-2 | enhancement | The escaped-defect rule excludes 32 `fix:` commits unexamined and is gameable in one direction |
| B-3 | enhancement | KPI 6's four-hop attribution join powers a tile that is ~77% unattributed |
| B-4 | bug | SC-07 declares `evidence: unit` but its only asserting test is registered as an integration script |
| B-5 | bug | The forbidden theme-token check covers 4 of the 9 client source files that exist at ship |
| B-7 | bug | KPI 1's change-size half nulls once a merged branch is pruned; most projects prune. `review_sha` survives it |
| B-8 | chore | The KPI 6 tile is labelled "by agent/model tier" but its payload keys by model name only |
| B-9 | chore | The start command is documented under `.agents/skills/` while the source is pinned under `.claude/skills/` |
| B-10 | chore | A design clause pins focus to the originating control on browser Back, unverifiable until TanStack Router is installed |
| B-12 | chore | Two plan comment blocks contradict the live YAML: one says no task touches `tests.yml` while `T-22` lists it, and one quotes `T-21`'s verify in its stale `reporter=verbose` grep form |
| B-13 | chore | `SC-17` declares `verify: automated` / `evidence: integration`, but its aggregate not-tracked-count clause is asserted only in `test-metrics-kpi.py`, which is registered as a UNIT script — so that clause has no integration-kind assertion |
| B-14 | chore | `T-12`'s 8.0s ceiling is vacuous in CI: `tests.yml` checks out with bare `actions/checkout@v4`, so the timed case measures the fast unavailable-with-reason branches rather than the real per-request cost `D-09` stakes its no-cache deferral on |
| B-23 | chore | `SC-13` asserts the count **and** that the rule is stated in the UI, under `verify: automated`; the UI half has no gate |
| B-25 | chore | `T-05`'s contract is the 3×3 seven-tile grid while the committed prototype is a six-tile 3×2 build, and `T-05`'s verify cannot detect the divergence |

B-6 was struck by you. B-11 and B-15..B-22 and B-24 were fixed. Nothing else survives.

---

## Harness defects found this pass

Not about this feature. Both are **second occurrences** and neither is fixable by a squad — both
edit the harness skill `bin/` tree.

1. **A plan-phase code review cannot close cleanly.** `validate-digest.py` rejected all five of the
   reviewer's yield attempts with `code_grade cannot be bound to review_sha ... unpinned feature
   (INV-6)` — `n_a`, omitted, empty and `reviewed: none` all refused — and the host returned exit 1
   on a well-formed `VERDICT: PASS`. DEC-207's plan-phase exemption exists on the **input** path and
   is missing on the **yield** path; this is BUG-1080's residue. The verdict and artifact were
   recovered from disk both times, so no work was lost, but every plan-phase panel pays for it.
2. **A lead cannot complete its own digest.** `check-domain.sh` refuses any Write that replaces an
   existing `<run_dir>/digest.md`, including one that strictly extends it, and directs the author to
   "a run directory of its own" — while `validate-digest.py` (DEC-156) requires the file at
   `artifact:` to carry the §10.4 block. A lead that writes its prose first is then stuck: extending
   is blocked, and a second run directory would record a panel run that never happened. Worked around
   here with a companion `digest-corrigendum.md`.

Also minor: line anchors inside the 25 carried panel findings shifted when `T-10`, `T-19` and `D-23`
were amended. A rotted anchor asserts nothing false and the summaries are immutable by design; say
the word if you want them re-pinned before signature.

---

## What I need from you

**Sign, or say what still blocks.** If you sign:

1. `BRIEF.md` `## Approval` — `status`, `approved-by` **and** `date`. The date is load-bearing: it is
   the start of the cycle-time KPI this feature builds (D-14), and this feature's own trend record
   will read it.
2. `plan.yaml` — `plan-merge.py sign-approval`.

Both are yours alone; I have touched neither, and both were byte-unchanged across all three runs of
this pass. On your signature the build phase opens with T-01 and T-06, the two tasks with no
dependencies, and 9 of 20 rework cycles unspent.
