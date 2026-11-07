# BRIEF — FEAT-71 Corpus independence

## Problem

Harness cannot prune its prior feature records without breaking gates and tests: executable exemptions, live-corpus fixtures, probe locations and document anchors depend on specific historical folders. Linked worktrees hide some failures by reading the main checkout, so worktree green does not establish independence (binding grilling, observed at c4e8bbc8).

## Done when — by perspective

**operator** — I can retain only this intake and the four recent Harness features, remove old project records, and obtain complete green merge evidence from an independent checkout without masking failures.

**code maintainer** — I can exercise the same contracts with synthetic fixtures instead of historical feature data, retain the useful accessor reproduction, and follow surviving documentation without deleted-folder pointers.

## Success criteria

- SC-01 (operator): At the committed review_sha, .harness/harness/features/ contains exactly FEAT-71-corpus-independence, BUG-2161-abandon-source-tickets, BUG-2141-dec174-main-orchestrator, FEAT-2037-product-document-guidance and BUG-20261006-fleet-planning-recovery. Review git show <review_sha>:<path> and the committed tree listing, not the linked working-tree corpus.
  verify: inspection
- SC-02 (code maintainer): Synthetic unit fixtures replace executable historical-id exemptions and the test-plan-depends-on.py corpus-size floor; affected assertions demonstrate fail-first against the pinned baseline and pass after the removal/refactor. Cover RUNS_AGENT_EXEMPT, BUILD_ENTRY_ERA_EXEMPT, HANDOFF_EXEMPT_LITERAL, both handoff_done_when_baseline configurations, and unit real-feature fixtures/live reads without depending on live corpus size.
  verify: automated evidence: unit
- SC-03 (code maintainer): Integration fixtures exercise corpus discovery, existing-flow, canonical-reader classification and conversion/non-regression contracts without real prior feature data or live-corpus reads; new independence assertions fail first for the identified baseline dependencies and pass on the retained five-folder corpus. Replace the test-corpus-real-owner.py corpus-size floor with synthetic non-vacuity that is asserted, not skipped.
  verify: automated evidence: integration
- SC-04 (code maintainer): At review_sha, git show <review_sha>:<path> establishes deletion of the BUG-1898 and FEAT-1928 probes and their test kinds, removal of only DEC-204's obsolete merge-gate sentence, and preservation of the FEAT-44 accessor probe plus README reproduction under tests/manual/. The suite_layout.py exception is removed and DECISIONS repointed. The FEAT-23 source-prompts pointer is dropped and the harness/harness-verification-rules examples use placeholders.
  verify: inspection
- SC-05 (operator): At review_sha, git show <review_sha>:<path> and the committed deletion list establish removal of .harness/logs/*.md and project .harness/notes/* dated before 2026-10-08, including the specifically authorized edited/untracked records. Newer records, DECISIONS, SPEC, BUILD, docs/, .harness/README.md and expertise change only paths/line anchors into deleted folders, apart from the explicitly authorized probe edits. DECISIONS-INDEX is regenerated. No .harness/kaya/ change or decision-semantics change is included.
  verify: inspection

## Verification gaps

No SC rests on a null or excluded runner. Unit and integration runners are active. The retained OMP accessor reproduction requires the existing credentialled live environment; relocation does not claim a fresh live run or change its contract. TypeScript typecheck remains an existing null/unresolved runner: SC-04 inspection carries byte-preserving probe relocation, not proof of live OMP behavior. No browser/component surface changes. Repository-wide merge gates are terminal task verification, not feature SCs: all five named gates must pass in a standalone canonical-path clone, including the full --kind all suite; the known /tmp symlink failure is not waived.

## Constraints

- Binding scope: /Users/molchairuangutai/GitHub/harness/.harness/notes/grilling-corpus-independence-2026-11-07.md (Settled, Facts, Out of scope); its recent record is read-only. Retain this new intake in addition to the four survivors settled by notes/answers-2026-11-07-02-product.md.
- DEC-174 BLOCKS spawned enforcement implementation: main session is orchestrator and builds directly, never harness-eng-lead. DEC-179 SUPPLIES declared routing for every touched surface.
- DEC-225 and DEC-228 SUPPLY the signed patch lane: at most 120 brief lines, exactly one task, no panel or goal-check. Escalate if the diff becomes unbounded or introduces a public interface.
- DEC-182 and DEC-232 SUPPLY controlled plan merging and resolvable anchors. Approval remains pending until the operator signs through main.
- DEC-204's lifecycle semantics remain unchanged; only the obsolete BUG-1898 merge-gate sentence is removed. DEC-213 SUPPLIES tests/manual placement and suite layout enforcement.
- Tests first where behavior changes; preserve pinned baseline, named failing assertions, commands, exits, stdout/stderr and final green receipts. Do not rerun the binding inventory simply to rediscover it.

## Out of scope

- .harness/kaya/ — the operator asked about Harness's own corpus only.
- Bare feature ids in comments, docstrings, test labels and decision rationale — provenance, not dependency.
- Any change to what a decision decides — DECISIONS edits are limited to the probe sentence, the FEAT-44 pointer, and path/anchor rewrites.

## Approval

status: approved
approved-by: Mike Ruangutai
date: 2026-11-07
