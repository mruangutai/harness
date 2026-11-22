# QA gate — FEAT-2229 c2 (pin a8b8df6196c6107b76cbd941bf2266b3e71476d6)

**BLUF: PASS.** matrix_ok true; unit and integration `satisfied`; signed T-01/T-02/T-03 verifies exit 0; fail-first for SC-01/02/03/07 reproduced as natural RED (signature-bearing, semantic) at base dfa52536; both cycle-1 fixes (F1, F2, F-01) reproduced red then green. No findings; no coverage gaps. Only my own evidence has examined these c1 fixes beyond the owning dev's receipts (independence of a second reviewer is the other readers' job).

## Pin, range, equivalence
- Pinned checkout (pinned-checkout.py, persona harness-qa, run r-20261121-validate-c2-validator): HEAD a8b8df61, clean. Range dfa52536..a8b8df61.
- `git diff --stat c8a8e174 a8b8df61`: only feature.json and plan.yaml (feature dir). Equivalence verified, but NOT relied on: every gate below was re-run at a8b8df61.
- Env: `env -u HARNESS_AGENT_TYPE -u HARNESS_CONTROL_PLANE_ROOT -u HARNESS_FEATURE_TREE_ROOT` on every run.
- Phase 1 (BRIEF+plan only, before source), expected tests: SC-01 unit shape contract (block type, five keys, dispositions, dec/clause/reason/successor syntax, writer round trip, no partial write); SC-02 CLI check, one failure each (absent block, unindexed dec, keep/amend on STRUCK, clause absent/neighbouring section, unresolved successor, no DECISIONS.md owner) plus valid controls; SC-03 both sides of era boundary, null/missing/malformed era, legacy bytes unchanged; SC-07 per-obligation assertion at its owner with deletion reddening it. All present; none missing.

## Matrix (control-plane .harness/harness.json)
T-01 cross_module -> always unit + integration (both `active`). T-02/T-03 docs -> always []. functional/eval excluded (DEC-187); locally_run kinds' detect surfaces untouched; component/ui/typecheck unresolved but no such surface changed.

## Commands and outcomes (all at pin a8b8df61)
| Command | Exit | Result |
|---|---|---|
| T-01 verify: `python3 tests/unit/test-decision-disposition-schema.py` ; `python3 tests/integration/test-plan-decision-dispositions.py` (set -eu) | 0 | 40/40 ; 98/98 |
| T-02 verify: `python3 tests/integration/test-plan-team.py` | 0 | 184/184 |
| T-03 verify: `set -euo pipefail; gen-decisions-index.py --stdout \| diff - .harness/harness/docs/DECISIONS-INDEX.md` | 0 | no diff |
| unit: `.agents/skills/harness/bin/run-unit-tests.py --kind unit` | 0 | OK; 62 files discovered (tests/unit 62 test-*.py), 1177 PASS lines, pool 8, 22.2s; test-decision-disposition-schema.py exit 0 (0.53s) |
| integration: `.agents/skills/harness/bin/run-unit-tests.py --kind integration` | 0 | OK; 89 files (tests/integration 89 test-*.py), 2848 PASS lines, 112.2s; test-plan-merge 13.2s, test-plan-team 9.2s, test-plan-decision-dispositions 34.0s, test-checker-structure-locks 4.4s all exit 0 |
- Unit log carries 4 bare `FAIL BUG-1290 ...` lines inside test-factory-claim-mutation.py (exit 0): its own mutation-proof tokens (G-09), not failures; graded on exit codes.
- Advisory: test-plan-decision-dispositions took 34s in the full integration run (under load, concurrent readers) vs T-01's "under 30 s" intent; ~12s alone in c1. Not a gate failure.
- Both runner invocations ran once after scoping; the earlier c1 test-check-domain-post load timeout did not recur.

## Fail-first (tier: natural RED, semantic) — base pin dfa52536, tests from a8b8df61 via git archive, source untouched
- SC-01: tests/unit/test-decision-disposition-schema.py rc1, 13/40, 27 FAIL lines (row/key/successor/disposition/clause/reason rejection, set-key refuses malformed, byte identity).
- SC-02/SC-03: tests/integration/test-plan-decision-dispositions.py rc1, 44/97, 54 FAIL lines (six check failures, STRUCK, wrong-section/partial clause, successor, owner, era exact boundary/null/malformed, stamping, backdating routes).
- SC-07: tests/integration/test-plan-team.py rc1, 31 of 154 FAILING (the 30 case-10 obligations + (10z) template empty list, plus the c2 strike-alternative assertion).
- Matches (and extends for c1 fixes) notes/red-first-T-01.md (13/40; 42/90) and red-first-T-02.md (30 of 153). Counts are higher than the receipts because the pin's tests include the c1 fix cases.

## Cycle-1 fixes — reproduced
- F1 (creation bypass) and F2 (fenced heading): pre-fix source 98305097 + a8b8df61 dispositions test: rc1, 92/98, 7 FAIL lines: the three fenced-example cases, DEC-11 end-scan, malformed creation APPLIED, no-file, valid-control (matches red-first-T-01.md). Green at pin: 98/98. Cases: test-plan-decision-dispositions.py:281 `case_fenced_heading_is_not_a_section` (plain and four-backtick nested fences, plus real-section pass controls), :436 `case_creation_validates_dispositions` (malformed creation refused, no file, valid control).
- F-01 (pm Mode 2 strike alternative; .omp/agents/harness-pm.md:78-79): owner-scoped assertion test-plan-team.py:484, scoped to the `## Mode 2`..`## Mode 3` slice (:431), with the (10m) deletion witness at :505. My own mutation at the pin (whitespace-tolerant regex removed the alternative clause, 1 substitution, restored; `git status --porcelain` empty): NEW test rc1 `1 of 183 FAILING` naming exactly that assertion; the c1 test (98305097 version) against the same mutant rc0, 182/182 (gap reproduced). Discrimination shown.

## SC -> covering test -> red-first evidence
- SC-01: tests/unit/test-decision-disposition-schema.py (case_block_types:71, case_keys:80, case_dispositions:88, case_dec_and_clause_values:104, case_reason_and_successor_values:113, case_set_key_round_trip:139, case_apply_creation_round_trip:162); red 13/40 at dfa52536 + notes/red-first-T-01.md.
- SC-02: tests/integration/test-plan-decision-dispositions.py case_missing_block:214, case_unindexed_dec:219, case_struck:225, case_clause_location:234, case_fenced_heading_is_not_a_section:281, case_successors:295, case_ownership:304, case_valid_controls:197; red 44/97.
- SC-03: same file case_era:343, case_malformed_instants:361, case_history_skipped:372, case_creation_stamp:406, case_creation_refuses_backdating:424, case_set_key_reservation:493, case_apply_reservation:499, case_alternate_rendering_path:505, case_ordinary_edits:543; red 44/97.
- SC-07: tests/integration/test-plan-team.py:436-509 (DISPOSITION_OBLIGATIONS, per-owner slices, deletion witnesses); red 31 of 154.
- SC-04/05/06: `verify: inspection`, not graded by QA.

## Capability limits / housekeeping
- Static prompt tests prove presence at owner, not agent obedience (stated in BRIEF).
- Redirect writes from bash were inconsistently denied by bash-write-guard (open Q-01 in my expertise); logs not persisted, outputs summarized here.
- Three pins (pin, base, prefix) removed on return via pinned-checkout.py remove.
