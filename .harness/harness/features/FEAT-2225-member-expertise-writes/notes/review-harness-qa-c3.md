# QA gate — FEAT-2225 @ 6d9e6053a6367c78f1e5848a6801e7ca09d82dd1 (cycle 3)

**BLUF: PASS.** Required unit + integration ran green at the pin under `env -u HARNESS_AGENT_TYPE`; matrix_ok true.
F2 (c2 high T-01/T-04) is CLOSED for the reported counterexample with discriminating evidence; N2 is now caught by exactly one named check. Two
advisory boundaries (below) stay open. No authored tests, no source edits. Pin removed on return.

Equivalence (measured): `git diff 6d9e6053 219690d0 -- . ':!.harness/harness/features'` empty (only feature.json/plan.yaml differ); same for working HEAD 30c8beb7. The pin tree is code-identical to fix 219690d0; diff base 594af2a8..pin read as 46 changed files.

## Phase 1 (BRIEF/plan only, before source)
Expected: every c1/c2 test (SC-01..05) plus c2 F2: a unreceipted deletion COMMITTED before a legitimate receipt refuses for member and lead, live yield, durable check and close-run, with and without `--base`; no default branch and no `--base` refuses 15; clean committed feature-branch application and supersession still verify; the unchained-active-batch guard (N2) has its own discriminating check. All have a named test. Gaps (no test): see N3, N4.

## Matrix (harness.json present; T-01/T-04 cross_module = always unit+integration; T-02/T-03 docs add none)
| kind | required | state | cmd | executed |
|---|---|---|---|---|
| unit | yes | satisfied | `.agents/skills/harness/bin/run-unit-tests.py --kind unit` | exit 0, 61 files, 1136 PASS lines, 47s |
| integration | yes | satisfied | `.agents/skills/harness/bin/run-unit-tests.py --kind integration` | exit 0, 88 files, 2922 PASS lines, "ALL PASSED", 145s |
| typecheck / component / ui | no | not claimed | cmd null, unresolved; BRIEF-recorded gap | not run |
Discovered = executed: unit 61 files, integration 88 files, no collection/import errors. Logs `/tmp/qa3/{unit,int}.txt` (volatile). test_kinds extras (omp_session_accessor, handoff_comprehension, issue_types_live) are locally_run kinds outside this diff's detect surface for unit/integration; not claimed.

## Source claims at the pin (all CONFIRMED)
- `expertise-merge.py:1564-1581` `_default_branch` resolves `refs/remotes/origin/HEAD` then `origin/main` then `refs/heads/main`; none resolves: exit 15 `NO AUTHORIZED BASE`.
- `authorized_base`: `merge-base(--base | default, HEAD)`; shares no history: exit 15.
- `_refuse_unreceipted_content` (L1584) anchors only on that commit's blob; HEAD anchor gone.
- `validate-digest.py` `_verify_receipt` (L2272) argv passes no `--base`; the single resolver is the core's.

## Measured probes of `authorized_base` (scratch repo, tree-less commits, no source touched)
| scenario | result |
|---|---|
| feature F, main M | default -> M |
| main moved to sibling M2 | default -> fork M (merge-base) |
| `--base` orphan commit, no shared history | exit 15 NO AUTHORIZED BASE |
| no origin/HEAD, no main | exit 15 NO AUTHORIZED BASE (fail closed) |
| `--base` = M (main fork) | M |
| **`--base` = F (feature HEAD itself)** | **F: anchors on HEAD** |
| **HEAD == default branch** | **default -> HEAD (self-anchor)** |

## N2 mutant and c2 discrimination (my own mutants, copies of the pinned bin under /tmp, via the suites' `EXPERTISE_MERGE_BIN` / `VALIDATE_DIGEST_BIN`)
- **N2** (`if unchained or anchor not in states` -> `if anchor not in states`): unit exit 0, validate-digest committed-tamper 4/4, integration exit 1 with exactly one FAIL: `verify c2: an active batch off the write chain refuses and is named (unchained-batch guard)`. **Caught, discriminating**; baseline at the pin passes the same check. Matches `red-first-fix-c2-core.md` RED 2.
- **N3** (anchor on `"HEAD"`, the c1 behaviour): integration exit 1, 5 FAIL (`verify c2 member/lead ... COMMITTED ... (base=default|--base)` x4, `no default branch and no --base refuses with 15`); validate-digest committed-tamper 4/4 FAIL (live member, live lead, durable, close-run). Unit u44 stays green under N3 (function still exists): discrimination lives in integration + digest, not unit.

## fail_first (every verify: automated SC), tier labelled
Natural RED (pre-fix core, retained command + failing outcome): `notes/red-first-fix-c2-core.md` (unit u44 + 5 integration), `notes/red-first-fix-c2-digest.md` (0/4). Raw logs `/tmp/f2225-c2/red-pre-*.txt` and `/tmp/t04c2/red-vd.txt` still present but volatile; I re-created the red via N3 above (mutation tier, semantic: the exploit succeeds, not just a missing symbol).
- SC-01: red-first-T-04-host.md (9 fail); red-first-fix-c1-host.md (5 rep mutant fails); receipt-harness-backend-dev-T-01-c1.md.
- SC-02: red-first-T-04-digest.md (22+2); red-first-fix-c1-core.md; red-first-fix-c1-digest.md; red-first-fix-c2-digest.md (0/4 committed tamper).
- SC-03: red-first-T-04-host.md; red-first-T-04-guard.md (51); red-first-fix-c1-digest.md (F1 10/10); red-first-fix-c2-core.md (committed tamper).
- SC-04: receipt-harness-backend-dev-T-01-c1.md (63 int / 12 unit, 17 mutants; raw logs volatile, c1 G2 stands); red-first-fix-c2-core.md (supersession `--base` control stays green).
- SC-05: red-first-t04-merge-gate.md (23).
- SC-06: inspection, not automated.
c2 regressions (F1 distill-authority, F3 real host-to-core reps): unit/integration suites at the pin cover them and are green (test-dispatch-guard, test-validate-digest authority group, test-omp-hooks); F1 mutant and F3 evidence from c2 not re-mutated this cycle: only my c2 note examined them, and the pin tree is identical to c2's reviewed F1/F3 code (c2 diff c2-pin..219690d0 touches only the F2 files per the receipt; not re-diffed).

## Findings
- **N3 (kind substance, low-advisory, owner T-01):** explicit `--base` accepts any commit sharing history with HEAD, including the feature's own HEAD: `authorized_base(--base=HEAD)` returns HEAD, re-authorizing a committed unreceipted deletion. Callers today (`merge-gate.py:447` passes fetched main; validate-digest passes none) never feed a feature commit, so no executable exploit; no test pins that `--base` must be an ancestor of the default branch.
- **N4 (kind substance, low-advisory, owners T-01/T-04):** default-branch self-anchor (HEAD == origin/HEAD, e.g. a checkout fast-forwarded to main) returns HEAD, as stated in the receipt. Counterexample: a tamper commit pushed/fast-forwarded onto the default branch, then verify-receipt run there: anchors on itself, passes. Stale-ref case: origin/HEAD ranks above a fresher local main. No test pins the boundary (untested: self-anchor, moved-main default, nonancestor `--base`; I measured all three by hand above). Per SC-03/T-04 close paths run on `chore/distill-*`/feature branches, so I count it advisory, not blocking.
- Evidence durability (low, T-01/T-04): c2 red logs only under /tmp; notes carry the failing counts, not raw output (carried from c1 G2).

## Not done
No authored tests; typecheck unresolved (BRIEF gap); host-side TS mutants not rerun; no second reader pass on F1/F3 beyond the green suites.

## Principles applied
Verification is the product (rule 7): green counted only with named tests and a re-run natural-or-mutation red. Never falsify the record (rule 15): the `--base=HEAD` and self-anchor boundaries are reported as measured, not rounded to CLOSED. Evidence for N2 is my own: no independent reader examined it (O-07).
