# FEAT-2297 ship review: a schema-validated harness.json contract (v3)

**Shipped.** PR #2395 was squash-merged to `main` as `b3c1041c` at 2026-11-22T23:00:31Z, after CI
run [45080557988](https://github.com/mruangutai/harness/actions/runs/45080557988) passed on the
merged head `ca9127c0`. Kaya was migrated first (mruangutai/kaya#29, merged as `b9dec8df`).

**One thing needs you personally:** SC-08 asked you to review and authorize the Kaya PR. Under your
run-level instruction ("defer questions, approvals to the fable-advisor"), the advisor did both, and
a signed amendment records that. Please accept it after the fact by looking at kaya#29. If you
decline, the recorded remedy is reverting `mruangutai/kaya` main's `.harness/harness.json` to the
pre-merge blob `d96b4484`.

No report round was spawned; this briefing was assembled from these digests on disk:
`runs/2026-11-22-01-plan-product/digest.md`, `runs/2026-11-22-02-plan-product/digest.md`,
`runs/validate-validator/digest.md` and `runs/fix-c1-validator/digest.md`. The goal-check is
`notes/research-FEAT-2297-harness-json-schema-goalcheck-validate-c2.md`.

## Definition of done, graded

| Perspective (as signed) | Verdict | Discharged by | Evidence |
|---|---|---|---|
| **operator**: invalid or missing configuration refuses work with a useful diagnosis, without losing the ability to repair it. Harness and Kaya accept the current contract after a deliberate upgrade, and Kaya's change reaches main only through my approved PR. | met (SC-08 under amendment) | SC-01, SC-02, SC-03, SC-08 | goal-check c2 §Perspectives; `notes/uat-kaya-migration.md`; BRIEF.md SC-08 amendment |
| **code maintainer**: one configuration contract and read boundary; valid test setup changes in one place; affected test code is smaller without losing meaningful policy coverage. | met | SC-04, SC-05 | fixture census (0 findings); `notes/qa-config-reduction.md` (Gate A −583 lines, 152 dispositions, 67 files) |
| **reader**: enforcement, exceptions, migration and test reduction trace to falsifiable evidence, including unit and integration checks and a pinned migration/reduction record. | met | SC-06, SC-07, SC-09, SC-10 | canonical reader audit (0 unresolved across 101 files); QA manifests `runs/fix-c1-validator/qa/`; PR CI runs 45080316265 and 45080557988 |

## What the validation found, and what happened to it

- **`validate-validator` @47d2e502: ESCALATE** (`runs/validate-validator/digest.md`). It raised a
  real defect: `github.repo` and signed `DEC-NNN` identifiers accepted a trailing newline, because
  Python's `$` matches before a final `\n`. It also found two missing regression assertions, a change
  record citing a nonexistent Kaya receipt, and two escalations: E-ACCEPTANCE (SC-08's personal
  review) and E-OWNER (one integration file red against the main checkout's pre-merge v2 config).
- **Fix c1:** whitespace is excluded from both identifiers (red then green receipts
  `notes/receipts/fix-c1-{red,green}.txt`), the assertions were added, and the change record was
  corrected. Advisor ruling #6 approved the SC-08 amendment and disposed E-OWNER to PR CI.
- **`fix-c1-validator` @fa6a3800: FAIL** (`runs/fix-c1-validator/digest.md`). Code, security, UI
  and goal-check passed and every SC was met. QA's FAIL rested only on the outstanding PR-CI proof
  for the real-owner case.
- **First PR CI run (45079815601) was red** on two things local checks had not covered. T-10 was at
  51 DEC-182 budget items; it was cut to 44 by depending on T-08 alone, which keeps the same
  transitive closure. The readers test's module loader also failed under CI's older Python; it now
  registers the module in `sys.modules` before executing it (reproduced under Python 3.9.6: the same
  5 failures before the fix, green after). Advisor ruling #7 waived a third validator run for this
  test-only, order-preserving delta, conditional on green CI.
- **CI run 45080316265: success.** It included `PASS test-corpus-real-owner.py` and
  `PASS test-harness-config-readers.py`, which discharges the fix run's FAIL (judgement recorded in
  `feature.json`).

There are no open blocking questions. One non-blocking question came from validation (OQ-KIND-ENUM,
backlog B-4).

## Spend

4 runs, 87 wall-clock minutes (29 of them rework, 1 rework round); tokens were not measured. The
ledger holds 25 judgements.

## Amendments

| at | decision | reason | overruled |
|---|---|---|---|
| 19:44:08 | T-03.intent | Operator ruling: move the two non-config reader migrations into T-01. | no |
| 19:44:24 | T-01.files | Same ruling. | no |
| 19:44:30 | T-03.files | Same ruling. | no |
| 19:44:35 | T-01.intent | Same ruling. | no |
| 20:19:53 | T-03.files | Advisor: five unowned suites broken by T-01..T-03 fallout join T-03 (fixture/data repairs only). | no |
| 20:19:55 | T-03.verify | Same ruling. | no |
| 20:21:52 | T-03.files | Advisor: one jsonschema guard (route through feature_schema). | no |
| 20:30:25 | T-04.files | Advisor: split `_classified_disposition_findings` back to grade ≥4, behaviour-preserving. | no |
| 20:58:27 | T-06.files | Advisor: load feature_schema via `load_repo_module`; map its failure to ArtifactAccessError. | no |
| 21:09:06 | T-07.files | Advisor: restore the user-site path after first-party imports in the sweep. | no |
| 21:27:12 | T-10.verify | Ruling #4: measure against `git merge-base <review-ref> origin/main`. | no |
| 21:27:15 | T-10.intent | Ruling #4: Gate A (existing files strictly negative) and Gate B (new files enumerated); total reported. | no |
| 21:27:17 | T-10.files | Ruling #4: minimal budget fixture; INV-13 and dead unpinned branches retired. | no |
| 21:28:21 | T-10.files | seams.py and the handoff docstring stay unchanged (accurate history). | no |
| 21:31:58 | T-10.files | Pin a sha256-checked copy of the 152-row inventory. | no |
| 21:32:19 | T-10.files | Retiring INV-13 updates the check-state table contract test. | no |
| 21:38:15 | T-10.files | Census gaps closed; 6 raw fixtures migrated to the builder. | no |
| 21:44:02 | T-10.files | Product-checkout upgrade command needs `--templates`; documented. | no |
| 21:53:27 | T-10.files | Simplify pass before pin. | no |
| 21:56:14 | T-10.files | feat59 predicate becomes a named helper (test grade bar). | no |
| 22:15:12 | T-09.files | Era-start prose corrected to "absent = null" (DEC-256). | no |
| 22:36:15 | SC-08 | Ruling #6: delegated review and authorization; your acceptance is requested here; decline remedy: revert kaya to `d96b4484`. | no |
| 22:53:01 | T-10.verify | Intended a one-line scalar to fit DEC-182. **It changed no counted item** (the serializer keeps the block), so its reason overstates its effect. | no |
| 22:5x (commit `15d67484`) | T-10.depends_on | T-01..T-08 → T-08: same transitive closure, 51 → 44 budget items. **No ledger judgement**: `plan-merge amend` records judgements only for intent/files/verify (backlog B-1). | no |

overrule rate: 0/24

## Proposed backlog

Existing related issues stay as filed: #2393 (simplify-pass leftovers from this feature), #2283,
#2293, #2257, #2329, #2109, #2107, #2106, #2229, #2225, #919.

| ID | Nature | Item |
|---|---|---|
| B-1 | bug | `plan-merge.py amend` changes signed task fields other than intent, files and verify (e.g. `depends_on`) without appending an amendment judgement, so the ledger can miss a contract change. |
| B-2 | chore | The DEC-182 per-task budget (`check-plan-routes.py`) runs in CI but not in local check-state, so a budget breach surfaces only after a PR opens. |
| B-3 | chore | Other test loaders that call `spec_from_file_location` without registering the module in `sys.modules` (e.g. the probe loader in `test-harness-config-readers.py`) carry the same latent Python-version failure. |
| B-4 | enhancement | QA's kind-state contract has no "ran and red" state; an executed red kind is encoded as missing (OQ-KIND-ENUM). |
| B-5 | chore | The non-object-root refusal is asserted for an array only; add null, number and string cases. |
