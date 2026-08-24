# Receipt — harness-documentor — FEAT-35 — 2026-08-24-01-product

**Done.** DEC-201's control sentence now says BOTH failing sidecars are watchdog deaths, in opposite
shapes. One sentence changed; nothing else in `DECISIONS.md`. The index needed no regeneration.

## The rewrite

`.harness/harness/docs/DECISIONS.md`, inside DEC-201's "**The open measurement, stated as open.**"
paragraph. New text (anchor on the string, not the line):

> The control discriminates: all 115 orchestrator sidecars on the machine were swept and exactly two
> fail, and BOTH are deaths on that same watchdog in opposite shapes — one stalled LOUDLY, 1043
> events of which 575 assistant and 342 `echo hold` calls, ending on a final gap of exactly 600.0s
> after 3457.4s alive; the other produced NOTHING, 8 events and zero assistant, ending on a final gap
> of 642.6s at a lifespan of 642.7s — and they are #744's two incidents, which that ticket files as
> two diseases sharing one watchdog, matching it independently.

Fixes: the old "one with 342 `echo hold` calls, one dead at 642.7s" implied only the second was
killed. It also used 642.7s where a *gap* was implied; the entry now labels 642.6s the final gap and
642.7s the lifespan explicitly.

## Bound of the change

- The preceding narrative "spent 354 of its 450 Bash calls on `echo hold` and `sleep` — 342 of them
  `echo hold`" is UNCHANGED and still at line 6810, byte for byte. Verified by grep after the edit.
- The edit was a single `str.replace` on a string asserted unique in the file (count == 1), so no
  other span could have been touched. File grew 6863 → 6865 lines, all inside DEC-201.
- `.claude/skills/harness/SKILL.md` not touched.

## Index — no-op, confirmed not assumed

`gen-decisions-index.py --stdout | diff - DECISIONS-INDEX.md` is clean. DEC-201 is the last entry and
its `@6800` anchor sits above my edit, so no offset moved. The row summary describes the wake/stop
decision and never mentioned a sidecar, so it needed no rewording either.

## Open — an off-by-one I did NOT reconcile (per dispatch)

Re-measuring `agent-a95e1e6e97e80de87.jsonl` myself over `tool_use` blocks named `Bash`: 450 total
calls (matches), but **341** with `echo hold`, 14 with `sleep`, 355 with either — against the entry's
342 and 354. Everything else re-measured exactly: 1043 events, 575 assistant, final gap 600.0s,
lifespan 3457.4s; and 8 / 0 / 642.6s / 642.7s for `agent-a73a98fe020a2ce41.jsonl`. I kept 342 because
the preceding narrative is frozen at 342 and writing 341 here would contradict it two paragraphs
apart. Raised as Q1, non-blocking.
