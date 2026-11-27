# Goal-check — FEAT-2557 validate cycle 2 (re-review after fix c1)

**BLUF: PASS.** At pin `afd20116a2d5b9ffcbd243cb61c1f282e3935318` (base `cf7b422b`, prior pin
`5c600680`), all three perspectives are discharged. SC-01..SC-06 are met, and SC-05 is now met on
its letter and on accuracy. D-01 → DEC-259 landed, and all six `keep` rows hold. The c1 must-fix is
**fixed**, not resolved by amendment: under the same contract, DEC-259 no longer presents FEAT-70 as
conformant to the no-shim rule, and what it now says about FEAT-70 matches `plan-merge.py` and
`check_state/ctx.py` at the pin. I raise no new findings. Every content read used
`git show afd20116:<path>` or a `git archive afd20116` extract. The worktree HEAD equals the pin,
and the five deliverable paths have no uncommitted changes.

## Perspectives

- **code maintainer: pass.** Carried by SC-01, SC-03 and SC-04. `git diff --quiet 5c600680 afd20116 -- .claude AGENTS.md`
  exits 0, so the skill, LAYOUT.md and AGENTS.md are byte-identical to the c1 pin. The c1 evidence
  therefore stands unchanged (see the c1 note's SC table).
- **reader: pass.** Carried by SC-02 (the same byte-identity argument). The `## Applying it` layout bullet names
  "a re-export shim" as a finding. That is the rule DEC-259's Because now points at.
- **operator: pass.** Carried by SC-05 and SC-06. DEC-259 records the convention, its provenance and its homes, and it now
  states the one known deviation truthfully. The non-feature diff is still exactly the five files.

## SCs (all `verify: inspection`)

| SC | Verdict | Evidence at afd20116 |
|---|---|---|
| SC-01 | met | `harness-codebase-design/SKILL.md` is unchanged since 5c600680, where c1 graded each clause |
| SC-02 | met | Same file, unchanged; `## Applying it` layout bullet |
| SC-03 | met | `bin/LAYOUT.md` unchanged. `check_state/__init__.py` and `plan_merge/__init__.py` still exist at the pin |
| SC-04 | met | `AGENTS.md` unchanged; the LAYOUT.md path occurs once |
| SC-05 | met (letter + accuracy) | See below |
| SC-06 | met | `git diff --name-only cf7b422b afd20116` lists, outside the feature dir, exactly `.claude/skills/harness-codebase-design/SKILL.md`, `.claude/skills/harness/bin/LAYOUT.md`, `.harness/harness/docs/DECISIONS.md`, `.harness/harness/docs/DECISIONS-INDEX.md` and `AGENTS.md`. `delete-first.md` is unchanged (`git diff --quiet cf7b422b afd20116`, exit 0). `plan-merge.py` and `check_state/ctx.py` are untouched |

**SC-05, letter.** `## DEC-259 —` sits at line 8758 in DECISIONS.md at the pin. It has Chose (the thin entry, the
twin package, modules named by reads, review only), Over (lint, length cap or ratchet), and Because
(FEAT-69 `d8b139de`, FEAT-70 `a98451c5`, and FEAT-71 `a41f7cfc` removing the note). Its three homes
are named. `gen-decisions-index.py --stdout`, run on a `git archive afd20116` extract, equals the
pinned DECISIONS-INDEX.md (diff empty). The DEC-259 row keeps its hand-written ruling after ` :: `.
Its derived tags changed to `[plan,state,dispatch,skills]`, which the generator produced. Running
`check-decision-anchors.py` at the pin gives "examined 25 anchor(s), 0 failed". DECISIONS.md versus base is
53 additions and 0 deletions.

**SC-05, accuracy (the c1 overrule, re-measured at the pin).** DEC-259's Because now reads "…split
`plan-merge.py` into `plan_merge/`, in this shape, with one exception this rule now names as a
finding: `plan-merge.py` still re-exports `plan_merge.approval.signed_task_hash`, because
`check_state/ctx.py` `_load_hash_module` loads the entry by path for INV-40. Removing it means
migrating that loader first." Each clause is true at the pin:
- `plan-merge.py`: `from plan_merge.approval import signed_task_hash  # noqa: E402,F401  INV-40's import`.
  Its docstring calls the file "the import surface check-state's INV-40 loads `signed_task_hash` from".
- `check_state/ctx.py` `_load_hash_module`: `harness_boundary.load_repo_module("harness_plan_merge", os.path.join(sys.argv[2], "plan-merge.py"))`,
  then `self.signed_task_hash = _pm40.signed_task_hash`. `check_state/feature_record.py`'s INV-40
  path consumes `ctx.signed_task_hash`.
- "One exception" holds as far as I probed. No other `load_repo_module` or `spec_from_file_location` call in `bin/`
  or `tests/` targets `plan-merge.py` or `check-state.py`. Every other reference forks the CLI by
  path. `AMENDABLE_KEYS` is imported for the entry's own argparse help, not re-exported.
  `main()` only builds the parser and dispatches `args.func`.
- The folded low finding is fixed. "is in the `autoloadSkills` frontmatter of every specialist that
  writes code and of eng-lead and code-reviewer" holds: `.omp/agents/harness-{ai-dev,backend-dev,data-engineer,frontend-dev,dev-ops,eng-lead,code-reviewer}.md`
  each list `harness-codebase-design` under `autoloadSkills`, and harness-qa does not, which matches
  DEC-259's Tradeoff. "DEC-149 brought the skill in" matches DEC-149's "`harness-codebase-design` — a
  new rule skill". "DEC-235 keeps craft leaves unpreloaded" matches DEC-235's "read at the seam,
  never preloaded" idiom. DEC-259 no longer cites DEC-149 for current delivery.

## Decision dispositions (DECISIONS.md at afd20116)

| Row | Verdict | Evidence (afd20116:.harness/harness/docs/DECISIONS.md) |
|---|---|---|
| D-01 → DEC-259 | met | The heading at line 8758 matches D-01's choice. Record: "plan decision D-01, signed by Mike Ruangutai on 2026-11-27" |
| DEC-149 keep | met | The clause is at line 3465 (section 3462). No new skill was added, and the entry is not amended |
| DEC-235 keep | met | The clause is at line 8000 (section 7992). delete-first is cited, not edited |
| DEC-158 keep | met | The clause is at line 3804 (section 3791). Provenance appears only in DEC-259, and the skill and LAYOUT.md are unchanged |
| DEC-202 keep | met | The clause is at line 6317 (section 6282). AGENTS.md is unchanged since c1 and has one row and one pathless bullet |
| DEC-179 keep | met | The clause is at line 4851 (section 4845). The fix was also main-session-direct (receipt-main-session-fix-c1.md) |
| DEC-205 keep | met | The clause is at line 6710 (section 6708). The diff is append-only (0 deletions versus base), and DEC-259 states current truth, including the deviation |

## Findings

None new. I probed one boundary further and found nothing: `check-state.py` keeps root-resolution
bootstrap (`_resolve_root`, `chdir`, `PYTHONPATH`, argv rewrite), which LAYOUT.md's "keeps its
module docstring and its bootstrap" explicitly allows, and nothing loads `check-state.py` by path for
an attribute. The re-export's removal (OQ-1) is with the operator, so I do not raise it again here.

## Principles applied

- Weakest sufficient specification (rule 6, harness-principles): I graded the signed SC text plus the
  lead's accuracy ruling, and widened nothing.
- Never falsify the record (rule 15): the c1 overrule is recorded as fixed by implementation, not as
  resolved by amendment.
