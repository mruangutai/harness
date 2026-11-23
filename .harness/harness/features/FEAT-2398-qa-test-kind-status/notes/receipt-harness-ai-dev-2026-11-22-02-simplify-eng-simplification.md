# Simplify · SIMPLIFICATION (plan surface, instruction contract) — FEAT-2398

Read-only, FLAG-ONLY. Scope: plan.yaml T-01/D-01..03, BRIEF SC-01..05, rules skill placement. Settled set honored (grilling Settled/Out of scope, cycle-1 dispositions, DEC-174 lane, accepted Kaya BLOCKED, INV-49).
Result: 4 findings (1 med, 3 low). None touches settled items.

## S-1 (med) — one rule, four spellings in T-01 intent (plan.yaml T-01 `intent`, paras "Replace cmd-based exclusion", "Separate three gates", "Cover SC-04")
- Summary: the non-PASS rule (always-floor unresolved/active-null omission refused under every verdict; no blanket floor; full floor only PASS+matrix_ok) is stated in full at least 3 times in intent, again in D-02 `choice`/`because`, SC-04, BRIEF Constraints (DEC-212/35 bullet) and the SKILL paragraph. Test paragraph also re-lists the same controls ("omission... regardless of matrix_ok" twice).
- Cost: an implementer reconciling spellings can read a variant as a new requirement (e.g. "regardless of matrix_ok" vs "PASS/matrix_ok true"); any later edit to one spelling drifts from others. Intent is ~190 lines for one task.
- Alternative: state the three-gate rule once (the "Separate three gates" paragraph) and have the other intent paragraphs say "per the three gates above"; D-02 stays the signed statement, SC-04 stays the acceptance.
- Disposition: **fold-in** (pm draft only; no behaviour change).

## S-2 (low) — SKILL placement: validator resolution mechanics copied into QA prose (plan.yaml T-01 intent, "Update harness-verification-rules/SKILL.md", vs "Resolve QA policy independently of the grading root")
- Summary: the SKILL replacement for line 23 is specified as the full binding/pin procedure (factory.repo, fleet workspace_path, dispatch-pin reconciliation, git show blob). That is the validator's resolution algorithm restated as QA instructions; QA only needs: read `test_kinds`/`test_matrix` from the product repo at `review_sha` (final CODE target of `feature-worktree.py path --repo --id`), record repo/full commit/path, never the current checkout. SPEC §9 is the place for mechanics.
- Cost: two prose copies of the same resolution order (SKILL + SPEC, plus validator) with no test cross-checking them (same drift class as expertise G-02); the skill is loaded every QA spawn, so mechanics tokens are paid per run and by a reader who cannot change them.
- Alternative: SKILL carries the short QA-facing procedure plus a pointer to SPEC §9 for refusal reasons; SC-05's "same contract at the pin" is met by consistent status/pin/conditional statements, not identical algorithms.
- Disposition: **fold-in** (narrow the SKILL wording in T-01 intent). Mark leave if pm judges SC-05 wants the full procedure inline.

## S-3 (low) — new D-02 prose should merge into existing SKILL lines, not append a section (rules skill `## The matrix is a floor`, state table)
- Summary: the SKILL already says the PASS+matrix_ok floor (line "refuses a PASS with matrix_ok: true...") and "misconfigured under any verdict but BLOCKED" (intro of five-states). Plan says "State the narrowed D-02 rule explicitly" and add a row, extend active/null wording, name repairs, constrain locally_run, excluded as sole soft skip. Done additively this yields the repairs text in row, in a paragraph and in the validator message, and a stale "five states" heading still true but with two misconfigured rows.
- Cost: repairs named 2-3 times in one 150-line skill; existing `not_applicable` row ("tooling genuinely is absent") then contradicts "excluded sole soft skip" unless edited, not just added to.
- Alternative: edit in place — one `misconfigured` row carrying unresolved + active/null + both repairs; reword `not_applicable` and `locally_run` rows; one sentence added to the floor paragraph for non-PASS; no extra section.
- Disposition: **fold-in** (state "edit in place, repairs named once" in intent).

## S-4 (low) — `files:` anchors do not cover the sections the intent edits (plan.yaml T-01 `files`)
- Summary: SKILL quote `## The matrix is a floor` but intent also edits the state table under `## Resolve each kind...`; SPEC quote `## 9. Test guardrails` but intent says sections 2 and 9; DECISIONS.md quote names only DEC-256 but intent also edits DEC-187 and records D-01/D-02. Same fact (edit surface) spelled two ways that disagree.
- Cost: reviewer/diff-scope checks keyed on anchors under-cover the real edit set.
- Alternative: add anchors for the table section, SPEC §2, and the DEC-187 heading (or relax to path-only entries).
- Disposition: **briefing-row** (anchor list is dispatch/briefing metadata; pm may fold in).

Empty parts: no dead references to a revised shape found beyond SPEC "no-browser-target soft-skip" wording, which the plan already targets.

## Principles applied
- migrate-callers-then-delete (read): S-3 applies it to prose — edit the old rows in place rather than append beside a contradicting row.
