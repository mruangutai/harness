# QA gate — FEAT-2225 @ a5d8687f31c9f05fa77f4d16f3634c3869f47b1f (cycle 4, confirmatory)

**BLUF: FAIL.** The integration kind is red at the pin: `tests/integration/test-gen-decisions-index.py::test_committed_index_matches_a_fresh_regeneration` fails, and T-02's own verify (verbatim) exits 1. Cause: the F2 amendment commit a5d8687f rewrote DEC-253's tags but did not regenerate `DECISIONS-INDEX.md`. Everything else is green. Fix is a one-line regeneration, owner T-02 (documentor). No authored tests, no source edits.

## Equivalence (measured)
`git diff --quiet 219690d0 a5d8687f -- . ':!.harness'` exits 0; numstat lines 0, diff bytes 0. The pin is code-identical to c2 tip 219690d0 outside `.harness/`. Changed paths are only DECISIONS.md, SPEC.md, BRIEF/STATE/feature.json/plan.yaml, and feature notes.

## Phase 1 (BRIEF SC-03 and plan T-04 intent only, before source)
Expected: every c1-c3 test for SC-01..05 stays green; SC-03's amended promise (close verify relative to the default branch as the local repo records it, with ref-moving as a stated boundary contained at merge-distill) has the same tests as c3. A boundary is documentation, so no new executable test is expected. The c3 tests already include the "main moved to sibling" and no-default-branch cases. Gap: none new. The accuracy of the amended prose is a doc fact and is not testable here.

## Pin and environment
Pin `.claude/worktrees/.pins/FEAT-2225-member-expertise-writes--r-c4--harness-qa`, HEAD a5d8687f (confirmed). All runs used `env -u HARNESS_AGENT_TYPE`. Logs: `/tmp/qa4/{unit,int,t01a,t01b,t04a,t04b,t04c}.txt` (volatile). Pin removed on return.

## Matrix (harness.json present; T-01/T-04 cross_module require unit+integration; T-02/T-03 add none)
| kind | state | cmd | executed |
|---|---|---|---|
| unit | satisfied | `.agents/skills/harness/bin/run-unit-tests.py --kind unit` | exit 0, 61 files discovered = 61 run, 1136 PASS lines, 39s |
| integration | **FAIL (assertion)** | `.agents/skills/harness/bin/run-unit-tests.py --kind integration` | exit 1, 88 files discovered = 88 run, 2921 PASS lines + 1 FAIL file, 131s |
| typecheck / component / ui | not claimed | cmd null, unresolved; BRIEF-recorded gap | not run |

The integration failure is a named assertion diff, not a load/import/collection error, so it is `FAIL` and not `misconfigured`. Unit and integration were run in parallel, so I reran the failing test alone: it fails identically.

Failure detail (`test-gen-decisions-index.py`, line 2098 of the log): the committed index row for DEC-253 carries tags `[expertise,dispatch,worktree,map]`; the generator produces `[expertise,dispatch,state,worktree]`. T-02 verify, run verbatim:
`python3 .claude/skills/harness/bin/gen-decisions-index.py --stdout | diff - .harness/harness/docs/DECISIONS-INDEX.md` gives `236c236` and exit 1. Provenance: a5d8687f touched DECISIONS.md and not DECISIONS-INDEX.md; the last index commit is 7c2f2d48 (T-02). Introduced by the amendment commit, after c3 (which was green at 6d9e6053).

## Task verify commands, verbatim, at the pin
- T-01 `python3 tests/unit/test-expertise-ops.py && python3 tests/integration/test-expertise-merge.py`: exit 0 both (202 and 375 ok/PASS lines, 0 fail).
- T-02 (above): **exit 1**.
- T-03: MANUAL (ordering note); satisfied by T-04 automation, nothing executed.
- T-04 `python3 tests/unit/test-digest-schemas.py && bun test tests/unit/omp-hooks.test.ts && python3 tests/integration/test-member-expertise.py`: exit 0 each (digest-schemas OK; bun 157 pass / 0 fail / 877 expects; member-expertise 85 ok, "0 failure(s)").

## fail_first (verify: automated SC-01..SC-05), pointers from c3
Tier: natural RED (retained command + failing outcome) unless noted. Fresh green at pin: T-04 suite above plus unit and integration floor files (test-dispatch-guard, test-validate-digest, test-merge-gate, test-bash-write-guard, test-omp-hooks all PASS in the integration/unit logs).
- SC-01: `notes/red-first-T-04-host.md` (9 fail); `notes/red-first-fix-c1-host.md`; `notes/receipt-harness-backend-dev-T-01-c1.md`.
- SC-02: `notes/red-first-T-04-digest.md` (22+2); `notes/red-first-fix-c1-core.md`; `notes/red-first-fix-c1-digest.md`; `notes/red-first-fix-c2-digest.md` (0/4).
- SC-03: `notes/red-first-T-04-host.md`; `notes/red-first-T-04-guard.md` (51); `notes/red-first-fix-c1-digest.md` (10/10); `notes/red-first-fix-c2-core.md` (committed tamper). The amended boundary clause adds no new executable behavior; its demonstration is the same c2/c3 evidence plus the merge-gate replay-mismatch refusal in `notes/red-first-t04-merge-gate.md`.
- SC-04: `notes/receipt-harness-backend-dev-T-01-c1.md` (63 int / 12 unit, 17 mutants); `notes/red-first-fix-c2-core.md`.
- SC-05: `notes/red-first-t04-merge-gate.md` (23).
- Durability gap carried from c1/c3: raw red logs lived under /tmp; the notes carry counts, not raw output. Mutation proofs were not recreated this cycle (per assignment).

## F1/F3, N3/N4
- F1 (distill authority) and F3 (real host-to-core reps) stay CLOSED: code is byte-identical to c2/c3 (0-byte diff) and their covering suites are green at this pin. No contradicting evidence.
- N3 (`--base` accepts the feature HEAD) and N4 (self-anchor when HEAD equals the default branch): unchanged code, remain **advisory low** (owners T-01/T-04) exactly as c3. N4 reconciles with the accepted F2 boundary: the self-anchor and moved-ref cases are the same local-ref family that the ruling accepts as a documented close-time boundary, contained by `merge-gate.py merge-distill` (live remote fetch, replay-mismatch refusal; backlog #2251). Existence is not a defect. I have no evidence the amended promise is inaccurate on this point. Unchanged: no test pins the three hand-measured cases.
- locally_run handoff evidence: nothing in this diff touches a locally_run kind's detect surface (omp_session_accessor, handoff_comprehension, issue_types_live); no run invented. `notes/probe-handoff-comprehension-2026-11-21.md` exists from prior work.

## Findings
- **C4-F1 (must_fix, kind: substance, severity medium, owner T-02):** DECISIONS-INDEX.md is stale versus DECISIONS.md at the pin (DEC-253 tags). Kind rationale: substance, not form. A committed generated artifact disagrees with its authority and a named assertion plus T-02's own verify fail; it is not a style or wording matter. (My earlier label test/documentation-sync is not a schema kind and is withdrawn.) Breaks T-02 verify and the integration kind. Repair: regenerate with `gen-decisions-index.py` (writes the index) and re-pin. This is not a code fix; it is not F2 reopened.

## matrix_ok vs integration state
`matrix_ok: true` means the floor is met: both required kinds (unit, integration) exist, were discovered and ran with named tests, none is absent or misconfigured. The digest enum has no "red" state, so integration is reported `missing` only as the closest non-satisfied value; the truth is present-but-red (one named assertion failure, 2921 PASS lines). The gate is NOT green: `suite: fail`, `failures: 1`, VERDICT FAIL.

## Open
Nonblocking: none new.

## Principles applied
Verification is the product (rule 7): integration kind graded by exit code plus failure kind, not the "ALL PASSED" lines from sibling files. Never falsify the record (rule 15): the red integration file is reported as FAIL, not as unrelated drift (O-01).
