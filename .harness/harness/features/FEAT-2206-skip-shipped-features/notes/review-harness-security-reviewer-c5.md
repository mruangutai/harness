# PASS — source-only security review

No exploitable security regression identified in T-01 at `7b8e2e1f485db72a4a574e04738533cb0ab821ed`. In scope: relaxing historical validation changes the tampering boundary between repository-authored records and audit enforcement. No tests, probes, grading, builds or linters executed; this is not runtime assurance.

## F-1 / Q-02 first

The approved operator ruling requires salvage, not a waiver (`notes/answers-validate-c2-validator.md`); T-01 now owns `check_state/corpus.py`. Source inspection closes the previously missing branch-claim path: `_branch_entry` re-reads only strict-refused, record-bearing, leniently shipped entries, preserving census identity (`corpus.py:145-153`). INV-52 still obtains its entire landed population through `feature_corpus.records`, and fails on census errors (`corpus.py:156-175`). `branch_claims` accepts only non-sentinel strings and uses the census ID, not raw JSON identity (`feature_corpus.py:445-459`). `_PLAN_YAML` is declared (`table.py:166`). The new regression binds the exact superscript-parent/shared-branch case in full and sparse checkouts and rejects shipped parse diagnoses (`tests/integration/test-check-state-shipped.py:258-270`). `notes/red-first.md`, Rework round 3, records baseline/c2 FAIL and candidate PASS; those outcomes were not independently executed here.

## Whole-feature boundary assessment

- SC-01/02: subject filtering precedes artifact loads (`ctx.py:223-233`); missing, unreadable and duplicate status keys retain checks (`ctx.py:59-78`). Explicit shipped selection follows layout/subject preflight (`runner.py:308-326`). A repository writer can declare done by design (DEC-252), not acquire a new principal or permission. This checker is not a ship-attestation authority.
- SC-03: raw shipped mappings remain comparison-only; active records still use `record`, scoped population still excludes in-progress siblings and replaces only local identities (`ctx.py:421-459`). INV-24 shape-checks factory/repository/container/number inputs and preserves cross-feature ownership while suppressing historical record grading (`board.py:74-269`). INV-29 remains repo-level and unchanged (`worktrees.py:317-333`); failed terminal lookup remains a finding, not an exemption (`worktrees.py:250-266`).
- SC-04: INV-28/30 implementations and table entries are removed, not retained as alternate enforcement; retirement matches DEC-252. The shared accessor converts numeric ValueError into its documented strict refusal rather than accepting an invalid active record (`artifact_accessors.py:145-163`).
- Changed-surface census: all 22 paths assessed: eight production/schema paths in scope for enforcement/input handling; two decision/index paths in scope as policy authority; twelve test/fixture paths assessed for subprocess/output and boundary assertions, with no new production privilege surface. Full-diff credential/injection sweep found no added credentials, dynamic execution, network destination or spreadsheet/HTML export sink. Subprocess additions are test-only argv lists. Existing diagnostic output is not executed by this change.

## Evidence limits and open questions

Independent `git diff 8cdbb3620037f9fd8c86621225fcaedd9555edaa 7b8e2e1f485db72a4a574e04738533cb0ab821ed` shows only feature.json review metadata differences: code equivalence established. The retained merge log ends with 146 files and `verify-exit=0` for **8cdbb362**, not exact-pin execution. The claimed 62 passing code-grade records remain delegated evidence, not a security execution result. Pinned production/test/decision paths match the inspected working files (empty pin-to-working diff).

Q-01, nonblocking: owner should reconcile T-01 YAML-mapping wording with DEC-252 column-zero text classification; retained adopted behavior is not a new security finding. No must-fixes; no source changes; no children spawned.
