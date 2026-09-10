# Simplification angle — FEAT-58 plan draft (cycle 0, pre-signature)

## SIZE ANSWER, FIRST, UNHEDGED

**19 is the floor. No task merge survives scrutiny.** The redraft is honest decomposition, not
padding. The operator's own DoD names 21 distinct runner-graded proof clauses across the seven
binding items (D-1..D-5, M-1, M-2); pm already bundled four of them down (T-03 carries 2 clauses,
T-07 carries 3, T-08 carries 2, T-13 carries 2 — saving 5 tasks versus a naive one-clause-one-task
count of 24) to reach 16 clause-discharging tasks, plus T-02 (the shared fixture every integration
test imports — cannot fold into any one clause-task without making every other task depend on a
proof task's own file), T-12 (the production hook-wiring `feature` task the T-13/14/15/16 proof
tasks grade — a build task, not a proof task, and change_type differs), and T-20 (the cross-cutting
"nothing altered" check, which by construction depends on every other task landing and so cannot
be folded into any of them). 16 + 3 = 19. This is the arithmetic, not a defended round number.

## 1. Per-task table (19 tasks, from `plan.yaml`, cross-checked against `research-plandraft2-coverage.md`)

| Task | traces | files (abbrev.) | verify (abbrev.) | Binding item | SC |
|---|---|---|---|---|---|
| T-01 | REQ-05, SC-14 | notes/suite-baseline.md | grep shape + `merge-base --is-ancestor` | D-5 (negative half) | SC-14 |
| T-02 | REQ-01/02/03 | tests/integration/f58_sparse_fixture.py | `--self-check` | prerequisite (no SC) | — |
| T-03 | REQ-01/02/06, SC-15, SC-17 | bin/worktree-state.py + 2 test files | unit `&&` integration | M-1 (2 of 3 clauses) | SC-15, SC-17 |
| T-04 | REQ-06, SC-16 | test-worktree-state-norepair.py | 1 file | M-1 (1 of 3) | SC-16 |
| T-05 | REQ-01, SC-02 | test-sparse-required-paths.py | 1 file | D-1 (1 of 3) | SC-02 |
| T-06 | REQ-01, SC-03 | test-sparse-derivation.py | 1 file | D-1 (1 of 3) | SC-03 |
| T-07 | REQ-02/08, SC-04/05/06 | .gitignore + test-corpus-readable.py | grep `&&` 1 file | D-2 (all 3) | SC-04, SC-05, SC-06 |
| T-08 | REQ-03, SC-08, SC-09 | check-state.sh, check-domain.sh + 2 test files | unit `&&` integration | D-3 (2 of 3) | SC-08, SC-09 |
| T-09 | REQ-04, SC-10 | bin/feature-index.py + index + test | unit `&&` `--check` | D-4 (1 of 3) | SC-10 |
| T-10 | REQ-04, SC-11 | merge-gate.py + 2 test files | 2 files `&&` | D-4 (1 of 3) | SC-11 |
| T-11 | REQ-09, SC-12 | FEAT-03 feature.json OR exemptions.json + test | 1 file | D-4 (1 of 3), D-06 exec | SC-12 |
| T-12 | REQ-07 | 2 hooks + post-merge-sweep.sh | `test -x` + grep `&&` 1 file | M-2 wiring (no own SC) | — |
| T-13 | REQ-01/07, SC-01, SC-19 | test-sparse-creation.py | 1 file | D-1 (1 of 3) + M-2 (1 of 4) | SC-01, SC-19 |
| T-14 | REQ-07, SC-18 | test-merge-skipbits.py | 1 file | M-2 (1 of 4) | SC-18 |
| T-15 | REQ-07, SC-20 | test-rebase-state.py | 1 file | M-2 (1 of 4) | SC-20 |
| T-16 | REQ-07, SC-21 | 2 test files (unit + integration) | unit `&&` integration | M-2 (1 of 4) | SC-21 |
| T-18 | REQ-03, SC-07 | test-check-state-equivalence.py | 1 file | D-3 (1 of 3) | SC-07 |
| T-19 | REQ-05, SC-13 | test-nonworktree-unchanged.py | 1 file | D-5 (positive half) | SC-13 |
| T-20 | REQ-10, SC-22 | notes/nothing-altered.md | `git diff` pathspec + grep | cross-cutting | SC-22 |

Clause-count check: D-1=3(T-05,T-06,T-13a), D-2=3(all T-07), D-3=3(T-08×2,T-18), D-4=3(T-09,T-10,T-11),
D-5=2(T-01,T-19), M-1=3(T-03×2,T-04), M-2=4(T-13b,T-14,T-15,T-16) → 21, all 21 accounted for, zero
gaps, zero double-counts.

## 2. Proof-task-pair analysis (T-04/05/06/13/14/15/16/18/19/20)

**T-05 vs T-06 — do NOT merge.** Same kind (integration), same sole dependency (T-03), no
kind-forced split. But each is its own *mandatory control* against a *different* way the same
requirement can be gamed — T-05 catches a hand-written include list that silently omits a path
(the `.agents/skills` omission that actually happened); T-06 catches a literal include list
disguised as a derivation. Each carries its own closed-loop discrimination proof (delete-one-entry
+ revert for T-05; literal-list-substitution + revert for T-06). The DoD's own D-1 test-matrix
section states both as separate, independently-mandatory bullets, and pm's coverage note names
this pair explicitly as a place "the DoD demands separation." Folding them into one task's chained
`verify: fileA && fileB` would not corrupt either fixture (each still builds its own instance) but
it would make one task-level PASS/FAIL represent two independently-traced SC (SC-02, SC-03) whose
individual status becomes unrecoverable from the task verdict alone when the first script fails —
exactly the "one failure hides another" shape this angle was asked to test for. Keep separate.

**T-14 vs T-15 — do NOT merge.** Same kind, same sole dependency (T-12), no forced split. But T-14
is explicitly authored as "ITS OWN TASK AND ITS OWN FILE, AND IT MUST FAIL TODAY" — a red-first
regression proof with its own host-baseline citation it must not leak into a fixture assertion —
while T-15 proves a different git operation (rebase vs. merge) against a different hook
(`post-rewrite` vs. `post-merge`). Each carries its own pre-change reproduction clause. Merging
combines two independent git-operation regressions and their own before/after mutation cycles into
one task, with the same task-verdict-granularity loss as above (SC-18, SC-20 masked into one
status). Keep separate.

**T-13's two cases (harness route / bare route) — already merged, correctly.** Both prove the same
mechanism claim (post-checkout fires regardless of creation route) and are two clauses of one
proof, not two independent controls — this is the same shape as T-03's five-checks bundle. Settled.

**T-16 Part 1 / Part 2 — already correctly split by kind**, per the dispatch's own note (unit vs.
integration, DEC-213 forces the directory to select the kind) — not re-litigated here.

**No other candidate pair examined shows a genuine merge.** T-09/T-10 touch different production
files under different REQ; T-18/T-19 serve different binding items (D-3 vs D-5) with different
dependency sets; T-11/T-20 are sequentially dependent, not siblings.

## 3. Findings

- **{id: D-02, severity: med, summary: "Bare unpadded `D-1`..`D-5` (operator DoD binding items) and
  zero-padded `D-01`..`D-11` (this plan's own decisions) are two live numbering namespaces that
  look nearly identical and are used inconsistently.", cost: "D-02's own choice/because text
  (lines 53, 54, 58, 59, 67) uses bare `D-2`/`D-3` to mean the *operator's* binding items while
  sitting inside decision `D-02` — a reader skimming for 'D-3' (operator: audit fail-closed) can
  land on plan decision `D-03` (three thin hook shims), an unrelated topic. Six more bare
  occurrences at lines 37-41 (D-01), 101 (D-05), 125 (D-06), 407 (T-03 intent), 1169 (T-19 intent).
  One spot, line 657, already disambiguates correctly: 'D-2's work (D-02)' — proving the plan's own
  authors recognized the collision but did not apply the fix everywhere.", alternative: "Apply the
  line-657 pattern everywhere: spell every operator-binding-item reference as 'binding item D-N' or
  'the operator's D-N', reserving bare 'D-NN' exclusively for this plan's own decisions section."}**

- **{id: D-03/T-12, severity: low, summary: "The parenthetical '(T-11, D-08)' shorthand for FEAT-34's
  own task/decision ids is repeated verbatim in two places (D-03's `because`, line ~82, and T-12's
  intent, line ~906) and collides in spelling with THIS plan's own T-11 (the D-06 real-data act) and
  D-08 (derived sparse cone) — entirely different subjects.", cost: "A reader grepping this file for
  'T-11' or 'D-08' gets three unrelated hits (two of which are the same foreign citation repeated),
  and a future edit correcting the ambiguity in one spot can silently miss the other since the text
  is duplicated rather than referenced once.", alternative: "Write 'FEAT-34's T-11/D-08' explicitly
  in both places, matching the disambiguation this plan already applies to FEAT-57's T-19 at line
  174-175 ('also touched by FEAT-57's T-19')."}**

- **{id: D-08/T-05, severity: low, summary: "The measured fact 'git sparse-checkout set exits 0
  both with no arguments and with patterns matching nothing' is restated verbatim in D-08's
  `because` (line 186) and in T-05's intent (line 500-501), each for a different argument (why
  derivation-not-literal; why a positive control is mandatory).", cost: "Both citations are stable
  and serve genuinely different arguments, so this is a low-risk duplicate rather than a real drift
  hazard — noted for completeness, not blocking.", alternative: "If touched again, T-05 could read
  'per D-08's measured exits-0 finding' instead of restating the git behaviour, but this is
  optional polish, not a defect."}**

- **{id: T-02/T-13/T-15, severity: low, summary: "The destroy-from-outside rationale ('git worktree
  remove exits 0 when run from inside the tree it deletes, which destroys the caller's working
  directory') is stated in full twice — T-02's `destroy()` doc (line 363-365) and T-13's intent
  (line 965-967) — while T-15 correctly just cites the helper without repeating the explanation
  (line 1052).", cost: "Two full copies of the same git-quirk explanation that would need to be
  edited in lockstep if the git behaviour citation ever needs correction; T-15 already shows the
  cheaper pattern is available.", alternative: "T-13 could read 'via f58_sparse_fixture's destroy()
  (T-02)' the same way T-15 does, dropping the restated explanation."}**

## 4. Dead references

None found. `T-17`/`D-15` do not appear in `plan.yaml` outside the panel block's own explicit,
self-documenting historical note (which states plainly that its subject no longer exists and is
not carried forward — already flagged settled and not re-raised here). `corpus_root`/
`corpus_features`/`corpus_read` appear once (D-09's `because`) explicitly as the *rejected*
halted-plan alternative, correctly labelled as dead rather than left dangling. Every `T-NN`
cross-reference checked (T-01 through T-20, `T-11, D-08` foreign citation aside, addressed above)
resolves to a task that exists in this draft.

## Empty-angle note

Part 4 is not empty — three low/med duplication findings above — but the size question (Part 3)
returns the "arithmetic forces the floor" answer with zero legitimate merges, which is itself a
real and complete result for this angle, not a shortfall.
