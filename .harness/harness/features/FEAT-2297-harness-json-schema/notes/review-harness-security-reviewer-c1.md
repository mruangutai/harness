# Security review — FEAT-2297 — c1

PASS: no attributable exploitable security defect identified by static inspection. This is not a ship/UAT approval.

Reviewed: `9fd1f6b414ed683cd5f5bcca4ad5fe17c35e0568..47d2e50243ad7fb080e13ef48115756d7d3b7c61` (base independently derived against `origin/main`). Reads used pinned Git objects; no checkout created.

## Scope and boundaries

Full changed-path census: 163 paths. In scope: 30 production bin paths, config/template/fleet changes, reader classification, and supporting tests/docs/receipts as evidence of authority and exceptions. Other feature records, generated index and plan/reduction tooling affect review evidence, not a new remote execution surface. Full pinned diff also received a credential-pattern sweep; no credential-shaped match requiring investigation was found.

- **T-01, untrusted config → policy (T/E):** `artifact_accessors.py:93` routes the mapping into `harness_config.validated`; defaults fill absent keys, not invalid present values. Duplicate keys and literal NaN/Infinity use the existing strict decoder. Unknown operational keys, conditional repo requirements and status-bearing records are enforced by `config-schemas/harness.json`. This inspection is not a claim of exhaustive numeric/resource-limit verification.
- **T-03, Bash → governed action (T/E):** `branch-create-gate.py:154`, `gh-close-gate.py:245` and `merge-gate.py:571` validate matched actions before sync; compound repair/action has no added exemption. Existing recognizers and closed crash boundaries remain. Invalid check-state config stops grading (`check_state/runner.py:326`), rather than substituting permissive policy.
- **T-03, fleet → remote authority (S/T/E):** `factory_config.py:157` fetches only the registered member's configured default branch, retains source/ref diagnosis and caches only successful validation keyed by repo/ref. `feature_schema._bound_mirror_binding` still requires repo identity equality and enabled sync before use. No new local fallback. `factory_decompose.py:516` resolves config before issue creation/backfill.
- **T-01, legacy input → repair write (T):** `upgrade-config.py:224` validates the candidate before backup/replacement; raw strict input does not authorize governed actions. Config-only migration writes no product manifest. Atomic writer implementation is unchanged.
- **T-01, schema → resource lookup (I/E):** `harness_config.py:82` installs a refusing reference retriever; config input cannot supply a schema URL. No new shell interpolation, export interpreter, network destination or dependency was introduced. Diagnosis output includes invalid values and source context, but no new secret source or cross-user disclosure path was established.

## Signed exceptions and inspection

SC-07 inspected against pinned SPEC §2/§2.2/§9, DEC-256, templates README and checkout-upgrade reference: absent-map defaults, null-board/sync-off behavior, explicit repair and the advisory TypeScript budgets-only exception agree with the intended authority model. Active/null runner validity is not permission to skip QA. INV-13 retirement, smoke fleet removal and D-06 measurement are signed choices, not security findings.

## Open question

SC-08 / T-09: `notes/uat-kaya-migration.md` explicitly records delegated advisor review/authorization, not the operator's personal review. Standing delegation supplies authorization; landing does **not** establish the literal personal-review criterion. PM/validator must obtain operator evidence or an explicit accepted amendment before claiming that ship gate passed. No unauthorized-merge exploit is alleged here.

Verification: static inspection only; no builds, tests, linters, formatters or probes executed. Prior receipts are not this reviewer's runner evidence. Candidate semantics above are not claims about the installed control-plane version. QA should run the pinned loader, reader, upgrade and configured unit/integration verification; production runner receipts remain QA-owned.
