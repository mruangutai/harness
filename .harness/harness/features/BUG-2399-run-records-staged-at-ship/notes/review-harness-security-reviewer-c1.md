# Security review — BUG-2399 — cycle 1

PASS: T-01 introduces Git index mutation from recorded run content; inspection found no concrete exploitable security defect.

Reviewed range: `9eb07b4f3cd235c234a10edddbfe5542c1e85fba..9db1ba98209df49017e73fae13da56f3e240086c`. Inspection only; no tests, grading tools, builds or mutation checks executed. QA owns final execution.

## Scope and boundary assessment

- IN: `prune-run-evidence.py`, its regression tests, ship instructions and DEC-238/index: recorded identifiers and filesystem content become Git pathspec input and committed evidence. OUT: new feature BRIEF/plan/state/feature.json and research/sign-off/red-first/simplify notes introduce no separate executable boundary. Full pinned diff credential screening matched only the synthetic `secret.txt` fixture containing `external`, not a credential.
- T-01 / SC-01: `_recorded_run_ids` rejects empty, dot, dot-dot and separator-containing identifiers (`prune-run-evidence.py:168-171`). `_run_files` rejects linked run roots, uses non-following `os.walk`, skips linked files and excludes exactly the run's top-level `ui/` directory (`:174-186`). Nested directories named `ui` remain ordinary non-UI-lane content. Unrecorded runs never feed staging.
- T-01 / SC-01: staging uses list-form subprocess argv, explicit `--literal-pathspecs`, and NUL-delimited stdin with `--pathspec-file-nul` (`:189-202`). Run/file names cannot introduce shell arguments, Git magic/glob pathspecs or newline-separated extra paths. No shell interpretation occurs.
- T-01 / SC-02: missing-evidence collection and exit-2 refusal precede `_prune` and `_stage` (`:161-165`, `:205-221`). This checks disk file existence, not digest hash validity. Dry-run returns before Git mutation. A Git add failure returns 1, not evidence-refusal 2; it occurs after pruning and is not represented as an atomic refusal.
- T-01 / SC-03: pinned diff preserves keep selection and UI deletion implementation, updates the ship commit to include staged records and confines the decision amendment to DEC-238's ship bullet. The base ship text had no explicit manual force-add instruction to remove; the new text accurately makes that operation unnecessary.

Threat model: a contributor able to supply run identifiers or run filenames must not expand staging outside selected records (Tampering); linked content must not be imported from external targets (Information disclosure); missing recorded evidence must not permit destructive pruning (Tampering). These boundaries are mitigated by the inspected control flow above. No distinct lower-trust concurrent filesystem writer was established; race resistance is not claimed.

Guidance: consulted governing DEC-238 and its pinned amendment. Assigned product `docs/spec.md`, `docs/decisions.md`, `docs/architecture.md` are absent (directory listing confirmed); approved BRIEF/plan provide the patch acceptance, not invented product guidance.

Findings: none. Must fix: none. Open questions: none.

QA commands remain exactly T-01's: `python3 tests/unit/test-prune-run-evidence.py`; `python3 .claude/skills/harness/bin/gen-decisions-index.py --stdout | diff - .harness/harness/docs/DECISIONS-INDEX.md`.
