# FEAT-1559: Corpus outside the worktree — ship review

**Ready to ship.** Validate passes at `review_sha` `f8a67546bcb42b6a5fd4327398615a4cfc07ae4d` with no must-fix: all five readers pass (qa, code, security, ui, goal-check). After this lands, a feature worktree holds only its own feature directory, and every other feature is read from the main checkout. The remaining gap is the one you deferred: converting today's standing worktrees, which runs after merge under #2101 and now with a HEAD-era precondition.

It took 5 validate passes and 4 main-session fix rounds. Round 3 came from the outside panel you ordered on PR #2103, after validate c3 had already passed; round 4 closed the one finding validate c4 raised against round 3. You raised the rework allowance twice to allow this (`notes/answers-operator-2026-10-05-rework-raise.md`, `notes/answers-operator-2026-10-05-rework-round-4.md`).

No report round was spawned. This briefing is assembled from:
- the digests `runs/plan-product`, `runs/validate-validator`, `runs/validate-c1-validator`, `runs/validate-c2-validator`, `runs/validate-c3-validator` and `runs/validate-c4-validator`;
- the readers' `notes/*-c5.md` reports;
- the goal-check `notes/research-FEAT-1559-corpus-outside-worktree-goalcheck-validate-c5.md`.

`runs/` is gitignored, and every run directory except the last is pruned before push. The durable record of each failing cycle is its reader notes (`notes/*-c1.md`, `*-c2.md`, `*-c4.md`) and the fix receipt that answers it (`notes/receipt-main-session-fix-c1.md` … `-c4.md`).

## Definition of done, graded (validate c5 goal-check)

| Perspective | As signed | Verdict | SCs that discharged it | Evidence |
|---|---|---|---|---|
| operator | Create or keep a record-bearing checkout without materialising other features, by any creation route. Landed records stay readable and unaltered, clean checkouts converge without losing dirty work, and clones and CI behave as before. | **partial** | SC-01, SC-06, SC-11 met; SC-10 deferred by your ruling | `receipt-T-04.md`; `non-regression-receipt.md`; #2101 for the conversion |
| reader | Read landed precedent on disk and trust that an audit examines its declared subject, not a silently smaller set. Duplicate branch claims stay detectable from a sparse checkout. | **met** | SC-02, SC-03, SC-04, SC-05, SC-12, SC-14 | `test-feature-corpus.py`; receipts c1–c3 |
| code maintainer | One deterministic, idempotent state command with explicit failure reasons, enforced at checkout, merge, rebase and gate boundaries. | **partial** | SC-07, SC-09 met; SC-08, SC-13 partial | `test-worktree-state*.py`; `suite-baseline.md` |

**Why the partials.**
- **SC-10 is deferred, not missing.** You moved the conversion after merge (#2101). Converting other sessions' worktrees now would leave them sparse while their tools are still pre-1559.
- **SC-08: one conjunct cannot be reproduced literally.** On Git 2.54 a merge does not leave skip bits cleared (`receipt-T-04.md`). The hooks, merge, rebase and repair are each tested; the literal "merge cleared the bits, then the hook repaired them" sequence is not.
- **SC-13 rests on historical evidence only.** Every predicate is shown to discriminate today, by mutants, but not every one has a red recorded before its production code existed. That cannot be produced retroactively.

## What was built

| Task | What it delivered |
|---|---|
| T-01 | `feature_corpus.py` (population, cone, identity) and `worktree-state.py` (verify and repair, exits 3/4/7/8). Repair runs only on classes A and B; dirty work (class C) is always refused. |
| T-02 | check-state verifies the layout before any invariant and audits the full landed population. Dirty work is reported without gating. |
| T-03 | merge-gate, branch-create-gate, the board audit, plan routes, decision anchors, skill references and `factory_claim` all read the main corpus. A missing landed directory refuses by name. |
| T-04 | Tracked `post-checkout`, `post-merge` and `post-rewrite` hooks run the repair, so the layout converges at the boundary. They stay silent when the only finding is ordinary uncommitted work. |
| T-05 | Regression locks, a one-time non-regression receipt, DEC-214 amended (landed reads anchor at the control plane), and the operator guidance. |
| T-06 | Abandoned here by your ruling; carried in #2101. |

## How validation went

1. **c1 at `0e8301a5`: FAIL, six must-fix.** Silently smaller plan-route audit, two untested cut-overs, nine functions below the grade bar. Fixed in round 1. The host refused that lead's final return, so the run is closed BLOCKED with the refused-return flag.
2. **c2 at `42856abb`: FAIL, one high.** The population was keyed by feature id, so one id in two segments dropped a feature directory. Fixed in round 2.
3. **c3 at `6c11ab62`: PASS.** PR #2103 opened here.
4. **Outside panel on PR #2103** (reviewer, security-reviewer, fable-advisor): correctness FAIL with 2 high and 4 medium findings, all reproduced, plus one design medium. Round 3 fixed all seven, each with a test that is red at `6c11ab62`:
   - `factory_claim` read other features locally;
   - a lossy clean filter could make repair delete bytes the index did not hold;
   - tracked symlinks were hashed through their target;
   - git-quoted sparse-checkout names never verified;
   - branch-named worktrees lost their identity mid-rebase;
   - a deleted active directory was answered from the landed copy;
   - the hooks nagged about ordinary uncommitted work.
   The two lows became #2107 and #2108, and #2101 gained its HEAD-era rule.
5. **c4 at `35587d8d`: FAIL, one medium.** All seven confirmed. Names written to git's `--stdin` readers were not quoted, so a top-level directory starting with `"` made repair exit 128. Round 4 C-quotes every name for both readers (`sparse-checkout set`, `hash-object --stdin-paths`).
6. **c5 at `f8a67546`: PASS.**
   - Leading-quote probe: red at the old pin, green now.
   - Each stdin writer fails independently under mutation.
   - Byte probes: 753 of 762 sparse-list names pass; the nine failures are git's own whitespace/LF cone limits and reproduce on the previous code. 711 hidden-file names hash correctly.

**Other evidence.**
- Exact-pin full-clone suites exit 0: unit 52 files (767 PASS), integration 80 files (2341 PASS).
- `code-grade` reports no high findings. Twelve grade-2 functions carry written reasons.
- Real-owner observation at the pin: 6/6, no skips.

## Spend and ledger

| Measure | Value |
|---|---|
| Runs | 6 |
| Wall clock | 245 min |
| Tokens | 126,518 measured, plan run only; the validate runs carry no host measurement |
| Rework | 84 of 240 min; 4 of 4 rounds (raised twice by you) |
| `cycles_used` | 7 = 4 fix rounds + 3 send-backs the lead reported |
| Judgements | 18: 13 amendment, 2 regate, 2 continue, 1 mission. One `continue` was recorded before the c5 run's regate by a chained command whose refusal a pipe hid; the ledger is append-only. |

## Amendments (build-side departures from the signed task text)

| at | decision | reason | overruled |
|---|---|---|---|
| 2026-10-05T13:16:11Z | T-03.intent | Your 2026-10-04 ruling: SC-02's byte-identical landed reads needed a direct assertion | — |
| 2026-10-05T13:32:11Z | T-01.files | Unit/integration basename clash; unit file renamed `test-worktree-state-rules.py` | — |
| 2026-10-05T13:32:14Z | T-01.verify | (same rename) | — |
| 2026-10-05T13:50:08Z | T-02.files | Basename clash; unit file renamed `test-check-state-corpus-rules.py` | — |
| 2026-10-05T13:50:09Z | T-02.verify | (same rename) | — |
| 2026-10-05T14:09:11Z | T-01.files | Basename clash; unit file renamed `test-feature-corpus-discovery.py` | — |
| 2026-10-05T14:09:13Z | T-01.verify | (same rename) | — |
| 2026-10-05T14:23:00Z | T-03.files | A sparse worktree broke 5 suite files and 2 readers; they now read through `corpus_path` | — |
| 2026-10-05T14:37:44Z | T-04.files | Basename clash; unit file renamed `test-worktree-state-hooks-rules.py` | — |
| 2026-10-05T14:37:47Z | T-04.verify | (same rename) | — |
| 2026-10-05T14:53:54Z | T-05.files | SC-14: the classifier and one citation for DEC-214; a shared `install_hooks` fixture helper | — |
| 2026-10-05T15:41:12Z | T-06.intent | Your 2026-10-05 ruling: conversion after merge (#2101) | — |
| 2026-10-05T19:15:44Z | T-03.files | Outside panel: `factory_claim` read other features' records locally; now via `corpus_path` | — |

overrule rate: 0/13

## Open questions

The readers raised three non-blocking advisories:
- **Q-C5-QUOTE-COVERAGE.** The committed test does not directly exercise backslash escaping; the ephemeral probes did. Listed as B-10.
- **Q-C5-GIT-NAMES.** Document git's own whitespace/LF cone-name limits. Listed as B-11.
- **Q-C5-EVIDENCE-GRANT.** QA's raw-evidence writes under `runs/` were refused by its grant. Listed as B-12.

Two questions I asked earlier are still unanswered; they are B-6 and B-7.

## Proposed backlog (strike any row by ID; unstruck rows become issues on ship)

| ID | Nature | Finding |
|---|---|---|
| B-1 | bug | `check_state/corpus.py:128-131` treats every `CorpusError` from `tracked_dirs` as an unborn HEAD, so a corrupt-tree git error skips the name-set refusal (narrow fail-open; medium, c3 code review). |
| B-2 | bug | The `BRANCH_ERA_EXEMPT` match in `feature_corpus.branch_collisions` uses `frozenset(ids)`, so a third same-id claimant in another segment slips the FEAT-02/FEAT-03 exemption. Merge-gate still denies (medium, c3 code review). |
| B-3 | bug | Harness lead yields are rejected at return ("data absent", "must return the digest as an object"). The `outputSchema` refusal is inconsistent: identical validator dispatches were accepted at c4 and refused at c5. |
| B-4 | chore | QA G-1: no test binds the `derive_cone` maximal-subtree clause. Advisory, since redundant nested cone entries change no materialised file. |
| B-5 | chore | QA G-4: the `check-domain` own-checkout sweep skip survives a mutant in isolation; it needs a binding test. |
| B-6 | bug | `plan-merge check` blind spot: a missing file under an existing directory passes as a planned file. |
| B-7 | bug | An orchestrator that runs `feature-worktree.py create` mid-run strands its in-flight claim in the main checkout's registry. |
| B-8 | chore | `tests/unit/test-feature-corpus-gates.py` `test_this_checkouts_copy_replaces_the_landed_one` is weak: its worktree lives under the owner, so `startswith(owner)` is trivially true. |
| B-9 | chore | SC-13 assurance limit: record a pre-production red for every new predicate in future plans (process note). |
| B-10 | chore | Commit a test that discriminates `quote()`'s backslash and `"` escapes, which today only ephemeral probes cover. |
| B-11 | docs | Document git's whitespace/LF limits on cone directory names, and the host byte exclusions (APFS refuses lone high bytes). |
| B-12 | bug | QA's raw-evidence writes under `runs/<run>/` were refused, so its logs stayed in `/tmp`; the grant and the evidence procedure disagree. |

Already filed: #2101 (post-merge conversion, SC-10, with a HEAD-era precondition), #2107 and #2108 (outside-panel lows).
