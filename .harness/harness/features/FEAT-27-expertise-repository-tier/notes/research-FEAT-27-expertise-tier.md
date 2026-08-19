# Research — FEAT-27 expertise repository tier

**BLUF.** Unit 6 is **not a file move**. Craft Expertise stays at `.harness/expertise/` by design
(the operator-shipped layer table, `.claude/skills/harness-distill/SKILL.md:43-46`). What is missing
is the *second* tier: `.harness/<repo>/expertise/<agent>.md` has **no read path**, **no grant**, **no
budget in the checker**, and **no entries in it**. Unit 6 = create the tier, grant it, read it, move
**eleven** adjudicated entries into it, and build #412's advisory scan. Measured at `ada8e99`.

## Two premise corrections

**1. The corpus is craft, not mixed.** Re-derived at `ada8e99` over all 15 files with #340's own
token set (`DEC-NN`, `INV-NN`, `FEAT-NN`, `.harness/`, `.claude/`, `check-*.sh`, `factory_*.py`,
`gh-sync`, `harness.json`, `team-config`), entry = a column-0 `- ` bullet plus its indented
continuation lines:

**16 of 374 entries carry a token — 4.3%. 8 of 15 files carry none.**

Per file: backend-dev 2/24, dev-ops 3/16, documentor 5/30, eng-lead 1/26, orchestrator 2/42,
pm 1/34, security-reviewer 2/32; ai-dev, code-reviewer, data-engineer, product-lead, qa,
ui-reviewer, validator-lead, visual-designer all 0.

This **confirms** #340's resolution (10/267, 3.7%, seven of thirteen clean) at a larger tree and
**contradicts the dispatch's framing** that "every one of the 15 files mixes both layers". The unit
adjudicates ~16 entries, not 1164 lines.

**2. Adjudicated: 11 move, 5 stay craft.** Counted off the `Ruling` column of the table below —
eleven `repository`, five `craft`, sixteen rows. A flag is not a violation — #340 says a craft entry may
cite a path as an example. Ruling per entry (ids at `ada8e99`):

| File | Entry | Ruling | Why |
|---|---|---|---|
| backend-dev | G-03 | repository | turns on this repo's fake-gh fixture file |
| backend-dev | G-08 | craft | `team-config.yaml` exists in every governed project |
| dev-ops | G-01 | repository | names this repo's gate script and its strike record |
| dev-ops | G-03 | craft | the fact is about the machine's bash; the path is an exemplar |
| dev-ops | G-05 | repository | two harness-owned files and their merge tool |
| documentor | P-02 | repository | this repo's DECISIONS.md |
| documentor | P-10 | repository | this repo's DECISIONS.md + index generator |
| documentor | G-03 | repository | DEC-188, a decision of one repository |
| documentor | G-04 | repository | the strike sweep's surface list is this tree's |
| documentor | G-05 | repository | this repo's index budgets and their test |
| eng-lead | G-01 | repository | this manifest's overlapping bin/** grants |
| orchestrator | G-11 | craft | true in any harness-governed checkout |
| orchestrator | OQ-02 | repository | an open question about this control plane (#375) |
| pm | P-01 | craft | the shipped-plan exemplar is illustrative |
| security-reviewer | P-01 | repository | says "this codebase's" boundary outright |
| security-reviewer | G-01 | craft | a platform fact; the DEC cite is provenance |

Eleven movers across six files: backend-dev 1, dev-ops 2, documentor 5, eng-lead 1, orchestrator 1,
security-reviewer 1 — sums to 11. Well under the 40-line repository budget per file.

## Measured facts (all at `ada8e99`)

- `inject-expertise.sh:27-29` — exactly two read paths, project and global. `cap_body` hardcodes 150.
- `check-expertise.sh` — 128 lines; `LINE_BUDGET = 150` unconditional; no path-flag scan (#412 stands).
- `check-state.sh` has **zero** `expertise` matches — no invariant covers either tier, so no DEC-174
  carve-out script needs editing for this unit.
- `.claude/skills/harness/bin/test-inject-expertise.py` does not exist. The hook that fires on every
  spawn has no test at all.
- `harness_boundary.matches`: a single `*` does **not** cross `/`. Verified —
  `.harness/*/expertise/harness-pm.md` matches `.harness/harness/...` and `.harness/kaya/...`, not
  `.harness/a/b/...` and not another agent's file.
- `team-config.yaml` `paths.expertise: .harness/expertise/` has **no code reader** (grep over
  `bin/**` finds none); it is documentation-in-data.

## Route resolution — `check-domain.sh --resolve`, run at `ada8e99`

| Path | Resolver output |
|---|---|
| `.claude/skills/harness/bin/inject-expertise.sh` | harness-backend-dev, harness-dev-ops |
| `.claude/skills/harness/bin/check-expertise.sh` | harness-backend-dev, harness-dev-ops |
| `.claude/skills/harness/bin/test-inject-expertise.py` | harness-backend-dev, harness-dev-ops |
| `.claude/skills/harness/bin/test-check-expertise.py` | harness-backend-dev, harness-dev-ops |
| `.claude/skills/harness/bin/run-unit-tests.sh` | harness-backend-dev, harness-dev-ops |
| `.harness/team-config.yaml` | **NOBODY** |
| `.harness/harness/expertise/<any agent>.md` | **NOBODY** (this is #372) |
| `.harness/expertise/harness-<agent>.md` | that agent, and only that agent |
| `.harness/harness/docs/SPEC.md`, `.harness/README.md` | harness-documentor |
| `.claude/skills/harness-distill/SKILL.md` | **NOBODY** |

## T-04 verify — probed both directions at plan time (2026-08-18)

A cycle-1 send-back reported that T-04's `verify:` could never print `MIGRATION-OK`, quoting a
`n_new=$(grep -c ... || echo 0)` shape whose two-line value breaks `[ ... -eq 0 ]`. **The finding was
real for the shape it quoted** — reproduced here: `grep -c` on a zero-match file prints `0` AND exits
1, so `|| echo 0` appends a second line.

The clause has since been rewritten twice and the shipped one counts nothing. It is a `python3`
heredoc holding sixteen `(expect, agent, anchor)` rows, asserting membership with `s in
open(path).read()` per row — eleven `m` rows requiring present-in-repository-tier and
absent-from-craft, five `s` rows requiring the mirror. The rewrite was forced, not cosmetic: the
`check()`-function version measured **54 machine-field lines** and `check-plan-routes.py` rejects
anything over 50 (DEC-182). The shipped version measures 46 and the checker exits 0.

Probed both directions at `ada8e99`, the clause lifted verbatim out of `plan.yaml` by `safe_load`:

| Tree | rc | Output |
|---|---|---|
| repository HEAD, nothing migrated | **1** | eleven `FAIL m ... (repo=False craft=True)` lines, then `MIGRATION-FAILED` |
| a scratch tree with the eleven entries moved by script | **0** | `MIGRATION-OK`, then `OK` for all 15 craft and all 6 repository-tier files |

Green is reachable and red is reachable. The five `s` rows passed silently on the HEAD run, which is
correct: they assert the state that already holds and would only redden if the migration over-reached.
The generated repository-tier files measured 15-29 lines each, all inside the 40-line budget T-03
introduces.

The other five clauses were probed the same way at `ada8e99` and every one exits 1 on the unbuilt
tree: T-01 (all sixteen repo-tier paths resolve `NOBODY`), T-02 and T-03 (the runner is green but the
new assertions are absent), T-05 (README names no repository tier), T-06 (the superseded 267-entry
measurement still stands). T-06's "seven of thirteen" check was case-sensitive in an earlier draft and
therefore non-discriminating; it now greps `-i` for `of thirteen files`.

## Open items carried into the plan

- The hook cannot know which repository a spawn is for — `agent_type` is its only input, and
  `fleet.yaml`/`harness.json` are no-touch this cycle. Resolved as D-01 (glob every present tier,
  label each by segment).
- `integration.detect` in `harness.json` does not list `test-check-domain.py` or
  `test-check-expertise.py`, although `run-unit-tests.sh --kind integration` runs both. Cannot be
  fixed here (`harness.json` is unit 5's). Raised as an open question.
- An undeclared `.harness/<seg>/expertise/` directory would be injected by the glob. `layout_migration`
  solves the same problem for features and docs by checking fleet-declared segments; the hook must not
  gain that dependency. Open question, not a task.
- The artifacts were drafted under `FEAT-25-expertise-repository-tier`, which a peer flow claimed
  first. The orchestrator re-homed them here. The stale `FEAT-25-expertise-repository-tier/`
  directory is not mine to delete and needs removing.
