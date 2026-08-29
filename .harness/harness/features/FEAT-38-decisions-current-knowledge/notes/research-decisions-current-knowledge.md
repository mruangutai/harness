# Research — FEAT-38 — re-derived at `7ebfc9e`, 2026-08-29

Every figure below was run in the worktree, not recalled. Predicates are stated so a later reader
can reproduce or falsify them. Where this note and an intake artifact disagree, this note was
measured later and governs.

## Three intake claims that are WRONG, and one that is right for the wrong reason

**1. "`test-gen-decisions-index.py` uses DEC-104's body as a test fixture; deleting the entry may
break the test." FALSE at HEAD.** `test-gen-decisions-index.py:137-148` is a *comment* recording
that the DEC-104 fixture was already removed when DEC-104 was struck, and that the fence guard is
now proven against a synthetic fixture planted in-test (`## DEC-9999`). The live assertion is a
relationship (`len(raw) < len(distinct)`), not a frozen total. Deleting DEC-104 orphans a prose
citation and nothing else. No task is needed for a fixture break.

**2. `check-docs.sh` does not exist.** #78 rests two claims on it (its `<!-- stale: -->` registry,
and `check-docs.sh` exiting 0 as a verification). `git ls-files .claude/skills/harness/bin` has no
such file, and `DECISIONS.md` carries zero `<!-- stale:` markers. The only surviving marker of that
family is `<!-- ok-stale -->`, consumed by `gen-decisions-index.py:271` on *index rows*. M2 therefore
cannot reuse an existing convention — it needs a new one.

**3. The documentor expertise entry to rewrite is `.harness/harness/expertise/harness-documentor.md:4`
(repository tier), not `.harness/expertise/harness-documentor.md`.** Both files exist and both hold a
`P-01`; only the repository-tier one is about amendment placement. The reconciliation's lane table
names the wrong file. Both resolve to `harness-documentor`, so the lane is unaffected.

**4. Amendment blocks are physically misplaced in THREE spans, not one.** Attributing each
`###`/`**Amendment` line to the `## DEC-NN` heading above it:
`### DEC-137 amendment 2` sits inside DEC-138's span; `### DEC-138 amendment 5-8` sit inside
DEC-168's span; `### DEC-189 amendment 1 (2026-08-16)` sits inside DEC-194's span. The triage found
only the third. The generator reads the id from the heading text, so the index is right and the file
is wrong — a folder walking the file top-to-bottom will fold four DEC-138 amendments into DEC-168
unless told.

## Measured surface

| Quantity | Value | Predicate |
|---|---|---|
| `DECISIONS.md` | 7,414 lines, 202 entries | `git show HEAD:… \| grep -cE '^## DEC-[0-9]+'` |
| `DECISIONS-INDEX.md` | 222 lines | `wc -l` |
| amendment sub-sections | 25 | `grep -cE '^###[[:space:]]+DEC-[0-9]+[[:space:]]+amendment'` |
| amendment bold-inline | 13 | `grep -cE '^\*\*Amendment'` |
| **amendments total** | **38** | sum of the two |
| fully struck entries | 8 | `^## DEC-` headings matching `STRUCK` |
| partly struck | 1 (DEC-181) | `^\*\*STRUCK` — one hit |
| `SUPERSEDED BY` index rows | 8 | DEC-19→85, 20→63, 37→70, 67→86, 82→83, 88→95, 92→99, 102→120 |
| literal "SUPERSEDED" in `DECISIONS.md` | 0 | the marker is derived, never authored |
| backticked `file:line` anchors | 32 distinct, 22 distinct files | see M1 below |

**Amendments owned by the seven entries being deleted: 9** — DEC-137 two (its own, plus
`DEC-137 amendment 2` living inside DEC-138's span), DEC-186 three, DEC-196 four. Deleting before
folding therefore leaves **29** amendments to fold, of which `DEC-145 am.3` is MOOTED
(`DECISIONS.md:3552`) and is deleted rather than folded — so **28 folds across 14 owner decisions**
(DEC-11, 138, 142, 145, 149, 152, 157, 158, 171, 174, 183, 189, 193, 194 — counted by the id the
amendment heading DECLARES, not by the span it physically sits in), plus DEC-181's partial-strike
paragraph, giving **15 entries rewritten**. Not 38, not 30, not 25. DEC-168 is a physical HOST of
four DEC-138 amendments, never an owner.

## Citation debt, by predicate

Occurrences of `DEC-N` with a numeric boundary, excluding `*/features/*`, `*/notes/*`,
`DECISIONS.md` and `DECISIONS-INDEX.md`:

- **Superseded eight: 29 occurrences** — DEC-19 11, DEC-102 16, DEC-82 1, DEC-92 1. DEC-20/37/67/88
  have **zero**. Excluding `.harness/logs/**` as well: **24**.
- **Struck seven (excl. logs): 30 occurrences** — DEC-192 16, DEC-186 7, DEC-137 4, DEC-104 3,
  DEC-103 0, DEC-140 0, DEC-196 0.
- **`am.N` / `DEC-N amendment`: 37 occurrences across 24 files** (excl. logs, `DECISIONS*.md`), of
  which 6 are `gen-decisions-index.py`'s own docstring and code and die with the machinery. Every
  match inspected in context; all are genuine citations, no false positives.

`.harness/logs/**` and `.harness/harness/features/**` are dated records of what was true on a day.
Rewriting them falsifies the record (PRINCIPLES rule 15). They are excluded, which is why the sweep
is 24+30+37 and not larger.

## #686 comes IN — the argument, with the instance shown

Not on the triage's authority; on a case that exists at HEAD and a case that will exist after T-08.

**Standing:** `DECISIONS-INDEX.md:123` and `:206` both list `DEC-161` in `refs:`. Zero `## DEC-161`
headings exist. The generator scrapes the id from prose describing the deletion and recreates the
rows on every run.

**Reachable, and provably:** `DECISIONS-INDEX.md:206` is DEC-188's row and reads
`refs: DEC-103 DEC-104 DEC-161 DEC-165 DEC-181`. **DEC-188 survives this feature and DEC-103/DEC-104
are deleted by it**, so the same defect is manufactured twice more by our own change, mechanically,
with no way to hand-edit it out — the index is generated.

`test_orphaned_ruling_is_reported_not_silently_dropped` catches a *row* whose DEC has no heading. It
does not look at `refs:` graphs. So the failure is both certain and unguarded. #686 enters **scoped
to one clause** — what the generator does with a `refs:` id that has no live heading — not as the
whole index-contract ticket. Anything wider is out.

## DEC-181 — the ruling, and why it is not the operator's

DEC-181 is **live**, not struck. Its budget half is enforced at `check-domain.sh:1335`
(`CLAUDE.md is {n} lines — budget is 80 (DEC-181)`). The `**STRUCK IN PART**` paragraph is an
amendment wearing a strike's clothes: it narrates what a *different* half used to say. Under the
grilled destination it is folded like any amendment, and DEC-181 is not a deletion candidate. This is
derivable from the code, so it is a decision, not a question.

Two false claims inside its body, both corrected in the same fold:
- it cites `check-domain.sh:779-780`, which at HEAD is a DEC-171 comment block about a manifest that
  will not parse — nothing to do with a budget;
- it says peers include `feature.yaml 200/20`; the code says `feature.json` 300
  (`check-domain.sh:1103`, `:1303`).

## M1 — existence proof, and the design that is weak enough

Of the 32 distinct anchors: **3 name a file that exists nowhere** — `feature.yaml:63-64`,
`FEAT-03-subissue-mirror/feature.yaml:73`, `FEAT-03-subissue-mirror/feature.yaml:97` (DEC-191 renamed
it to `feature.json`). **0 are out of range. 29 resolve.**

So a bare existence-plus-range check reddens on exactly three sites today and greens after they are
fixed: it is discriminating without a single stored snippet. Stored snippets were considered and
refused — 29 snippets to author, and the DEC-181 case above shows a snippet still cannot see a line
that exists and now says something unrelated. That is M2's job, and duplicating it in M1 buys nothing
(PRINCIPLES rule 6).

## Confirmed runnable, at `7ebfc9e`

- `gen-decisions-index.py --stdout | diff - DECISIONS-INDEX.md` → **exit 0** (clean baseline).
- `test-gen-decisions-index.py` → **10 ok, 0 FAIL**, 0.8s.
- Absence assertions written as `! grep -qE …` (exit-status form, never `test "$(… | wc -l)" = 0`)
  **fail today** on the amendment pattern, and the 15-id per-id loop reports all fifteen present.
  Each verify in the plan was shown to reject the current tree.
- `run-unit-tests.sh` is deliberately **not** a task `verify:` — it is the whole suite and belongs to
  the qa gate (SC-11), not to a 60-second task check.

## Lanes — `check-domain.sh --resolve`, run per path

`harness-documentor`: `DECISIONS.md`, `DECISIONS-INDEX.md`, `SPEC.md`, `BUILD.md`,
`.harness/harness/expertise/harness-documentor.md`.
`harness-backend-dev`: everything under `.claude/skills/harness/bin/`.
`harness-dev-ops`: `.harness/harness.json`, `.github/workflows/tests.yml`.
**NOBODY** — carved to `main-session-direct`: `.claude/skills/harness/SKILL.md`,
`.claude/skills/harness-team/SKILL.md`, `harness-brief/SKILL.md`, `harness-init/SKILL.md`,
`harness-wayfinding/SKILL.md`, `.claude/skills/harness/references/github-mirror.md`,
`references/debug-mission.md`, `.claude/skills/harness/templates/gitignore.snippet`,
`.claude/commands/harness.md`, `.claude/agents/harness-orchestrator.md`,
`.omp/agents/harness-orchestrator.md`, `.harness/factory/fleet.yaml`, `CLAUDE.md`, `.gitignore`.

`.agents/skills` is one tracked symlink (mode 120000 → `../.claude/skills`); `git ls-files .claude/skills`
returns 149 files. No path in the plan spells `.agents/skills`.

## Registration trap for the two new checkers

`run-unit-tests.sh:123` runs a KIND-DRIFT check: every name in `INTEGRATION_SCRIPTS` must appear as
an explicit literal path in `harness.json`'s `integration` detect. The two halves live in **different
lanes** (`run-unit-tests.sh` → backend-dev, `.harness/harness.json` → dev-ops), so a new test script
registered on one side only makes the runner exit 2. The plan orders `harness.json` first and gives
that task a verify that does not invoke the runner.

## Open, for the operator

Nothing blocking. Two disclosures rather than questions, both stated in `BRIEF.md`: the 2026-08-26
widening from 0 deletions to 15, and the deliberate loss of amendment dates from the prose.
