# QA gate — BUG-2305 T-01 — pin 297913318472d066ecb9d5eb3f83ee2ca82c3ad7 (base 7f9cc9d8)

**VERDICT PASS.** matrix_ok true. `unit` satisfied (164/164 at the pin). Fail-first reproduced by me on SC-01 and SC-03 (5 named reds on the base hook). SC-02 refusal tests are green-on-base by construction, so their discrimination is unshown (advisory, not a finding). No findings ranked above advisory.

## Scope and binding
- Checkout: managed pin (`pinned-checkout.py add`, run 2026-11-22-02-validate-validator, persona harness-qa), `git rev-parse HEAD` = review_sha. Ambient feature worktree HEAD is 5928feea (station commit after the pin, dirty `feature.json`); it was NOT used for any run. Pin is an ancestor of that HEAD. Pin removed on return.
- `git diff --stat 7f9cc9d8 <pin>`: 14 files. Product files: exactly T-01's four (`.omp/extensions/harness-hooks.ts`, `tests/unit/omp-hooks.test.ts`, `DECISIONS.md`, `DECISIONS-INDEX.md`); the rest is feature-directory records. No file outside T-01 ownership.
- Product docs/spec.md, decisions.md, architecture.md absent (BRIEF); not substituted.

## Phase 1 (from BRIEF/plan only, before reading source)
Expected tests: (a) per-persona x {flat, tasks[]} exact-copy + strict accepted, with reordered keys; (b) mixed batch positions; (c) refusals: changed schema, permissive/other modes, lone schema, lone mode, batch top-level, non-harness, each flat and per item, naming field/location; (d) accepted item does not mask later invalid; (e) bundle-load failure stays fail-closed; (f) no `additionalContext` note on success, unrelated context retained; (g) existing no-control injection coverage retained. Gaps vs Phase 1: none (every item maps to a test below). DEC-237 text/index = SC-04 inspection, not a QA test.

## Matrix (harness.json at control plane)
- T-01 change_type bugfix: `always: []`; `when`: unit if touches_runtime_code -> TRUE (hook .ts changed); integration if fix_confined_to_tests_and_contract_docs -> FALSE (runtime source changed); `__bug_class__` placeholder never fires (repo gotcha G-08). Required kind: **unit** only.
- `unit` cmd `run-unit-tests.py --kind unit`, active. Discovery: 63 files, 131-test final script, rc 0 (`env -u HARNESS_AGENT_TYPE`), run once at the pin after inspection.
- Disclosure (#2257, approved, not a finding): the runner does not execute `tests/unit/omp-hooks.test.ts` (grep of `run-unit-tests.py` for `.test.ts`/`bun` returns nothing; no omp-hooks.test line in its output). The binding evidence for the kind is the T-01 verify clause, run verbatim at the pin: `set -eu; bun test tests/unit/omp-hooks.test.ts` -> rc 0, **164 pass / 0 fail**, 1218 expect() calls, 13.0 s. Runner rc 0 is therefore adjacent, not binding.
- typecheck: cmd null/unresolved (#2257, disclosed in BRIEF); not run, not a finding. integration/component/ui/functional/eval: not required for this change.

## fail_first (my own reproduction; builder's note graded)
Method: in the disposable pin, `git checkout 7f9cc9d8 -- .omp/extensions/harness-hooks.ts` (hook == base, verified by `git diff --quiet 7f9cc9d8 --`), pinned test file unchanged, `bun test tests/unit/omp-hooks.test.ts` -> rc 1, **159 pass / 5 fail**, all assertion failures (not load/import errors). Hook restored to the pin; `git diff --quiet <pin>` clean. Log was transient (`/tmp/qa2305-red.log`); outcomes below quoted from it. Tier: natural RED against base source (strongest tier), semantic assertions.

| SC | Test (pin line) | Base failure |
|---|---|---|
| SC-01 | `BUG-2305: every persona's injected bundle, copied back strict, is accepted flat and per item` (tests/unit/omp-hooks.test.ts:1743) | `toEqual` diff: flat exact copy refused (block true) |
| SC-01 | `BUG-2305: a batch accepts copies at any position beside plain and non-harness items` (:1767) | `block` expected undefined, received `true` |
| SC-02 | `BUG-2305: an accepted copy never masks a later invalid item` (:1836) | reason named `tasks[0]...` too: accepted item refused; expected `tasks[2]` only |
| SC-03 | `injects every one of the 16 personas' own strict bundle...` (:1687) | `not.toHaveProperty("additionalContext")` received the #2240 note |
| SC-03 | `injects into a flat governed dispatch and keeps its other fields` (:1714) | `toEqual`: extra `additionalContext` |

Same five names and failure kinds as builder's `notes/red-first-T-01.md`; the claim is reproduced, not adopted. Limits:
- Fail-fast loop: the SC-01 per-persona test (:1743) is one `test()` over `DIGEST_PERSONAS`; on base it stops at the first persona (`harness-ai-dev`, per builder note). Pre-fix red is shown for that first persona only; red for the other 15 is **[INFERENCE]** (base refuses any caller control for every target). Post-fix, the loop passes all 16 (`DIGEST_PERSONAS` length 16 asserted at :2318; 16 `.omp/agents/harness-*` and 16 digest-schema files exist).
- SC-02: the refusal-variant tests (:1789 every other control flat/per item, :1820 batch top-level, :1853 unloadable bundle) **pass on base**, because base refused everything. Their discrimination against an over-permissive hook is unshown (no mutant flipped by me, e.g. accept any strict, or key-order via JSON string). Say "unshown", not "cannot discriminate". Preserved/non-harness and top-level refusal coverage stays green at the pin (164/164). Only :1836 is a red SC-02 criterion.
- Reordered-key arm: the test feeds a deep-reversed copy (:1744-1760 region) beside a plain clone; the red run stops on the first (plain) copy, so base red does not isolate the reorder arm. Source uses `isDeepStrictEqual` (hook line 379-391), key-order insensitive; arm green at the pin.

## SC coverage (sc_evidence)
- SC-01: tests/unit/omp-hooks.test.ts:1743 (16 personas x flat/item x plain/reordered), :1767 (mixed positions).
- SC-02: :1789 (12 refusal variants, flat and item, field+`tasks[0].` location asserted), :1820 (top-level x3), :1836 (no masking), :1853 (load failure, no guard calls). `guardCalls` is asserted empty on each refusal (no claims/side effects).
- SC-03: :1687, :1714 (note removed; no `additionalContext`), :1862 (no-control path retained). `INJECTION_NOTE` / `SCHEMA_INJECTION_NOTE`: grep over `.omp` and `tests` at pin returns no hits.
- SC-04: inspection (verify: inspection) — outside QA's test gate; not graded here.

## Findings
None ranked. Dismissed/advisory, all T-01, kind form, severity advisory, reader harness-qa:
1. Runner does not run the bun test file (P-14 pattern) — dismissed: #2257 approved/disclosed; the verify clause was run directly.
2. SC-02 refusal arms green on base — dismissed as not a defect (base refused all); discrimination unshown, no mutant run.
3. Fail-first per-persona shows first persona only — advisory, stated above; post-fix coverage of all 16 is asserted.
No SCOPE CHANGE; no open question required.

## Principles applied
None cited from craft leaves (not read this run). `harness-verification-rules` governed: Phase 1 then 2, five kind states, fail-first by own reproduction, perturbation in a pinned checkout.
