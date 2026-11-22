# QA gate — FEAT-2225 @ 130592528844321c27fbb628fdc05f6f17f86d0d (cycle 1)

**BLUF: PASS.** Required unit and integration kinds ran green at the exact pin, under own hand, with
`env -u HARNESS_AGENT_TYPE`. matrix_ok true. One substantive finding (F1, medium) and two evidence-durability gaps (below).

Pin: `pinned-checkout.py add --run-id qa-c1 --persona harness-qa` (HEAD verified `13059252…`), removed on return.
Worktree tip 3ab9f467 differs from the pin only in feature.json (`git diff --stat`: 1 file, 1 line).

## Phase 1 (derived from BRIEF/plan, before source)
Expected: member tool availability for 16 personas + Write/own-file grants (SC-01); persona-required/state-forbidden digest items,
lead-vs-child receipt matching, live + durable close refusals (SC-02); spoof/held/non-distill/escape/shell-mutator refusals (SC-03);
replay collision renumber, changed-main refusal, cap refusal, idempotence, original-member supersession (SC-04); merge-distill
serialization, stale/missing receipt, DEC-220 build-entry refusals, ordinary merge unchanged (SC-05); SC-06 inspection. All have
a named test below. Gap against Phase 1: the marker-on-non-distill-run boundary (F1) has no test.

## Matrix
test_matrix: cross_module = always [unit, integration] (T-01, T-04); docs = [] (T-02, T-03). harness.json present; unit/integration `active`.

| kind | state | cmd | exit | discovered |
|---|---|---|---|---|
| unit | satisfied | `.agents/skills/harness/bin/run-unit-tests.py --kind unit` | 0 | 61 files, 1129 PASS lines, includes test-expertise-ops, test-digest-schemas, test-omp-hooks, test-harness-boundary; 4 `FAIL` tokens are test-factory-claim-mutation's own BUG-1290 mutation proof (repo G-09), runner exit 0 |
| integration | satisfied | `.agents/skills/harness/bin/run-unit-tests.py --kind integration` | 0 | 88 files, 2922 PASS lines, "ALL PASSED"; 0 FAIL tokens; includes test-expertise-merge, test-member-expertise, test-merge-gate, test-validate-digest, test-dispatch-guard, test-bash-write-guard |

Task verifies, verbatim, at the pin: 
- T-01 `python3 tests/unit/test-expertise-ops.py && python3 tests/integration/test-expertise-merge.py` → exit 0 both ("PASS test-expertise-ops.py", "PASS test-expertise-merge.py"); T-01 receipt counts 194 unit + 355 integration checks.
- T-02 `gen-decisions-index.py --stdout | diff - …DECISIONS-INDEX.md` → exit 0, empty diff.
- T-03 MANUAL (per plan); exercised via T-04's test-member-expertise (below), not a separate gate.
- T-04 `python3 tests/unit/test-digest-schemas.py` → `Ran 34 tests OK`; `bun test tests/unit/omp-hooks.test.ts` → 149 pass / 0 fail / 794 expect; `python3 tests/integration/test-member-expertise.py` → exit 0, 111 PASS lines, "0 failure(s)".
- typecheck cmd null (BRIEF known gap): not claimed. locally_run handoff probe: recorded, `notes/probe-handoff-comprehension-2026-11-21.md` (as-written 4/4, stripped 0/4); not rerun.

## SC → covering test → fail-first
| SC | Covering tests | Fail-first evidence (natural RED, pre-change source) |
|---|---|---|
| SC-01 | `tests/integration/test-member-expertise.py` (16 tool lists, Write, own-file grants, 5 capability-class reps, craft+repo apply); `tests/unit/omp-hooks.test.ts` "FEAT-2225: registers expertise_apply…", "craft and repository destinations run member-ops…"; `tests/integration/test-expertise-merge.py` member-ops cases | host: `notes/red-first-T-04-host.md` (140 pass/9 fail, tool undefined). core: `/tmp/t01/red-int.txt` (232 PASS/63 FAIL, exit 1) and `red-unit.txt` (12 FAIL). 16-persona file: receipt-main-session-T-03-T-04.md claims 28 FAIL vs 7c2f2d48; no retained capture (G1) |
| SC-02 | `tests/integration/test-validate-digest.py` run_member_expertise_{leaf,lead,supersession}_cases (13/13, 13/13, 8/8); `tests/unit/test-digest-schemas.py` test_expertise_update_shapes, test_expertise_persona_enum_is_the_canonical_sixteen | `notes/red-first-T-04-digest.md`: unit 2 FAIL, validate-digest 22 FAIL (fabricated, missing, file-inconsistent, durable close-run) |
| SC-03 | `tests/unit/omp-hooks.test.ts` spoof/held/unidentified/non-distill/escape cases; `tests/integration/test-bash-write-guard.py` 89 FEAT-2225 CLI cases (lead, reviewer, dev-ops, leaf); `test-dispatch-guard.py` cases 32–34; `test-validate-digest.py` durable cases; `test-expertise-merge.py` nine boundary refusals | `red-first-T-04-host.md` (9 fail); `red-first-T-04-guard.md` (51 FAIL, 40/89); `red-first-T-04-digest.md` (dispatch-guard 16 FAIL) |
| SC-04 | `tests/integration/test-expertise-merge.py` replay collision/renumber, changed-main, cap, idempotent, supersession incl. empty withdrawal; `tests/unit/test-expertise-ops.py` u30–u42 | `/tmp/t01/red-int.txt` 63 FAIL (subcommands absent), `red-unit.txt` 12 FAIL; 17 one-mechanism mutants in T-01 receipt |
| SC-05 | `tests/integration/test-merge-gate.py` FEAT-2225 cases (65 ok); `tests/unit/omp-hooks.test.ts` "Main's Bash git merge and gh pr merge reach merge-gate…" | `notes/red-first-t04-merge-gate.md` (23 FAILED incl. DEC-220 build-entry refusals); host 9th red |
| SC-06 | inspection (not graded by QA test) | n/a |

Tier: natural RED for all rows. T-01 red outputs live only under `/tmp/t01` (volatile).

## Findings
- **F1 (med, kind substance; T-04 `.omp/extensions/harness-hooks.ts` `applyCallerRefusal` ~L1151 + `.claude/skills/harness/bin/dispatch-guard.py` `_distill_preflight`) — REAL, compensated only late.**
  I confirm from pinned source: `applyCallerRefusal` trusts `currentMission` parsed from prose; `inflight_registry authorize` is run-kind-blind (no `distill` in inflight_registry.py); `_distill_preflight` only requires the marker when a bound `distill-*` run exists and never refuses the marker where none does. A governed child under a non-distill run carrying `HARNESS-MISSION: distill` therefore writes its own Expertise file and receipt before any yield gate. Compensations: (a) own-file/own-tier only (SC-03 destination checks); (b) validate-digest refuses a yield claiming those ops (test "member whose parent's registered run is not a distill run is refused") but an empty list on a non-distill run is ordinary-legal and not matched against existing receipts; (c) replay and merge-distill reconstruct from receipts and contain no distill-run lineage check (grep of pinned expertise-merge.py and merge-gate.py: none), so such a receipt replays clean into a distill PR; (d) human PR review. Reaching it needs a governed lead to mis-dispatch or inject the marker, so blast radius is one persona's own file: medium, not high. Close verification catches inconsistency, not provenance. Fix is one derivation: dispatch-guard refuses the marker with no bound distill run (orchestrator case needs `_require_feature_distill`'s registered-feature route), or the host checks the registered run kind. Owner: T-04, main-session-direct (DEC-174).
- **F1 coverage gap (T-04, `tests/unit/omp-hooks.test.ts`, `tests/integration/test-dispatch-guard.py`):** no test seeds marker-without-distill-run and asserts refusal at write or dispatch. The boundary is untested; a fix lacks a red.
- **G1 (low, kind evidence; T-04 `tests/integration/test-member-expertise.py`):** the 28-FAIL red against 7c2f2d48 for the 16-persona file is only asserted in a receipt, with no retained output. My reproduction attempt (copy the pinned test into a base pin) was denied by bash-write-guard, so I did not capture one. SC-01's other legs have retained reds.
- **G2 (low, kind evidence; T-01):** T-01 red logs are in `/tmp/t01`, not copied under the feature. SC-04's fail-first is retained only there.
- No uncovered Phase 1 expectations other than F1.

## Not run (by instruction)
No perturbations, no authored tests, no probe rerun. No new mutation proofs by QA; T-01 mutants are the implementer's own record.

## Principles applied
Verification is the product (rule 7): green only counted with named tests, nonzero discovery, and a recorded red per SC. Never falsify the record (rule 15): G1 stated as unreproduced rather than marked satisfied.
