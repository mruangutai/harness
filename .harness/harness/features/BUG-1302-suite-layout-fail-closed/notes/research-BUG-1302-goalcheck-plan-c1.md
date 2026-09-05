# Goal-check — BUG-1302 plan vs the operator's stated intent — cycle 1

**Answer: MOSTLY, NOT YET.** All five B-rows reach a task, both halves of the issue title are
delivered, and every AST count and every literal corpus expectation the plan dictates is CORRECT as
re-derived at `c369fb1`. Three defects block a clean yes, and all three are pm-routable:

1. **F-1 (BRIEF Non-goals bullet 1, REQ-01, T-02) — a false factual claim, and a dropped half of
   B-4.** The BRIEF says "No code-grade record is produced, re-graded or cleared by this feature."
   Measured: `_literal_key_present` is grade **2** at HEAD (cyc 12 / cog 13 / abc 18.4, bar 3 →
   `med` record) and grade **3** after T-02's removal (cyc 10 / cog 13 / abc 15.1) — i.e. T-02
   **clears exactly the "remaining grade-2 med code-grade record" B-4's row names**, and the BRIEF
   asserts the opposite. Fix: state the measured before/after in the BRIEF and pin it (a `verify:`
   clause on T-02, or an SC) so B-4's second clause is a verified deliverable rather than a
   disclaimed one. `suite_layout.py:44 tracked_paths` is the other grade-2 record and stays out of
   scope under the read-only constraint — say which one the row means.
2. **F-2 (BRIEF SC-09) — not falsifiable as written.** SC-09's prose promises "cases 1 to 10, real
   layout clean, sole-implementation sweep, case 11 hygiene certification still report PASS"; its
   `verify:` is only "both files exit 0 with no FAIL line". Deleting any pre-existing check passes
   that verify. Nothing in the plan pins WHAT is discovered. Fix: pin an expected PASS-line count
   (or grep the named pre-existing check strings) at `<review_sha>`.
3. **F-3 (BRIEF SC-10) — wrong evidence kind.** `evidence: unit`, but nothing under `tests/unit/`
   runs `check-plan-routes.py` over a live plan; the live-tree run is the CI step in
   `.github/workflows/tests.yml:152-197` (DEC-183). Use `integration` or `inspection`.

Advisory, non-blocking: **F-4 (plan D-02/D-03)** — both carry `dec: none`, so the BRIEF's section
titled "Accepted risk" reads as the plan accepting risk against the operator's stop condition
"Risk acceptance, scope reduction, or failed-gate waivers" (grilling note, Out of scope). The
substance is fine — remedy (a) is the Advisor's R2 RECOMMENDATION, and the grilling note delegates
material questions to the Advisor — but the provenance must be cited in D-02/D-03 so a later reader
does not see self-granted risk acceptance. This is a signature-visibility fix, not a re-opening of (a).

## Per-lens verdicts

| # | Lens | Verdict |
|---|---|---|
| 1 | Coverage B-row→REQ→SC→task→verify | **PASS** — B-4→REQ-01→SC-01/02→T-02; B-5→REQ-02→SC-03/04→T-01; B-6→REQ-03→SC-05/06→T-03; B-14→REQ-04→SC-07→T-04; B-8→REQ-05→SC-08→T-05. Only gap is B-4's second clause (F-1). |
| 2 | Both halves of the title | **PASS** — fail-closed: T-03, T-04, T-05; dead branches removed: T-01, T-02. T-03 leaves the else branch live-but-unexecuted under the live config, which is inherent to remedy (a) (R2); the compensating controls are real — reachability via `CORPUS_BLIND_KINDS` and the AST message check. |
| 3 | Falsifiability | **FAIL** — on SC-09 only (F-2); SC-05 partial (below). All counts and corpora verified correct. |
| 4 | Scope fidelity | **FAIL** — F-1 is a silent drop of half a B-row; F-4 is a provenance gap. No task exceeds scope; all five stay inside the two test files. |
| 5 | Task order | **PASS** — T-01 adds `import ast`; T-02 and T-03 consume it; `depends_on` runs T-01→T-02→T-03→T-04, so no intent assumes a later edit. T-04's link is same-file serialization only (correct, but the reason is unstated). |
| 6 | Specification completeness | **PASS** — no placeholders, no "follow the pattern"; all five `verify:` are literal `\|` blocks and run from repo root. Nit: T-03's "the ast parse already present in the file" is the only under-anchored phrase. Task-level greps read the working tree, not `<review_sha>` (the SCs correctly use `git show`). |

## Re-derived AST counts (parsed at `c369fb1`, HEAD)

| Measurement | pre-fix | post-fix | BRIEF says | match |
|---|---|---|---|---|
| (a) `ast.Call`/`ast.Name` id `any` in `_literal_key_present` | **2** | **1** | pre 2, post exactly 1 | YES |
| (b) `ast.Constant` `"*?["` in `_literal_key_present` | **2** | **1** | pre 2, post exactly 1 | YES |
| (c) `ast.Constant` `".."` in `_is_inside_tests` | **2** | **1** | post exactly 1 | YES |

SC-02 and SC-04 are therefore safe: a correct fix cannot fail them. Note (c) alone does not
distinguish removing the line-433 tuple element from removing the line-424 segments guard — but
B5_CORPUS does: `("a/../tests/*.py", False)` returns True if the early guard is dropped. Good pairing.

## Corpus spot-check (executed against the pre-removal functions at HEAD)

`B5_CORPUS` 15/15 and `B4_CORPUS` 13/13 expectations match the live functions — **zero mismatches**.
T-03's two measured claims also hold: under the live `test_kinds`, `select_control_candidate` returns
`.harness/tools/test_dir/gen.py`; under `CORPUS_BLIND_KINDS` it returns `None`. No red test on a
correct fix from any stated value.

Caveat on T-02's claim that B4_CORPUS "covers both halves of the removal": no input can distinguish
the conjunct's presence (it is tautological), so B4_CORPUS is verdict-preservation only. The
structural check is the sole reintroduction detector — correctly, and the plan says so.

## Open questions for the operator

- Q1 (blocking): does B-4's "Also the remaining grade-2 med code-grade record" mean
  `_literal_key_present` (cleared incidentally by T-02) or `suite_layout.py tracked_paths` (grade 2,
  in a file this feature declares read-only)? The BRIEF currently disclaims both.
- Q2 (non-blocking): confirm that recording remedy (a)'s residual risk is the Advisor's R2 call and
  not a stop-condition breach, and let D-02/D-03 cite it.

Read-only run: `plan.yaml` and `BRIEF.md` are unmodified.
