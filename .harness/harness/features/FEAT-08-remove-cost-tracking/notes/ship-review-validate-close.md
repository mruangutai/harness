# FEAT-08 — remove cost tracking · validation review

**For: Mike Ruangutai. Written by the orchestrator; presented by the main session. Not yet merged.**

---

## Where this stands

**The feature is built, reviewed and goal-checked. It is not ready to merge, and three things are
waiting on you.** Everything else is done.

The harness no longer meters, budgets, gates on, or reports money. `cost-report.py` and its test are
deleted; `cost_usd` and `max_cost_usd` are out of the digest schema; the state-file invariant that
required a `cost:` block is gone; the budget keys are out of both configs; the docs are rewritten.
`max_total_cycles` — the one budget with teeth — is untouched, deliberately, and proving it untouched
is itself a criterion.

Twelve of twelve tasks are done and every task issue is closed. Three amendments you signed this
morning are landed. The blocking test gate passed 12 of 12. The four-wide review panel ran in full.
The goal-check verified all fifteen criteria by their own declared methods, and one was re-graded
after its blocker was fixed. The reviewed range is 21 commits and 33 files; the branch now carries 26,
the last five being state, evidence and this document.

**What is waiting on you, in order of what it costs you to decide:**

| # | What | Why it is yours |
|---|---|---|
| 1 | A two-line edit to `.claude/commands/harness.md` | No agent in the org may write that file. I confirmed it by running the domain guard against four personas — all blocked. Only you can |
| 2 | Two criteria are red on their own wording, with correct delivery behind them | Correcting either edits text you signed. I authorised nothing |
| 3 | Merge, and the backlog list at the end | Always yours |

---

## The one live defect, and why no agent could fix it

`.claude/commands/harness.md` is the file the main session reads at the top of every `/harness`
invocation. Two lines in it still describe a meter that no longer exists:

- `:18` tells the session to list in-flight features with a **`cost vs budget`** column.
- `:83` tells it to **log every return as `feature, verdict, status, cost`**.

**What happens if this ships as-is:** the next time you run `/harness` with no argument, the session
is instructed to render a spend column sourced from a deleted script. It will emit an empty column,
stall, or invent a figure — and inventing one is the specific failure this whole feature exists to
make impossible.

It is two prose deletions. It reached me twice independently — the review panel found it, and the
goal-check found it again from the other direction — and neither could fix it, because
`.claude/commands/` is in no agent's writable domain at all. That may itself be an oversight worth a
separate decision: the config documents `.claude/agents/**` as deliberately unowned and says why, and
says nothing about `.claude/commands/**`.

**A third line in the same file is your call rather than a defect.** `:49` names a dollar figure in a
historical anecdote justifying a rule. It does not instruct anyone to produce a figure, and pm ruled
it outside the relevant criterion on structural grounds — no dispatched agent's rules can reach that
file at all. Delete it for consistency or keep it as history; I have no recommendation.

---

## Three findings I am not softening

### 1. The routing wall recurred for the fourth time — inside this feature

One task's declared lane cited a permission that did not cover the file it named. That is the fourth
recurrence of the same shape, and it landed **inside the feature running concurrently with FEAT-09,
which exists specifically to prevent it.**

The cause is precise and worth keeping: **the lane was resolved at plan time by *reading* the org
config rather than by *asking* the live guard.** The guard is a runnable program that answers exactly
that question. Reading the config gave the wrong answer where running the guard gives the right one.

**The part that went right is the part I would not want lost.** The engineering lead returned
`BLOCKED` rather than routing around the guard — and a rewrite was available to it that would have
passed the sibling write-guard unseen. **A silent pass was on the table and was refused.** You then
ruled the task splits by lane; no permission was widened to make a problem go away.

### 2. Four times, a task told an agent to write prose containing a word its own check forbade

A task's stated intent prescribed text carrying a token that the same task's verification clause
counted or banned. Four instances. The two halves are authored together and the conflict is invisible
on reading — **every one was caught by *running* the clause, never by reading it.**

This is the previous feature's lesson recurring inside the feature that inherited it. It is the
strongest candidate for a check that runs at plan time rather than at execution.

### 3. A task passed all four of its checks and still left two live defects — this is the sharpest one

T-10 removed the cost model from the spec. All four of its verification clauses came back green. It
had left **two live defect sites standing**, one of which meant the spec instructed an orchestrator
not to emit a cost line and then, twenty-five lines below, showed one being emitted.

**Why every clause missed them: all four matched compound tokens — `cost_usd`, `cost-report`,
`max_cost` — while both sites used only the plain English word "cost".** A site outside the token set
is not merely unlisted; it is unfalsifiable. The survey's grep had silently become the criterion.

**An all-green `verify:` is not an absent defect.**

Then it happened again, wider. The review panel found **three more** surfaces of exactly that shape,
in files the criterion's own scope covered — and the criterion was green. And the goal-check found
the counter-example that makes this actionable rather than fatalistic: **the one criterion in the
whole feature that grepped the plain word, over one file of scope, came back clean and reproducible.**
The gap is a drafting habit, not a limit of the tool.

---

## What the review panel did, and what it cost to learn

All four reviewers ran — code, qa, security, ui — under your standing ruling that there are no
pre-emptive skips. **The ruling paid for itself, and I can say exactly how.**

- **Security did not scope out.** On a pure-deletion diff it reasoned that a guard which *lost* a
  constraint is a tampering question, declared itself in scope, and *executed* both fixture suites
  rather than reading them. Under the previous feature's practice that spawn would have been skipped
  on my own inference. It returned zero findings — a measured zero, not a predicted one.
- **UI did scope out** — with a file-extension census across the 33 changed files and a
  confirmed-absent design contract. That is a reviewed finding, not a null.
- **All four members returned PASS. Their lead then found three real violations they had all missed**
  — every one in a file no member's scope reached. The code reviewer ran the plain-word sweep it was
  asked to run, correctly, and scoped it to files the diff *touches*; all three violations live in
  files the diff does not touch. **Instruction followed, criterion green, requirement still violated.**
  The gap was a property of the *union* of four scopes, not of any single lens.

My own standing note said to skip the UI reviewer when there is no design contract. **Your ruling
overrode it, and the ruling was right** — that note has now been reversed in my expertise file to say
the opposite: dispatch it and record the reviewer's own verdict, never your prediction of it.

**The three findings, and what happened to each:**

| | Where | Disposition |
|---|---|---|
| MF-1 | `.claude/commands/harness.md` | **Open. Yours** — no agent domain covers the file |
| MF-2 | `docs/harness/org.html` | **Fixed.** It described the cost budget as live in three places, including a rule card. Hand-maintained, no generator, and absent from both signed artifacts — so no task ever scoped it in or out |
| MF-3 | `.harness/expertise/harness-orchestrator.md` | **Fixed.** A stale operating procedure for the deleted meter, injected into *every* orchestrator spawn. Highest blast radius of the three, and only I could write that file |

---

## Goal-check: fifteen criteria, verified by their own methods

**Fourteen met, two red — and the difference between the two reds and the one that was real matters.**

| Criterion | Verdict | What it means |
|---|---|---|
| SC-15 | **was not met — now MET** | **This one was a real delivery failure, not a wording problem.** Its blocker was MF-3: a live rule advertising the deleted meter, loaded into every orchestrator spawn. I fixed it, then had pm re-grade rather than marking it met myself. pm swept all twelve rule-surface files, the agent definitions, the skills and the team YAML — 57 hits, zero money — and flipped it |
| SC-05 | **not met** | Red on **wording**. The delivery is correct: the preserved budget key and its rationale are byte-identical in both configs. The clause also forbids any diff line mentioning the counter — and one line matched, because removing the cost entry from a shared line touches it |
| SC-06 | **not met** | Red on a **rotted number**. The criterion pins two figures measured before this feature's own directory existed. Restricted to the features it was measured against, it returns those figures exactly — 89, and 67 of 67. The historical record is byte-identical, as claimed |

**SC-05 and SC-06 need your signature or your shrug, not a fix cycle.** Correcting either edits a
criterion you signed. A fix aimed at the code would be work aimed at nothing — the code is right.

**Three criteria were met by a method that cannot detect the failure it exists to detect.** SC-01
(token *and* scope — MF-1 sat *inside* its scope and was invisible to all five of its patterns),
SC-03 (scope: it is repo-wide, so a concurrent flow can fail it — it passes today only because
FEAT-09 sits in its own worktree, which makes the hazard dormant, not gone), and SC-12 (its line
anchors were 4-of-12 dead within about 21 commits, on pm's measurement, while every piece of content
it protects survived intact). **A criterion marked met on an insufficient method is worse than one
marked unmet**, because nothing downstream looks again. I asked for that judgement explicitly and it
is recorded.

---

## Cost

**The harness no longer meters spend.** T-03 deleted the meter, which was the point. `$370.53` at
`3503d1d` is the last measurable figure this project will ever produce, against a `$120` budget —
over, reported at the time, never invented. Everything after that commit is unmeasurable by design,
and no number for it appears anywhere in this document because none exists.

Cycles: **4 of 10.** Two from build, one for the panel's fix round, one for the re-grade.

---

## Proposed backlog

**Anything not on this list dies silently.** Strike what you do not want; on your ship acceptance the
survivors become issues.

| # | Item | Nature |
|---|---|---|
| B-1 | **The deployed global rules are stale** — they still instruct every lead to run the deleted meter and to write a `cost:` key. Four agents hit it this feature; one earlier run complied, so the placeholder is sitting in a run dir on disk right now. `/harness-deploy` must run after merge, and **before** the queued preload-trimming batch | chore, near-term |
| B-2 | **`check-domain.sh:308` carries `cost` in an allowlist with no explanatory comment**, unlike its sibling which explains the same entry. FEAT-09 is live on that file; the next editor removes it as cleanup and all 67 historical runs become violations | bug, urgent — collides with in-flight work |
| B-3 | **The rule surfaces injected at every spawn are outside the standing removal sweep.** Expertise files were never searched by any criterion here, and the highest-blast-radius finding of the feature was exactly that miss | enhancement |
| B-4 | **`.claude/commands/**` is in no agent's domain.** Deliberate, like `.claude/agents/**`, or an oversight? Nothing records which | chore |
| B-5 | **Three comments justify themselves with "this task's `verify:`"** — a justification that stops existing the moment this merges. The code reviewer ruled it low and corrected the site list to three; low is not absent, and it rots on merge | chore |
| B-6 | **One literal deviation from signed amendment text.** A-4 said to delete a whole test case; what landed deleted only the offending line and its comment, keeping the case. The reviewer judged the result *better* on the merits — the case still asserts a schema shape that deleting it would have dropped — but reported it rather than waiving it, which is correct | chore |
| B-7 | **A send-back gives the returning member a fresh context**, so questions it raised in its own prior return are unrecoverable to it. Raised independently twice | bug |
| B-8 | **The task regex cannot tell a task *definition* from a *reference* to one**, so amending a task by heading trips the state checker on a correct amendment | bug |
| B-9 | **Nothing detects divergence between a live config and its template.** The unit suite exited 0 on a half-stripped pair. Raised twice from the engineering lane | bug |
| B-10 | **`check-expertise.sh` silently ignores any line it does not recognise.** Caught live, not hypothesised: a lead's write leaked two stray lines that matched no rule, and the checker would have reported OK on a file that is then injected into that agent at every spawn | bug |
| B-11 | **`check-expertise.sh` does not enforce the entry shape**, only section names, word cap and file budget. One accepted entry this feature is past-tense narrative and passes | enhancement |
| B-12 | **`bash-write-guard.sh` over-blocks.** It denies `cp` and redirects into the *session scratchpad*, not just repo paths, and reads a bare `>50` inside quoted prose as a redirect to a file named `50` | bug |
| B-13 | **A `grep -v` allow-list clause exits 1 while printing nothing.** Correct as written, since the clause is defined on output — but any wrapper treating non-zero as failure reads a green clause as red | chore |
| B-14 | **No `verify:` clause can prove that text a task promised to leave verbatim did not move.** Every clause in this feature is an absence or a count check; the guarantee was discharged by reading the diff | enhancement |
| B-15 | **An `expertise_update` receipt is never checked against the file it claims to describe** — and the digest is all the tier above reads. Two agents returned abbreviated entry text this feature | enhancement |
| B-16 | **A missing expertise file is silent.** One reviewer had none, so every prior spawn of it ran with zero expertise injected and nothing surfaced that | enhancement |
| B-17 | **A rotted anchor inside a signed artifact** — A-4 cites a spec line that is three lines off. Harmless here; the class is not | chore |
| B-18 | **A lead's returned digest and its digest FILE can diverge silently.** When the stop hook rejects a return and the agent re-returns, nothing re-checks the file — and the file is what a successor context reads. It happened twice this feature and I caught both by running the validator myself | bug |
| B-19 | **A dispatcher can name a run-dir path its callee provably cannot write.** I did exactly that: the squad suffix must come last for the domain glob to match, and my dispatch inverted it. The lead chose the compliant name rather than working around the guard | chore |
| B-20 | **Issue #79 is filed and unscheduled** — count and budget *runs*, not only cycles. With the meter gone this is the only remaining signal that a feature is running long | enhancement |
| B-21 | **Question IDs are treated as a feature-wide namespace but nothing allocates them.** Concurrent runs collide, and both failure modes fired this feature: one id carrying two different questions, and one question filed under two ids | bug |
| B-22 | **Issue #104 is filed** — the strict-schema question you already ruled on. Recorded so it is not re-opened by accident | chore |

---

## What I did not do

- **No amendment or re-signature was raised for the three panel findings.** They violate an
  already-approved requirement — *no surviving document, index row or rule surface advertises a
  script, key or invariant this change deleted* — so they are approved-but-unmet, which is a fix, not
  a scope change. That ruling is mine and it is on the record so you can overturn it.
- **The state checker was not re-rooted** to make a repo-wide criterion pass. You forbade that
  re-baselining and it was not proposed.
- **No replacement test fixture was added** for the deleted pin. You ruled "add nothing"; the ruling
  was relayed to the panel and to the goal-check as closed, and neither re-opened it.
- **The three leads were not re-spawned to file domain reports for this document.** All three ran
  inside this phase, minutes before it was written, and their own digests are its source. **That is
  my judgement, not a rule, and it is the one place in this phase where I substituted my reading for
  a prescribed step. Say the word and it costs three spawns to do properly.**
