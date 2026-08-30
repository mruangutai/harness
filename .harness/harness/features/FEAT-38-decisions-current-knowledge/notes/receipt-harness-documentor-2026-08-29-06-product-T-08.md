# T-08 receipt — 28 amendments folded into 14 owner decisions

**All 28 live amendments are folded and the dead DEC-145 block is deleted.** The task's `verify:`
block, run verbatim from the worktree, exits **0**; the generator emits exactly the fifteen expected
ORPHAN lines and no other stderr. Only `.harness/harness/docs/DECISIONS.md` was edited (57 hunks,
+381/−829); the 188 `^## DEC-` headings are unchanged in number and text, and DEC-181 is untouched.

## Falsified claims preserved as current-truth clauses

One line per claim; each now reads as present-tense truth in the owner entry, with no date and no
attribution.

| Owner | The claim the tree measured false, now stated so it cannot be re-proposed |
|---|---|
| DEC-11 | `hooks` is not a frontmatter capability at all — agent-frontmatter `PreToolUse` hooks do not fire for spawned subagents; enforcement lives in `.claude/settings.json` |
| DEC-142 | the title convention's `·` and spaces are illegal in an agent `name`; a name omitting the flow id while the description carries it reproduces the untraceable-spawn failure |
| DEC-145 | authoring discipline does not hold the Expertise caps — where the checker was not yet deployed, 9 of 15 files failed it again within a day of distillation |
| DEC-149 | mission `deepen` was tried and retired — it read a codebase map tier removed after 35 features never built one, so it had nothing to scan |
| DEC-152 | the three domain leads at `effort: high` was tried and reversed; the `high` tier is four agents, not seven |
| DEC-157 | counting rework only leaves length unmeasured — FEAT-03 ran 19 times against a 6-cycle count and tripped nothing, and cost no longer exists as the other signal |
| DEC-158 (move 3) | keying extraction on FREQUENCY does not survive contact: the `gh-sync.py` contract runs every ship and the context probe every wake, yet both are lookup-shaped |
| DEC-158 (pointers) | a pointer can be silently skipped — every preloaded artifact worked first contact, every pointed-at artifact failed silently at least once |
| DEC-158 (move 1) | the orchestrator playbook's red-flag table restated rules already in its body; the other nineteen tables stand, so this is one file's narrowing |
| DEC-171 | graceful degradation to a line scanner was reversed — a fallback keeps a hand-rolled parser at every call site and its bugs are never exercised |
| DEC-171 | fail-OPEN on a missing PyYAML was rejected for the two guards: the project is configured, the hook has no bug, one action resolves it |
| DEC-174 | the factory-workspace route was reachable but never sanctioned; a harness path there now resolves to no declared repository and `--resolve` exits 2, not NOBODY |
| DEC-174 | declaring the station board in `fleet.yaml` was tried twice (top level, then per `repos[]` entry) and reversed; `load_fleet` REJECTS both |
| DEC-183 | a lighter in-workflow guard is not the answer — a `safe_load` predicate was planned then abandoned, because it cannot see the deletion of the step that runs it |
| DEC-189 | the glob-keyed-classifier argument covers ONE of the four named paths, not two — `README.md` and `.github/**` are verbatim grants |
| DEC-193 | "preserved" held for two of three fleet states — a malformed `fleet.yaml` now refuses every write outside the harness root (0 → 2) |
| DEC-193 | `<product>` for the second write location is both a second name for one segment and the narrower word |
| DEC-194 | keying applicability to the checker's own path fails by construction — `harness-init` installs `bin/` into products, so every onboarded product reported CANNOT VERIFY forever |
| DEC-194 | accepting any first-level `.harness/` subdirectory as a repo root forces a MIXED verdict no reader edit can clear |
| DEC-194 | "every finding names the reader path" overclaimed — `blame()` may return an empty list, structurally always for no-rows |
| DEC-138 | there is no third category between doing the work and not — `absorbs:` was struck, and nothing closes an issue because another task mentioned it |
| DEC-138 | branching a parent's fate on recorded origin failed on the two newest cases: `parent_origin` read null on FEAT-34/35 and #728 sat open with thirteen finished children |
| DEC-138 | a closed issue's card does not move on its own — #818–#830 are all closed and all sit at `Review` |
| DEC-138 | the blanket ban on agent-authored comments was too wide; the line is PROVENANCE, not which skill is asking |

## The five misfiled blocks

Attributed by the id in their own heading, never by span.

- `DEC-138 amendment 5`, `6`, `7`, `8` sat inside DEC-168's span → folded into **DEC-138**, and
  removed from DEC-168, whose remaining text (cascade measurement, `sub_issues_summary` eventual
  consistency) is untouched.
- `### DEC-189 amendment 1 (2026-08-16)` sat inside DEC-194's span → folded into **DEC-189** (named
  path respelled `.harness/*/docs/**`, redundancy note, ONE-of-four arithmetic correction).
- **The two blocks both titled `DEC-189 amendment 1` were folded SEPARATELY**: the 2026-08-20 one
  (illustrative paths spelled `<repo>`, already reflected in the body, so its remaining content is
  the one-name rule now stated in DEC-193) and the 2026-08-16 one above.

## Deleted rather than folded, with justification

- **The MOOTED DEC-145 block** (`Note (2026-08-24): am.3 below is MOOTED` plus the ship-refresh
  amendment beneath it). Dead: ship-refresh was removed with the codebase-map tier, so there is no
  second dispatch to run concurrently with. DEC-205 already records that this block's reasoning is
  recoverable only from history.
- **DEC-138's SC-13 pre-ship prose note** (the two `.claude/skills/harness/SKILL.md` sites and the
  staleness-marker reasoning). Checked, not assumed: `grep 'everything it absorbs'` on that file now
  returns nothing, so the to-do is discharged and its reasoning was about a marker never declared.
- **DEC-138's "codebase map" entry** in the not-mirrored list — that tier no longer exists (DEC-149).

## Collateral corrections inside the file

Deleting the structures orphaned six citations that named them. Each was repointed to the owner
entry rather than left dangling: DEC-165 ("DEC-138's amendment"), DEC-170 ("DEC-138 am.6"), DEC-190
(two × "DEC-171 am.1"), DEC-200 (three × amendment 6/7, including a `DECISIONS.md:4359-4362` line
anchor that my edit invalidated), DEC-203 (amendment 7's parent table, amendment 8's station row).
DEC-200 quotes DEC-138's write-only clause verbatim, so that clause was kept in DEC-138's own voice
("issue state is never read back into an approval-gated artifact"). Two stale phrasings the fold
would otherwise have preserved were also corrected: DEC-149's glossary path (`.harness/glossary.md`,
matching `harness-spec-driven/SKILL.md:132`) and its "update at ship-refresh" trigger, and DEC-189's
"nothing in `docs/` outside `docs/harness/`".

## Verification

- Task `verify:` block, verbatim, from the worktree: **exit 0**.
- Generator stderr contains exactly fifteen `ORPHAN: DEC-N …` lines — 19, 20, 37, 67, 82, 88, 92,
  102, 103, 104, 137, 140, 186, 192, 196 — and nothing else; `gen-decisions-index.py` exits 1, which
  is the expected shape until T-11 regenerates the index.
- `grep -c '^## DEC-'` is 188 before and after, and the diff contains no `+`/`-` line matching
  `^## DEC-` or `DEC-181`.
- Structural sweep: no `^### DEC-N amendment`, no `^**Amendment`, no `am.N`, no `MOOTED`, no orphan
  section, no empty decision body.
- DEC-138's shipped behaviour was read from code before being written down: `gh-sync.py` holds no
  `parent_origin` branch, and `cmd_ship` HELDs a parent on the first child whose card is not at the
  done station (`gh-sync.py:1296-1320`).
