# QA-C0 — FEAT-16 factory per-repo board

## BLUF

PASS. Both required kinds (`unit`, `integration`) run real, named coverage for this diff and exit 0.
SC-01/02/04/05/08/09 are evidenced by named cases whose assertions are on recorded gh-call
arguments, not counts. SC-13 is a genuine, non-vacuous test (I mutation-killed the exact
"silent exit 0" defect it exists to prevent), but I could **not** reproduce the BRIEF's specific
narrower claim that C1 is blind to that mutant — my most literal mutant kills C1 too. That claim is
downgraded from "verified" to "unproven as narrowly stated," logged as an open question, not a
blocker.

## Pin confirmation

- `git rev-parse HEAD` = `12e93f9937c15a1c802cb81711dc6e57ea7ad2f6`
- `git branch --show-current` = `feat/FEAT-16-factory-per-repo-board`
- `git merge-base --is-ancestor ec195ec... HEAD; echo $?` = `0` (ancestor confirmed)
- `git log --oneline ec195ec..HEAD` = exactly one commit, `12e93f9 FEAT-16: the run ledger catches up
  and review_sha is pinned for the validator phase` — bookkeeping only (`feature.json`). Diff under
  review is `a7c429c..ec195ec` as instructed.
- Checkout: `/Users/molchairuangutai/GitHub/harness` (no `.claude/worktrees/*` present — confirmed
  with `ls`). Ran everything from here.

## Phase 1 — expected coverage, derived from BRIEF + plan.yaml only, before reading source

- SC-01: `load_fleet` unit case(s) accepting a fully per-repo fleet, rejecting an entry with no
  `board`, naming the repo in the error.
- SC-02: `load_fleet` unit case rejecting a leftover top-level `board:` key, error names `board`,
  says move under `repos:`.
- SC-04: two-repo/two-board fixtures in claim, decompose, land (and integration) asserting *recorded
  gh call arguments* (board number + station names) match the acted-on repo and never the other's —
  count-based assertions explicitly insufficient per BRIEF.
- SC-05: a case pinning the kaya-ai → board 2 pairing, failing if either side changes alone.
- SC-08/SC-09: `run-unit-tests.sh --kind unit` / `--kind integration` both exit 0.
- SC-13: a claim run scoped via `--repo` to a repo with an empty `ready` station reports "no work
  available" on stderr, empty stdout, exit 1 — not a silent 0.

This list matches what landed; no coverage was found to be missing at Phase 2 that Phase 1 didn't
already anticipate.

## The two suites, exact commands and exit codes

```
.claude/skills/harness/bin/run-unit-tests.sh --kind unit
```
exit code: **0** (all scripts reported ALL PASS / N/N checks passed, no FAIL/ERROR/Traceback lines)

```
.claude/skills/harness/bin/run-unit-tests.sh --kind integration
```
exit code: **0** (106/106 in `test-factory-integration.py`'s own tally; no FAIL/ERROR/Traceback
anywhere in the run; whole run ends `PASS test-factory-integration.py`)

## Matrix ruling

`change_type` per task: `api` (T-01, T-08), `logic` (T-02–T-06, T-09, T-11), `config` (T-07),
`docs` (T-10). Read from `harness.json` `test_matrix`: `logic.always = [unit]`, `api.always = [unit]`,
`api.when = [{kind: integration, if: touches_db_or_external}]`, `config.always = []`,
`docs.always = []`.

I concur with the dispatch's ruling: `touches_db_or_external` holds for the `api` tasks (T-01's
`factory_config.py`/T-08 are read by every tool that shells to live `gh`), T-05 and T-06 declare
`--kind integration` as their own `verify:`, and `harness.json`'s `integration.detect` names
`test-factory-integration.py` explicitly. **Required kinds: `{unit, integration}`.** Both ran, both
named real tests for this diff (not pre-existing unrelated ones — every fixture touched carries new
per-repo-board cases dated to this feature), both exit 0.

`matrix_ok: true`

## Per-kind results

| kind | state | cmd | exit | named tests (this diff) |
|---|---|---|---|---|
| unit | satisfied | `run-unit-tests.sh --kind unit` | 0 | `test-factory-config.py` cases 3,4,25-31 (+28a-d); `test-factory-claim.py` P1-P6; `test-factory-decompose.py` T-03; `test-factory-land.py` T-04; `test-no-distribution.py` case5 (3 checks) |
| integration | satisfied | `run-unit-tests.sh --kind integration` | 0 | `test-factory-integration.py` case (H); `test-check-domain.py` case (d) fixture migration |
| component | skipped-with-reason | n/a | n/a | `cmd: null` in harness.json, status `unresolved`; BRIEF's Verification-gaps records no surface touches it |
| ui | skipped-with-reason | n/a | n/a | same — `cmd: null`, no rendered surface in this feature (D-11: no `.tsx`/`.ts` in any task's `files:`) |
| eval | skipped-with-reason | n/a | n/a | same — `cmd: null`, no `ai_behavior` change_type in this feature |
| typecheck | skipped-with-reason | n/a | n/a | same — `cmd: null`, not in the matrix at all |

## SC evidence

| SC | evidenced? | test |
|---|---|---|
| SC-01 | evidenced | `test-factory-config.py` case (3) `a repos entry has no board`; cases (27), (28a-d) — per-repo board field rules raise with repos-prefixed key |
| SC-02 | evidenced | `test-factory-config.py` case (8b) `a leftover top-level board key raises FleetError`, asserts key `board` and `next_step` mentions `repos[].board` |
| SC-04 | evidenced | `test-factory-claim.py` P1-P4 (asserts query built from each board's own field/option, refusal names the right board, never the other's); `test-factory-decompose.py` T-03 case (asserts `project_item_add`/`project_field_set` issue no call against B's board); `test-factory-land.py` T-04 case (same, via `b_markers` non-membership check); `test-factory-integration.py` case (H) (`no recorded gh call names the other repository's board number` + a power-check that the served repo's own board number IS named). All assert on recorded call **arguments**, not counts, per the BRIEF's requirement. |
| SC-05 | evidenced | `test-no-distribution.py` `case5`/`kaya_ai_is_paired_with_board_2`, plus its siblings `board_lives_per_repo_not_fleet_level` and `every_repo_declares_its_own_board` — three separate `check()` calls, each independently named |
| SC-08 | evidenced | `run-unit-tests.sh --kind unit` exit 0 (see above) |
| SC-09 | evidenced | `run-unit-tests.sh --kind integration` exit 0 (see above) |
| SC-13 | evidenced, with a caveat — see mutation section below | `test-factory-claim.py` P6 (`(P6) SC-13: ...` three checks) |

SC-03, SC-06, SC-07, SC-10, SC-11, SC-12 are `verify: inspection`/`uat` — outside this gate's remit
except where the BRIEF asked me to spot-check mechanically (SC-10, SC-11 — see below). SC-06 was
**not run and not simulated**, per the LEAVE LIST.

## SC-10 / SC-11 spot check (mechanical, inspection-class, done because it's a one-line grep)

- `git diff --name-only a7c429c..ec195ec | grep -E "check-domain.sh|bash-write-guard.sh|validate-digest.py|check-state.sh"` → **empty**. SC-10 holds.
- `grep -rnE "fleet[A-Za-z_]*\[['\"]board['\"]\]|fleet[A-Za-z_]*\.get\(['\"]board['\"]\)" .claude/skills/harness/bin/` → **empty**.
- `grep -n "def station(" .claude/skills/harness/bin/factory_config.py` → **empty**. SC-11 holds.

## SC-13 mutation testing — the substantive finding

Method: copied `factory_claim.py`, `factory_config.py`, `factory_cli.py`, `factory_gh.py`,
`gh_issues.py`, `harness_yaml.py`, `test-factory-claim.py` into the scratchpad (only the literal
absolute destination path was accepted by `bash-write-guard.sh` — a `$VAR`-based destination was
denied because the guard parses command text, not the shell-expanded path; noted as a gotcha, not a
finding). All mutation and re-runs happened only in
`/private/tmp/claude-501/.../scratchpad/mutant-bin/`. `git status --porcelain` on the real repo is
empty (appended below) — the tree was never touched.

**Mutant 1 (the literal reading of the BRIEF's description):** replace
```python
if not candidates:
    factory_cli.nothing_to_do(TOOL, "no work available")
```
with
```python
if not candidates:
    sys.exit(0)
```
Result: **P6 goes RED** (all three of its `check()` calls fail) — confirms the case is not vacuous
and does catch a real silent-exit-0 defect. **But C1 also goes RED** (`(C1) exit 1` and `(C1) stderr
carries 'no work available'` both fail) — full run: `7 of 113 FAILING`, including both C1 and P6.
This **contradicts** the BRIEF's specific claim that "C1 passes on that mutant": both C1 and P6
converge on the exact same single call site (`factory_claim.py:292-293`), confirmed by
`grep -n "no work available" factory_claim.py` returning exactly one hit. There is no structural
difference in the current, correct implementation between a single-repo whole-run empty case and a
`--repo`-filtered two-declared-repo empty case — `repos_to_serve` reduces to a one-element list in
both, and every downstream read (`boards`, the poll query, the final aggregate check) is scoped to
that one element identically.

**Mutant 2 (repo-count-gated, closer to "per-repository loop" wording):** gated the same
`nothing_to_do` call on `len(repos_to_serve) < 2`. Did **not** manifest under P6's own fixture,
because P6 uses `--repo` to filter to exactly one served repository — `len(repos_to_serve)` is 1
there regardless of how many repos the fleet *declares*. Both C1 and P6 stayed green; this mutant is
not a counterexample either way.

**Mutant 3 (a real T-02-adjacent board-resolution bug):** made `factory_config.board_for` ignore its
`repo_name` argument and always return `fleet["repos"][0]["board"]`. This **was** caught — but by
SC-04's own evidence (`test-factory-claim.py` P1, P3), not by P6/SC-13. P6 stayed green on this
mutant (station validation and the empty-board query both happened to still resolve to "nothing
found" under the wrong board, producing the same exit 1 / same message by coincidence of the test
fixture's default `field_options`).

**Verdict on SC-13's mutant claim: killed for the case I could construct closest to the literal
description, but not proven "P6-alone, C1-blind" as specifically stated.** I could not, within a
reasonable number of attempts, construct a mutant that P6 kills and C1 survives — every mutant
either killed both (Mutant 1) or neither on the SC-13 assertions (Mutants 2 and 3). This reads as a
genuine gap in the BRIEF's own narrative rather than an authored test I can fault: **P6 is real,
useful, non-vacuous coverage for the exit-0-in-silence defect** (Mutant 1 proves that), but its
claimed uniqueness over C1 does not hold in the code as it actually landed. I'm logging this as an
open question rather than a FAIL, because the test itself is sound and does add coverage (the exit-1
diagnostic is now enforced under `--repo` scoping specifically, which C1 alone does not literally
exercise even though it happens to fail identically under the one mutant that breaks it).

## Test-first / authoring

I authored nothing (`files_touched: []`). All source and test edits under
`.claude/skills/harness/bin/` are outside my domain (verified against `team-config.yaml` lines
160/202/217-235 per the dispatch's own correction) and none were needed — no coverage gap required a
new test spec.

## Coverage gaps

None found beyond the Phase-1 list — everything I expected to exist, exists, with real assertions.

## Full git status --porcelain (as instructed, verbatim)

```
(empty — clean tree)
```

## Exit codes, verbatim

```
UNIT_EXIT:0
INTEGRATION_EXIT:0
```
