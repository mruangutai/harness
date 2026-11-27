# Goal-check — FEAT-2489-plan-routes-split — validate c3 (r-20261124-10-validate-validator)

Pin `776909d2ab6cf9c4f5facc3f627d5839c52aa72a`, base `261fdf726428bd8325fbd3d4beccad23b67e83cc`, prior validate pin `25132b7e`. I read everything with `git show <pin>:…` or `git diff`. I re-ran no suite or receipt. My only executions were read-only comparisons: AST/source-segment comparisons, byte comparisons of BRIEF text, and `gh issue view`.

**BLUF: PASS.**
- All three perspectives pass, and SC-01 to SC-05 are met.
- SC-02's replaced item six is met against both gates of the ESC-2 ruling (Q1). I re-measured gate (ii) independently at the pin.
- Every perturbed-tree divergence on record is a census member that passes both gates. Under Q4 it is graded MET, with no escalation.
- The three BRIEF edits are byte-identical to the ruling's prescribed texts, and C5 still holds.
- C1 to C6 are met. C7 is partial, which is its literal status; it is ruled a distill item and does not gate this diff.
- No decision disposition is graded, because all four rows are `keep`.

## Claim checked: code unchanged since be0807b0

The claim is verified, not assumed:
- `git diff --name-only be0807b0 776909d2` lists only paths under this feature's directory.
- `rev-parse` gives the same tree ids at be0807b0, 25132b7e and 776909d2: bin `d542c641`, tests `3f8731cd` and `.github` `d15368eb`. `.github` is also the same tree at base.
- 25132b7e..776909d2 touches only BRIEF.md, feature notes, run records, backlog-issues.json and feature.json.

So earlier evidence over these trees carries over by identical subject. That is an evidence transfer, not a re-execution.

## BRIEF edits against the ruling's texts (byte comparison)

| Edit | Verdict | Evidence |
|---|---|---|
| Item six (BRIEF.md line 33) | verbatim | Line 33 == `"  " +` the ruling's first `> - ` blockquote (notes/answers-2026-11-24-validate-c1.md, Q1) → `True` |
| Verification-gaps item-six bullet | verbatim | It is the only line starting `- **Item six (per-file state):**` (line 66), and it equals the ruling's second blockquote (Q2) → `True` |
| `amended:` line in `## Approval` | verbatim, placed as ruled | It equals the ruling's fenced line (Q3), sits at line 107 and immediately follows `date: 2026-11-24` |
| Commit scope | clean | `git diff 25132b7e 776909d2 -- BRIEF.md` is the one replaced line plus the two inserted lines, nothing else |
| C5: item five unedited | holds | Line 32 is byte-equal at 9a308303 (signature), be0807b0, 25132b7e and 776909d2. `git log 9a308303..776909d2 -- BRIEF.md` shows only 778ea992 and 776909d2, and neither touches line 32 |

## Perspectives

| Perspective | Verdict | SCs | Evidence |
|---|---|---|---|
| operator | pass | SC-02 (with SC-01, SC-05) | **Items 1–5:** `equivalence-final.txt` has 9 PASS, `ALL PASS`, `exit=0` over head trees `d542c641`/`3f8731cd`, which are the pin's trees. **Item 6:** both gates hold (below). `.github` tree is identical at base and pin, so tests.yml is byte-identical. |
| code maintainer | pass | SC-01, SC-04, SC-05 | My AST re-measure (below): 164 top-level defs moved, all byte-identical except `T07_TERMINAL_REMEDIES`, with none left behind or lost. The code-reviewer c2 anchors stand over identical trees. |
| reader | pass | SC-03 | The c2 qa integration manifest (`runs/r-20261124-9-…/qa/manifest-integration.json`, tested_commit 25132b7e, runner_exit 0) has `tests/integration/test-check-plan-routes.py` returncode 0, over the pin's identical tests and bin trees. The red-t01, red-t03 and green-t01 receipts are unchanged. qa's c3 note was not yet written when I graded. |

## Success criteria

- **SC-01: met (inspection).**
  - Independent re-measure. I parsed `git show` of base `check-plan-routes.py` and of the pin's two modules and entry, then compared each top-level def/assign `ast.get_source_segment`:
    - 164 base names now live in the two modules, and only `T07_TERMINAL_REMEDIES` differs. That is the sanctioned key.
    - No moved name remains in the entry, no base name is lost, and the modules define no new names.
    - The entry's only changed def is `main`, which is AST-equal to base. The single added line is the C3 COUPLED comment at `check-plan-routes.py:932`.
  - Reviewer carrier: `review-harness-code-reviewer-c2.md`, "Other inspection anchors".
- **SC-02: met (inspection).**
  - *Items 1–5:* carried as at c2 by `equivalence-final.txt` over identical trees. The clean state passes all six argv shapes. The clean canonical output differs only by 101→103 (item 4). The perturbed canonical output differs only by the relocated `_classification_document` locator (item 5) and the count (item 4), and perturbed consolidation is identical.
  - *Item 6, gate (i): the real tree at the pin is base-equal apart from items 1–5. MET.*
    - The "tree this feature ships" is exactly equivalence-final's HEAD tree: the base commit with only the pin's bin and tests overlaid.
    - On that tree all 6 clean argv shapes match on exit, stdout and stderr, apart from items 4 and 5.
    - The census "Current-tree impact ledger" (`per-file-state-census.md`, §1 and §5) finds no member changing any real-tree finding, exit or stderr.
    - The qa-c2-cr3-probe pristine controls reproduce canonical 0/0 (101/103) and consolidation 0/0.
  - *Item 6, gate (ii): the mechanism is per-file state of verbatim-moved rules, or per-file compile/import. MET.*
    - I re-measured it at the pin, as in SC-01. `_ReaderAliasCollector`, `reader_candidates_from_source` and `_scan_reader_tree` (canonical_reader_audit.py) are byte-identical to base, as are `consolidation_findings` and `_broad_catch_count` (structure_audit.py).
    - So no rule changed behaviour. Each divergence comes only from the rule's per-file scope meeting the new layout.
  - *Divergences on record, each checked against both gates:*
    - P1 (canonical 2→0) and P2 (0→2): census A.2, alias map.
    - P4 (exits 1/1, +4 traceback lines): census B.11, eager import.
    - Seam (a), broad-catch straddle with k=2, and the reviewer's measured k=3: census C.20.
    - Seam (b)/(b2), reader parse scope: census A.1.
    - Consolidation-mode parse scope (my c2 note): census C.15.
    - All are census members, and none fails either gate. Under ruling Q4 each is graded MET, with no escalation or re-sign. None is absent from the census, so no census extension is needed.
  - *Scope:* I can grade only the divergences on record. Any NEW member the c3 readers report (qa and code had not yet written their notes) falls under the same Q4 test for the lead. It is sanctioned iff the census or a note places it, gate (i) evidence is unchanged, and the rule's source segment is base-identical. Everything that test needs is measured above.
- **SC-03: met (automated, integration).** See the reader row. The tests tree is identical, so the c2 manifest transfers. qa's c3 manifest is the declared carrier for this run, and was not out when I graded.
- **SC-04: met (inspection).**
  - It carries over by the identical tests tree. Anchors are at `test-check-plan-routes.py:2326`, `test-broad-catch-census.py:203` and the others listed in reviewer c1/c2.
  - All five test files returned 0 in the c2 manifests.
- **SC-05: met (inspection).** It carries over by the identical tree (`canonical_reader_audit.py:62` re-key; `plan_merge/check.py:198`). The only moved-def difference is the T07 key (SC-01 re-measure).

## Signoff conditions (notes/answers-2026-11-24-signoff.md)

| Cond | Verdict | Evidence |
|---|---|---|
| C1 | met | `split-equivalence.py` is unchanged 25132b7e..pin, so it keeps its c2-graded byte-exact form. The ruling adds no sample and no widening, and the item-six text restates "(C1)". |
| C2 | met | `equivalence-final.txt` is unchanged since 6b483a2c, and its MAP is derived from moved names. `verify-c1-T-04.txt` is a PASS. |
| C3 | met | COUPLED comment at `check-plan-routes.py:932` names `canonical_reader_audit._run_canonical_reader_audit`. `.github` tree is identical at base and pin. |
| C4 | met | Case 19b's copy list carries both modules (`test-check-plan-routes.py:448–450`). The import-failure disclosure (BRIEF line 61) is unchanged. |
| C5 | met | Item five is byte-identical since the signature (table above). The ruling's replacement is signer-side and touches item six only. |
| C6 | met | #2525 is OPEN (record-panel readers replaced wholesale, and reason serialized as 'none'), and it is recorded in backlog-issues.json. |
| C7 | partial (literal); ruled a distill item, not this diff's gate | The exit-7 item is logged (`observations/harness-pm.md`, 4th bullet). The record-panel observation is still absent: `grep -ci record-panel` = 0 at the pin. Distill has not run. |

The ruled backlog items are all filed: #2526 (SEC-1), #2527 (sign-approval amendment marks) and #2528 (reviewer write-guard and QA measurement-only verdict) are all OPEN and recorded in backlog-issues.json. #2519 is OPEN, as ruled, and closes via the PR.

## Decision dispositions

None to grade. At the pin, `decisions_affected` is DEC-174 ×2, DEC-183 and DEC-179, all `keep`. `git diff --name-only base pin` has no `.harness/harness/docs` path, so DECISIONS.md is unchanged.

## Findings

None of these is a product defect, and no task owns BRIEF.md (it is signer-owned).
- **G-1 (form, info, task: none).** BRIEF item six cites "replaced at validate c2 ESC-2 … and the ESC-2 ruling note" without a filename. The note resolves only through its own header line ("the ESC-2 ruling note cited by BRIEF SC-02 item six"). *Failure scenario:* a reader searching for the filename does not find the ruling from the BRIEF. This is mitigated by the header and commit 776909d2. It is ruled naming drift (Q5), so edit nothing. It is the ruling's own prescribed text, recorded here only.

## Open questions

- OQ-1 (non-blocking, Main): C7's record-panel observation is still not in the pm feature log. Route it before distill, as the ruling directs (Q5).

## Principles applied

- harness-principles rule 7 (verification is the product): I re-measured gate (ii) and SC-01 from source at the pin rather than transferring the reviewer's reading alone.
- harness-principles rule 15 (never falsify the record): C7 is graded at its literal partial status, and SC-03's carrier is named as an evidence transfer, not a c3 run.
