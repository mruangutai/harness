# T-07 receipt — delete the eight superseded entries, repoint citations

**Done. T-07 verify exits 0** (baseline before any edit: **1**, first failure `kept 19`).
**T-05's verify re-run after my edits also exits 0** — no regression on the sibling task.
Generator stderr is 15 `ORPHAN:` lines and nothing else: my eight plus T-04/T-05's seven, which is
the failure shape T-07 asserts. `DECISIONS-INDEX.md` untouched and absent from `git status`.

`verify:` block cross-checked against `plan.yaml` T-07 (`plan.yaml:588-602`) — byte-identical to the
dispatch. HEAD unmoved at `57a3bf3`; MAIN checkout `git status --porcelain -uno` empty.

## Per-id account — every repoint is a rewrite, none is an id swap

| Deleted | Sites | Outcome |
|---|---|---|
| **DEC-19** | 16 (15 `DECISIONS.md`, 1 `BUILD.md`) | **Mixed, by site.** Cited DEC-85 at the 3 sites where DEC-85 demonstrably carries the claim (DEC-18's lead-safety caveat, DEC-58's `Bash`-bypass tradeoff, DEC-85's own `Over:`) — DEC-85 says verbatim *"a useful guardrail over the common `Write`/`Edit` case, **not** a guarantee"* and its point 1 is the `Bash` bypass. At the other 13 the citation was for the **pattern**, which DEC-85 does not hold: I stated the pattern in words and dropped the pointer — *"an unenforced write path around a guarded surface"* (GitHub sync, bug lane), *"prose guarding a safety claim"* (DEC-122's three-lesson list, DEC-123, DEC-125 addendum), *"bare imperatives get rationalized around"* (DEC-158 ×2), *"the test for when prose must become a script"* (wayfind), *"approval bypass class"* (BUILD D5). `DEC-19/DEC-122` → `DEC-122` alone, which does carry it. |
| **DEC-20** | 4 | DEC-63 cited at 3 (its own title, `Over:`, `Because:` — all inside DEC-63, which holds the replacement). At DEC-61's findings list DEC-20's *finding* ("`agent_skills` was the only rule-delivery mechanism") is not in DEC-63, so the finding is stated in words and DEC-63 cited only for the replacement. |
| **DEC-37** | 3 | DEC-70 carries it — its own `Over:` restates the v1 gap. Title suffix dropped, `Over:` reworded to "the declared v1 gap this replaces". |
| **DEC-67** | 5 | **DEC-86 carries only the roster arithmetic, not DEC-67's applier split — so DEC-86 is never cited as a substitute.** Title suffix dropped; DEC-86's body reworded to "The roster arithmetic and SPEC §5.3 said…". DEC-65's `(DEC-66, DEC-67)` → `(DEC-66)`. DEC-110's narrative now states the rule directly and points at the live sites that hold it: `(SPEC §5.3, DEC-87)`. |
| **DEC-82** | 5 | DEC-83 carries it (it is the correction). Title reduced to "Nesting default is 3, not off"; two body clauses reworded to "the earlier reading". `BUILD.md:517` repointed to DEC-83, which holds the corrected default. |
| **DEC-88** | 5 | DEC-95 carries it. Title suffix dropped; three body clauses reworded to "the 'one feature in flight at a time' constraint this replaces" / "the withdrawn constraint". |
| **DEC-92** | 7 | DEC-99 carries the reversal, DEC-93 the A/B withdrawal. Both title suffixes dropped; bodies reworded to "the pilot's original design" / "the pilot gate". `BUILD.md:555` table header → "Before the pilot gate was lifted". |
| **DEC-102** | 11 (4 `DECISIONS.md`, 5 `SPEC.md`, 2 `BUILD.md`) | **DEC-120 carries only the shape change, not the empirical tool-withholding finding.** DEC-120 cited nowhere new; its own sentence reworded to "**The shape changed** — `depth: 2` is no longer the harness shape." The *hierarchical-works* claim (SPEC ×4, BUILD:15) repoints to **DEC-100**, which holds it directly (§3: three concurrent nested spawns). The *tool-withholding* claim (DEC-118, SPEC §11, BUILD:173) is stated with no citation — the mechanism is spelled out in the sentence itself. |

**`DEC-84` introduced as DEC-19's successor: zero.** The only `DEC-84` in the whole diff is its own
heading, on both sides of one hunk (`- ## DEC-84 … — CORRECTS DEC-19's safety rail` /
`+ ## DEC-84 — \`delete: false\` is deleted; it never existed`). Verified: `git diff -U0 | grep '^+.*DEC-84'` → 1 line, that heading.

## Cut shape

Each entry cut heading-through-(next-heading − 1); DEC-19 and DEC-20 were adjacent so the eight cuts
leave **seven** seams. Every neighbourhood here uses the blank-line seam, not `---`, and all seven
reproduce it. Two quoted:

```
orchestrator in the loop for every step (which pushes toward flat hosting).
                                     <- single blank line, DEC-18 -> DEC-21
## DEC-21 — Rules are static, uniform, and human-authored; agents never write them
```
```
written — it is done when it has been run against an input that would expose it.**
                                     <- single blank line, DEC-101 -> DEC-105
## DEC-105 — The per-spawn baseline is ~15.3k tokens; CLAUDE.md is 31% of it, the rules 11%
```

**My own deletions are 153 lines**, not the 853 in `git diff --stat` — the rest is T-05, uncommitted
in this tree at spawn.

## Content inventory — what left the live tree, and where it still lives

Seven of the eight lose nothing: each holding is quoted inside its successor, or at SPEC.md:69 /
BUILD.md:942 (files-only exception), DECISIONS.md:41+685 (`agent_skills`), SPEC §5.3+DEC-87 (applier
split), SPEC §15.2 (worktree concurrency), BUILD.md:629-640 (the withdrawn A/B).

**DEC-102 loses two findings with no live site:** that the `settings.json` `env` block takes effect
mid-session without a restart, and the `Explore`-is-defined-as-"all tools except Agent" confound that
invalidated the first probe. Both recoverable only from history:
`git show 57a3bf3:.harness/harness/docs/DECISIONS.md`, the `DEC-102` section — verified retrievable
at that SHA. Its load-bearing claim — `Agent` stripped from the loaded list *and* the
deferred pool at the cap — survives at `BUILD.md:173-177`.

## Dangling-prose sweep

Swept the three files for wordless references to the removed content (`files-only` / `deliberate
exception`, `one feature at a time`, `agent_skills`, `self-injection`, `defects escaped`, `declared
v1 gap`, `8 doers`, `depth: 2`, `workers-as-leaves`). Every hit either names the content it refers to
or cites a live successor. **Nothing dangling.**

## Stale found — reported, not fixed (out of T-07's scope)

`SPEC.md:2037` and `DECISIONS.md:2167` both describe the depth cap in **layer numbers from the
pre-DEC-120 org** (lead at layer 1, members at layer 2), while `SPEC.md:1399` and `BUILD.md:174`
already use DEC-120's cap of `"3"` (orchestrator 1, lead 2, members 3). Both files contradict
themselves. I removed only the dead ids and phrased my replacements without a layer number
(`SPEC.md:2037`) or in the past tense with the historical number kept (`DECISIONS.md:2167`, which is
DEC-118's own dated record and is correct as history). **The live-doc contradiction in SPEC needs an
owner.**
