# Goal-check FINAL — FEAT-47 tests-layout — pinned `9a76e979`

Supersedes `notes/research-FEAT-47-goal-check.md` (pinned `43fd04b9`, still true of that sha).
Delta graded: `43fd04b9..9a76e979`. Read-only; nothing edited but this file.

## BLUF

**PASS. The single blocker is closed and nothing regressed.** REQ-07's residue —
`.harness/harness/expertise/harness-pm.md` G-08 presenting the deleted KIND-DRIFT cross-check and
the two script arrays as live `run-unit-tests.sh` gates — is rewritten to the directory invariant.
All ten SCs stay met on the prior session's re-derived evidence, which the delta cannot have
falsified: the delta touches **no source and no test file**.

## The blocker — closed

New entry at `9a76e979:.harness/harness/expertise/harness-pm.md:17`:

> G-08: WHEN a plan adds, moves, or deletes a Harness test DO account for the directory invariant:
> `tests/unit/` and `tests/integration/` select the kind, `suite_layout.py` refuses undiscoverable
> or duplicated test shapes, and the runner exits 2 on any violation.

Every clause verified at the pinned sha against the shipped runner, not accepted as prose:

| Claim | Evidence at `9a76e979` |
|---|---|
| directory selects the kind | `run-unit-tests.sh:25-27` — `SCRIPTS=(tests/unit/test-*.py)`, `(tests/integration/test-*.py)`, union for `all` |
| `suite_layout.py` refuses bad shapes | `suite_layout.py:6` `def violations(root)`; called at `run-unit-tests.sh:31` |
| runner exits 2 on any violation | `run-unit-tests.sh:32-39` — crash → `MISCONFIGURED: layout check crashed`, exit 2; non-empty output → one `MISCONFIGURED:` line per violation, exit 2 |

No deleted mechanism survives the rewrite: `git grep -E
'UNIT_SCRIPTS|INTEGRATION_SCRIPTS|check-kinds|KIND-DRIFT|script array'` over
`9a76e979:.harness/harness/expertise/harness-pm.md` → **exit 1, zero hits**.

**Same sweep widened past the token set that missed it the first time** (the prior finding was
prose-shaped, invisible to `RESIDUE_TOKENS`). Over all 29 files under `.harness/expertise/` and
`.harness/harness/expertise/`, plus `.claude/skills`, `.agents` and `.harness/glossary.md`:
**exit 1, zero hits.** The remaining tree-wide matches are all per-feature `notes/`,
`observations/`, shipped `BRIEF.md`s and this feature's own goal-check prose — record paths REQ-07
exempts, exactly as the pinned reviewer's F-1 scoped it.

SC-07's declared method re-run at the new sha: `tests/manual/suite-census.py residue --ref
9a76e979` → **exit 0**, exactly the three declared exemptions `covered`
(`DECISIONS.md:5591`, `probe-omp-session-accessor.py:14`, `suite-census.py:12`), no fourth. Run with
`env -u HARNESS_AGENT_TYPE` per the prior session's false-red note.

## No fix-delta regression

`git diff --name-only 43fd04b9 9a76e979` = 5 paths, all under `.harness/`: the one Expertise entry,
`feature.json` (`review_sha` → `43fd04b9`), the prior goal-check note, this agent's observations log,
and `review_sha`. **Zero files under `.claude/`, `tests/` or `.harness/harness.json`.** So every
SC-01…SC-10 verdict re-derived at `43fd04b9` — the strict verdict-line census, the conservation law,
the child-process probe over 66 files, the nine layout cases, the 21 `suite_layout` cases, the
detect byte-equality, the `locally_run` registration — remains a measurement of the identical code
at `9a76e979`. Only SC-07 was re-taken, because only SC-07's grading set includes the changed file.

Working tree carries two unstaged review-pin metadata files (`feature.json`, `review_sha`), same as
the prior session. No source or test file is dirty.

## REQ coverage

REQ-01…REQ-06, REQ-08 — met, as re-derived at `43fd04b9` and unaffected by the delta.
**REQ-07 — met** at `9a76e979` per the two sweeps and the residue run above.

## Open

- **Advisory, not graded, unchanged:** `.harness/expertise/harness-dev-ops.md` P-02 counsels keeping
  an explicit list and a glob drift detector separate — advice against what DEC-213 chose, but
  cross-repo craft asserting nothing false about this tree. Declared non-blocking previously; not
  reopened.
- **Carry to #979:** SC-07 is written to three literal tokens and was green while REQ-07 failed on
  prose. A criterion whose sweep cannot see its own requirement's residue needs a reader, not a
  wider token list.
- SC-01/SC-02 verdict-line counts and SC-09's probe stay point measurements, as the BRIEF's
  Verification gaps disclose. No `verify: uat` criterion exists, so there is no UAT gate here.
