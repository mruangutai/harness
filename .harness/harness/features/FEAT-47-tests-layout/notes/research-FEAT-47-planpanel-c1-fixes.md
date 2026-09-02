# FEAT-47 — plan-panel cycle 1 fixes

**BLUF.** All three `must_fix` findings are closed and both non-gating findings are answered. The
critical one is closed by changing what the sweep asserts rather than where it looks: REQ-07's
instrument is now a **declared line-exemption census** (`suite-census.py residue`, D-16), not a
widened pathspec, so the two sentences the plan mandates preserving are excused **by sentence** while
every other live mention — including the two Expertise entries — stays inside it. The Expertise
entries are repaired by a new **T-07**, main-session-direct (D-17). A fourth instance of the same
defect class, which neither panel half caught, was found while proving this and is fixed: **T-05
step 7 instructed a live test file to assert `UNIT_SCRIPTS`/`INTEGRATION_SCRIPTS` by name**, which
would have reddened T-06's sweep from inside `tests/integration/`.

`python3 .claude/skills/harness/bin/check-plan-routes.py <plan>` → **0 violation(s) across 1
plan(s), exit 0.** Two `DEVIATION` lines (T-06 docs, T-07 expertise), both the expected DEC-174/
granted-path shape that exits 0. Task machine-field budgets: T-05 exactly 50/50, T-07 24, all ok.

## Dispositions by id

| id | disposition | where |
|---|---|---|
| `F-01` critical | **resolved** — instrument replaced, not pathspec widened | D-16, T-05 step 9 `residue`, T-06 verify + intent step 3 |
| `F-02` high | **resolved** — real task, correct ownership | D-17, **T-07** |
| `F-03` med | **resolved as a repair, not an exemption** | T-02 intent, "ONE COMMENT REPAIR INSIDE THE MOVED SET" |
| indep. reader — SC-05 sweep base rate zero | **dismissed with reasons**, honesty clause added | BRIEF gaps, SC-05 bullet |
| indep. reader — `suite-census.py` shelf life | **resolved** — shelf life moved into the interface | D-18, T-05 step 9, BRIEF gaps |
| `Q1` (widen vs reword) | **answered: neither.** Exempt the sentence | D-16 `because:` |
| `Q2` (Expertise repaired here?) | **answered: yes, here, by T-07** | D-17 |

## Why the exemption is per-SENTENCE, and how F-01 and F-02 hold together

The three tokens sit in two kinds of place and no pathspec separates them. A widened exclusion
(`.harness/harness/**`) covers `DECISIONS.md`'s *What forced it* **and** the two Expertise files at
once — green gate, falsified craft still injected at every spawn. So the exclusion unit is a
`(path, literal fragment)` pair naming one sentence. Three consequences, and the third is the one
that makes the fail-open branch unreachable rather than merely unused:

1. Every **future** line of `DECISIONS.md` and of the moved probe stays inside the sweep.
2. A pair that stops matching is **red** — repairing a preserved sentence later forces its pair out
   instead of leaving cover behind.
3. The mode **refuses its own list** if any exempted path lies under an expertise directory. Nobody
   later can buy silence for an Expertise entry by adding a pair.

Rejected, recorded so it is not re-suggested: paraphrasing the two sentences. "Eight of twelve
`INTEGRATION_SCRIPTS` entries" names the artifact that existed and can be checked against the commit
it describes; "the forking-side script array" cannot.

## Demonstrated, not asserted

A prototype of the mode (`/tmp/feat47-residue/residue_proto.py`) was run against a synthetic
post-plan git tree carrying exactly the residue this plan leaves. **Case A: exit 0**, both in
working-tree and `--ref HEAD` mode, printing the three excused lines. Six discrimination cases, all
**exit 1**:

- `B` eng-lead Expertise left un-repaired → reported by path and line
- `C` `test-factory-integration.py` comment left un-repaired
- `D` T-05 step 7's struck mirror-negative reinstated in a live test
- `E` stale exemption (probe sentence reworded away)
- `F` **an expertise path added to the exemption list** → refused before anything is scanned
- `G` positive control empty at the ref

T-07's own verify was run for real: **red** on the current tree, naming all three offending lines
(`harness-eng-lead.md:9,10`, `harness-code-reviewer.md:7`); **green** on a repaired pair of files
built in `/tmp/feat47-t07/`, with `check-expertise.sh` also `OK` on both.

**A cap discovered while doing that, now written into T-07:** `check-expertise.sh` caps a single
entry at **50 words**, not just the file at 40 lines. A first draft of the G-04 replacement came in
at 51 and failed with `G-04 is 51 words — cap is 50; a rule, not a story`.

## The fourth instance (new, unfiled by either panel half)

T-05 step 7 said to replace `test-check-plan-routes.py`'s `case_13` with an assertion that
`run-unit-tests.sh` "contains neither `UNIT_SCRIPTS` nor `INTEGRATION_SCRIPTS`". That file lands in
`tests/integration/`, which is not a record prefix, so the assertion is itself a live file naming the
deleted mechanism: the task would have broken the next task's gate in order to assert something. The
negative clause is struck; only the positive glob property remains, and the reason is D-02's own —
the arrays' absence has exactly one reader, and a second copy of it in a test file is the
two-readers duplication this feature exists to delete.

## Honest limits

- The `residue` mode does not exist yet; the proof above is of a prototype of the specified
  behaviour against a synthetic tree, not of shipped code. Same standing as every other T-05 claim.
- The exemption is per **line**. `DECISIONS.md`'s present-tense "The fix IS to name each file" sits
  on a different line from "Eight of twelve" and carries no token, so the sweep never sees it — its
  past-tensing is mandated by T-06's intent, and only by that. Stated rather than implied.
- Nothing here re-checks the FEAT-48 coupling. The lead's `adequacy_notes` are right that it must be
  re-checked at FEAT-47's build start; this pass did not touch it.

## Untouched on purpose

The census work, the `-ge 37` / `-ge 20` floors, T-02's rename provenance, and the `F-01`/`F-07`/
`G-01` repairs from prior passes. No id renumbered; `D-09`–`D-12` and the old `T-07`–`T-09` gap
stays a gap (D-13). `## Approval` and `approval:` remain unsigned.
