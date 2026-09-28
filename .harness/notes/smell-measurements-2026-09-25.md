# Smell measurements — `.claude/skills/harness/bin/` at 4e4e50bd — 2026-09-25

Purpose: pick the next code-smell family from data, not intuition (ruled after the wave-4 grader
extension was dropped as premature). One-off AST measurement; nothing lands from this note.
Scope: the 69 `bin/*.py` control-plane scripts, 39,561 lines. Grades are `code_grade.grade_source`
(the fleet grader's own numbers, bar 4 for production code).

## Long file
| lines | file |
|---|---|
| 4,975 | check-state.py |
| 3,738 | plan-merge.py |
| 2,584 | validate-digest.py |
| 2,498 | gh-sync.py |
| 2,394 | check-domain.py |
| 2,362 | check-plan-routes.py |
| 1,229 | board_lifecycle.py |
| 1,167 | harness_boundary.py |

10 files over 1,000 lines; 18 over 500. The top six hold 18,551 lines — 47% of the tree.

## Long / complex function (the grader's own axis)
1,716 functions. Grade distribution: 5 → 799, 4 → 778, 3 → 51, 2 → 57, **1 → 31**.
82 functions sit below bar 4 and are not grade 2: they are legacy debt the ratchet tolerates
(the grader gates only a *drop*), so every touch of one is a touch nobody can make worse but
nobody is asked to improve. 52 functions exceed 60 lines; 23 exceed 100.

Grade-1 concentration (cyc / cog / abc):
- check-domain.py `shape_problems` 135 / 356 / 320.6 — 691 lines, the largest function in the tree
- validate-digest.py `validate` 134 / 286 / 274.3 — 416 lines
- plan-merge.py `apply_merge` 59 / 136 / 162.9 — 244 lines
- check-domain.py `approval_guard` 44 / 139 / 105.1
- factory_decompose.py `_main` 37 / 71 / 117.2; factory_claim.py `_main` 41 / 74 / 107.6
- gh-sync.py `main` 39 / 50 / 104.4; `cmd_ship` 23 / 30 / 74.3
- validate-digest.py `hook_mode` 30 / 58 / 84.2; `parse_digest` 30 / 73 / 75.4
- check-omp-port.py `check` 42 / 72 / 111.0; render-brief.py `md_to_html` 30 / 78 / 96.4
Twelve of the 31 are CLI `main`/`_main`/`cmd_*` dispatchers; the other nineteen are rule
evaluators whose bodies are one if/append per rule.

Below-bar by file: plan-merge 9, check-domain 7, factory_gh 6, gh-sync 5, validate-digest 5,
wayfind 5, board_lifecycle 4, factory_decompose 3.

## Duplicated code (identical function bodies across files, docstrings stripped)
2 pairs: `bash-write-guard._root` / `check-domain._root` (DEC-234 twin prologues — a ruled,
locked duplicate, byte-identity is the lock); `check-omp-port.frontmatter` /
`check-skill-weight._frontmatter`. Wave 1's consolidation held.

## Primitive obsession / stringly-typed navigation
906 string-keyed `.get("…")` calls; 313 distinct string keys; 27 nested chains
(`a["x"]["y"]`, `.get().get()`). Top keys: `id` 107, `parent` 78, `number` 54, `status` 45,
`name` 37, `github` 37, `issues` 36, `claims` 29, `tasks` 26, `milestone` 25. Heaviest files:
check-state 146, check-plan-routes 91, plan-merge 68, validate-digest 62, factory_gh 60,
inflight_registry 51. Every record (feature.json, plan.yaml, registry, GitHub payloads) is
navigated as an untyped dict at every site; the schema of each lives only in the validators
that reject it. #1928 (digest as text-in-fence-in-JSON) is the same smell at the agent boundary.

## Comments
5,494 comment lines / 39,561 = 14%. Comments are load-bearing by repository rule (moved
byte-for-byte, cited to decisions); this family is excluded from the pick on purpose.

## Not measured
Shotgun surgery (files-per-concept from D-ledgers) — needs a per-feature read, not an AST pass.
