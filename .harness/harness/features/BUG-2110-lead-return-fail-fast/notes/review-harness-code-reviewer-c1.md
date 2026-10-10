# Code review — BUG-2110 — c1

PASS: no spec violation or actionable code-quality defect found in the pinned change.

- Reviewed `63cac11a3216aa8d34792665a05fcb185f7cf73b..a83198b1740c4d5f92905495695ec94ebe42779a` in the assigned feature worktree. `git merge-base origin/main <pin>` agrees; tracked tree was clean. Full commit list contains no human-tagged or foreign commits.
- Stage 1: BRIEF SC-01–SC-04 and signed D-01 read before diff. T-01 assertions/evidence, T-02 enforcement, and T-03 producer migration serve those criteria; feature lifecycle records are in scope. Direct-build handoff reports deviations, not a lead `amendments` list; reuse of user-site dependency loading and unchanged existing return tests do not weaken acceptance.
- SC-01 inspection: `dispatch-guard.py:606` reuses `registered_destination`, and `:688` invokes preflight before `live_claim`/claim creation. All three leads share this path.
- SC-02 inspection: `dispatch-guard.py:642` selects checkout-local canonical `plan.yaml`; `:653` calls the existing pending-status predicate. Product absent-plan drafting is allowed; standalone validator/scope missing-plan starts refuse. D-01 mission parsing preserves engineering-lead exemption (`:520–555`).
- SC-03 inspection: `dispatch-guard.py:588` preserves the actual binding error plus feature/lead and registration/reconciliation remedies; `:657` supplies plan target/status context and the legitimate pre-signature phase remedy.
- SC-04 inspection: no diff changes to `digest_destination.py`, `validate-digest.py`, or `harness-hooks.ts`. Real startup/bind/return sequences and exact destination-byte assertions are in `tests/integration/test-lead-start-return.py:341–511`; invalid identity/binding/artifact returns assert refusal with unchanged bytes alongside successful append controls.
- Stage 2: expected read/import failures explicitly refuse; authorization and YAML predicates are reused, not copied. Tests execute production subjects in private trees and pair refusal/absence checks with successful controls. `notes/evidence-T-01.md:24–127` records baseline startup failures and independently discriminating missing-binding/pending-only mutants; this is historical evidence, not a reviewer execution claim.
- Mechanical Python grade: QA reports `code-grade --base 63cac11a --head a83198b1 --json`: 96 passing, zero non-PASS, no ungraded functions. Evidence: `notes/review-harness-qa-c1.md`. Thus `code_grade: pass`, no grade-2 reasons required. No builds, tests, grading, linters, formatters, or mutants executed by this reviewer.

## Principles applied
- Model the Domain: accepted the shared `LEAD_SQUADS` authorization policy instead of requiring another runs predicate.
- Delete First: kept the existing return authorities and hook intact; no additional authorization module or compatibility seam required.

Open questions: none. QA owns gate execution. No developer receipt with a Principles applied section exists for these main-session-direct tasks.
