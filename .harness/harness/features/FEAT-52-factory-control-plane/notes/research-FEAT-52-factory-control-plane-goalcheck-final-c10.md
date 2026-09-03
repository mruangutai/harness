# Goal-check — FEAT-52 factory-control-plane — final, at `review_sha 49df4bee`

## BLUF

**FAIL — do not ship yet.** Twelve of fifteen signed criteria are met with named, re-verified
carriers. Three are not, and two of the three are new since the reviews that passed this feature:

1. **A committed integration test is RED at the pin.** `test-gen-decisions-index.py` exits 1 on
   `test_committed_index_matches_a_fresh_regeneration`: FEAT-52's own index row reads
   `DEC-213 @6563` while the generator produces `@6647` (heading at
   `.harness/harness/docs/DECISIONS.md:6647`). T-13's signed `verify:` clause
   (`gen-decisions-index.py --stdout | diff - DECISIONS-INDEX.md && test-gen-decisions-index.py`)
   is therefore also red at the pin. Reproduced twice in the worktree with a clean tracked tree.
2. **The decision number collides with `origin/main`.** The branch is **11 commits behind** main,
   which already carries `## DEC-213 — Harness's own tests live under tests/**` at
   `DECISIONS.md:6645` (and `DEC-197`'s row refs it). FEAT-52 renumbered its own entry 212 -> 213
   against a stale main, so a merge produces two `## DEC-213` headings. Only two files cite it
   (`DECISIONS.md`, `DECISIONS-INDEX.md`) — a small fix, but it must happen before the merge.
3. **SC-06's discriminating assertion was deleted by a quality-pass commit.**
   `9dbc19f4 [harness:review] split instruction path test runner` dropped the `product_cwd`
   fixture and the `not os.path.exists(<product_cwd>/.agents/skills/harness-systematic-debugging/SKILL.md)`
   half. What survives (`test-check-instruction-paths.py:64`) is `os.path.isfile(debug_path)` only —
   and that passes on the **pre-change spelling** too: with the placeholder stripped, `debug_path`
   is the relative `.agents/skills/harness-systematic-debugging/SKILL.md`, which exists relative to
   the suite's cwd (the harness checkout). SC-06's own text: "the second half is what makes the
   first discriminating." Grade taken at the pin was correct at `ff4ca877`; the remediation commit
   falsified it.

Issue **#1260** (validator host-metadata defect) is confirmed out of scope: it is not reachable
from any REQ or SC here, and no criterion above turns on it.

## Criterion verdicts

| SC | Verdict | Method | Evidence at `49df4bee` |
|---|---|---|---|
| SC-01 | met | automated/unit | `test-inject-expertise.py:180 case4b` — hook run with `cwd=product_cwd`, asserts `injected == root and injected != product_cwd` |
| SC-02 | met | automated/unit | `case4c:199` (UNRESOLVED + `VERDICT: BLOCKED`, exit 0) and `case14:388` (zero `exit [1-9]` + positive control) |
| SC-03 | met | automated/unit | `test-check-instruction-paths.py:59` — five separate `scope contains <S1..S5>` checks |
| SC-04 | met | automated/unit | `HARNESS_REVIEW_SHA=49df4bee test-anchor-directions.py` exit 0 — five per-site rows + `reviewed-sha whole scope`; checker `scanned 62 file(s), 0 violation(s)` |
| SC-05 | met | automated/unit | `test-check-instruction-paths.py:40` — inline `:1:`, fenced `:3:`, `2 violation(s)`, exit 1 |
| **SC-06** | **not_met** | automated/unit | `test-check-instruction-paths.py:64` — sole surviving assertion is non-discriminating (see BLUF 3); no cwd is set anywhere in the file |
| SC-07 | met | inspection | `.harness/team-config.yaml` zero-line diff `06bd60c8..49df4bee`; the 16 `.omp/agents/*.md` diffs only re-anchor existing writable claims — no new path, no `tools:` change |
| SC-08 | met | automated/unit | `case_workflow_gate:68-74` — real `tests.yml` plus the two mandated mutants (step renamed, `exit "$rc"` -> `exit 0`), both asserted false |
| **SC-09** | **partial** | inspection | Contract present: `harness-handoff/SKILL.md:62-66` (both placeholders, resolver command, read-only). Entry present: `DECISIONS.md:6647`. **Index row stale (`@6563`) and the number collides with main** — BLUF 1 and 2 |
| SC-10 | met | automated/integration | `test-inflight-registry.py:1043 case_35_feature_root_cli` + `:1033 _ambiguous_feature_root_case` — exit 0, 126 ok |
| SC-11 | met | automated/unit | `test-anchor-directions.py` row `SC-11 S2 write observations` at the reviewed sha; RED fixtures at `test-check-instruction-paths.py:45` (both mis-anchor directions) |
| **SC-12** | **partial** | automated/unit | `case4d:218` asserts `HARNESS_PATH_DRIFT: none` and `1 unanchored path(s)` but never the `<file>:<line>` detail line the criterion names — carried unaddressed since remediation-c9 F3 |
| SC-13 | met | automated/integration | `test-dispatch-guard.py:461 case_17` — six sub-checks covering REFUSED / ALLOWED / bash-persona discrimination / MISMATCH; exit 0, 48 ok |
| SC-14 | met | inspection | Four per-file findings: `harness-product-lead.md:92`, `harness-eng-lead.md:110`, `harness-validator-lead.md:138` (each: no shell, dispatch-line anchor, `VERDICT: BLOCKED` if absent), `harness-orchestrator.md:146` (emit duty), plus `harness-handoff/SKILL.md:66` |
| SC-15 | met | automated/integration | `test-check-domain.py` `SC-15 PAIR` — exit 0, 275 ok |

Suites run by me at the pin (tracked tree clean, `HARNESS_AGENT_TYPE` unset):
`test-dispatch-guard.py` 48 ok, `test-inflight-registry.py` 126 ok, `test-check-domain.py` 275 ok,
`test-inject-expertise.py` 21 ok, `test-check-instruction-paths.py` 16 ok, `test-anchor-directions.py`
7 ok — all exit 0. `test-gen-decisions-index.py` **exit 1**, one FAIL, cause is FEAT-52's own row.

## REQ coverage

REQ-01 -> T-03/T-14 (`inject-expertise.sh` control-plane block). REQ-02 -> T-04..T-08, T-10, T-11
(the five canonical sites re-anchored; whole-scope checker clean) — **its family-5 half is the one
whose proof SC-06 lost.** REQ-03 -> SC-07 evidence (no grant widened). REQ-04 -> T-02, T-12
(`check-instruction-paths.py` + the enforced `integration` step). REQ-05 -> `case4c`. REQ-06 ->
T-01, T-09, T-15 (`feature-root` verb, `dispatch-guard.sh:171-183`, anchor-direction rows). Nothing
in the brief is unimplemented; the gaps are evidence and record gaps, not missing product.

## Recommended next ship action — one short remediation cycle, then ship

Not a re-plan and not a full re-review. Four edits, all small, all inside already-approved tasks:

1. Merge/rebase `origin/main` (11 commits) into the branch, renumber FEAT-52's decision to the next
   free number, then regenerate with `gen-decisions-index.py` — never hand-edit the row (the anchor
   is generator-derived; a hand-carried `@line` is exactly what rotted here).
2. Restore SC-06's deleted half in `test-check-instruction-paths.py` — the `product_cwd` fixture and
   the placeholder-stripped `not os.path.exists(...)` assertion — and keep the split shape that
   satisfied `code-grade.py`.
3. Add the `<file>:<line>` assertion to `test-inject-expertise.py::case4d` (SC-12).
4. Re-run the six feature suites **plus** `test-gen-decisions-index.py`, re-pin `review_sha`, and
   re-take SC-06, SC-09, SC-12 only.

Advisory, not gating and not covered by any SC: T-09's post-amendment fifth case
("AMBIGUITY REFUSED") was never written into `test-dispatch-guard.py`, and T-09's intent header
still says "FOUR NEW CASES" while listing five bullets. The guard code itself is correct on
inspection and the practical surface is closed upstream by the resolver's loud refusal
(`_ambiguous_feature_root_case`); worth folding into the same cycle as item 3.

## Open questions

- Q1 (blocking, operator): the record-integrity route for the DEC collision — renumber FEAT-52's
  entry to the next free number after merging main (my recommendation, and the only option that
  leaves main's `DEC-213` and `DEC-197`'s ref intact), or something else? Renumbering a signed
  decision is not a pm write.
- Q2 (non-blocking, harness owner): a `[harness:review]` quality-pass commit silently deleted a
  test assertion a signed criterion names, after that criterion had been graded met. Nothing in the
  simplify/review path re-takes criterion grades against the post-simplification tree — the
  falsification is invisible by construction.
- Q3 (non-blocking, harness owner): nothing gates `DECISIONS-INDEX.md` regeneration in CI or in
  `check-state.sh`; the only gate is one feature task's own `verify:` clause, so index rot ships
  whenever no live plan happens to carry that clause.
