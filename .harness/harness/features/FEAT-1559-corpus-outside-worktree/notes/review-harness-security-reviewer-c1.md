# Security review — cycle 1

**FAIL — one medium, must-fix corpus-discovery fail-open.** Pinned range: `e8d868f78a6ec43880598af5c5873f5daa8ba985..0e8301a58a7de7dc23a067005c9aa8b3ee528de0`.

## Finding SEC-01

- **substance / med / scope none** — `.claude/skills/harness/bin/check-plan-routes.py:790-795,809-824,909`: default discovery resolves `corpus_roots`, lists existing directories and returns the resulting plans; it never compares landed expected directory names with reached names. `feature_corpus.py:259-268` explicitly documents that `corpus_roots` performs no tracked-structure check.
- **Scenario:** an operator, or an actor with unusual owner-root filesystem access, removes a tracked landed feature directory containing a nonterminal plan with routing violations, while other feature directories remain. A structurally correct sparse feature checkout still passes its local layout check. The missing landed directory never enters the owner scan, so its violations disappear without the required named missing-set refusal. This is detection bypass, not a newly granted ability to write the owner corpus. The scenario is a static control-flow inference, not an executed mutation.
- **Binding:** SC-04; T-03; execution owner **main session**, `main-session-direct` under DEC-174. Require owner-root expected/reached name-set validation before this default scan, preserving explicit-path semantics, and a missing-landed-directory negative control paired with the normal scan.
- Independently corroborated by code reviewer ControlledPossum at the same pinned site. Security severity remains med because the access/precondition is unusual; the literal approved criterion makes it blocking regardless.

## Other assessed boundaries

- Corpus ownership/ordinary absolute reads: `feature_corpus.py:141-199,236-287`; no sibling or git-content provider introduced. Main corpus is mutable landed disk data by signed ruling, not a snapshot guarantee.
- Governed Write/Edit and Bash writes: guard authorization remains checkout-bound; `tests/integration/test-feature-corpus.py:210-246` supplies own-feature allow and main-corpus exit-2 refusal controls. `harness_boundary.py:188-245` normalization uses pointer files, not git subprocesses. Digest authorization stays local (`digest_destination.py:24-33`).
- Gate decisions: structural and dirty findings are separated (`feature_corpus.py:298-364`); merge/branch consumers map discovery failure to deny payloads. No shell interpolation introduced by list-form subprocess calls; quoted hook arguments preserve checkout paths.
- Repair/data loss: `worktree-state.py:166-196,253-280` preclassifies class-C work before sparse mutation and removes only empty residual directories. Post-hook exit 0 is intentional; subsequent structural verification is the enforcement boundary.
- Full 75-path census assessed: enforcement/readers/hooks and changed regression fixtures are in scope; documentation/feature records supply scope and evidence, with no credential-bearing addition found in a full-diff credential sweep. No new dependency, network, spreadsheet/export or tenant-auth surface.

Read approved brief, signed plan, state, feature identity, research/rulings and task/non-regression receipts. Immutable structural diff confirms code-final `69e3d819` to this review pin changes only this feature's records; suite receipts are not re-execution claims. No tests, builds, linters, formatters or mutation probes run. Hardlink strengthening (#1638/D-14) and post-merge conversion (SC-10/#2101) are explicitly excluded, not findings.

Open questions: none. Source changes: none. Managed security pin removed before return.
