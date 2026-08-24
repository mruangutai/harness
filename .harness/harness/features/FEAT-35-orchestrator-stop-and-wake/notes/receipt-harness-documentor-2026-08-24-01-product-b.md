# Receipt — harness-documentor — FEAT-35 — 2026-08-24-01-product-b

**PASS.** DEC-201's `echo hold` count is 341 everywhere, the shape of the other 13 calls is now in
the entry, and `DECISIONS-INDEX.md` needed no change.

## What changed — `.harness/harness/docs/DECISIONS.md`, DEC-201 only

Two `342` → `341`: the "Over keeping the orchestrator alive" narrative, and the control sentence in
"The open measurement" ("1043 events of which 575 assistant and 341 `echo hold` calls").
`grep -c 342 DECISIONS.md` now returns 0 for the whole file.

One sentence added to the narrative paragraph, between the watchdog-kill clause and
"A partial return is resumable":

> The other 13 were not that command again: `sleep N; echo tick`, `echo waiting`, `echo heartbeat`,
> `date '+%H:%M:%S tick'`, `echo t`, `echo t1`, a bare `sleep N`, and one trailing a real
> `git status` — an agent with nothing to do does not merely repeat itself, it keeps INVENTING new
> ways to look busy.

Nothing else in DEC-201 moved. The clause "was killed by the platform's 600s no-progress watchdog"
and the prior control-sentence rewrite are byte-identical apart from the digit.

## The measurement, taken from primary source, not carried forward

Re-derived over Bash `tool_use` blocks in
`~/.claude/projects/-Users-molchairuangutai-GitHub-harness/070b3f94-b495-4deb-b352-6896cfb60ad3/subagents/agent-a95e1e6e97e80de87.jsonl`:

| measure | value |
|---|---|
| total Bash `tool_use` blocks | 450 |
| commands containing `echo hold` | 341 |
| commands matching `\bsleep\b` | 13 |
| both in one command | 0 |
| either | 354 |

341 + 13 = 354, nothing double-counts. **My previous run's 355/14 was one high and is withdrawn** —
a word-boundary count of `sleep` gives 13. All 341 `echo hold` commands are the identical string
`echo hold`; the 13 are 12 distinct strings (`sleep N; echo tick` appears 6 times across five
different N, the rest are singletons), which is what the added sentence reports.

Unchanged and re-verified present exactly once each: `354`, `450`, `1043`, `575`, `600.0s`,
`3457.4s`, `642.6s`, `642.7s`.

## Index

`gen-decisions-index.py --stdout | diff -` against `DECISIONS-INDEX.md` is clean, so no
regeneration and no hand-edit. DEC-201 is the last row and its `@6800` anchor still lands on
`## DEC-201 —`; both edit sites are below it, so the added lines shifted nothing. The index's `M`
status in `git status` is the pre-existing DEC-201 row from an earlier task, not this run.

## Open

None. Not committed — the main session commits.
