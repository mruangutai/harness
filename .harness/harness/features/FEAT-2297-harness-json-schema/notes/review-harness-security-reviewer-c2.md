# Security c2 — PASS, scoped in

No concrete exploitable regression found in the complete pinned input-boundary diff. This is static security clearance, not unconditional ship readiness or fresh suite evidence.

**Range:** `9fd1f6b414ed683cd5f5bcca4ad5fe17c35e0568..fa6a38009e54f4380daebd59a78629a68de7c1d0`; requested `git merge-base <pin> origin/main` returned that base. Prior c1 pin: `47d2e50243ad7fb080e13ef48115756d7d3b7c61`.

**Scope census:** all 175 changed paths considered. Production readers, schema, gates, config/template/fleet changes and canonical-reader classification are in scope as policy/remote-input boundaries. Tests and contract docs are assurance evidence; feature records, plans, reduction tooling, generated index and run receipts are reviewed as authority/record surfaces, not new execution endpoints. Full-diff added-line credential sweep found no exposed credential requiring a finding. No new dependency, export interpreter or user-selected schema URL was introduced.

## Boundary assessment and task ownership

- **T-01 / SC-01, D-01–D-04 — input → policy (T/E):** `artifact_accessors.py:76–97,465–476` shares strict duplicate/non-finite-token decoding and mapping-root refusal. `harness_config.py:98–123,162–177` defaults only absent named keys before validation; required kind/board/matrix fields are not filled to conceal incomplete records. Unknown structural keys close; underscore prose remains the signed exception, while `_matrix_provenance` is explicitly constrained. Schema resource retrieval refuses remote references (`harness_config.py:48,76–90`).
- **T-01 newline closure:** actual pinned schema adds `not: {pattern: "\\s"}` to both repository and DEC identifier rules (`config-schemas/harness.json:144,181`), rejecting the terminal newline that `$` alone admitted. Pinned unit refusal rows bind both inputs; `notes/receipts/fix-c1-red.txt` records their earlier failures and `fix-c1-green.txt` their later passing run. Root-refusal and missing/unparseable upgrade-source assertions bind already-correct behavior; no natural red is claimed for those additions.
- **T-03 / SC-02, SC-06 — commands/config → governed action (T/E):** close, branch and merge gates recognize actions before loading config, then refuse invalid/missing config before sync exemptions. Compound repair-plus-action is not exempt. Check-state records the diagnosis and stops config-dependent grading (`check_state/ctx.py:333`, `runner.py:326`). Non-config digest schemas, run markers and comparison data use the strict generic accessor, not configuration defaults.
- **T-03 / SC-02 — remote main → local authority (S/T):** `factory_config.py:155–195` resolves fleet membership/default branch before memo lookup, validates fetched text, caches successes only, and retains contextual refusal without disk fallback. Bound-target identity checks remain in `feature_schema.py:519–526`; board-required operations still refuse null.
- **T-01 / SC-03 — repair input → filesystem (T):** `upgrade-config.py:204–252` diagnoses missing/unparseable sources, validates the candidate before invoking the backup/atomic writer, and keeps check-only read-only. `artifact_accessors.py:479–499` replaces only after temporary-file flush/fsync. Config-only does not install a manifest.
- **T-04/T-08 / SC-07, D-08:** the named TypeScript `resolveBudgetNumber` exception remains advisory and budgets-only; production TypeScript is unchanged. SPEC §2 and DEC-256 agree with the schema and retain that exception, without claiming condition evaluation shipped.

## Assurance and settled dispositions

No suites, probes, builds, lint or formatters executed. QA's fresh configured runs remain independently owned. Historical raw integration red is preserved: only `test-corpus-real-owner.py` against installed owner v2 has the settled E-OWNER CI disposition; ship still requires green PR CI and its run ID, not a waiver of any other failure (`qa-config-reduction.md:370–402`). The refreshed reduction measurement names `8c945a8e`; its tail to this pin changes records only, not measured test/helper populations. SC-08 delegated authorization/amendment, INV-13 retirement and #2393 deferral are accepted settled inputs, not reopened findings.

**Findings / must-fix / open questions:** none.
