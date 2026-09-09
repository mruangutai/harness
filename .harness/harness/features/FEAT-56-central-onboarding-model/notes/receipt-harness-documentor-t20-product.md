# Receipt — T-20 — amend DEC-83 and BUILD.md (version band survives, declared floor does not)

**PASS.** The verify block ran verbatim from the worktree root and exited 0. DEC-83's pin bullet and
BUILD.md's pin sentence now record the 2.1.217 band as a compatibility fact a reader checks; the
`cli_min_version` key is named in DECISIONS.md as removed-and-why, and appears nowhere in BUILD.md.
No new `## DEC-` entry, no "Amended by" paragraph, no dated sub-section, no attribution.

Agent: harness-documentor · run: t20-product · HEAD at spawn: 44e97ca0 · plan cross-check: T-20's
`intent:` and `verify:` in `plan.yaml:2112-2176` match the dispatch verbatim.

## What changed — three sentences, rewritten in place (DEC-205 house form)

1. `.harness/harness/docs/DECISIONS.md:977-981` (was the single line `- **Pin CLI ≥ 2.1.217** — the floor
   for all three spawn env vars. Nothing pinned a version before.`) → now states that no
   `cli_min_version` is declared in any configuration file — not `.harness/harness.json`, not
   `.harness/team-config.yaml`, not the three templates — because nothing ever read it (no reader, no
   schema entry, no reference under `.claude/skills/harness/bin/`), and that the 2.1.217 floor stands as
   the band table's documented compatibility fact, consulted by a reader rather than enforced by a gate.
   The key is named literally so a future grep finds the reason it is gone.
2. `.harness/harness/docs/BUILD.md:96-97` — the pin-doctrine first clause is now
   `**CLI ≥ 2.1.217 is the floor for all three spawn env vars** — a compatibility fact to check against
   the bands above, declared nowhere in config —`. The `set the depth explicitly to \`3\`` instruction and
   the following sentence (`Setting it explicitly is correct in *all* bands …`) are unchanged.
3. `.harness/harness/docs/BUILD.md:436` — the `.harness/harness.json` key enumeration drops the
   `cli_min_version: "2.1.217"` item and ends cleanly on `` `schema_version`. ``
4. `.harness/harness/docs/DECISIONS-INDEX.md` — regenerated with `gen-decisions-index.py`. 128 rows
   changed; after normalising `@<line>` every changed row is byte-identical to its predecessor, i.e. the
   diff is purely the anchor shift DEC-83's longer bullet caused. No row text changed.

Untouched, as the intent requires: the verified `env-vars` quote and band table (DECISIONS.md:957-969),
BUILD.md:33/:78/:85-86/:88-94, and the platform-claims verification rows.

## The BUILD.md "Requires CLI ≥ 2.1.217" judgement (intent's `:517`, now line 526)

**Left exactly as it stands, as a verified record.** `Verified 2026-07-26 against \`code.claude.com/docs\`.
**Requires CLI ≥ 2.1.217.**` heads the `## Platform claims — cited, quoted, version-pinned` table and
scopes *the claims below it* — the row beneath it (`CLAUDE_CODE_MAX_CONCURRENT_SUBAGENTS … min-version
2.1.217`) is what the sentence is about. It is a statement about which CLI the documented env vars exist
on, addressed to a reader checking the evidence, not an instruction to declare a floor in config. It
therefore needed no repointing; adding a cross-reference clause would have restated what the adjacent
row already says.

## Observation for a later task — NOT edited here (lead's scope ruling)

`BUILD.md:88` reads `**Version bands — the behavior changed three times, so the CLI version must be
pinned:**`. That heading sits inside the intent's untouched `:88-94` range, so it stands. Its "must be
pinned" framing is residual pin doctrine and now sits two lines above a sentence saying the floor is
declared nowhere in config; a follow-up should reword it to "so the band matters". Recorded, not acted on.

## Evidence

### Before any edit

```
grep -c cli_min_version .harness/harness/docs/BUILD.md      -> 1          DISCRIMINATING: RED
grep -n cli_min_version .harness/harness/docs/DECISIONS.md  -> no match   DISCRIMINATING: RED
grep -c '2.1.172' .harness/harness/docs/DECISIONS.md        -> 2          preservation: GREEN
grep -c '2.1.172' .harness/harness/docs/BUILD.md            -> 2          preservation: GREEN
grep -c '2.1.219' .harness/harness/docs/BUILD.md            -> 2          preservation: GREEN
grep -c '^## DEC-' .harness/harness/docs/DECISIONS.md       -> 204
```

### After

```
grep -c cli_min_version .harness/harness/docs/BUILD.md      -> 0          DISCRIMINATING: GREEN
grep -c cli_min_version .harness/harness/docs/DECISIONS.md  -> 1          DISCRIMINATING: GREEN
grep -c '2.1.172' .harness/harness/docs/DECISIONS.md        -> 2          preservation: still GREEN
grep -c '2.1.172' .harness/harness/docs/BUILD.md            -> 2          preservation: still GREEN
grep -c '2.1.219' .harness/harness/docs/BUILD.md            -> 2          preservation: still GREEN
grep -c '^## DEC-' .harness/harness/docs/DECISIONS.md       -> 204        equal to before: no new entry
git diff -U0 -- DECISIONS.md BUILD.md | grep -c 'Amended by'  -> 0
```

### The verify, verbatim, from the worktree root (after regenerating the index)

```
$ ! grep -q cli_min_version .harness/harness/docs/BUILD.md &&
  grep -q cli_min_version .harness/harness/docs/DECISIONS.md &&
  grep -q '2.1.172' .harness/harness/docs/DECISIONS.md &&
  grep -q '2.1.172' .harness/harness/docs/BUILD.md &&
  grep -q '2.1.219' .harness/harness/docs/BUILD.md &&
  env -u HARNESS_AGENT_TYPE python3 .claude/skills/harness/bin/check-decision-anchors.py &&
  env -u HARNESS_AGENT_TYPE python3 .claude/skills/harness/bin/gen-decisions-index.py --stdout | diff - .harness/harness/docs/DECISIONS-INDEX.md
examined 34 anchor(s), 0 failed
VERIFY_EXIT=0
```

### `git status --porcelain` — nothing committed

```
 M .claude/commands/harness-grilling.md
 M .claude/commands/harness-plan.md
 M .claude/commands/harness-ship.md
 M .claude/commands/harness.md
 M .claude/skills/harness-grilling/SKILL.md
 M .claude/skills/harness/references/github-mirror.md
 M .claude/skills/harness/templates/BRIEF.md
 M .claude/skills/harness/templates/DESIGN.md
 M .claude/skills/harness/templates/PLAN.md
 M .claude/skills/harness/templates/harness.json
 M .harness/harness/docs/BUILD.md
 M .harness/harness/docs/DECISIONS-INDEX.md
 M .harness/harness/docs/DECISIONS.md
 M .harness/harness/features/FEAT-56-central-onboarding-model/plan.yaml
?? .harness/harness/features/FEAT-56-central-onboarding-model/notes/receipt-harness-documentor-t20-product.md
?? .omp/commands/
```

Mine are the three `.harness/harness/docs/*` files plus the untracked receipt. Everything under
`.claude/commands/`, `.claude/skills/` and `.claude/skills/harness/templates/` is the main session's
concurrent T-12, and `plan.yaml` was already modified at spawn — all left untouched. `.omp/commands/`
is untracked tooling state, not mine. Nothing was committed.
