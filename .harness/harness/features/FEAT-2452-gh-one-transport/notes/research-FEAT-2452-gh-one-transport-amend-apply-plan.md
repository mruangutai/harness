# FEAT-2452 — amend-apply r-20261123-4 (signoff §2 OQ-1 → amend, C1)

**BLUF:** C1 is applied. The DEC-138 runner-clause row is now `amend`, successor `D-01`. T-05 owns DECISIONS.md and its index and carries the amendment after T-04. `plan-merge.py check` ends `5 task(s), 33 anchor(s) resolved, 0 failure(s)`, exit 0. `approval.status` is still `pending`, and no writer printed `APPROVAL-RESET:`. Base worktree HEAD 1e3f4a9e (uncommitted).

## What changed (plan.yaml through plan-merge verbs only)
- `decisions_affected` (`set-key`): row 1 (`DEC-138`, clause `each caller keeps its own\nrunner, because`, unchanged and verbatim in DEC-138's section) changed from `keep`/`none` to `amend`/`D-01`. Its reason is one line citing OQ-1 (b) and C1, the scope (gh_bin location/existence; each caller keeps its own runner) and delivery by T-05 after T-04. Before the write, a yaml-load comparison showed the other 10 rows were value-identical. The git diff touches only row 1. The best-effort DEC-138 keep row and the DEC-146 row are byte-unchanged.
- T-05 `files` (`amend --yaml-value`): adds `.harness/harness/docs/DECISIONS.md` (quote `Shared code, and migration scope.`, unique in the file) and `DECISIONS-INDEX.md` (quote `- DEC-138 @`, which survives regeneration). `depends_on: [T-04]` is untouched.
- T-05 `intent` (`amend`): lines 3, 5 and 6 are byte-identical to the old text (diff-checked). Line 1 adds DEC-205 to the consult list and says the task carries the one signed amendment. Line 2 now reads "do not widen DEC-138/146 beyond the DEC-138 amendment below". A new paragraph scopes the rewrite to the gh_bin and own-runner sentences, names factory_gh as the shared transport with failure policy kept at the caller, keeps the regression-guard sentence, the policy clauses and DEC-146 byte-unchanged, rewrites in place under DEC-205 (no dated sub-section) and regenerates the index. The final line now reads "No DEC amendment other than this DEC-138 one".
- T-05 `verify` (`amend`): all original lines are unchanged. Three lines are inserted before the final print. They locate the Shared-code paragraph inside DEC-138's section, then assert it names factory_gh, does not mention gh_bin or "keeps its own runner", and still carries the write-only regression guard. The first attempt used 8 lines, and check FAILed the 50-line machine-field budget (53). The compressed 3-line form passes. Discrimination was checked in memory against four inputs. The current DECISIONS.md fails it. A simulated amendment passes. A simulated amendment that drops the guard fails, and so does one that keeps gh_bin. `len(owned) == 29` is unaffected because `.harness/` paths are filtered out.
- BRIEF.md (direct edit) lines 41 and 49 now state the ruled outcome: one DEC-138 amendment, scoped as above and delivered by T-05 after T-04; the other governing decisions are kept. `## Approval` is untouched.

## Successor: D-01
D-01's choice ("Consolidate operator and library execution in factory_gh while keeping caller failure policy outside the transport") is exactly the replacement content, and it is a `decisions:` id of this plan, so check resolves it. No DEC supersedes the clause. No new decision was added.

## Deviation (reported, not worked around)
The dispatch named the receipt `notes/receipt-amend-apply-r-20261123-4.txt`. check-domain refuses that path for harness-pm, so the receipt is at `notes/receipt-harness-pm-amend-apply-r-20261123-4.md` instead. That path is pm-permitted, under notes/ and not /tmp, so C6 still holds. The value files are in /tmp/feat2452-r4/ because pm cannot write any other notes/ name. The receipt carries each value file in full, as cat'd beside the command.

## Open
- None blocking. The build-time DEC-138 rewrite and the index regeneration are T-05's work.
