# QA gate — BUG-276 — cycle 0 — pinned SHA ef8efd99

**GATE-ONLY.** No source, test, or fixture files touched; nothing authored beyond this note.
Confirmed the pin is safe to test in place: `git diff ef8efd99..08f0baa3 -- <the 3 code files>` is
empty — HEAD's two bookkeeping commits touch only STATE.md/feature.json, so the working tree at
HEAD is byte-identical to the pin for every file under review. All commands below ran directly in
the worktree, `env -u HARNESS_AGENT_TYPE`, no checkout/detach performed.

## matrix_ok: **true**

Both tasks' `change_type: bugfix`. Resolving `.harness/harness.json`'s `bugfix` row against this diff:
- `unit` — `when.touches_runtime_code` **fires** (`.claude/skills/harness/bin/expertise-merge.py` is
  production/runtime code) → **required**.
- `integration` — `when.fix_confined_to_tests_and_contract_docs` does **not** fire (production code
  changed, not tests/docs only) → not required by the floor.
- `__bug_class__` — `match_bug_class` is an unresolvable placeholder repo-wide (no bug-class taxonomy
  entry exists yet; repo Expertise G-08) → does not fire.

Floor = `{unit}`. Both `unit` and `integration` are `active` kinds with real runners and both already
reach the changed code (BRIEF's own "Verification gaps: None"); the plan supplies integration coverage
beyond the floor voluntarily. Both kinds ran green, so the floor is met with margin.

## Per-kind results

| kind | runner | exit | FAIL lines | PASS lines (pooled, all files) |
|---|---|---|---|---|
| unit | `run-unit-tests.sh --kind unit` | 0 | 0 | 520 (31 files, 3.80s wall) |
| integration | `run-unit-tests.sh --kind integration` | 0 | 0 | 1636 (49 files, 66.57s wall) |

FAIL count captured via `grep -c '^FAIL '` on the full pooled log (not a tail read — hazard (a)
observed). Exit status captured into a shell variable immediately after each run, per hazard (a).
`HARNESS_AGENT_TYPE` unset for every invocation, per hazard (b).

Single-file re-measurement, the two files this diff actually touches:
- `tests/unit/test-expertise-ops.py` alone: exit 0, 121 PASS, 0 FAIL. u23a/u23b/u23c all present
  and PASS (9 lines: code-11 assertion + 2 message-token assertions per sub-case).
- `tests/integration/test-expertise-merge.py` alone: exit 0, 220 PASS, 0 FAIL. case27a/case27b/case27c
  all present and PASS (9 lines: exit-11 assertion + message-token assertion + byte/absence
  assertion per sub-case).

## Task verify blocks (verbatim from plan.yaml)

- **T-01** (loads module by path, asserts `compute_union` raises `MergeRefusal(11)` with
  `AMBIGUOUS TARGET`/`section=Patterns`/`id=P-02`): **exit 0**.
- **T-02** (drives the real CLI via subprocess against a temp `.harness/expertise/harness-pm.md`
  with a duplicated-id proposal): **exit 0**.

## Re-measurement against notes/qa-BUG-276-c0.md's prior claims

| claim | prior note | this run | match? |
|---|---|---|---|
| unit PASS/FAIL | 520 / 0 | 520 / 0 | **exact match** |
| integration PASS/FAIL | 1513 / 0 | 1636 / 0 | **FAIL count matches (0); PASS total differs by 123** |
| T-01 verify exit | 0 | 0 | match |
| T-02 verify exit | 0 | 0 | match |
| six checks redden under live mutation | claimed, in a disposable copy | **not re-run this cycle** | not independently re-measured |

The integration PASS-total delta (1636 vs 1513) is a pooled, repo-wide count across 49 files, not
scoped to this diff — the two files this review actually covers (u23*/case27* markers) match the
prior claim exactly, and FAIL is 0 either way. Flagging the delta per instruction rather than
silently reconciling it: [INFERENCE] most likely explained by unrelated integration test growth
elsewhere in the shared repo between the two measurements (multiple sibling features were running
concurrently at review time), not by anything in the three files under review. Not a finding against
this diff — no test in either of the two changed test files is missing, misnamed, or failing.

The mutation-proof claim (six new checks reddening under a live guard-callsite mutation, in a
disposable worktree copy) was **not independently re-measured this cycle** — this dispatch is
gate-only/author-nothing and the authoring segment already performed and recorded that proof at
6d969ed3. Per O-03/O-09: this is inherited assurance, not measured by me; I did not detect anything
in the pinned diff that would make me doubt it (the guard fires as the first statement of
`compute_union`, ahead of the base comparison, matching D-03), but I did not myself flip
`_check_proposal_duplicate_ids` to confirm the cases redden.

## Inspection (SC-06, not automated)

Read `expertise-merge.py` lines 1-27 directly: docstring's exit-code table lists exactly
`0, 6, 7, 8, 9, 11` — 9 and 11 both present, 10/12 both absent. Matches SC-06 and D-05 exactly.

## Findings

None against the diff. FAIL=0 on both required and voluntarily-run kinds; both task verify blocks
pass verbatim; SC-06's docstring table is correct by direct read; the two changed test files'
new markers (u23a-c, case27a-c) are all present and green, matching plan.yaml's intent line by
line (names, sub-case count, assertion shape).

Open items are not mine to raise fresh — PF-8eac8a4b4f41d3ea8f759cdec6e73186 (D-09's exit-11 row
gap in harness-distill/SKILL.md) and PF-59b9da56871cca170a7f66678c292035 (D-07's parse/render
silent-drop) are already recorded OPEN in plan.yaml's panel findings, settled by their own decisions
as out of scope for this ticket; I did not re-litigate either.
