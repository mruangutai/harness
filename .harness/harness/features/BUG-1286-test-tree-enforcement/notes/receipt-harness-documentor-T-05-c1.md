# Receipt — harness-documentor — BUG-1286 T-05 c1

**DEC-213 now states the shipped repository-wide invariant, and the index is regenerated clean.**
T-05's `verify:` runs verbatim at exit 0; the full unit suite is exit 0 / 341 PASS / 0 FAIL / 27
files, identical to the `5f76d6b1` baseline.

## What landed

- `.harness/harness/docs/DECISIONS.md` — ONE amendment paragraph appended to DEC-213 after its
  "Considered and refused:" paragraph, house style (single physical line, bold opener), opening with
  the exact literal `**Amended by BUG-1286-test-tree-enforcement — the predicate's reach, not its
  principle.**`. 608 words. Anchor by content, not line: grep `Amended by BUG-1286`.
- `.harness/harness/docs/DECISIONS-INDEX.md` — the DEC-213 ruling tail (right of ` :: `) rewritten by
  hand, then regenerated. The generated left side recomputed: tags moved
  `[tests,plan,dispatch,hooks]` → `[tests,plan,state,skills]` and `refs:` gained `DEC-189`, both
  effects of the longer body, not hand edits (see `gen-decisions-index.py` `compute_tags` /
  `compute_refs`).

## Every clause verified against the shipped code, not the plan

Authority read: `.claude/skills/harness/bin/suite_layout.py` at HEAD `5f76d6b1`.

- Two groups, different extension policies: `is_test_shaped` returns True for any
  `AGNOSTIC_NAME_PATTERNS` basename match at any extension, and for a `RESTRICTED_NAME_PATTERNS`
  match only when `os.path.splitext(path)[1] in SOURCE_EXTENSIONS`. Consequence stated per group;
  patterns and extensions NOT re-listed.
- Matcher semantics: `code_grade._is_test_path` (`.claude/skills/harness/bin/code_grade.py`,
  `_is_test_path`/`_patterns`) `fnmatch`es the full relative path over every kind with status
  `active` or `locally_run`, minus that kind's `exclude`. Superset framing written as such.
- Enforcement is an assertion: `tests/unit/test-suite-layout.py` `offenders()` + the two
  `case 11 behavioural` checks read `repo_cfg["test_kinds"]` at test time and flag any non-`tests/`
  path the matcher counts that `is_test_shaped` rejects or that sits in `DOCUMENTED_EXCEPTIONS`.
  No globs, corpus or synthesised names transcribed.
- Bin clause retained: `violations()` still globs `("test-*.py", "*.test.*", "probe-*")` over bin
  from the filesystem, and `planted_rel` suppresses the second report (D-04).
- Index read: three conditions cited, not restated (`.git` exists; `tracked_paths` refuses a root
  that is not its own toplevel; index carries `suite_layout.py`). No index → other clauses only;
  `LookupError` in a `.git` root → `cannot enumerate tracked files under …` violation.
- Registry: exact paths, self-policing over glob / duplicate / untracked / unnecessary
  (`_registry_findings`); sole live entry is FEAT-44's `evidence/probe-session-accessors.ts`.
- Prohibited over-claims: both explicitly negated in the text ("not a property of the whole
  vocabulary", "does not hold in the other clauses"); neither wider claim appears.

## Evidence

- Pre-edit non-vacuity: `grep -c "tracked test-shaped file outside" …/DECISIONS-INDEX.md` → **0**.
- T-05 `verify:` verbatim (string cross-checked against `plan.yaml` line 1047): output
  `examined 30 anchor(s), 0 failed`, exit **0** (the `diff` stage printed nothing — an empty diff is
  the pass condition).
- `env -u HARNESS_AGENT_TYPE .claude/skills/harness/bin/run-unit-tests.sh --kind unit`: exit **0**,
  341 `^PASS `, 0 `^FAIL `, `pool: 8 workers, 27 files`.
- HEAD unmoved: `5f76d6b1`. Nothing staged, nothing committed.

## Incident worth knowing

The first pass of both edits landed in the MAIN checkout (`/Users/molchairuangutai/GitHub/harness`)
because the hunk headers carried repo-relative paths while the process cwd is the main repo, not the
worktree — the snapshot tags still matched, since the two copies were byte-identical at `5f76d6b1`.
Detected when regeneration in the worktree "reverted" the ruling. Both main-repo edits were reversed
by hand (not by git), and `git -C <main> status --porcelain .harness/harness/docs/` is now empty.
Every subsequent edit used absolute worktree paths.

## Open

- None blocking. Note for review: `notes/qa-tree-audit.md` in the worktree's porcelain belongs to the
  concurrent validator run, not to this one.
