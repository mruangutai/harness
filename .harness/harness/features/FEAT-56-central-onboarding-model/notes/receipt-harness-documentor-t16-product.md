# Receipt — harness-documentor — FEAT-56 · T-16 (run t16-product)

**PASS.** DEC-221 records the two-artifact onboarding split, the index carries its hand-written
ruling, and SPEC / BUILD / org.html / both READMEs now name `harness-init` and `harness-add-repo` as
the two skills that own the two jobs. T-16's `verify:` ran verbatim from the worktree root and exits 0.

Contract cross-check: the dispatch's `intent:` and `verify:` match `plan.yaml` T-16 lines 1873–1923
character for character. No mismatch, so no BLOCKED.

## DEC number — COMPUTED from the file at HEAD

```
$ grep -n '^## DEC-' .harness/harness/docs/DECISIONS.md | tail -1
6985:## DEC-220 — Onboarding is fleet registration plus one product-resident file
```
Integration-branch ceiling: `git show main:.harness/harness/docs/DECISIONS.md | grep '^## DEC-' | tail -1`
→ DEC-219. Branch sweep for an existing `## DEC-221 ` heading found one only on
`feat/FEAT-46-decision-standard` — unmerged, a 396-entry corpus numbered to DEC-548, i.e. a different
numbering scheme rather than an append to main's sequence. **DEC-221 allocated**, at line 7019.

## The DEC-221 entry — where each required claim lands

`.harness/harness/docs/DECISIONS.md` DEC-221, house form Chose / Over / Because / Record.

| Required claim | Where |
|---|---|
| onboarding is two artifacts — `harness-init` configures a harness checkout, the `harness-add-repo` skill registers a repository into a configured control plane | **Chose**, sentences 1–3 |
| the seam: Track A plus `--upgrade` stays, Track B minus its BRIEF/approval/design steps moves | **Chose**, sentence 4 ("The seam is the old skill's own two tracks") |
| first BRIEF, its approval and any design pass are `/harness-plan`'s; a configured fleet member without a BRIEF routes there | **Chose**, sentence 5 |
| canonical door root is `.omp/commands` with generated `.claude/commands` adapters, because a door authored only under `.claude/commands` is discovered by one provider | **Chose**, final sentence |
| rejected: a **symlinked `.claude/commands`**, because no test here can exercise Claude Code's own discovery | **Over**, sentence 2 |
| DEC-06 **not overturned** — its conclusion is what `harness-add-repo` conforms to; only its distribution premise expired, when `deploy.sh` was deleted in commit 45859123 | **Because**, final sentence (one clause) |
| refs DEC-220, DEC-06, DEC-120, DEC-174 | **Record** |

`45859123` verified: `git show --stat 45859123` deletes `.claude/skills/harness/bin/deploy.sh` (287 lines)
and `.claude/commands/harness-deploy.md`.

## Index

Regenerated with `gen-decisions-index.py` (exit 0). Because the entry was appended at EOF, the diff is
**one inserted line** — every existing `@line` anchor is unmoved. The generator emitted
`⚠ RULING PENDING`; the ruling tail was then hand-written right of ` :: ` only:

> DEC-221 @7019 [plan,brief,skills,approval] refs: DEC-06 DEC-120 DEC-174 DEC-220 :: Onboarding
> splits in two: `harness-init` configures a checkout, `harness-add-repo` registers a repository;
> first BRIEF and design are `/harness-plan`'s; `.omp/commands` is the canonical door root.

24 words — inside the 30-word cap the neighbours obey. `gen-decisions-index.py --stdout | diff` is
clean afterwards, so the hand-written tail survives regeneration.

## BUILD.md — the judgement, per site

BUILD.md's own header says it "changes as work completes". I treated everything under
`## Task 12`, `## Task 14` and `## GSD-removal migration map` as historical record, and everything
under `## Step 0` and `## Critical files` as present-tense claims about the live system.

| Site | Disposition | Reason |
|---|---|---|
| `:104` | **corrected** → `harness-init` (de-slashed, named as a skill) | Step 0a states a standing requirement on this control-plane clone, not what a task delivered — and the job is still `harness-init`'s |
| `:200` | **left as history** | migration-status row: "task 12 … **done** — flat skill at `.claude/skills/harness-init/`" is a record of delivery |
| `:370` | **left as history** (heading `## Task 12 — /harness-init: complete spec — BUILT`) | it names the task that was built |
| `:378` (`Delivered as a flat skill …`) | **left as history** | past-tense delivery record; its DEC-06 clause is still the reason the artifact is a skill |
| `:389` (division-of-labour table row) and `:392` | **left as history, covered by an added correction** | they sit under the section preamble "The spec below is what was built"; rewriting them would falsify that preamble |
| new note after `:373` | **added present-tense correction** | states the DEC-221 split, and says explicitly that the table and interview steps below name `/harness-init` for jobs `harness-add-repo` now owns |
| `:784` (migration map row 18) | **left as history** | "**DONE** (DEC-112) … Amended by DEC-220" is a delivery record that already carries its amendment trail |
| `:808`, `:819`, `:821`, `:830` (Detail #14) | **left as history** | that block says in its own words it is "kept as the record of what that command was specified to do, in the past tense it now belongs to" |
| `:844` (Detail #15, `.gitignore`) | **left as history** | same migration map; the block opens "The repo has **none**", which is already past-true, so a partial present-tense fix inside it would be inconsistent |
| `:948` | **corrected**, and a row **added** | `## Critical files` is a present-tense inventory of what is on disk: `harness-init` is now described as "configures a harness checkout", and `.claude/skills/harness-add-repo/SKILL.md` gained its own row |

## Other surfaces

- **SPEC.md** — sites `:84` (DESIGN.md established by `/harness-plan`'s design pass), `:134-137`
  (onboarding is two skills), `:145` (not-onboarded → run `harness-add-repo`), `:152` and `:483`
  (`schema_version` gap → `harness-init --upgrade`), `:406` and `:1363` (dev-ops detection happens
  during `harness-add-repo`), `:420` (conventions inherited by a repository registered by
  `harness-add-repo`), `:457` (both skills read the templates), `:459-471` (the "interview" block
  rewritten: `harness-init` configures the checkout, `harness-add-repo` is the registration
  interview with the BRIEF/approval/design steps replaced by a route to `/harness-plan`).
  No `/harness-init` spelling survives in SPEC.md.
- **org.html** — owner cell for `team-config.yaml` now reads `harness-init` skill · control plane
  only; two rows added to the doors table ("set this checkout up" → `harness-init`, "add this repo
  to the fleet" → `harness-add-repo`), each labelled *a skill, not a command*; the footer currency
  line moved to 2026-09-09 (through DEC-221).
- **README.md:192** — one paragraph: two skills, neither a command; registration order preserved
  with its DEC-220 citation; first BRIEF/approval/design are `/harness-plan`'s.
- **.harness/README.md** — `:6-8` (written by `harness-init`; a member's `harness.json` is landed by
  `harness-add-repo`), `:17`/`:18` (`Written by` cells split between the two skills), `:83-86`
  (Getting started routes to `harness-add-repo`, with `harness-init` / `--upgrade` for an
  unconfigured checkout).
- The ~20 `/harness-init` spellings elsewhere in the corpus were **not** touched (declared non-goal).
  Those that remain inside my seven files are all in historical BUILD.md sections and in earlier
  DECISIONS.md entries, which are the record and are never rewritten.

## Verification — run verbatim from the worktree root

```
$ env -u HARNESS_AGENT_TYPE bash -c "
grep -q 'harness-add-repo' .harness/harness/docs/DECISIONS.md &&
grep -q 'harness-add-repo' .harness/harness/docs/DECISIONS-INDEX.md &&
grep -q 'harness-add-repo' .harness/harness/docs/SPEC.md &&
grep -q 'harness-add-repo' .harness/harness/docs/BUILD.md &&
grep -q 'harness-add-repo' .harness/harness/docs/org.html &&
grep -q 'harness-add-repo' README.md &&
grep -q 'harness-add-repo' .harness/README.md &&
grep -q 'omp/commands' .harness/harness/docs/DECISIONS.md &&
python3 .claude/skills/harness/bin/gen-decisions-index.py --stdout | diff - .harness/harness/docs/DECISIONS-INDEX.md &&
python3 tests/integration/test-gen-decisions-index.py &&
python3 tests/integration/test-check-decision-anchors.py"
ok - test_row_per_distinct_dec_matches_authority
... 14 gen-decisions-index cases ok ...
ok - test_dec_210_index_row_names_the_compatibility_host_in_the_ruling
ok - test_in_range_anchor_reports_nothing_and_exits_zero
... 8 check-decision-anchors cases ok ...
ok - test_live_authority_anchors_all_resolve
VERIFY EXIT: 0
```
(The `diff` conjunct was run only after the index was regenerated and the ruling tail hand-written;
it printed nothing, which is its pass condition.)

```
$ env -u HARNESS_AGENT_TYPE python3 .claude/skills/harness/bin/check-decision-anchors.py
examined 34 anchor(s), 0 failed
ANCHORS EXIT: 0

$ env -u HARNESS_AGENT_TYPE python3 .claude/skills/harness/bin/check-instruction-paths.py
scanned 62 file(s), 0 violation(s)
PATHS EXIT: 0
```

Baseline before any edit: the same verify block exited **1** (DECISIONS.md had no `harness-add-repo`),
so the green run is this task's work and not a pre-landed change.

## `git status --porcelain`

```
 M .claude/agents/harness-dev-ops.md              <- SIBLING T-15
 M .claude/agents/harness-visual-designer.md      <- SIBLING T-15
 M .claude/skills/harness/templates/examples/harness.kaya-ai.json   <- SIBLING T-19
 M .claude/skills/harness/templates/harness.json  <- SIBLING T-19
 M .claude/skills/harness/templates/team-config.yaml                <- SIBLING T-19
 M .harness/README.md                             <- mine
 M .harness/harness.json                          <- SIBLING T-18
 M .harness/harness/docs/BUILD.md                 <- mine
 M .harness/harness/docs/DECISIONS-INDEX.md       <- mine
 M .harness/harness/docs/DECISIONS.md             <- mine
 M .harness/harness/docs/SPEC.md                  <- mine
 M .harness/harness/docs/org.html                 <- mine
 M .harness/team-config.yaml                      <- SIBLING T-19
 M .omp/agents/harness-dev-ops.md                 <- SIBLING T-15
 M .omp/agents/harness-visual-designer.md         <- SIBLING T-15
 M README.md                                      <- mine
?? .../notes/receipt-harness-dev-ops-t18-eng.md   <- SIBLING T-18
?? .../notes/receipt-harness-documentor-t16-product.md   <- mine
```
All seven of my `files:` are present and nothing outside them is mine. The nine other entries are the
concurrent siblings T-15 (`.omp/agents/**`, `.claude/agents/**`), T-18 (`.harness/harness.json`) and
T-19 (`.harness/team-config.yaml`, `templates/**`); I left every one untouched. Nothing was committed.
`check-state.sh` was not run, as instructed, and no project-wide suite, formatter or linter was run.

## Write refusals encountered

One. My first `edit` of `DECISIONS.md` used a worktree-relative path, which resolved against the
process cwd (the control plane) and was refused:

> check-domain: BLOCKED — harness-documentor holds worktree claim(s): …/FEAT-56-central-onboarding-model.
> Destination /Users/molchairuangutai/GitHub/harness/.harness/harness/docs/DECISIONS.md belongs in its
> proper checkout at /Users/molchairuangutai/GitHub/harness; write it from a bound worktree.

Correct refusal, not a claim conflict. Re-issued with an absolute worktree path and it landed. Every
subsequent write used absolute worktree paths. No write to `runs/` was attempted.

## Open questions

- Q1 (non-blocking): `feat/FEAT-46-decision-standard` carries a 396-entry `DECISIONS.md` numbered to
  DEC-548 including a DEC-221 of its own. It is unmerged and its numbering is not main's sequence, so
  DEC-221 here is correct against the integration branch — but whoever merges FEAT-46 will have a
  wholesale renumbering to reconcile, not a one-entry collision.
