# BUG-2190 c1 code review — PASS

Both prior med must-fix omissions are closed in the pinned tests. No new substantive findings; spec compliance passes before the quality assessment below. Execution assurance remains QA-owned.

## Scope and immutable evidence

- Reviewed `924c548690a8a7c0e51baf5ad2485a97d7219b98..cf13aab63f308c1d59e33737205a3064fa35b194`; base measured with `git merge-base origin/main <pin>`. `feature.json` agrees with the dispatch pin.
- Walked the commit list and measured c0 `33c0c181e62c5e75692c8320fc01aaaaf06fa40b` → c1. Executable changes are confined to the two regression tests; `board.py` is unchanged. FEAT-71's merged work is already in the measured base. No `[harness:human]` commits; no modified tracked product files. Untracked `.harness/notes/` is outside reviewed code.
- Product `docs/spec.md`, `docs/decisions.md`, `docs/architecture.md` are absent. Consulted AGENTS.md's explicit authority mapping, product `.harness/harness/docs/SPEC.md:432-453` and `DECISIONS.md:7171-7274`; no architecture guidance was invented. Reviewed all four amendment receipts against BRIEF criteria and DEC-221's approved narrow exception.

## Stage 1 — acceptance and prior must-fix closure

- **SC-03 closed:** unit `tests/unit/test-check-state-inv37-local-binding.py:134-139` exercises string/list factories through public `inv_37`, requiring the mapping-specific invalid-binding finding and exactly zero resolver/config calls. Integration `tests/integration/test-check-state-inv37-offline.py:173-183` drives the real entrypoint, requiring that finding, zero contents reads and no traceback. Presence assertions prevent absence-only success. Guard deletion raises before the unit returns and fails integration's explicit traceback/finding checks; owner fallback cannot satisfy the mapping finding.
- **SC-02 closed:** unit `:111-125` and integration `:136-157` now bind actual recovery verbs for missing, mismatched and unproven receipts, alongside distinct provenance findings. The owner-recorded mismatch is the discriminating twin: passing owner repo to recovery selection would choose `open` (integration) or `recover-terminal` (unit), not required `recover-mirror`. Integration also binds `--previous-repo org/repo`. Missing/unproven cases alone do not distinguish owner selection; the mismatch case does. Selection traced through `feature_schema.py:151-183,560-575`.
- **SC-01/04/05/06 preserved:** valid opened/recovered-terminal offline twins and zero-read checks (`integration:107-124`); authenticated success/read-failure pair (`:186-203`); owner, legacy, sync-off and no-plan controls (`:206-247`); real local-validation/public-gate unit seam (`unit:62-93,103-159`). Production still chooses the offline-only local validator and otherwise delegates unchanged (`board.py:306-323,333-355`). No acceptance criterion is marked inspection-only.
- Table auth declaration, canonical-reader inventory and amended DEC-221 serve the same change; no scope-creep, omission or mismatch found. Prior baseline/mutant execution is recorded in c0 validator evidence and main's `notes/fix-evidence-c1-2026-11-08.md`; not independently executed by this reviewer.

## Stage 2 — quality and regression risk

- Ran only the required Python risk grader at the exact measured base/pin before manual review: **37 passing function records**, grades 4–5; production helpers grade 4. No high or grade-2 records. `code_grade: pass`.
- Local binding validation reuses the raw repository predicate, canonical fleet accessor and exact fleet lookup; it returns the authoritative repository into existing receipt/provenance/recovery predicates. Remote failure after authentication remains fail-closed; unbound resolution and the shared resolver are unchanged. Test patches restore collaborators and clear memo state in `finally`.
- New assertions observe real findings, not fixture-only facts; malformed-shape cases pair negative remote/traceback checks with positive invalid-binding output. No concrete regression or avoidable abstraction requiring a finding identified.

## Principles applied

- **Delete First:** accepted the small selection/local-validation change in the existing owning module; no extra adapter or speculative fallback is introduced (`board.py:306-323`).
- **Model the Domain:** retained existing binding and provenance predicates rather than adding independently synchronized state; recovery remains selected by the shared formatter (`board.py:327-355`).

## Verification boundary and open questions

No tests, builds, lint, formatting or mutant runs executed. QA must establish exact-pin literal verify and M4/M6 closure; main's evidence is attributed, not presented as reviewer measurement. Open questions: none.
