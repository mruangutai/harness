# QA gate — FEAT-2229 c3 (pin ab1e42460b5310a9473724edfb574454d39f6ca8)

**BLUF: PASS.** matrix_ok true; unit and integration `satisfied`; signed T-01/T-02/T-03 verifies exit 0; full unit and integration runners exit 0; code-grade `--base dfa52536 --head ab1e4246` PASSING 90, no failing function. F3/SEC-C2-01 fix is closed: the new regression `case_info_string_run_does_not_close_a_fence` was measured RED 99/100 at pre-fix source 48cc5b6a and GREEN 100/100 at the pin. One new **advisory** residual (low, same T-01/SC-02 surface, not F3's suffix defect): a 4+-space/tab-indented fence line inside an open fence closes it. Only my own evidence has examined the F3 fix beyond the dev's red-first receipt; no second-reviewer independence applied by me.

## Pin, equivalence, environment
- Pinned checkout via pinned-checkout.py (persona harness-qa, run r-20261121-validate-c3-validator): HEAD ab1e4246, clean. Removed on return. Review range dfa52536..ab1e4246.
- Equivalence MEASURED: `git diff --quiet 8cf1d93f ab1e4246 -- . ':!.harness'` -> identical (0 code files); `git diff 8cf1d93f..ab1e4246 --name-only` = feature.json, plan.yaml only. Station HEAD 9712ec62 differs from the pin only by feature.json (excluded). Gates still run at the actual pin, not inferred.
- Every command: `env -u HARNESS_AGENT_TYPE -u HARNESS_CONTROL_PLANE_ROOT -u HARNESS_FEATURE_TREE_ROOT` (G-07, G-11).
- Phase 1 (BRIEF + plan only, before source), expected: SC-01 unit shape contract; SC-02 CLI check, one failure each plus controls, plus fence-boundary spoof regression (c2 F3); SC-03 era boundary both sides; SC-07 per-owner prompt assertions with deletion witnesses. SC-04/05/06 inspection. All present; no Phase 1 gap.

## Matrix (control-plane .harness/harness.json)
T-01 cross_module -> always unit + integration (both `active`). T-02/T-03 docs -> always []. functional/eval excluded (DEC-187); locally_run kinds' detect surfaces untouched; component/ui/typecheck unresolved, no such surface changed. Per P-04, each required kind directly exercises T-01: unit script tests the shape contract; integration script drives the real CLI.

## Commands and outcomes (at pin ab1e4246)
| Command | Exit | Result |
|---|---|---|
| T-01 verify (set -eu): unit schema script ; integration dispositions script | 0 | 40/40 ; 100/100 |
| T-02 verify: `python3 tests/integration/test-plan-team.py` | 0 | 184/184 |
| T-03 verify (pipefail): `gen-decisions-index.py --stdout \| diff - DECISIONS-INDEX.md` | 0 | no diff |
| `run-unit-tests.py --kind unit` | 0 | OK; 62 files discovered; 1177 PASS lines; 22.0s wall |
| `run-unit-tests.py --kind integration` | 0 | OK; 89 files discovered; 3032 PASS lines; 114.0s wall; test-plan-merge 12.8s, test-plan-team 9.0s, test-plan-decision-dispositions 36.9s (all exit 0) |
| `code-grade.py --base dfa52536 --head ab1e4246` | 0 | PASSING: 90, no FAIL; `_fence_after` cyclomatic 5, cognitive 4, ABC 12.0, grade 4 vs bar 4 PASS |
- Integration count 3032 vs 2848 at c2: pass-line count is not a case total (G-04); the file counts (62/89) match c2. Unit log's `FAIL BUG-1290` tokens are the mutation-proof's own (G-09); graded on exit codes.
- Advisory (already ruled, unchanged): test-plan-decision-dispositions 36.9s under full-suite load versus T-01's 30s intent; ~12s alone.
- Tree cleanliness: pin clean; primary checkout shows only feature.json modification plus other readers' untracked c3 notes.

## Fail-first (tier: natural RED, semantic, signature-bearing) — F3 regression
- Regression: `tests/integration/test-plan-decision-dispositions.py` `case_info_string_run_does_not_close_a_fence` (:317-322), asserting "a clause after a ```python run inside an open fence fails the DEC-10 row" (discriminating arm) plus a real-section pass control.
- Red commit: **48cc5b6a** (pre-fix source; parent of fix 8cf1d93f). Isolated immutable fixture: `git archive 48cc5b6a` into a temp dir (source byte-checked `cmp` equal to 48cc5b6a check.py, no `not line[m.end():].strip()` guard), overlaid with the test file from `git archive ab1e4246`; no source mutation, no reader run at an old pin. Result: exit 1, **99/100 passed**, exactly one FAIL: `a clause after a ```python run inside an open fence fails the DEC-10 row :: OK T-01 1 anchor(s) resolved` (spoof clause wrongly accepted). Matches red-first-T-01.md claim (99/100).
- Green: pin ab1e4246 -> exit 0, **100/100**. Matches claim.
- red-first-T-01.md inspected: its F3 section names the regression, HEAD 48cc5b6a, 99/100 red, 100/100 green; both numbers independently reproduced. 8cf1d93f's own diff vs 48cc5b6a is check.py `_fence_after` (+6/-3 lines) and test/receipt only.
- Prior fail-first (not re-measured; source equivalence ab1e4246 == 8cf1d93f, and a8b8df61 -> 8cf1d93f check.py delta is only `_fence_after`, so c2's measured F1/F2/F-01 reds and the c2 SC-01/02/03/07 base-pin reds stand): SC-01 13/40 at dfa52536; SC-02/SC-03 44/97; SC-07 31 of 154; F1/F2 92/98 at 98305097; F-01 owner-scoped mutation old-green/new-red. All now green at the pin (100/100, 40/40, 184/184), so none regressed: **F1, F2, F-01 remain closed**.

## F3 edge probes (read-only import of pin's check.py on synthetic docs; no source change)
Behavior of `_fence_after`/`_real_headings`, spoof heading placed after an early-close candidate inside an open ```text fence:
- ```python info run, `~~~` other char, shorter `` run, "``` x" trailing text: fence stays open, genuine DEC-10 section wins (CommonMark-correct).
- Trailing spaces/tabs, longer closer (````), 1-3-space-indented closer, tilde-closes-tilde, ```-vs-~~~ mismatch: all CommonMark-correct.
- **Residual:** a closer indented 4+ spaces or by a tab, inside an open fence, still closes it here (CommonMark: indented 4+ is content), so a following spoof `## DEC-10` heading resolves as the section ("SPOOF CLAUSE"). Also an unfenced 4-space-indented ``` would open a fence (fails closed). Live corpus check: pinned DECISIONS.md has 0 indented fence lines; 220/220 `## DEC-` headings resolve as real. Executed on synthetic input only, not through the CLI.
- Classification: advisory, low, owner T-01 / SC-02, outside F3's stated fix (info-string suffix) and untested by the suite. Not a QA gate failure; lead/code and security readers to adjudicate whether to fold into F3 or backlog. Backtick-bearing info string ("```foo`bar" is not an opener in CommonMark but opens a fence here) is the same fail-closed class.

## SC -> covering test -> evidence
- SC-01: tests/unit/test-decision-disposition-schema.py (case_block_types:71, case_keys:80, case_dispositions:88, case_dec_and_clause_values:104, case_reason_and_successor_values:113, case_set_key_round_trip:139, case_apply_creation_round_trip:162); red 13/40 at dfa52536.
- SC-02: tests/integration/test-plan-decision-dispositions.py case_fenced_heading_is_not_a_section:281, case_info_string_run_does_not_close_a_fence:317, plus c2 list; red 44/97 at dfa52536, F3 99/100 at 48cc5b6a.
- SC-03: same file era/creation/reservation cases (343-554 range); red 44/97 at dfa52536.
- SC-07: tests/integration/test-plan-team.py:424-509; red 31 of 154 at dfa52536.
- SC-04/05/06: `verify: inspection`, not graded by QA.

## Assurance limits
- Static prompt tests prove presence at owner, not agent obedience (BRIEF states this).
- My probe is a pure-function check on synthetic markdown, not a CommonMark reference parser; the CM column is from the spec's indentation rule, not an executed reference.
- Prior-cycle reds (SC-01/02/03/07, F1/F2/F-01) were carried by source equivalence, not re-executed this cycle; only F3 was freshly measured red/green.
- bash-write-guard denied redirect into /tmp (Q-01 reproduces); fixture was built with git archive/tar instead; temp fixtures removed.
