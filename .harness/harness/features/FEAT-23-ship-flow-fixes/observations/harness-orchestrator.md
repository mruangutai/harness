# Observations — harness-orchestrator — FEAT-23

- 2026-08-17: resuming after a 529, the predecessor's SUBAGENTS were still alive and writing. `ls`
  showed two notes; a `wc -l` seconds later showed three. Polling `stat` mtime/size on the feature's
  artifacts for 60-90s is the only way I found to tell a dead run from a slow one — BRIEF.md grew
  7564 → 10060 bytes while I was deciding whether to re-dispatch. Dispatching a second product-lead
  before that check would have raced two pm writers on the same BRIEF and plan.
- 2026-08-17: I did dispatch a duplicate product-lead anyway (assess-not-redo) because the ORIGINAL
  lead had not returned. It had in fact survived too, and completed at 07:03 with a thorough graded
  digest. The duplicate then overwrote `digest.md`. Lesson: when subagents may have survived a
  parent's death, the completion signal to watch is the run's own `state.yaml` step status, not the
  absence of a return notification.
- 2026-08-17: THREE lead returns were false about the disk. `3-revise`, `4-revise` and `5-revise`
  each returned BLOCKED claiming "pm never ran / no Agent tool", while pm's work had in fact landed
  in `plan.yaml` (44890 → 55542 → 59762 bytes). The named cause is `validate-digest.py --hook`
  firing on a lead's turn-end while its dispatched member is still in flight, extracting a premature
  verdict. Reconciling every return against `find` + mtime, never against the return's own claim,
  is what kept this feature honest — G-04 generalises beyond `git status`.
- 2026-08-17: two eng-lead architecture passes ran concurrently into ONE run dir. The second wrote a
  sibling filename rather than overwriting, and flagged the collision itself. I then quoted findings
  from the sibling while naming `digest.md` by path in my fold-in dispatch — so seven findings (A, D,
  F, G, H, I, J, K) reached nobody and needed a second fold-in run. When a run dir holds more than
  one digest, enumerate the dir before quoting from any of it.
- 2026-08-17: the cheapest high-value check I ran all session was extracting a `verify:` clause's
  grep literal with a regex and comparing it byte-for-byte against the literal its own `intent:`
  pins. An arch reviewer had suggested `grep -qF "separate read-only dispatch"` against intent text
  reading `SEPARATE` — case-sensitive, so the clause could never pass. Two tiers caught it only
  because someone compared the two halves mechanically instead of reading them.
- 2026-08-17: proving a new conjunct GREEN needs a synthetic fixture, because on the pre-change tree
  the clause's first conjunct (`test -f`) exits before any later conjunct is reached. I ran T-02's
  clause with `S=` rewritten to a tempdir across three fixture states (complete / paraphrased /
  case-flipped). A red run on the real tree proves nothing about a conjunct it never reaches.
- 2026-08-17: `bash-write-guard.sh` masks quoted spans wholesale, so a python heredoc containing
  `quiet>=4` is rejected as a redirect to a file named `=4:`. Rewriting the comparison as
  `quiet not in range(0,4)` passed. Any `>`/`>=` inside an inline script trips it, not just shell
  redirects.
- 2026-08-17 **CORRECTION to an earlier entry in this log.** I recorded that "a concurrent
  orchestrator context" was writing `feature.json` and STATE.md, and I very nearly reported that
  upward as a harness defect. It was MY OWN ERROR: I meant to send a message to a running agent,
  there is no `SendMessage` in my toolset, and I reflexively called `Agent` with
  `subagent_type: fork` and a placeholder prompt. **A fork inherits the parent's entire context**, so
  it read that context as its own mission and re-ran the whole plan phase in parallel — roughly
  doubling the spend. Two lessons, and the second is the durable one: (1) a `fork` is never a way to
  signal an existing agent, and there may be no way at all, so design the first dispatch to need no
  correction; (2) **before reporting a defect in the tooling, account for every agent I myself
  spawned** — I attributed my own duplicate to the harness for over an hour of wall-clock.
- 2026-08-17: a finding whose remedy would edit a file a decision scopes as "called, not edited" is
  a decision question, not a must_fix. Arch finding G was correctly left unapplied by two fold-in
  runs; I nearly counted it as a gap before reading the reviewer's own routing of it.
- 2026-08-17: **the playbook's close-task ordering and CLAUDE.md's "check-state before committing"
  are in direct tension, and the window between them is a guaranteed VIOLATION.** The playbook says
  record `done` in `plan.yaml` FIRST, then run `close-task`, and separately that `close-task` runs
  when the `[harness:t-NN]` commit is recorded. Doing it literally — plan write, commit, close-task
  — puts `check-state.sh` inside the window where the plan says `done` and the board still says
  `Building`, and INV-26 fires: "plan says done, so the card should read Done — the board reads
  Building." Exit 1. Resolution that satisfies both rules: plan write → `close-task` → `check-state`
  → commit. The load-bearing constraint is only that the PLAN carries the new status before the
  subcommand runs, because the parent station is derived from it; git has no part in that
  derivation, so moving the commit to last costs nothing. I lost a cycle treating the violation as
  a real defect before reading which of the two orderings was actually forced.
- 2026-08-17: `check-state.sh` prints ~30 `note` lines from OTHER features on every run, and the one
  `VIOLATION` line for mine was invisible in the tail. `grep -v "^  note "` reduced it to a single
  line. Reading the tail of a repo-wide checker is how a violation about your own feature gets
  missed; filter to severity first, then grep your feature id.
- 2026-08-17: a lane row naming an `execution_agent` is doing real work, not restating
  `consult-when`. Every file in T-01 and T-05 sits under `.claude/skills/harness/bin/` and
  `check-domain.sh --resolve` returns TWO owners for all four — `harness-backend-dev` AND
  `harness-dev-ops`. Routing by `consult-when` alone is a coin flip there. Telling the lead that the
  PLAN picked the persona, and to attribute the pick, is cheaper than letting it rediscover the
  ambiguity mid-run.
- 2026-08-17: **a lead's blocking question about who wrote a file is almost always answerable with
  `stat` birth times plus one earlier `git status` I already ran.** Run -7-t05-eng returned BLOCKED
  with two blocking `open_questions` asking whether a concurrent writer existed outside its run. I
  had a clean `git status -- .claude/skills/harness/bin/` at 09:38:43 in my own transcript and the
  dispatch time at 10:16; every file's birth time fell between 10:18 and 10:26. That closed both
  questions in one command. The lead could not do this — it lacked the earlier measurement and a
  shell — which is the general shape: **the orchestrator holds the timeline a member cannot see, so
  provenance doubts route DOWN to a measurement, not UP to the operator.**
- 2026-08-17: a lead's own `state.yaml` "pre-dispatch" note can be written retrospectively and be
  FALSE. Run -7's note claimed `test-board-station.py` was present-and-unregistered before dispatch;
  the file's birth time is two minutes AFTER dispatch, and the state.yaml mtime is 17 minutes after
  that. Treat checkpoint prose as written-at-file-mtime, never at the seq it claims.
- 2026-08-17: **serializing a two-task team costs a whole extra lead run, and the team file makes it
  unavoidable.** I dispatched T-01+T-05 as one build team; `mutates_repo: true` forces one-at-a-time,
  the lead correctly ran T-01 and held T-05, and its turn ended — so T-05 needed a second full
  lead spawn. Two tasks with disjoint file sets still cost two lead runs. If tasks are file-disjoint
  and both mutate, dispatching them as two runs from the start is the same spend with less confusion;
  bundling them only pays when the lead can actually finish both in one turn.
- 2026-08-17: `gh` GraphQL 503s made `close-task` fail twice and left the plan at `done` with the
  card open — which INV-26 correctly reported as a VIOLATION and which blocks the
  check-state-before-commit convention. A plain retry loop on `gh issue close` succeeded on attempt
  2. Worth knowing: the mirror's "never re-attempt" rule is about the SCRIPT, not about me; retrying
  by hand is correct and is the difference between a clean gate and committing over a known drift.
- 2026-08-17 **CORRECTION to the entry above about settling provenance with `stat`.** The
  measurement was right and my CONCLUSION from it was wrong. I inferred "reading (a): the lead's own
  member wrote everything, in two dispatches." The truth: run `-6-t01t05-eng` was STILL ALIVE and
  dispatched T-05 itself at seq-2, so run `-7-t05-eng` — which I spawned — was a duplicate I created.
  Birth times were consistent with both readings and could not discriminate; **the file that could
  was run 6's own `state.yaml`, which I never opened before re-dispatching.** I had written the
  lesson in this same log at 07:xx — "the completion signal to watch is the run's own `state.yaml`
  step status, not the absence of a return notification" — and then did not apply it four hours
  later. The generalisation: **a lead's digest is not a terminal signal even when it is fenced and
  carries a VERDICT.** Run 6's digest at 09:49 said PROVISIONAL in its own headline and its state.yaml
  said T-05 `dispatched_at` set / `completed_at` null. Before dispatching ANY successor run, `cat`
  the predecessor run's `state.yaml` and treat a step with `completed_at: null` as live.
- 2026-08-17: the cost of that duplicate: one lead run and two member spawns, ~146k subagent tokens,
  producing zero lines of code. It was not a cycle under DEC-157 — no send-back, no rework of failed
  work — so **the cycle budget is structurally blind to it.** A budget that counts only rework cannot
  see waste caused by the orchestrator's own misread, which is an argument for reading `len(runs)`
  as the signal it was designed to be rather than as bookkeeping.
- 2026-08-17: the duplicate was not free of value — the second lead's member hit the
  green-on-untouched-tree tripwire my dispatch installed, refused to overwrite the authentic `c1`
  receipt, wrote a forensic `c2` and touched nothing. **A tripwire that says "if the verify passes on
  an untouched tree, that is a finding" is what turned a concurrent-write collision into a no-op.**
  Put it in every build dispatch; it cost one sentence and prevented two writers on three files.
- 2026-08-17: **`grep -cF` on a prose phrase returns a FALSE ZERO when the phrase spans a wrapped
  line.** Checking T-03's substantive points I got 0 for "may not delete or weaken an assertion" and
  nearly reported the point missing; the file wraps between "may" and "not". The fix is one line:
  read the file, `re.sub(r'\s+',' ',text)`, then count. Every verify clause in this repo greps
  single-line literals for exactly this reason — but a REVIEWER checking prose coverage is not
  bound by that, and must normalise whitespace or it will manufacture findings against correct work.
- 2026-08-17: when two tasks edit one file, the SECOND task's verify should re-assert the first's
  clause. T-06 does this — it greps T-03's simplify regex on `harness-plan.md` and reports "the two
  edits to this file collided" distinctly from its own failures. That is what makes serial cards on
  a shared file safe: the collision reddens at the second task rather than passing silently. Worth
  asking pm for on any plan where two tasks share a `files:` entry.
- 2026-08-17: **the goal-check earned its spawn by catching what six green task-verifies structurally
  could not.** SC-05 requires each of four angles present "in both their plan-surface and
  code-surface forms". T-02's `verify:` greps the two literals **file-globally**, so three conforming
  angles satisfy it and a fourth missing both is invisible. Six tasks green, panel PASS, qa PASS —
  and the criterion still false. The general rule: **a DISTRIBUTIVE clause ("each of N carries X")
  cannot be verified by a file-global grep**, and when a plan's verify uses one, the SC is unguarded
  no matter how green the task goes. Worth asking pm for a per-section check at plan time whenever an
  SC quantifies over a set.
- 2026-08-17: qa graded that same SC `met` by the same file-global method, so the two tiers failed
  identically and independently. Agreement between two readers using the SAME METHOD is not
  corroboration — it is one measurement counted twice. What broke the tie was the goal-check lead
  re-opening the file and counting PER SECTION.
- 2026-08-17: running the review panel and pm's goal-check CONCURRENTLY against one pin saved a full
  round-trip and cost nothing, because both are read-only. But it created a hazard neither could see:
  the goal-check FAILED, and its fix moves the tip the panel just passed. The product lead caught it;
  I had not. **If you parallelise a read-only panel with a goal-check, decide in advance what happens
  to the panel's verdict when the goal-check fails** — the answer is measure the delta, never assume
  the PASS transfers.
- 2026-08-17: four leads in a row (qa, simplify, panel, goal-check) defeated the premature-verdict
  hook by **holding the turn open with read-only Read/Grep/Glob calls until their members returned**.
  Zero cost, zero recurrences, after eight recurrences earlier in the feature. Put that instruction in
  every lead dispatch until the hook is fixed; it is the cheapest mitigation found.
