# The CEO briefing — three triggers, not every completion

Read this when one of the three triggers fires: `ship-feature` completes · a lead returns
`BLOCKED` · the main session relays "where are we?". History: DEC-69, DEC-138, DEC-141.

1. **Do NOT spawn a report round — read the digests from disk.** Read every digest `feature.json`
   `runs:` names, including phases you did not run — a ~60-line handoff note is not a phase record
   (DEC-69). If a digest cannot answer something the briefing needs, spawn **that one lead** with
   the specific question, never all three.
2. **Disclose it (DEC-69).** Say that no report round was spawned and **name the digest paths you
   assembled from** — without that the reader cannot tell a complete briefing from one missing a
   phase.
3. **Assemble one document, and open it with the definition of done graded.** First, a table
   from the validate goal-check — one row per perspective of `## Done when — by perspective`:
   the perspective's text as signed, its verdict (met / unmet), the SCs that discharged it, and
   the evidence pointer for each. The operator signed the seats; this is the seats coming back
   graded, before anything else. Then each lead's summary cited to its digest by path, all open questions,
   resolved escalations, the feature's spend
   (`feature-record.py spend`) and judgement count, **the amendments** (below), the UAT if
   required, and a **proposed
   backlog** table with an `ID` column (`B-1`, `B-2`, …) — one row per residual finding that
   survived collation but does not gate, each with its nature (`bug`/`chore`/enhancement). The
   IDs let the user strike rows by name. Unstruck rows become backlog issues on ship acceptance
   (DEC-138), and **anything not listed dies silently — list them all.** When `len(runs)` has
   passed `max_total_runs`, say so here: the count, the budget, and your one-line read on whether
   the runs still earn their place. Never as an apology.

   **Amendments (DEC-229/DEC-230).** One table from `feature.json` `judgements[]` of kind
   `amendment`: the entry's `at`, its `decision` (`T-NN.intent|files|verify`), the reason, and
   whether it is `overruled`. That is every departure from the signed task text the build made
   on its own authority, shown to the operator once, here. Close the table with one line —
   `overrule rate: <overruled>/<total>` — as a count over a count, `0/0` when the build amended
   nothing (never a division). When the operator overrules one, the main session runs
   `feature-record.py overrule-amendment --file <feature.json> --at <that entry's exact at>`
   BEFORE the ship record is finalized; the entry stays in the ledger, marked. No build advisor
   seat and no fresh approval question comes of this: the signature stands, the ledger is the
   audit.
4. **Write it** to `<HARNESS_FEATURE_TREE_ROOT>/.harness/harness/features/<FEAT>/notes/ship-review-<runid>.md`
   — plain English, conclusions first, the one artifact addressed to a human. Then
   `<HARNESS_CONTROL_PLANE_ROOT>/.agents/skills/harness/bin/render-brief.py <that path>` renders
   the reading view; the markdown stays the record and the HTML is **never hand-authored** (DEC-141).
5. **Return it** as `briefing:` in your digest. The main session presents it and sends the
   instruction — ship, fix, re-scope, stop — back down to you.
