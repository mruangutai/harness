# Security fix-c1 — PASS

**The empty-kind PASS policy bypass is closed by static inspection; no actionable security finding remains in T-01's reviewed delta.** Scope IN: agent-controlled QA reports cross the policy-authority/acceptance boundary. Reviewed `685e861a..2f50e8bb1f5e6442742c53e1e2997a8be341d58b`, using the exact five-path dispatch delta, not HEAD or the installed hook.

## Boundary assessment

- **Report → acceptance (T):** `validate-digest.py:1796–1823` now requires policy for reported kinds, started work, or PASS/matrix_ok true. Thus empty kinds and absent trusted feature no longer bypass `_qa_policy` on a valid PASS. PASS with false/n/a matrix is independently refused by the existing gate-field checks (`:1597–1644,1697`). A missing-policy error permits only kind-free BLOCKED/ESCALATE; a reported kind still refuses. With policy established, started-task omission enforcement remains active even for BLOCKED/ESCALATE. This is an explicit stop path, not coverage or permission to ship.
- **Runtime identity → feature/pin (S/T):** `_hook_validate` supplies QA's registered feature separately from the digest artifact (`:3124–3134`); registration checks unique checkout-local matching identity (`digest_destination.py:23–68`). `_qa_policy`, `_qa_code_repository`, `_qa_review_commit` (`validate-digest.py:418–483`) retain malformed-binding refusal, exact fleet membership, canonical workspace selection and agreement of externally supplied pins. Digest text cannot choose an alternate policy ref or object store.
- **Pin → local Git/blob (T/E):** commit resolution remains list-form argv, rejects option-like revisions and uses `--end-of-options` (`code_grade.py:290–301`). Policy reads use the resolved commit and constant `.harness/harness.json`, then canonical schema validation (`validate-digest.py:486–500`). No new shell, network, dependency or credential surface. Operator-owned fleet, feature records and Git configuration remain trusted, not capabilities granted to the reporting agent.

## Prior must-fix disposition

1. **High empty-kind bypass: resolved by inspection.** Real CLI empty-PASS refusal and kind-free BLOCKED controls are now present (`test-validate-digest.py:7180–7202`), alongside unpinned hook BLOCKED acceptance. Migrated acceptance assertions retain their content under `run_qa_pinned_cases`.
2. **Medium fixture audit: source remedy present.** `_kp_write_policy`/`_kp_pin_policy` use shared `write_config`; deliberately malformed P3 truncates `build_config` output. No independent audit execution claimed.
3. **Medium omission proof: source remedy present.** `KP_OMISSIONS` crosses BLOCKED/ESCALATE/FAIL with true/false/n/a and PASS with true for both statuses; `_kp_refuses` requires exit 2, the kind and both repairs, excluding tracebacks (`test-validate-digest.py:7103–7143`).
4. **Low instruction error: resolved by inspection (SC-05).** Changed verification-rules SKILL:36–43 says INV-49 is BRIEF disclosure only, never waiver; SPEC §9:1456–1462 and DEC-256:8544–8553 agree on the missing-policy stop path.

## Assurance and scope

Static review only: no tests, builds, lint, formatters, complexity tools or smoke runs. Read `notes/receipts/t01-fix-c1-{red,green}.txt` as supplied receipts: they report the prior CLI bypass red and fixed group green, but the green receipt identifies an uncommitted candidate, not an independent execution at this review pin. QA owns pinned execution assurance and the authorized focused command `python3 tests/integration/test-validate-digest.py --only run_feat2398_qa_policy_cases`.

Full-range path census and credential-term sweep found no introduced credential material; imported BUG-2399/BUG-2420 production changes are outside T-01 and not attributed or re-reviewed here. Feature/run records and receipts are publication/provenance inputs; changed fixture helpers add no production ingress. Product `docs/spec.md`, `docs/decisions.md`, `docs/architecture.md` are absent as disclosed; AGENTS.md points to the existing Harness authority. No invented guidance, source edits or changed scope. Findings: none. Open questions: none.
