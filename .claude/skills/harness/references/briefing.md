# The CEO briefing — three triggers, not every completion

Read this when one of the three triggers fires: `ship-feature` completes · a lead returns
`BLOCKED` · the main session relays "where are we?". History: DEC-69, DEC-138, DEC-141.

1. **Do NOT spawn a report round — read the digests from disk.** `feature.json` `runs:` names
   every `runs/<run-dir>/digest.md`, so a "report on your domain" spawn buys a re-narration of a
   file you can open (DEC-69). **Read every one, including phases you did not run** — a ship-phase
   successor inherits a ~60-line handoff note, not the plan and build digests, so a briefing built
   from context alone silently omits whole phases. If a digest cannot answer something the
   briefing needs, spawn **that one lead** with the specific question, never all three.
2. **Disclose it (DEC-69).** Say that no report round was spawned and **name the digest paths you
   assembled from** — without that the reader cannot tell a complete briefing from one missing a
   phase.
3. **Assemble one document:** each lead's summary cited to its digest by path, all open questions,
   resolved escalations, the goal-check result per perspective, the feature's spend
   (`feature-record.py spend`) and judgement count, the UAT if required, and a **proposed
   backlog** table with an `ID` column (`B-1`, `B-2`, …) — one row per residual finding that
   survived collation but does not gate, each with its nature (`bug`/`chore`/enhancement). The
   IDs let the user strike rows by name. Unstruck rows become backlog issues on ship acceptance
   (DEC-138), and **anything not listed dies silently — list them all.** When `len(runs)` has
   passed `max_total_runs`, say so here: the count, the budget, and your one-line read on whether
   the runs still earn their place. Never as an apology.
4. **Write it** to `<HARNESS_FEATURE_TREE_ROOT>/.harness/harness/features/<FEAT>/notes/ship-review-<runid>.md`
   — plain English, conclusions first, the one artifact addressed to a human. Then
   `bin/render-brief.py <that path>` renders the reading view; the markdown stays the record and
   the HTML is **never hand-authored** (DEC-141).
5. **Return it** as `briefing:` in your digest. The main session presents it and sends the
   instruction — ship, fix, re-scope, stop — back down to you.
