# Independent verification of the context arithmetic — orchestrator, build phase

**BLUF.** The plan's corrected arithmetic is RIGHT and I confirmed its central premise exactly. I also
found one latent defect in it and then DISPROVED my own claim that it matters: `usage.iterations`
contains foreign-context `advisor_message` entries, and the plan's rule (max over ALL iterations)
picks the advisor's prompt in 82% of the entries that carry one — but it changes neither published
statistic on any surviving transcript, so it is a BACKLOG row, not a fix cycle. Separately, and this
one does need the operator: **the BRIEF's headline evidence no longer exists on disk.**

Taken by the orchestrator during the T-01..T-13 eng run, so it is a CHECK on the lead's receipt
rather than a restatement of it. Population: `~/.claude/projects/*/*.jsonl`, **76 transcripts across
23 project dirs** as of 2026-08-21 — exactly the count `BRIEF.md:37` cites. 74 carry usage data.

## Confirmed: the top-level field IS a sum, and the corrected method is the max

`plan.yaml:106` and T-01's intent (`:207-210`) are correct in substance. Measured:

- **31,286** entries carry `message.usage.iterations`.
- The top-level `input_tokens` + `cache_read_input_tokens` + `cache_creation_input_tokens` equals the
  **sum over the non-advisor iterations** in **409 of 418** multi-iteration entries — exact, field by
  field, zero rounding. So "reading the top level reports a sum, not a context" is established, not
  assumed.
- Over multi-iteration entries, top-level-as-context / true max is **median 1.987, i.e. +99%**
  (min 1.000, max 1.997). The BRIEF's own headline case is +99% (1,497,025 vs 750,837), consistent.

## The latent defect: `iterations` is not homogeneous, and the plan names no type

`iterations[].type` takes **three** values across the corpus, and neither `plan.yaml` nor `BRIEF.md`
mentions any of them (grepped both for `advisor`, `type`, `iterations`):

| type | count |
|---|---|
| `message` | 31,695 |
| `advisor_message` | 395 |
| `fallback_message` | 9 |

An `advisor_message` iteration is a **different agent with its own context window** — a worked
example: three iterations where iter1 is `type: advisor_message`, `model: claude-opus-5`,
`input_tokens: 103691`, `cache_read: 0` (fresh, uncached), while the two `message` iterations read
100,077 and 101,739 from cache. The top level (`input 4`, `cache_read 201816`, `cache_creation 3109`)
sums the two `message` iterations and **excludes the advisor entirely** — which is the strongest
evidence that the advisor is not part of this agent's context.

Consequence: the plan's literal rule, max over ALL iterations, returns **103,691** there — a foreign
agent's prompt — instead of the true 103,188. Across the corpus this changes the naive max in **325
of 395** advisor entries (**82%**).

The 9 `fallback_message` iterations are exactly the 9 entries where top-level != sum-over-non-advisor,
so fallback is accounted differently again. Unexamined; 9 of 31,286.

## Why it is NOT a fix cycle — I ran the check that settles it, and it overturned me

The tool publishes two numbers: **peak** (max over entries) and **current** (last entry). Both are
unaffected:

- **Peak differs in 0 of 74 transcripts.** An advisor prompt is ~100k; a session's genuine peak
  reaches 750k+, so the contaminated value is never the maximum.
- **Current is contaminated in 0 of 74.** No transcript's last usage entry is even multi-iteration
  (multi-iteration entries are 418 of 31,286 = 1.3%).

So the defect is real per-entry and inert at the reporting surface. Adding a `type == "message"`
filter is a one-line hardening with no observable effect today; it earns its place only because the
ratio of advisor entries is a property of how the operator works, not a constant. **Backlog, not a
gate.** I am recording that my initial read of this as a must-fix was wrong.

## For the operator: the BRIEF's cited evidence has aged out

`BRIEF.md:26` and `:33-37` rest on the docs-migration planner transcript — 992 entries, naive peak
1,497,025, corrected 750,837, "confirmed exactly on transcript line 990: 746,878 + 0 + 747,992 =
1,494,870". **That entry is not on disk.** I searched all 76 transcripts in all 23 project dirs for
`746878`: no match. Claude Code transcript retention is 30 days by default, so the measurement the
BRIEF is built on is already unreproducible.

What the surviving 74 transcripts show, which is a weaker claim than the BRIEF's:

- naive peak == corrected peak in **60 of 74**; they differ in **14 of 74**, up to **+87.4%**.
- median naive/corrected peak ratio is **1.000**, not the BRIEF's ~78%.

Both are honest measurements of different populations, and the BRIEF's is the one that no longer
exists. `BRIEF.md:37`'s "every one of the 76 transcripts carries `iterations`" still holds — 74 of 74
with usage data do — but "the naive method is wrong on all 76" does not reproduce, because being
wrong at the peak requires the peak entry itself to be multi-iteration, which is true for 14 of 74
today.

**This does not invalidate the feature; it sharpens what its tests may rest on.** Fixture-based tests
(T-02, T-07) are self-contained and unaffected — the plan's fixture hardcodes 746878/0/747992 and
stays reproducible forever, which is exactly why fixtures were the right choice. The exposure is
T-13's live half (`verify-context-watch-live.py`): a live check that asserts the BRIEF's *magnitude*
would fail on today's data, whereas one that recomputes inline and compares tool-to-recomputation
passes and is the right design. Per `plan.yaml:892` and `:905-907` T-13 does recompute inline, so it
should be fine — verify at acceptance rather than assume.

## Method, so this can be re-derived

Per iteration, prompt = `input_tokens` + `cache_read_input_tokens` + `cache_creation_input_tokens`,
each defaulting to 0 — the plan's own definition, written inline here and NOT imported from
`context-watch.py`, so this is an independent recomputation and not the tool checking itself.
Population `~/.claude/projects/*/*.jsonl` at 2026-08-21, 76 files, worktree
`.claude/worktrees/harness/FEAT-31` at HEAD e5f88c4. Any re-run after 2026-09-20 will see a different corpus.
