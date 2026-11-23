# QA c3 — narrow re-validation of the post-CI fix — FEAT-2397

**FINAL VERDICT: ESCALATE, matrix_ok: false** (see "Final gate outcome" at the end; supersedes the PASS wording below). Scoped green facts for the delta:
**Delta only.** The delta `eda06a68..1133d63c` changes one non-notes file,
`tests/unit/omp-hooks.test.ts` (14 lines, T-01's file). It changes zero production files and no SC
text. The three assigned commands are green. This is a scoped fresh result, **not** a whole-matrix
runner receipt: the full unit/integration suites carry from c1/c2 per
`notes/answers-2026-11-23-fix-c2.md` (DEC-230), and I did not rerun them.

Pin: `1133d63c55c8994f7c809f7be73616d049ab163b` (managed checkout, `git rev-parse HEAD` = pin, clean).
Run `r-20261122-7-validate-validator`. Policy blob read:
`git show 1133d63c:.harness/harness.json`. unit/integration/typecheck are `active`; the omp_session_accessor,
handoff_comprehension and issue_types_live kinds are `locally_run`. This delta touches no `detect` surface of those.

## Phase 1 (before reading the source) — expected coverage
From the ruling and `fix-c2.md` only:
1. The FEAT-2225 host-core block passes with the project-root override exported (CI shape).
2. It passes with the override unset (local/old shape).
3. `test-no-distribution.py` case6 stays green: the edited file may not spell the retired/renamed env literal.
4. The block restores the inherited value so later describes are unaffected.
5. The red case binds to the repaired block and discriminates on the override.
6. Production and SC are unchanged (test-only).
7. Appended corrections are accurate against existing evidence.
No Phase-1 expectation lacks a test. (4) rests on the diff plus the full-file runs (below).

## Commands (pin checkout; HARNESS_PROJECT_DIR was not in the ambient env)
| Command | Result |
|---|---|
| `HARNESS_PROJECT_DIR="$PWD" bun test tests/unit/omp-hooks.test.ts` | 247 pass / 0 fail, 1575 expect(), exit 0 |
| `env -u HARNESS_PROJECT_DIR bun test tests/unit/omp-hooks.test.ts` | 247 pass / 0 fail, 1575 expect(), exit 0 |
| `python3 tests/unit/test-no-distribution.py` | ALL PASS, exit 0; all 10 `case6_*` lines PASS |
Raw output kept in /tmp/c3-set.txt, /tmp/c3-unset.txt, /tmp/c3-nd.txt (host temp, not committed).

## Fail-first
Natural RED: `fix-c2-evidence/red-ci-env.txt`. Command `HARNESS_PROJECT_DIR=$PWD bun test
tests/unit/omp-hooks.test.ts -t 'FEAT-2225 expertise_apply through'` at immutable ref
`e1cd52705ef20c2b36d38e00e3e9ad210ad93496`: 2 pass / 5 fail, exit 1. Not rerun.
- Binding: the five `(fail)` names are `FEAT-2225 expertise_apply through the real policyRunner into the
  real core > harness-{product-lead,code-reviewer,dev-ops,orchestrator,backend-dev}` — the describe
  whose hunk is `@@ -4167` of the diff. Every failure is `distill-authority: REFUSED no live claim binds
  runtime … to FEAT-9003-host-core`, i.e. the gates judged the workspace rather than the fixture copy.
- `e1cd527`'s test file is byte-identical to `eda06a68`'s (`git diff --stat` empty) and has 0 occurrences of
  `PROJECT_DIR`, so the red is the pre-fix file, not a different one.
- Discrimination: red appears only when the override is exported and the block does not scrub it. Green with
  it set (247/0, above) proves the scrub works. The unset run proves no regression to the old shape.
- Tier: natural red (the red is the CI-observed failure reproduced locally). Semantic, not signature-absent.
- Not shown: a mutation of just `delete process.env[...]` against my pin. The user-reported red plus my set-run
  green bracket it; I did not add a perturbation proof (out of scope: no widening).

## Fix soundness (QA-visible only; code review owns kind)
`const ROOT_ENV = "HARNESS" + "_PROJECT_DIR"`; the inherited value is captured at describe time, deleted in
`beforeAll`, restored in `afterAll`. case6 is green at the pin, so the assembled name works (the earlier literal
spelling was the `fix-c2.md` follow-up). Restoration correctness rests on the diff plus the full 247-case
file being green in the two reported runs (override set, override unset); test ordering was not varied; I ran no cross-file leak probe.

## Corrections judged
- `c1-evidence/README.md` Correction: accurate. The clone-pair headers set the variable (consistent with
  `fix-c2.md`); BUG-1290 lines are mutation-proof output. Base evidence for `test-factory-config.py` failing
  exists: `c1-evidence/unit-522c94b2-clone-cleanenv.txt:973,1089` (FAIL at base).
- Ship briefing Correction: accurate in the two withdrawals.
- **Minor, advisory (kind: doc, owner: Main / ship briefing, severity: low):** the c1 README correction alone asserts the INV-29 row is
  "the same at base". `checks-job-local.txt` records INV-29 only at `c1eb9eaa`; no base-ref INV-29 receipt exists
  in `c1-evidence/` (grep: INV-29 appears only in that file). The host-only attribution is plausible (path is
  `harness-factories/kaya`, outside the checkout) but the "same at base" half is unsupported by committed evidence.
  Concrete failure: a reader cannot verify base parity for INV-29. Not a gate.
- `checks-job-local.txt` is a CI-faithful local summary at `c1eb9eaa` (a pre-pin ref); the non-notes diff
  `c1eb9eaa..1133d63c` is empty, so it applies to the pin. It shows only 2 job-local reds
  (factory-config, INV-29); omp-hooks and no-distribution are not in the red list.

## Carried vs fresh
- Fresh (scoped): the three commands above, on the pin.
- Carried: full `--kind unit` / `--kind integration` / typecheck evidence from c1 and c2 (the ruling);
  SC evidence for SC-01..SC-12 is unchanged because no production/SC file changed.
- **No whole-matrix runner receipt was written by this run** (I wrote nothing under `runs/…/qa/`).
  If the installed digest gate refuses this scoped PASS for missing `manifest-unit.json`/`manifest-integration.json`,
  the repair is DEC-255's production runner from the pin checkout for each kind (`.agents/skills/harness/bin/run-unit-tests.py --kind unit|integration`
  with the receipt path), which would be a widening beyond this delegated scope; I did not run it.

## Principles applied
- Verification is the product (rule 7): the claim stays scoped to the three measured commands.
- Never falsify the record (rule 15): the INV-29 base gap is reported, not smoothed.

## Final gate outcome (appended)
The installed gate refused the scoped PASS verbatim: "matrix_ok: true but the matrix floor requires integration
(test_matrix.<change_type>.always for this plan's tasks) and kinds: does not report it satisfied. The floor is never
lowered: run the kind, or return FAIL with it missing."
Returned: VERDICT ESCALATE, matrix_ok false, suite pass (scoped), kinds unit=satisfied (scoped commands only), integration=missing
(not run fresh; carried from c1). No runner receipts were written. Repair, if authorized: DEC-255 production runner from the pin
checkout, `run-unit-tests.py --kind unit` and `--kind integration`, writing `runs/r-20261122-7-validate-validator/qa/manifest-<kind>.json`
(widens the delegated scope; not run). Decision needed from Main/validator-lead.
