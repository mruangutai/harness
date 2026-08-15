# Receipt — T-14 — strike DEC-12, strike DEC-113 in part

**DEC-12 is gone from the record and DEC-113 keeps only its override ruling.** Verify exits 0
(`STRUCK`), the index generator is clean, and `run-unit-tests.sh` is 0 with
`PASS test-gen-decisions-index.py`. Nothing committed.

## What changed

- `docs/harness/DECISIONS.md` — DEC-12's whole section deleted, heading included (it sat between
  the agent-manifest entry and `## DEC-13`). DEC-113 retitled and reduced to its surviving ruling.
  Three hunks total, all intended: `@@ -149,11 +148,0`, `@@ -1975 +1964`, `@@ -1987,20 +1976,8`.
- `docs/harness/DECISIONS-INDEX.md` — DEC-12's row removed, DEC-113's hand-written summary
  rewritten, generator re-run. Every other changed row differs **only** in its `@NNNN` anchor
  (verified by parsing `git diff -U0` and comparing row bodies with the anchor stripped).
- `docs/harness/BUILD.md` — one parenthetical removed from the sentence ending `first half dumb
  and safe`. Nothing else in that paragraph touched; T-12's struck sites untouched.

## DEC-12 inbound references — the full enumeration

`git grep -nE 'DEC-12([^0-9]|$)' -- . ':!.harness/logs' ':!.harness/notes' ':!.harness/features'`
returned exactly three hits, all inside T-14's `files:` and none in a DEC-174 carve-out file:

| Hit | Disposition |
|---|---|
| `docs/harness/DECISIONS.md:149` — the section heading | deleted with the whole section |
| `docs/harness/DECISIONS-INDEX.md:32` — the index row | deleted, then regenerated |
| `docs/harness/BUILD.md:393` — parenthetical citation | deleted together with the claim it carried |

The search covered `.claude/skills`, `.claude/commands`, `.claude/agents`, `CLAUDE.md` and
`README.md`; no preloaded skill cited DEC-12.

## DEC-113 after the strike

- **New title:** `## DEC-113 — Team and crew overrides live outside the tool tree, and are
  resolved first`. It names the surviving ruling and nothing else. A title retaining "deploy
  reconciles instead of copying" was rejected: `.claude/skills/harness/bin/deploy.sh` was deleted
  in e987c6d, so that clause would assert a mechanism the tree no longer has. The title opens
  with no supersession verb, so `gen-decisions-index.py` does not stamp the row (G-07).
- **Rulings 1 and 3 deleted.** The block heading `### Three decisions, each a deviation worth
  naming` became `### The deviation worth naming` in the same edit, and the orphaned `**2.**`
  numbering went with it (G-11, G-10).
- **Ruling 2's replacement justification:** the skill tree is this repository's own source,
  rewritten by harness development itself, while the override directory is project-owned state
  harness development never edits — so precedence only holds if the override sits outside the
  tool tree. Ruling 2's claim text and its `crews` naming were left alone; the crew→team rename
  is a separately recorded decision.

## Gate results

| Check | Result |
|---|---|
| T-14 `verify:` (run as one script from repo root) | **exit=0**, printed `STRUCK` |
| `gen-decisions-index.py` | exit 0, silent, **no ORPHAN** — matches the SUPERSEDED note for 835b297 |
| `run-unit-tests.sh` | exit 0, `PASS test-gen-decisions-index.py` |

The `grep -q 'harness/teams'` assertion is green off the crew→team rename record later in
DECISIONS.md, as the dispatch measured; nothing was written to satisfy it.

## Left standing deliberately — two stale citations

1. `docs/harness/BUILD.md:829` cites DEC-113 for the `agent_skills`-cleanup ruling that this task
   deleted. Out of T-14's scope (step 3 is DEC-12-only) and inside T-12's reserved BUILD.md
   sites. A reader following it now lands on a decision that no longer says it.
2. DEC-113's remaining body — `### What the fixture caught that reading did not` and
   `### Safety properties, and why each exists` — narrates the behaviour of a shell script that
   e987c6d deleted, and the safety block still rests on wholesale replace, the footing removed
   from ruling 2. Out of T-14's scope (the intent named the title, ruling 2's justification, and
   rulings 1 and 3 only). The verify's absence pattern does not reach either block.

`.claude/skills/harness-team/SKILL.md:37`, `docs/harness/SPEC.md:277` and `:2007` cite DEC-113 for
ruling 2 only and remain valid — checked, no action.
