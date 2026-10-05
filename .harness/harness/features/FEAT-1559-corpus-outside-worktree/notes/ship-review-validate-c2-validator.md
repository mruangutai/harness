# FEAT-1559: Corpus outside the worktree — ship review

**Ready to ship.** Validate passes at `review_sha` `6c11ab626ed568236978b1640928162b8cf0139f`
with no must-fix: all five readers pass (qa, code, security, ui, goal-check). After this lands,
a feature worktree holds only its own feature directory; every other feature is read from the main
checkout. The remaining gap is the one you deferred: converting today's standing worktrees, which
runs after merge under #2101.

It took 3 validate passes and 2 fix rounds, the full rework allowance (2 rounds, 120 min; 38 min
used). Each fix round closed a real gate gap, not cosmetic findings.

No report round was spawned. This briefing is assembled from these digests:

- `runs/plan-product/digest.md`
- `runs/validate-validator/digest.md`
- `runs/validate-c1-validator/digest.md`
- `runs/validate-c2-validator/digest.md`

It also draws on the readers' `notes/*-c3.md` reports and the goal-check at
`notes/research-FEAT-1559-corpus-outside-worktree-goalcheck-validate-c3.md`.

`runs/` is gitignored, and every run directory except the last was pruned before the PR. The
durable record of each failing cycle is therefore its reader notes (`notes/*-c1.md`,
`notes/*-c2.md`) and the fix receipt that answers its must-fix list
(`notes/receipt-main-session-fix-c1.md` and `notes/receipt-main-session-fix-c2.md`).

## Definition of done, graded (validate c3 goal-check)

| Perspective | As signed | Verdict | SCs that discharged it | Evidence |
|---|---|---|---|---|
| operator | Create or keep a record-bearing checkout without materialising other features, by any creation route. Landed records stay readable and unaltered, clean checkouts converge without losing dirty work, and clones and CI behave as before. | **partial** | SC-01, SC-06, SC-11 met; SC-10 deferred by your ruling | `receipt-T-04.md`; `non-regression-receipt.md`; #2101 for the conversion |
| reader | Read landed precedent on disk and trust that an audit examines its declared subject, not a silently smaller set. Duplicate branch claims stay detectable from a sparse checkout. | **met** | SC-02, SC-03, SC-04, SC-05, SC-12, SC-14 | `test-feature-corpus.py`; `receipt-main-session-fix-c1.md`; `receipt-main-session-fix-c2.md` |
| code maintainer | One deterministic, idempotent state command with explicit failure reasons, enforced at checkout, merge, rebase and gate boundaries. | **partial** | SC-07, SC-08, SC-09 met; SC-13 partial | `test-worktree-state*.py`; `suite-baseline.md` |

**Why the two partials.**

- **Operator: SC-10 (the conversion pass) is deferred.** It is deferred, not missing: you moved it
  after merge (#2101). Converting other sessions' worktrees now would leave them sparse while
  their tools are still pre-1559.
- **Maintainer: SC-13 is partial on historical evidence only.** Every predicate is shown to
  discriminate today, by mutants. Not every predicate has a recorded red from before its
  production code existed. That cannot be produced retroactively.

## What was built

| Task | What it delivered |
|---|---|
| T-01 | `feature_corpus.py` (population, cone and identity) and `worktree-state.py` (verify and repair, exits 3/4/7/8). Repair runs only on classes A and B; dirty work (class C) is always refused. |
| T-02 | check-state verifies the layout before any invariant and audits the full landed population. Dirty work is reported without gating. |
| T-03 | merge-gate, branch-create-gate, the board audit, plan routes, decision anchors and skill references all read the main corpus. A missing landed directory refuses by name. |
| T-04 | Tracked `post-checkout`, `post-merge` and `post-rewrite` hooks run the repair, so layout is converged at the boundary rather than by instruction. |
| T-05 | Regression locks, a one-time non-regression receipt, DEC-214 amended (landed reads anchor at the control plane) and the operator guidance. |
| T-06 | Abandoned here by your ruling; carried unchanged in #2101. |

## How validation went

1. **c1 at `0e8301a5`: FAIL, six must-fix.**
   - Plan-route discovery walked whatever was on disk, so a missing landed directory meant a
     silently smaller audit.
   - The board audit's and the decision anchors' cut-over to the main corpus had no
     behaviour test.
   - Nine functions were below the grade bar.

   All six were fixed in the main session (`receipt-main-session-fix-c1.md`), each with red or
   mutant proof. The host refused that lead's final return, so the run is closed BLOCKED with
   the refused-return flag. Its findings were read from disk.
2. **c2 at `42856abb`: FAIL, one new high.** The population was keyed by feature id, so one id
   in two segments dropped a feature directory. That hid it from the board audit and from
   merge-gate's owner count. It is now keyed by segment and id, with four tests that fail on
   the old code (`receipt-main-session-fix-c2.md`).
3. **c3 at `6c11ab62`: PASS.** The deferred general code review is now complete.

**Other evidence.**

- Exact-pin full-clone suites exit 0: unit 52 files, integration 80 files.
- `code-grade` reports no high findings. Twelve grade-2 functions carry written reasons.
- The non-regression receipt corrected one error of mine: it reported 54/86, which were
  PASS-line counts rather than file counts. The erratum is appended to the receipt; the original
  lines are kept.

## Spend and ledger

| Measure | Value |
|---|---|
| Runs | 4 of a 20-run budget |
| Wall clock | 199 min |
| Tokens | 126,518 measured, plan run only; the validate runs carry no host measurement |
| Rework | 38 of 120 min; 2 of 2 rounds |
| `cycles_used` | 2 of 10 |
| Judgements | 14: 12 amendment, 1 mission, 1 regate |

## Amendments (build-side departures from the signed task text)

| at | decision | reason | overruled |
|---|---|---|---|
| 2026-10-05T13:16:11.359779+00:00 | T-03.intent | Your 2026-10-04 ruling: SC-02's byte-identical landed reads needed a direct assertion | — |
| 2026-10-05T13:32:11.935170+00:00 | T-01.files | Unit/integration basename clash; unit file renamed `test-worktree-state-rules.py` | — |
| 2026-10-05T13:32:14.980196+00:00 | T-01.verify | (same rename) | — |
| 2026-10-05T13:50:08.823717+00:00 | T-02.files | Basename clash; unit file renamed `test-check-state-corpus-rules.py` | — |
| 2026-10-05T13:50:09.894704+00:00 | T-02.verify | (same rename) | — |
| 2026-10-05T14:09:11.258025+00:00 | T-01.files | Basename clash; unit file renamed `test-feature-corpus-discovery.py` | — |
| 2026-10-05T14:09:13.582507+00:00 | T-01.verify | (same rename) | — |
| 2026-10-05T14:23:00.238719+00:00 | T-03.files | A sparse worktree broke 5 suite files and 2 readers; they now read through `corpus_path` | — |
| 2026-10-05T14:37:44.514835+00:00 | T-04.files | Basename clash; unit file renamed `test-worktree-state-hooks-rules.py` | — |
| 2026-10-05T14:37:47.030278+00:00 | T-04.verify | (same rename) | — |
| 2026-10-05T14:53:54.118813+00:00 | T-05.files | SC-14: the classifier and one citation for DEC-214; a shared `install_hooks` fixture helper | — |
| 2026-10-05T15:41:12.590347+00:00 | T-06.intent | Your 2026-10-05 ruling: conversion after merge (#2101) | — |

overrule rate: 0/12

## Open questions

None from the readers. Two questions I asked earlier are still unanswered; they appear below as
B-6 and B-7.

## Proposed backlog (strike any row by ID; unstruck rows become issues on ship)

| ID | Nature | Finding |
|---|---|---|
| B-1 | bug | `check_state/corpus.py:128-131` treats every `CorpusError` from `tracked_dirs` as an unborn HEAD. A corrupt-tree git error therefore skips the name-set refusal (a narrow fail-open; medium, from the c3 code review). |
| B-2 | bug | The `BRANCH_ERA_EXEMPT` match in `feature_corpus.branch_collisions` uses `frozenset(ids)`, so a third same-id claimant in another segment slips through the FEAT-02/FEAT-03 exemption. Merge-gate still denies (medium, from the c3 code review). |
| B-3 | bug | Harness lead yields are rejected at return: "data absent" in the plan run, and "must return the digest as an object" six times in validate c1. One dispatch refused `outputSchema` while identical dispatches were accepted. |
| B-4 | chore | QA G-1: no test binds the `derive_cone` maximal-subtree clause. Advisory, since redundant nested cone entries change no materialised file. |
| B-5 | chore | QA G-4: the `check-domain` own-checkout sweep skip survives a mutant in isolation (one pool-only red was not reproducible); it needs a binding test. |
| B-6 | bug | `plan-merge check` blind spot: a missing file under an existing directory passes as a planned file. |
| B-7 | bug | An orchestrator that runs `feature-worktree.py create` mid-run strands its in-flight claim in the main checkout's registry. |
| B-8 | chore | `tests/unit/test-feature-corpus-gates.py` `test_this_checkouts_copy_replaces_the_landed_one` is weak. Its worktree lives under the owner, so `startswith(owner)` is trivially true. |
| B-9 | chore | SC-13 assurance limit (PM G-5): record a pre-production red for every new predicate in future plans. This is a process note; nothing can be fixed retroactively. |

Already filed: #2101, the post-merge conversion (SC-10).
