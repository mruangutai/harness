# Receipt — simplify · ALTITUDE · policy data contract placement (FEAT-2398 plan draft)

BLUF: 4 findings, all FLAG-ONLY on plan.yaml T-01 / D-02. No source or plan edits. files_touched [].
Settled set (grilling, DEC-174 lane, three-part scope, accepted Kaya BLOCKED, cycle-1 dispositions) not reopened.
Read: simplify SKILL, angle-altitude, craft migrate-callers-then-delete (context only), plan.yaml, BRIEF.md,
validate-digest.py policy readers, factory_config.product_config, DEC-256 text.

## A-1 — "one validated document" has three entry points, so "once per QA validation" is unproven (T-01 intent, "Read test_kinds and test_matrix ... once")
- Anchor: T-01 intent, pinned-policy paragraph; validate-digest.py `_declined_gate_errors`→`_qa_floor_requires_nothing`, `_qa_kinds_errors`, `_receipt_problems`→`_active_receipt_kinds`, `_load_matrix_inputs` (each today re-reads the Harness root independently, four readers of one doc).
- Cost: the intent lists the consumers but not the one resolver they call. Without a single named resolver (memoised per feature_dir+full pin, or resolved once in validate and threaded), the pin/binding/git-blob read happens up to 3x per QA return and each site can word or fail the refusal differently; the SC-03 "named contract refusal" could be emitted by one path and swallowed (fail-closed False) by another.
- Alternative: one resolver returning a validated policy value (kinds, matrix, repo, full sha, path) that all readers consume; the refusal surfaces once from `_qa_kinds_errors`, the other paths read the same memo/fail closed.
- Recommendation: **fold-in** (state the single resolver and its call-once guarantee in T-01 intent; no new files).

## A-2 — After the cmd-based exclusion is removed, `_excluded_kinds` and `_explicitly_excluded_kinds` become the same predicate
- Anchor: T-01 intent "Replace cmd-based exclusion in _qa_kind_policy_error and _excluded_kinds"; validate-digest.py `_excluded_kinds` vs `_explicitly_excluded_kinds`.
- Cost: two authorities for "what is excluded" (one currently status-or-null-cmd, the other status only) that the edit makes byte-equivalent; the plan removes one body but not the duplicate, leaving a drift site for the very rule SC-02 pins.
- Alternative: keep one function, migrate its callers (`_matrix_floor`, `_active_receipt_kinds`, `_matrix_requires_no_kind`), delete the other (craft: migrate callers, then delete).
- Recommendation: **fold-in**.

## A-3 — D-02's recorded home is DEC-212 (disposition keep) but its rule enforces DEC-187's hard gate
- Anchor: plan D-02 `dec: DEC-212`; decisions_affected DEC-212 keep/successor none; DEC-187 gets only the D-03 Kaya consequence; T-01 intent "Record D-01 and D-02 ... in the existing policy authority".
- Cost: the new non-PASS rule (unresolved/active-null always-floor omission refused under every verdict) is a required-kind block, i.e. DEC-187's clause. Recording it against an unchanged DEC-212 leaves the reader of DEC-187 without the rule and implies DEC-212 changed; SPEC §9 / skill / validator then cite different decisions for one rule.
- Alternative: D-02.dec → DEC-187 (carrying both D-02 and D-03), DEC-212 stays untouched and is cited only for conditional-applicability latitude.
- Recommendation: **fold-in** (re-point D-02 and the decisions_affected row; no scope change).

## A-4 — Rule statements across DECISIONS / SPEC §2,§9 / QA skill / validator: name the one authority
- Anchor: T-01 intent documentation paragraphs; BRIEF SC-05 ("state the same contract").
- Cost: the narrowed D-02 rule, pin procedure and two repairs are written in four places; intent says SPEC should "link to the existing policy authority rather than copying" but does not say which file is that authority. The skill (QA-facing) legitimately needs its own procedural copy (separate reader), SPEC and DECISIONS do not.
- Alternative: DEC-256 amended text + DEC-187 carry the rule; SPEC §9 holds the status table and links; the skill restates procedure only, with the rule sentence verbatim from the DEC.
- Recommendation: **briefing-row** (authority designation to the SC-05 inspection checklist: skill procedure copy accepted, SPEC links).

## Placement note (leave)
The pinned local-git blob read could live beside `factory_config.product_config` (same `load_harness_json(text=, context=)` shape, same "repo@ref:path" diagnostic, no-fallback) rather than inside the 3000-line validator. Adding it there widens T-01's file set/lane rows and plan forbids changing product_config, not adding a sibling. Recommendation: **leave** — a validator-local resolver satisfies A-1; revisit only if a second consumer of pinned product policy appears.

## Checks performed (P-04)
Read all four validator policy readers and their callers; product_config and DEC-256 D-01..D-06; confirmed no existing local pinned-blob reader (`file_at_ref` is remote/gh); decisions_affected rows vs D-01..D-03 anchors.
