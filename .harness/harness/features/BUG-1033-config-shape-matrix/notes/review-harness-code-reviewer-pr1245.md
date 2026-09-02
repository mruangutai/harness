# Review — PR #1245 (BUG-1033-config-shape-matrix)

Reviewed `b7956fc4a053f7dcc9cb2a2d061215d38e4bd9d3..86cd8c496d9d3376ec7859f0ac99b6b3d17d26f9` (`main`'s
merge-base..HEAD; single commit `86cd8c49`, no `[harness:human]` trailers). No `BRIEF.md`/`plan.yaml`
exists for this slug (direct worktree/PR flow, per assignment) — Stage 1 checked against issue #1033's
narrative and DEC-212's own text instead. No project-wide suites were re-run (already verified by the
requester); ran only scoped checks against this diff.

## VERDICT: PASS — one should-fix (med): a stale table row this PR itself made stale

## Stage 1 — spec compliance (against DEC-212 / issue #1033)

`.harness/harness.json` and `.claude/skills/harness/templates/harness.json` both gain
`test_matrix.config.when: [{"kind":"integration","if":"touches_config_shape"}]`, matching what DEC-212
says it chose (`DECISIONS.md:6618-6620`) — verified identical in both files via the new unit test.
`_matrix_provenance.config` in the project file is `{"removed": [], "added": ["integration"], "signed":
"DEC-212"}` — correctly shaped per DEC-187's `removed`/`added`/`signed` triple, matching the sibling
`api`/`cross_module`/`feature` entries' shape exactly (`harness.json:105-118`). No scope creep: every
touched file maps to one of DEC-212's five stated deliverables (predicate, matrix binding, provenance,
skill prose, SPEC.md, test) and nothing else was touched.

**`touches_config_shape` as a predicate**: coherent by the same standard DEC-35 already accepts for its
three siblings — DEC-212 states its own tradeoff explicitly ("the predicate is a judgment call, not a
mechanical diff rule... same latitude DEC-35 already accepts for the other three") rather than claiming
false precision. The shape-vs-value line it draws (container type / required-ness / structural nesting,
vs. a value a key already holds) is the same distinction `stations` mapping→list vs. `max_total_runs`
20→25 illustrates concretely in the decision text itself, and matches the worked example repeated
verbatim in both skill files (`harness-qa-gate/SKILL.md:44-46`, `harness-verification-rules/
SKILL.md:36-38`). Not fuzzier than `has_interaction_flow` or `match_bug_class` already are in production
use (per this repo's own `harness-qa.md` Expertise G-08: `match_bug_class` has never once fired for a
real diff, and nobody treats that as a defect in the predicate).

**Nothing elsewhere needed a matching change.** Predicate names are pure prose/data — no script in
`.claude/skills/harness/bin/` enumerates or validates the fixed-predicate set mechanically (grepped;
zero hits outside the two skill files, `harness.json`×2, `DECISIONS.md`, `DECISIONS-INDEX.md`, `SPEC.md`
and the new test). `templates/examples/harness.kaya-ai.json` was correctly left untouched: it is a dated
(2026-07-26), already-DEC-187-tailored snapshot of one onboarded project's actual config, not a living
template — it already diverges from `templates/harness.json` in several other ways (no `functional`, a
`python` kind, `bugfix.always: ["__bug_class__"]`) and updating it here would misrepresent history.

## Stage 2 — code quality

### F1 — should fix (med): SPEC.md's illustrative table now contradicts its own JSON example, in the section this PR edited

`SPEC.md:1265` (§9 Test guardrails, the row `| config / scaffolding / docs | exempt | exempt | exempt |
exempt |`) still reads unconditionally exempt across all four test-kind columns. Twelve lines below it,
the JSON block this PR *did* update (`SPEC.md:1277-1278`) now reads `"config": { "always": [], "when":
[{"kind":"integration","if":"touches_config_shape"}] }` — a conditional integration requirement. The
section's own lead-in states the table "sets the baseline" (`SPEC.md:1263`), and DEC-35's own rationale
for making conditionals structured data in the first place is "if the 'if touches DB/external' cells
were prose they would silently vanish and high-risk changes would ship untested" — the merged
config/scaffolding/docs row is now exactly that silently-vanished cell, reintroduced in the
human-readable half of the same section this PR touched. A reader who consults only the table (the
documented fast path) concludes config changes are unconditionally exempt from every kind, missing the
one conditional this PR exists to add.

**Not a live gate defect** — the actual enforcement path is `harness.json`, which both skill files
correctly say is authoritative ("never restate or paraphrase it"), and that file is correct. This is
confined to a hand-maintained illustrative table; SPEC.md was already flagged as "somewhat stale"
elsewhere per the assignment, but this specific cell was accurate before this commit and is made wrong
by it — a new inconsistency, not a pre-existing one.

**Fix**: either split the merged row (`config` on its own line, `scaffolding / docs` on another) with
the `config` row's Integration cell reading `if config-shape` (matching the `api` row's `if touches
DB/external` convention), or add a footnote under the table pointing at the JSON block. Cheap, does not
touch code, no re-verification cycle needed beyond re-reading the table.

### Other checks, no findings

- **`DECISIONS-INDEX.md`**: ran `gen-decisions-index.py --stdout` and diffed against the committed file
  — byte-identical. The DEC-212 row (`@6616`, tags `[state,qa,budget,github]`, `refs: DEC-35`) is
  correctly machine-derived, not hand-edited-and-drifted. Ruling is 25 words (cap 30, per the existing
  `test-gen-decisions-index.py` gate already covering this file generically for every DEC entry — no
  duplicate check needed in the new test).
- **New unit test genuinely guards regression**, verified by direct execution (10/10 pass on the real
  tree) plus reasoning about each of the three named threats: (1) silently reverting the `when` clause
  — `len(matched) == 1` on the filtered list fails if the entry disappears; (2) dropping the
  `_matrix_provenance` entry — `isinstance(provenance, dict)` fails if the key or the `config` sub-key
  is removed, and `added`/`signed` are checked for exact equality, not mere presence; (3) the DEC-212
  heading being deleted or renamed away from describing a config-shape change — both the heading-exists
  check and the "config-shape change" substring check (within 200 chars of the heading) fail
  independently. One minor gap, not worth gating: the test checks `added`/`signed` but never `removed`,
  so a provenance entry corrupted to e.g. `"removed": ["unit"]` (nonsensical but structurally valid)
  would stay green — low impact, since nothing else in the repo consumes `removed` mechanically either
  (it is a human-audit field per DEC-187's note).
- **Registration**: `test-config-shape-matrix.py` is in `run-unit-tests.sh`'s `UNIT_SCRIPTS` array (not
  `INTEGRATION_SCRIPTS`), matching the file's own docstring claim ("nothing here forks a subprocess, so
  this is a UNIT-kind test") and the `unit` kind's `detect` glob.
- **code_grade**: ran `code-grade.py --base $(git merge-base main HEAD) --head HEAD` directly (merge-base
  `24d2faea`, HEAD `86cd8c49`) — 8 gated functions, all new test code in `test-config-shape-matrix.py`,
  all grade 4-5 against bar 3, zero `SEVERITY` lines, `code_grade: pass`.
- **JSON validity**: both `harness.json` and `templates/harness.json` parse; the new `when`/
  `_matrix_provenance` shapes match sibling entries field-for-field, no stray keys.

## Verdict rationale

No `must_fix`, `severity_max` = med (F1 only) → `PASS` with notes per the gate rule. F1 is cheap and
worth taking before merge, but it is a documentation-consistency gap in a hand-maintained illustrative
table, not broken behavior or a live gate defect.
