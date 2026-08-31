# Intake reconciliation — FEAT-38 — measured at `7ebfc9e`, 2026-08-29

Measured by harness-orchestrator inside the worktree
`.claude/worktrees/harness/FEAT-38-decisions-current-knowledge`, which is **level with `main`**
(`git rev-list --count HEAD..main` = 0 and `main..HEAD` = 0). Every row below was run, not recalled.
**Where this file and an intake artifact disagree, this file governs** — the grilling was measured
2026-08-24 at a sha that was never an ancestor of anything current, and the triage was measured
2026-08-26.

## 0. The run-1 blocker is CLEARED

`.harness/.inflight-claims.json` in the main checkout reads `{"claims": [], "schema_version": 2}`.
The orphaned `harness-pm` claim that refused run 1 under single-flight — and that triage §8 says
killed four product-lead runs — is gone, and the registry was reworked at HEAD (`fee9d5f` tells a
recycled supervisor pid from the claim-maker; `47a9381` hardens the same file). Nothing needs
clearing before a pm dispatch.

## 1. Corrections to the grilling note (`.harness/notes/grilling-decisions-current-knowledge-2026-08-24.md`)

| Grilling claim | Current truth at `7ebfc9e` |
|---|---|
| `DECISIONS.md` 6,984 lines / 199 entries | **7,414 lines / 202 entries** (`^## DEC-[0-9]+`) |
| `DECISIONS-INDEX.md` 219 lines | **222 lines** |
| 22 entries carry amendment text, 2,046 lines / 29% | **38 amendments**: 25 `### DEC-N amendment` headings across **9** decisions (DEC-137, 138, 142, 171, 174, 186, 189, 193, 194) + 13 `**Amendment` bold-inline across **8**. The triage's §3 count is the correct one and it reproduces at HEAD |
| `DEC-19` repoints to `DEC-84` | **`DEC-85`.** `DECISIONS-INDEX.md:38` reads `— SUPERSEDED BY DEC-85`. DEC-84 appears in the same row's `refs:`, which is what the grilling mistook for the target |
| 13 live citations to superseded entries (DEC-19: 7, DEC-102: 6), 9 files | **29 live occurrences** outside `features/` and `notes/`: DEC-19 **11** across 9 files, DEC-102 **16** across 9 files, DEC-82 **1**, DEC-92 **1**. DEC-20/37/67/88 have **zero** live sites. Frozen receipts additionally hold 40 (DEC-19 14, DEC-102 14, DEC-88 6, DEC-82 4, DEC-67 2) and are not to be rewritten |
| 35 `file:line` anchors across 23 files; stale examples `.claude/settings.json:112` and 3× `feature.yaml` | **32 backticked anchors across 22 distinct files.** The `feature.yaml` rot survives — 3 anchors name a file DEC-191 renamed to `feature.json` and that exists nowhere. M1's existence proof holds; its numbers moved |
| "**LANES** — this feature is entirely squad work. Nothing is `main-session-direct`" | **FALSE, and it is the largest correction here.** See §3 |

## 2. Correction to this orchestrator's own 2026-08-24 observation

That log says the OMP port "RENAMED `.claude/skills/` to `.agents/skills/` — 138 renames" and that
"every tool path in this feature's scope has moved." **It did not.** `git ls-files .agents` returns
exactly one entry, `.agents/skills`, mode **120000** — a tracked **symlink** to `../.claude/skills`.
`readlink -f` on `.agents/skills/harness/bin/gen-decisions-index.py` lands in `.claude/skills/`.
`git ls-files .claude/skills` returns **149** files.

**Every path in the plan is written against `.claude/skills/…`.** A task whose `verify:` or file
list names `.agents/skills/…` addresses a symlink and will not match a `git ls-files` check.

## 3. Lanes — re-resolved with `check-domain.sh --resolve` at HEAD

| Path | Owner |
|---|---|
| `.harness/harness/docs/DECISIONS.md`, `DECISIONS-INDEX.md`, `BUILD.md`, `SPEC.md` | `harness-documentor` |
| `.claude/skills/harness/bin/gen-decisions-index.py`, `test-gen-decisions-index.py`, `check-state.sh`, `validate-digest.py` | `harness-backend-dev harness-dev-ops` |
| `.harness/expertise/harness-documentor.md` | `harness-documentor` |
| `.claude/skills/harness/SKILL.md` | **NOBODY** |
| `.claude/skills/harness-team/SKILL.md` | **NOBODY** |
| `.claude/skills/harness/references/debug-mission.md` | **NOBODY** |
| `.claude/agents/harness-orchestrator.md` | **NOBODY** |
| `.omp/agents/harness-orchestrator.md` | **NOBODY** — a citation surface no intake artifact saw |
| `.harness/factory/fleet.yaml`, `CLAUDE.md`, `.harness/logs/*.md` | **NOBODY** |

A `NOBODY` path is a **violation** in `check-plan-routes.py` under `execution_mode: team`. The
citation-repoint work therefore **splits**: documentor and backend-dev/dev-ops take their own lanes
as squad tasks, and every `NOBODY` site must be carved into a `main-session-direct` segment. Any
plan that routes them to a squad fails the plan gate.

## 4. Facts from the triage that reproduce at HEAD (`.harness/notes/triage-decisions-authority-2026-08-26.md`)

- **8 struck headings**, ids unchanged: DEC-90, 103, 104, 137, 140, 186, 192, 196.
- **A ninth, partial**: DEC-181 is `**STRUCK IN PART, 2026-08-10.**`.
- **C-9 verified**: zero `## DEC-161` headings exist, yet `DECISIONS-INDEX.md:123` and `:206` both
  carry `DEC-161` in `refs:`. The generator scrapes the id out of prose describing its deletion.
- **8 `SUPERSEDED BY` rows** (plus the convention line at `:19`): DEC-19→85, 20→63, 37→70, 67→86,
  82→83, 88→95, 92→99, 102→120.
- **DEC-188's retention clause stands**: "Struck decisions keep their heading and a strike record.
  They are not deleted from the file."

**The triage's line numbers have already drifted.** DEC-188's clause is at `:5949`, not `:5942-5944`;
DEC-181's partial strike is at `:5416`, not `:5409`; DEC-186's heading is at `:5678`, not `:5673`.
Anchor every task on a **content string**, never a line number.

## 5. The scope conflict pm must resolve — the reason this note exists

The grilling **settled** (2026-08-24): *"Do strike records go too? → **NO.** DEC-188 keeps a struck
entry so citations still land somewhere."*

The triage carries a later **OPERATOR RULING, 2026-08-26** (§9): *"delete the seven"* — DEC-103,
104, 137, 140, 186, 192, 196 — with DEC-90 the single recorded exception, kept because its successor
is a SPEC section rather than a decision.

**These are the same question answered twice, and the later answer reverses the earlier one.** The
later ruling governs, but it widens FEAT-38 past the destination the grilling recorded, and it
cannot execute while DEC-188:5949 stands (triage §6.3: any agent following decision discipline will
open DEC-188 and correctly refuse). pm must:

1. carry the 2026-08-26 ruling as the governing scope, citing it;
2. specify striking DEC-188's retention clause **by DEC-188's own procedure**, with the narrower
   replacement rule the triage recommends (*a struck decision is deleted only when a named successor
   exists to repoint its citations to*), as its own decision in the plan; and
3. surface the widening explicitly in `BRIEF.md` so the user signs the wider scope knowingly rather
   than inheriting it.

## 6. Scope boundary the dispatch sets

FEAT-38 is **#615 + #78 + the 2026-08-26 ruling + M1 + M2**. The triage's §7 ordering names other
tickets — #686, #844, #748, #678, #687, #438, #448, #680/#803, #486. **None enters this plan unless
pm's own analysis shows FEAT-38's outcome cannot be reached without it**, and the one candidate that
plausibly qualifies is **#686** (the index-generation contract), because triage §7.1 argues every
deletion is undefined behaviour until a signed contract says what happens to a row whose entry
disappears — and DEC-161 is the standing proof of what that costs. pm either brings #686 in with
that argument stated, or records why the plan is safe without it. **#448 is the opposite of #615 on
the same surface** and stays out; note it for closure on ship.
