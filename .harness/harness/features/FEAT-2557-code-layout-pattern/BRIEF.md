# BRIEF — FEAT-2557-code-layout-pattern The code layout pattern: entry plus package, modules named by reads

## Problem

FEAT-69 and FEAT-70 split `check-state.py` and `plan-merge.py` into a thin entry over a twin
package whose modules are named for what they read. The convention never reached a skill: its only
full record was the FEAT-69 grilling note, removed by FEAT-71 (`a41f7cfc`), and the one written split
rule left is a single bullet in `harness-craft/references/delete-first.md` ("split at the seam where
its reads diverge"). The next author or reviewer facing a long file has no layout to follow and
must dig a deleted note out of git history, or invents a different shape — flat prefixed siblings,
`utils` modules, a re-export shim — that review then has no written rule to catch.

## Done when — by perspective

**code maintainer** — When I split a long file, in any repository Harness builds, the skill I
already load tells me where the split lands and what the modules are called; in Harness `bin/`, one
short file tells me the Python mechanics and shows me the two existing examples.

**reader (eng-lead architecture review / code-reviewer)** — I can name a layout defect as a
finding by pointing at a written rule, rather than at my own taste.

**operator** — The convention and where it came from are in the decision record, so I can audit
it later without reconstructing FEAT-69/70 from history, and this change touched only the prose it
promised.

## Success criteria

Each inspection SC is graded on `git show <review_sha>:<path>`, never the working tree.

- SC-01 (code maintainer): `harness-codebase-design` SKILL.md gains a section headed
  `## Layout — where a split lands`, language-neutral (no `bin/`, `.py` or `__init__` in it),
  stating each of: split where reads diverge, citing delete-first; the entry stays put and thin
  (parse + dispatch, no logic); the package is the entry's twin, never flat prefixed siblings;
  modules named for what their functions read, never by subject or kind (`utils`, `helpers`,
  `common`), short nouns the package path completes; one home per domain; a split moves code
  without changing it and callers migrate in the same change, no re-export shim; size judged in
  review, never capped. The reviewer cites the line for each clause.
  verify: inspection
- SC-02 (reader): that skill's `## Applying it` gains one bullet, for eng-lead architecture review
  and code-reviewer stage two, naming as findings: flat prefixed siblings, subject/kind module
  names, an entry that kept logic, two homes for one domain, a re-export shim; and, in the Harness
  control plane, judging a `bin/` change against the layout entry in AGENTS.md's project map.
  verify: inspection
- SC-03 (code maintainer): `.claude/skills/harness/bin/LAYOUT.md` exists and holds only: a scope
  line; an Entry → Package table (`check-state.py` → `check_state/`, `plan-merge.py` →
  `plan_merge/`) with no size column; hyphenated entry kept because callers invoke it by path,
  underscore package with an empty `__init__.py`; the entry puts its own directory on `sys.path`
  and imports what it dispatches, docstring and bootstrap kept; a flat module serving one
  package's domain moves into it, and only cross-cutting modules many entries share stay flat
  (`harness_boundary.py`, `harness_merge.py`). It carries no "A split" section, no script
  catalogue, no grade-bar, DEC-174, test-forking or scanner rule, no FEAT provenance; every file
  it names exists in `bin/` at the pin.
  verify: inspection
- SC-04 (code maintainer): `AGENTS.md` gains one `## Project map` row whose Where is
  `.claude/skills/harness/bin/LAYOUT.md`, and one `## Conventions` bullet reading exactly "Before
  writing code, read the harness-codebase-design skill and, for Harness `bin/`, the layout entry in
  the project map." The LAYOUT.md path occurs exactly once in AGENTS.md.
  verify: inspection
- SC-05 (operator): `DECISIONS.md` carries a new entry DEC-259 recording the convention (thin entry
  over a twin package, modules named by reads, review-only enforcement with lint and cap rejected),
  its FEAT-69/FEAT-70 provenance and FEAT-71's removal of the note, and its three homes (the skill
  section, LAYOUT.md, the AGENTS.md map row); `DECISIONS-INDEX.md` carries its row with a
  hand-written ruling and otherwise equals `gen-decisions-index.py --stdout`.
  verify: inspection
- SC-06 (operator): the diff from the merge base touches exactly the five files above plus this
  feature's directory: no hook, gate, validator, schema or test file, and
  `harness-craft/references/delete-first.md` unchanged.
  verify: inspection

## Verification gaps

- No test kind executes prose. Every SC is `inspection`; `change_type: docs` requires no test kind
  (`.harness/harness.json test_matrix.docs`). The index regeneration and anchor checks run as task
  verifies, not as SC evidence. No SC rests on a null, unresolved or excluded kind.
- Growing `harness-codebase-design` raises the preload of every seat that autoloads it;
  `check-skill-weight.py` reports overage as a note, never a failure (eng-lead 4931 of 5500 words at
  cf7b422b). The reviewer reads its output on the pin; nothing gates it.

## Constraints

- The grilling's `## Settled` wording and content is binding
  (`.harness/notes/grilling-code-layout-pattern-2026-11-27.md`). LAYOUT.md has no size column and no
  "A split" section; the Conventions bullet names no location — the path lives once, in the map row.
- No hook, gate, validator, schema or test changes; no lint, length cap or ratchet (FEAT-69's
  prose-first ruling holds).
- `delete-first.md` gains no pointer (settled at plan): the new section cites delete-first, and
  that leaf already points readers to `harness-codebase-design` twice, which eight seats preload;
  a second, section-level pointer would be a second home for the same link.
- Routing by `check-domain.py --resolve`: the skill and AGENTS.md have no squad grant (declared
  main-session step, DEC-179); `bin/**` is backend-dev's; `.harness/harness/docs/**` is
  documentor's. Three routes, so three tasks — the patch lane's one task yields to one route per
  task.
- SUPPLIES: DEC-149 and DEC-235 (`harness-codebase-design` is the home for reader-side design
  rules; craft leaves are read at the seam), DEC-158 (rule in the skill, history in DECISIONS.md),
  DEC-202 (AGENTS.md points, never copies; `.claude/skills/` is the authored tree), DEC-205 (the new
  entry states current truth). BLOCKS: none.

## Out of scope

- The `feature.json` package refactor and deleting `feature-json-merge.py` — feature 2; its
  grilling settles the name (`check_state/feature_record.py` exists beside a proposed top-level
  `feature_record/`).
- Test-code layout and adding `harness-codebase-design` to harness-qa — a later feature (Q5).
- Any mechanical check — lint, length cap or ratchet (Q3).
- Splitting any of today's long files.

## Approval

status: pending
approved-by:
date:
