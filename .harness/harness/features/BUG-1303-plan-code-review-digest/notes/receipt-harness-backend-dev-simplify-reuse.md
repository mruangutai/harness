# REUSE angle — BUG-1303 simplify pass — receipt (harness-backend-dev)

**BLUF: one confirmed finding worth a backlog row (med), one confirmed-but-minor finding
(low), and two leads refuted with evidence.** Nothing here changes intended behaviour or
warrants an apply against `NOBODY`-owned files anyway — every touched path in this diff
resolves to NOBODY per the dispatch (main-session-direct or documentor-owned), so this pass
is FLAG-ONLY by construction (harness-simplify §Applying: "domain guard resolves … to NOBODY,
the finding is FLAG-ONLY"). No file was edited; see verification at the bottom.

## Findings

### F1 — `_reviewer_plan_mode_results`'s hard-coded reviewer-template tuple duplicates
`_reviewer_template_paths`'s mechanical discovery — **med**

- File: `tests/integration/test-validate-digest.py:394-399`
- `reviewer_sources` hard-codes `.claude/agents/harness-code-reviewer.md` and
  `.omp/agents/harness-code-reviewer.md` as string literals.
- The same two paths are already produced mechanically, 74 lines earlier, by
  `_reviewer_template_paths(validator)` (`tests/integration/test-validate-digest.py:117-136`),
  which walks both `agents_dir` trees and keeps any file where
  `validator.norm(fname[:-3]) == "reviewer"` — true for `harness-code-reviewer` via
  `ALIAS["harness-code-reviewer"] = "reviewer"` (`.claude/skills/harness/bin/validate-digest.py:243`).
- Concrete cost: two spellings of "where does the code-reviewer agent template live" now
  live in the same file — one mechanical, one literal — and only the mechanical one updates
  itself if `.omp/agents` or `.claude/agents` is ever reorganized (rename, new nesting, a
  filename-pattern change). The literal tuple does not silently rot unnoticed — `_contract_source`
  returns `None`→`""` for a missing path and the plan-mode check then FAILs loudly — but a
  reviewer who reads only the second definition has no reason to know the first one already
  computes the same set, and every future edit to one path needs a matching edit to the other
  or a stale copy sits there until the loud failure fires.
- Exact alternative: derive the first two `reviewer_sources` entries from
  `_reviewer_template_paths(validator)` filtered to `os.path.basename(path) ==
  "harness-code-reviewer.md"`, and keep only the third entry
  (`.claude/skills/harness-code-review/SKILL.md`) literal — that one is not an agent template
  and genuinely cannot come from `_reviewer_template_paths`, which only scans `agents_dir`.
- Backlog per `harness-simplify`'s "apply may not delete or weaken an assertion" is not in
  play here (this is a pure dedup, not a weakened check) — but the touched file resolves to
  NOBODY under domain, so it is FLAG-ONLY regardless (see rule cited above).

### F2 — SKILL.md's new plan-phase block is a third restatement of the same two-line
contract already carried by the (single-sourced) agent templates — **low**

- Files: `.claude/skills/harness-code-review/SKILL.md:170-173` (new in this diff) vs.
  `.omp/agents/harness-code-reviewer.md:93` / `.claude/agents/harness-code-reviewer.md:92`
  (new in this diff, identical comment line in both).
- The `.claude`/`.omp` pair is **not** a duplication in the relevant sense: `.claude/agents/*`
  is a generated adapter of `.omp/agents/*` (pre-existing mechanism, DEC-174) — one edit,
  one propagation, confirmed by diffing both files in this range: the two hunks are
  byte-identical. That is one spelling, not two.
- SKILL.md's new fenced example (`reviewed: plan:<path-to-plan.yaml>` /
  `code_grade: n_a`) restates that same fact a second time, independently, with no
  generator or shared block behind it — and the new test itself
  (`_reviewer_plan_mode_results`, `tests/integration/test-validate-digest.py:394-419`) already
  treats this as fragile enough to need an explicit cross-source string check, which is the
  REUSE tell: a fact three humans must remember to keep in lockstep, guarded by a test rather
  than eliminated by a single source.
- Judged low, not med: SKILL.md is a distinct-purpose document (protocol explanation, worked
  example for a reader who never opens the agent template) and duplicating a two-line
  contract for that audience is a defensible editorial choice, not an accident — unlike F1,
  which duplicates a *file-discovery mechanism* that already existed for exactly this purpose.
  No concrete alternative edit is offered beyond noting it; forcing SKILL.md to `import`/quote
  the agent file's comment would couple a protocol doc to an agent template's literal text,
  which is its own cost.

## Leads — explicitly answered

**Lead: is `CONTRACT_SOURCES` (16-entry hand-written map,
`tests/integration/test-validate-digest.py:297-314`) a re-implementation of
`_reviewer_template_paths`'s mechanical discovery, or load-bearing in a way discovery cannot
be?** — **Refuted as a re-implementation; confirmed load-bearing.** The two do different jobs.
`_reviewer_template_paths` answers "which files on disk match persona X, in both trees" —
useful for the severity-enum sweep, which must check every discovered copy for drift.
`CONTRACT_SOURCES` answers "which single canonical file documents persona X's *whole* output
contract" for 16 personas, 13 of which are non-reviewer personas whose canonical source is a
*shared* skill file spanning multiple personas (`harness-digest-dev/SKILL.md` for four dev
personas, `harness-team/SKILL.md` for three leads) — a mapping mechanical per-file discovery
cannot produce, because there is no filename pattern that maps "backend-dev" to a file named
after "digest-dev". Only 3 of 16 entries (the reviewer personas) point at a single path each
that overlaps what `_reviewer_template_paths` could also find; that narrow overlap is F1
above, not a case for collapsing the whole map.

**Lead: `_contract_source()` vs. whatever the pre-existing section used to read agent
templates — two file-reading helpers where one would do?** — **Refuted.** The pre-existing
`_severity_line_values(path)` (`tests/integration/test-validate-digest.py:168-173`) takes an
absolute path already known to exist (produced by `_reviewer_template_paths`, which only
returns paths `os.listdir` actually found) and raises on absence — that's fine, absence there
is a programming error. `_contract_source(path)` (`tests/integration/test-validate-digest.py:372-377`)
takes a repo-relative path, joins `REPO_ROOT`, and must return `None` on a genuinely absent
file, because the synthetic-fixture tests deliberately exercise "absent" and "unlocatable"
personas (`_synthetic_contract_results`, lines 434-449) that assert the missing-file path is
reported as a named failure rather than crashing the whole suite. Different contracts
(raise-on-missing vs. return-None-on-missing; absolute vs. repo-relative), not a duplicate.

**Lead: `_reviewer_plan_mode_results`'s hard-coded three-path tuple against any existing
derivation of the same set?** — **Confirmed, this is F1 above** (with the added nuance that
the third path, the SKILL.md, has no existing derivation and is correctly literal).

**Lead: three reviewer sources restating the same plan-mode contract text — does the tree
already have a generator or shared block one of them should derive from?** — **Answered: yes
for two of three (the `.omp`/`.claude` pair, via the pre-existing adapter-generation
mechanism, DEC-174), no for the third (SKILL.md), which is F2 above.**

**Lead: DEC-216 entry vs. DECISIONS-INDEX.md — content restated rather than referenced?** —
**Refuted.** The index row (`DECISIONS-INDEX.md:216`) is a one-line compressed ruling
summary in the exact format every other row in the file uses (`- DEC-NN @<line> [tags]
refs: <graph> :: <ruling>`) — compared against neighbouring rows DEC-209, DEC-213, DEC-215,
it follows the same convention of paraphrasing the decision's ruling, not quoting its prose.
The full entry (`DECISIONS.md:6792-6815`) carries evidence, mechanism and scope that the
index deliberately omits. This is the established index/detail relationship, not new
duplication.

## Verification — no edits made

```
$ cd /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-1303-plan-code-review-digest && git status --porcelain
 M .harness/harness/features/BUG-1303-plan-code-review-digest/feature.json
 M .harness/harness/features/BUG-1303-plan-code-review-digest/plan.yaml
?? .harness/harness/features/BUG-1303-plan-code-review-digest/notes/receipt-harness-dev-ops-simplify-efficiency.md
```

Both modified paths and the untracked receipt belong to concurrent sibling/orchestrator
activity (plan/feature-state bookkeeping and the EFFICIENCY-angle sibling's own receipt) —
none are files this REUSE angle was scoped to touch, and none were written by this run.
