# Goal-check — BUG-2451 validate c1 (harness-pm)

**BLUF: PASS. Both perspectives are discharged at review_sha b2c1f55e. SC-01..SC-04 are met, the DEC-238 amendment (D-01) landed exactly, and all five keep rows are untouched and honoured. There are no must-fix findings and three advisories.**

Pin: b2c1f55e89bc20a9ef397cb183452270548aa3ee. Every read below is `git show b2c1f55e:<path>`, from the feature worktree. The control-plane copy was not read. `git diff --stat e83c4e20 b2c1f55e` shows T-01's five files plus the feature directory and nothing else. The only DECISIONS.md hunk in that diff falls inside DEC-238, at lines 8152-8162. Product docs/spec.md, docs/decisions.md and docs/architecture.md are absent, as the BRIEF records; that is not a finding.

## Perspectives

| Perspective | Grade | Carried by | Evidence |
|---|---|---|---|
| operator | pass | SC-02, SC-03 | Both refusals fire before mutation in both modes and name every offender (test lines 270-313). The pruner's unreadable walk returns only error paths (`_unreadable_dirs`, `_unreadable_records`). The ship paragraph and the DEC-238 bullet equal their 5e51124e text plus the single refusal sentence, and neither carries a staging claim. |
| code maintainer | pass | SC-01, SC-04 | The regression reddens against the 47d6c54d pruner on assertions and greens at the pin. The staging implementation and every staging assertion are gone. Coverage for retention, refusals and symlinks is kept, and the CLI is unchanged. |

## Success criteria

- **SC-01 met (automated).** I ran the test at a `git archive b2c1f55e` with HARNESS_AGENT_TYPE, CLAUDE_PROJECT_DIR and HARNESS_PROJECT_DIR cleared. Result: rc 0, 46 PASS, 0 FAIL, 0 SKIP, `all checks passed`, and all three T-01 verify lines present.
  - I re-ran the same test with PRUNE_RUN_EVIDENCE_BIN set to the 47d6c54d pruner. Result: rc 1, `5 failure(s)`. The failures were the dry-run and prune staging-output checks, `prune starts no subprocess`, `pruner invokes no git subprocess`, and `complete cycle evidence … leaves the index alone`. All are assertions, and they match notes/red-first-T-01.md RED 2.
  - The audit hook is at test lines 65-84. Index bytes are compared in real repositories with an unrelated pre-staged change, at lines 213-255.
  - At the pin, `gen-decisions-index.py --stdout` equals DECISIONS-INDEX.md.
  - This is pm-observed corroboration. qa's fail_first receipt (notes/review-harness-qa-c1.md) had not landed when I wrote this note.
- **SC-02 met (automated).** `evidence_refused` (lines 270-276) runs prune and dry-run with two missing paths and checks exit 2, that every path is named, that the tree is byte-identical and that the index is byte-identical. `unreadable_checks` (lines 306-313) runs both modes with two unreadable dirs and checks exit 1, that every dir is named, that the index is unchanged and that the prunable ui/ is unchanged. In the pruner, `_unreadable_dirs` collects no file paths. `main` returns 1 before `_prune`.
- **SC-03 met (inspection).**
  - DECISIONS.md lines 8152-8162: with whitespace normalised, the bullet minus the one sentence equals the 5e51124e bullet. The sentence occurs exactly once. The bullet has no force/stag/`git add`/ignored claim, and the whole DEC-238 entry has none either.
  - harness-ship.md lines 47-56, with the sentence at lines 51-53: the entire file minus the sentence equals the 5e51124e file after normalisation.
  - Pruner docstring lines 18-29: it describes deletion only, says "never runs git or touches the index", and names both refusals as "dry-run included".
  - Index: the DEC-238 row (line 232, @8140) is unchanged. Later anchors shift by -2, and the regeneration matches.
- **SC-04 met (inspection).**
  - The argparse block (pruner lines 97-103) has no diff.
  - The removed test lines are only staging cases: `staged_runs`, `staging_*`, `expected_staged`, `symlink_staging`, the stage-asserting halves of the evidence and unreadable checks, and the `.gitignore runs/**` fixture.
  - Keep-selection, BUG-2294 record-bytes, `--keep`, review-pin/placeholder/empty/duplicate-key refusals, FEAT-2229 and symlink cases all remain (lines 150-185, 347-486).
  - In harness-ship.md, Terminus (line 36) comes before the prune step (line 38), which comes before both invocations (lines 43-44) and the paragraph. The commit name is preserved at line 55.

## Decision dispositions (DECISIONS.md at b2c1f55e)

| Row | Verdict | Evidence |
|---|---|---|
| DEC-238 amend (D-01) | met | The `**Ship keeps the record and drops the rest.**` bullet (lines 8152-8162) is the 5e51124e text plus exactly one sentence naming both refusals: the exit 2 missing cycle_evidence refusal and the exit 1 unreadable-directory refusal. The index matches. Owning task: T-01. |
| DEC-174 keep | met | The heading at line 4479 is untouched; the only DECISIONS.md hunk is inside DEC-238. Main built T-01 directly with no hosted dev (plan T-01 execution_mode). |
| DEC-179 keep | met | The heading at line 4844 is untouched. All five paths were declared as main-session-direct lanes before signature (plan `lanes:` resolved at 47d6c54d). |
| DEC-225 keep | met, with an advisory | The heading at line 7502 is untouched, and the `with no panel and no goal-check run` clause is at line 7511. Intake held to it: no panel, one task (plan `adequacy_notes`). See A-1. |
| DEC-254 keep | met | The heading at line 8419 is untouched. The plan carries five-field rows, and a single owner (T-01) holds the amendment. |
| DEC-257 keep | met | The heading at line 8661 is untouched. The pruner now relies on tracked records and runs no git. |

## Advisories (none must-fix; all T-01)

- **A-1 (substance, advisory).** DEC-225 conflicts with this run in two places:
  - Its text says the patch lane drops "a goal-check on a document" (line ~7532). Its validate gates are "qa's fail_first evidence and the batched readers over one review_sha" (line 7512).
  - Its text says T-01 runs `execution_mode: team` (line 7510), but T-01 runs main-session-direct.

  Read as an intake rule, the clause is honoured. This validate goal-check reads the diff, not a document. It is hosted by teams/validate.yaml step `goalcheck` and required by DEC-254's "pm grades amend/strike landing at review_sha". The team-to-direct override is DEC-174's, as the keep row's reason declares. The tension lies in DEC-225's wording, not in the work. Failure scenario: a later reader cites DEC-225 to argue that patch features must skip the validate goal-check, which would silently drop DEC-254's disposition grading.
- **A-2 (form, advisory).** The dry-run half of "index byte-identical" cannot discriminate against 47d6c54d, because that pruner's dry-run never staged either. RED for index mutation comes from normal mode only, through the audit hook and `evidence_complete`. This is truthful but worth knowing.
- **A-3 (substance, advisory).** Every hooked no-git test passes `--root`, but the ship invocations (harness-ship.md lines 43-44) omit it. Without `--root`, root resolution goes through `harness_boundary.root_above`, and by my reading (harness_boundary.py root_above) that function is pure os.path. So that entry path is covered by my inspection only; no test executes it. Failure scenario: a future change adds a git call to default root resolution, and no test reddens.

## Principles applied

- harness-pm P-05 / P-06: each SC was graded from evidence that discriminates its clauses, and I re-measured RED myself rather than citing the builder's note.
- harness-pm P-19 / G-22: I probed one boundary beyond the hooked test, the `--root`-less entry path. That is A-3.
