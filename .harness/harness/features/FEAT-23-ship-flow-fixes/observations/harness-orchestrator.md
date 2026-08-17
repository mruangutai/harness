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
