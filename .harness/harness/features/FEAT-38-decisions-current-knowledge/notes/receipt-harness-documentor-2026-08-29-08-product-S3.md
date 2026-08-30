# Receipt — documentor — FEAT-38 segment-D S3 — residual amendment fold

**All eight residual amendment paragraphs are folded and DEC-101's falsified bullet is deleted.**
`.harness/harness/docs/DECISIONS.md` only; 6291 → 6277 lines. `DECISIONS-INDEX.md` deliberately NOT
regenerated — T-11 owns it and runs after this.

## What changed, by site (identified by lead-in, line numbers post-edit)

| DEC | fold | now reads |
|---|---|---|
| 38 | lead-in + falsified-design sentence deleted | `**Chose:** the orchestrator is the main session running the /harness playbook` (`:414`); falsification stays in the existing `**Because:**` line |
| 41 | lead-in replaced by its negation | `**Chose:** no harness-synthesizer and no generic consolidation step — panels do not need one` (`:452`); `**Because:**` line untouched, so the defining-job claim is stated once |
| 76 | wrapper dropped, paragraph re-flowed | opens `**Astryx is not globally available as a Claude Code capability.**` (`:878`), still in body position before `**Tradeoff accepted:**` |
| 132 | standalone paragraph merged into the second body paragraph (`:2848-2851`) | "Adding criteria beyond the user's is **expected**, not merely permitted" — no date, no attribution |
| 171 | lead-in rewritten as current truth (`:4099-4103`) | `**PyYAML is permitted.**` + the falsified zero-dependency ruling as one clause ("was measured false: the scanner dropped an entire run from `runs` on a legal trailing `# comment`") |
| 101 | **companion edit** — `- **Zero dependencies.**` bullet and its body deleted | the falsified claim now survives exactly once, in DEC-171 |
| 172 | two-bullet correction → two bold-led prose paragraphs (`:4190-4201`) | **Q1 decided: prose.** Every other clause in this entry is a bold-led paragraph; bullets only made sense while the block was a list of two errors |
| 180 | duplicate block deleted; the surviving statement put in past tense | the `**Superseded:**` block was byte-identical to the sentence already in the `_norm`/`_show` paragraph, so folding = deleting it and changing "The sweep walks" → "Before this change the sweep walked" (`:4700-4704`). Restating it would have been a third copy |
| 202 | clause appended to the "Claude Code stays usable" paragraph (`:5964-5967`) | the reverse link direction "was tried and measured to fail"; `#836` and the issue attribution gone |

## Verification

- Amendment lead-ins: `grep -nE '^\*\*(Correction|Supersedes|Superseded|Amended|Revised|Amendment)'` → **no matches, exit 1**.
- `grep -n 'Zero dependencies'` → **no matches, exit 1**.
- Provenance sweep `#836|same day, per the user|as first written|Both halves were wrong|Amended by` → one hit only, `:4039`, inside **DEC-169** ("SC-06's absence-greps, as first written") — not one of the eight sites, and it describes a prior draft of a *brief*, not this file's own provenance. Advisory, not folded.
- Excluded near misses DEC-99 (`1267-1300`), DEC-178 (`4536-4581`), DEC-187 (`5031-5104`), DEC-203 (`5994-6136`) — HEAD line ranges; my ten hunks start at old lines 414, 453, 880, 1405, 2852, 4105, 4195, 4708, 4727, 5975, none inside any range. All four lead-ins count 1 in HEAD and 1 in the worktree.
- Structure unchanged: `## DEC-` headings 188 → 188; ```` ``` ```` occurrences 27 → 27; consecutive-blank-line pairs 52 → 52.
- Live-surface sweep for the falsified claim (`zero.depend|no YAML library`, case-insensitive, across
  `CLAUDE.md`, `AGENTS.md`, `docs`, `.claude/{skills,commands,agents}`, `.agents`, `.harness/expertise`,
  `.harness/harness/docs`): two hits, both correct. `upgrade-config.py:95` states the historical grounds
  in the past tense; `SPEC.md:1810` says the *replaced markdown* format was "parseable by no YAML
  library", which is true of markdown and is not the ruling. Nothing to repoint.
- `git diff --stat` shows three tracked files. `DECISIONS.md` and my observations log (`+2` bullets,
  the mid-run log `harness-expertise` requires) are mine. **`plan.yaml` is not** — it was already ` M`
  in the porcelain I took before my first edit, and its hunks are a sibling's. Likewise the
  `DECISIONS.md` hunk at old `:5111` (DEC-188's "DEC-181 keeps only its budget rule") pre-existed my
  spawn; it is `Dec188ClauseFix`'s work, not mine. My own ten hunks are listed above.
- Nothing staged, nothing committed, HEAD still `0a120c657cb7`.

### Host-defect cross-check, verbatim

```
$ git -C <WORKTREE> status --porcelain
 M .harness/harness/docs/DECISIONS.md
 M .harness/harness/features/FEAT-38-decisions-current-knowledge/plan.yaml
?? .../notes/receipt-harness-documentor-2026-08-29-08-product-S2.md
?? .../notes/research-residual-amendment-formats.md
?? .harness/notes/grilling-decisions-current-knowledge-2026-08-24.md

$ git -C /Users/molchairuangutai/GitHub/harness status --porcelain
?? .harness/harness/features/FEAT-43-code-risk-grading/
?? .harness/harness/features/PR-922-omp-supervision/
?? .harness/logs/2026-08-25.md   (+ 8 more untracked notes/logs; DECISIONS.md absent)
```

`DECISIONS.md` present in the worktree porcelain, absent from the main porcelain. No misroute.

## Open

- `DECISIONS-INDEX.md` is now stale by 14 lines of anchor drift and `gen-decisions-index.py` is
  expected to exit 1 on orphan rows. T-11's regeneration is what closes that; do not hand-fix.

## Cycle 2 — fence rebalance in DEC-172 (send-back)

**Defect I introduced in cycle 1:** my DEC-172 prose reflow put a literal triple-backtick at column 0,
opening a fence that never closed. Anchored `grep -c '^```'` read 23 (odd) in the worktree against 24
(even) in the pre-feature control at `/Users/molchairuangutai/GitHub/harness/.harness/harness/docs/DECISIONS.md`.
My cycle-1 evidence counted ALL triple-backtick occurrences (27 -> 27), inline ones included, which is
why the imbalance did not surface. The anchored count is what a fence-aware parser uses.

**Fix:** reflowed the sentence only — no content removed, meaning preserved. The clause still reads
"a closing ``` fence at column 0 is an ordinary dedent it handles"; the fence token now sits mid-line.

Before (cycle-1 state, lines 4198-4201):

    `digest ok`, exit 0, because the `artifact:` key at column 0 already ends the block and a closing
    ``` fence at column 0 is an ordinary dedent it handles. **Templates may therefore ship FIRST,
    independently and safely.** What must not ship first is the parser's *rejection* of unfenced returns
    — that is the half that breaks every not-yet-updated agent.

After (lines 4198-4201):

    `digest ok`, exit 0, because the `artifact:` key at column 0 already ends the block and a
    closing ``` fence at column 0 is an ordinary dedent it handles. **Templates may therefore ship
    FIRST, independently and safely.** What must not ship first is the parser's *rejection* of
    unfenced returns — that is the half that breaks every not-yet-updated agent.

### Cycle 2 verification

- `grep -c '^```'` on the worktree file: **22, even**. (It is 22 and not 24 because the two fenced
  blocks that cycle 1's residual-amendment fold deleted took their four fence lines with them; that
  deletion was even, so it never affected balance.)
- All 22 anchored fence lines enumerated and pair open/close in order: 1245/1248, 1310/1313,
  1346/1351, 1939(```js)/1941, 1996/2000, 2072/2078, 2089/2093, 2143/2147, 2252/2258, 2268/2272,
  2712/2716. No stray opener anywhere else in the file.
- Old wrapping gone: `grep -c '^``` fence at column 0'` returns 0.
- `wc -l`: 6277 before, 6277 after — the reflow redistributed four lines, it did not add or drop any.
- Host-defect cross-check: `DECISIONS.md` appears as ` M` in the worktree porcelain and is absent
  from the main porcelain. Nothing staged, nothing committed, HEAD untouched.
- `DECISIONS-INDEX.md` deliberately untouched and `gen-decisions-index.py` deliberately not run —
  T-11 owns both.
