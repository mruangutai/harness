# Plan-review application — BUG-1286, fix cycle 1

**Path note:** the dispatch named `notes/plan-review-application-c1.md`; `check-domain.sh` denies
that name for harness-pm (grants are `notes/research-*.md` and `notes/uat-*.md`). This file is the
same artifact under a granted name — per harness-handoff #216, the guard wins over the dispatch.

**All thirteen recommendations are applied; none rejected.** Two additions were forced by the
rulings and are recorded below: the SC list is renumbered SC-01..SC-15 with an explicit REQ/AC
traceability table, and T-01 gains a ninth unit case so R11's split criterion SC-14 can actually be
met by the method it declares. `plan.yaml` still reads `status: plan` and
`approval.status: pending`; no `panel:` block, no implementation file, no decision-record edit.

**One route correction.** `plan-merge.py apply` is ADD-ONLY — exit 7 CONFLICT when a proposed id
carries a different value than the base (`plan-merge.py:729-743`), so re-proposing an existing
T-NN/D-NN cannot change a field. Every amendment went through
`plan-merge.py amend --key … --id … --field … --expect-sha256 … --value-file …`, the
compare-and-swap verb (BUG-1128) and still a plan-merge write route. Eleven field amendments, each
reporting `AMENDED`/`APPLIED`.

## Disposition

| R | artifact / id | applied? |
|---|---|---|
| R1 | plan.yaml T-03 intent | applied verbatim — `--against` reuses only the fenced-block pattern, never `baseline()` |
| R2 | plan.yaml T-03 + T-04 `verify:` | applied verbatim, both literal blocks, census exit code primary, `grep -q` appended with `&&` |
| R3 | plan.yaml T-05 intent bullets 1, 3 | applied — `suite_layout.py` named as the vocabulary authority, no re-enumeration |
| R4 | plan.yaml T-05 `verify:` | applied — index-row clause added, plus a pre-edit zero-occurrence confirmation in the intent |
| R5 | BRIEF `## Verification gaps` | applied — residual (`unit.detect` extension-agnostic) and its control (T-03 selects without the extension filter) both stated |
| R6 | BRIEF SC-09 → **SC-11** | applied verbatim — ancestor-of-`review_sha` grading |
| R7 | plan.yaml T-01 case 7; BRIEF SC-07 → **SC-09** last sentence | applied verbatim |
| R8 | plan.yaml T-01 dedup bridge | applied verbatim — `{p.relative_to(root).as_posix() for p in set(planted)}` |
| R9 | plan.yaml D-03 `because`; T-05 bullet 3; BRIEF **SC-14** | applied with the third citation: two controls + DEC-189; T-05 cites DEC-189 rather than restating it |
| R10 | plan.yaml D-03 `choice` | applied verbatim — toplevel comparison pinned as a precondition of enumeration |
| R11 | BRIEF SC-05, SC-06, SC-11 | applied — three splits, full renumber, SC-05's second clause kept as its own SC-06 |
| R12 | plan.yaml D-05 `because` | applied verbatim — archival consequence and the grant asymmetry |
| R13 | plan.yaml T-04 intent bullet 3 | applied verbatim — `suite_layout.DOCUMENTED_EXCEPTIONS` as the classification authority |

**R3/R4 compose — checked, no adjustment needed.** R3 governs the DECISIONS.md amendment prose
(where the enumeration is dropped); R4's grep targets the hand-written tail of the
DECISIONS-INDEX.md DEC-213 row, whose text T-05's intent dictates and which contains the literal
"tracked test-shaped file outside". Measured: the pattern matches 0 lines in the index today
(non-vacuous) and 1 line against the row T-05 instructs the documentor to write (positive control).

## SC numbering after the split (SC-01..SC-15)

| SC | REQ | issue #1286 acceptance criterion |
|---|---|---|
| SC-01 | REQ-01 | tracked test-shaped file outside `tests/**` rejected |
| SC-02 | REQ-02 | all offending paths, deterministic order |
| SC-03 | REQ-01 | runner exits misconfigured before any sentinel |
| SC-04 | REQ-03 | enumeration failure is a closed failure |
| SC-05 | REQ-04 | valid `tests/{unit,integration,manual}` accepted |
| SC-06 | REQ-04 | manual files outside active discovery (SC-05's second clause, kept) |
| SC-07 | REQ-04 | ordinary support modules remain accepted |
| SC-08 | REQ-04 | the existing `bin/` support-module case |
| SC-09 | REQ-05 | exact documented exceptions; stale/broadened/duplicated/unnecessary refused |
| SC-10 | REQ-01 | coverage demonstrates the tracked-file distinction |
| SC-11 | REQ-06 | audit re-run at `review_sha`, no unexplained match |
| SC-12 | REQ-07 | DEC-213 + index state the shipped invariant |
| SC-13 | REQ-08 | `harness.json` and mutation-snapshot scope unchanged |
| SC-14 | REQ-08 | product-checkout discovery unchanged |
| SC-15 | REQ-03, REQ-04 | no-index root: not a failure, not a silent scan |

All eleven ticket criteria are covered; every SC declares exactly one `verify:`, and each
`automated` one names `unit` or `integration`, both `active` in `.harness/harness.json`
`test_kinds`. No SC id is referenced by any task's `traces:` (tasks trace REQ only), so the
renumber required no task re-proposal.

Grounding for the split criteria: **SC-06** is already asserted by the live
`manual tests are not actively detected` check (`tests/unit/test-suite-layout.py:104-105`) and
**SC-08** by `import layout_fixtures` in `tests/integration/test-layout-migration.py:62`, so
neither needs new work. **SC-14** did — nothing covered inertness on a `.git` root that does not
track the predicate, so T-01 case 9 builds exactly that fixture; the single-caller half is pinned by
the existing `runner delegates layout once` check (`tests/unit/test-suite-layout.py:136-139`).

## Verification evidence (run from the worktree root)

1. `python3 -c "import yaml; yaml.safe_load(open('…/plan.yaml'))"` → `LOADS OK`.
2. `CLAUDE_PROJECT_DIR=… python3 .claude/skills/harness/bin/check-plan-routes.py …/plan.yaml` →
   `OK T-01 … OK T-05`, `0 violation(s) across 1 plan(s)`, exit 0.
3. All five tasks carry id, title, traces, change_type, execution_mode, execution_agent,
   depends_on, status, files, verify, intent → `T-01..T-05 ALL KEYS PRESENT`; 6 decisions and
   5 tasks intact; each `verify:` still a one-line literal block.
4. `status: plan`, `approval: {'status': 'pending'}`.

Plus: `bash -n` clean on all three new `verify:` bodies; the R4 grep measured non-vacuous (0 matches
today) and positive-controlled (1 match against the intended row).

## Surviving question

None blocking. The eng lead's Q1 is closed by the ruling (two controls + DEC-189) and is not
re-opened. Advisory, not mine to fix: the review notes that
`receipt-harness-data-engineer-simplify-efficiency.md` ends in leaked tool markup — cosmetic.
