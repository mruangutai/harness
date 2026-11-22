# Receipt — harness-ai-dev — r-20261121-simplify-eng — altitude angle — FEAT-2229

BLUF: altitude is largely right. Two low findings, no fold-in required; one briefing-row, one leave. No source, plan or BRIEF edits made; no checks run.

Read: angle-altitude.md, plan.yaml (T-01/T-02/T-03, decisions_affected), BRIEF.md, grilling note, craft leaf redesign-from-first-principles, check_state/ctx.py:464-490, plan_merge/guards.py:50-107, harness-validator-lead.md:59-126, teams/validate.yaml (grep).

## Checked and clean
- Landing check lives in pm Mode 2 (existing sc_status producer), not a new script; matches settled set.
- validator-lead wiring (plan.yaml T-02 intent, lines 306-313) is NOT redundant: harness-validator-lead.md:100-103 gates only on `must_fix`/`severity_max` and never mentions `sc_status`/unmet SC (grep: only must_fix hits at 83,102,123), so a disposition-only wire is the missing producer-to-gate link. Not flagged.
- validate.yaml prompt is thin pointer to Mode 2 (already applied trim). Mechanical checks live once in `plan_merge/check.py#cmd_check`; scope keeps only judgment. Single owner per rule in those pairs.
- DEC-254 collision handling is named in T-03 (plan.yaml:346).

## Findings

### F-1 (low) — era resolver has no named home; a third bespoke harness.json era reader risks drifting
- file: .claude/worktrees/harness/FEAT-2229-decision-dispositions/.harness/harness/features/FEAT-2229-decision-dispositions/plan.yaml
- line: 173-183 (T-01 intent: era key, null/missing/malformed semantics inside `cmd_check`)
- summary: T-01 specifies era semantics (missing=legacy, null=no pre-era, malformed=diagnostic never exemption) in the check task but does not say where the resolver lives. Existing homes: `check_state/ctx.py:464` `_era_start_for` (date-only, INV-bound, appends to `self.bad`) and `plan_merge/guards.py:50-107` `_harness_root` (manifest-probe walk, deliberately not respelled, see its docstring and case_20).
- cost: if the implementer writes an ad-hoc `json.load` + walk inside `cmd_check`, it respells the root probe the guards docstring forbids and forks the missing/null/malformed rule a third time beside `panel_era_start`/`seam_era_start`; instants differ from dates, so `_era_start_for` itself cannot be reused as-is.
- alternative: one small resolver in plan_merge (reusing `guards._harness_root` or the `--root` already passed to check) returning instant|None|diagnostic, with the contract stated once. Does not weaken any T-01 assertion.
- recommended route: briefing-row (one line in the T-01 dispatch briefing: reuse `guards._harness_root`/`--root`, do not respell the probe; keep rule in one resolver). Not a plan.yaml edit.

### F-2 (low) — plan-team draft prompt restates mechanical rules owned by check.py
- file: same plan.yaml
- line: 277-286 (T-02: draft prompt requires verbatim clauses, resolvable successors, DECISIONS.md-owning task)
- summary: the six mechanical rules are stated in check.py (authority), the template, the draft prompt, SPEC (T-03 line 348) and pm Mode 2.
- cost: a later rule change edits several prose copies; no test ties the draft-prompt list to check.py.
- alternative: draft prompt names the block and says "the check is the contract". Rejected as a recommendation because SC-04/SC-07 pin the drafting obligation at that owner, and a pointer-only prompt weakens a settled assertion; the prompt is the pm's sole point-of-use instruction and listing what the author must satisfy avoids a draft/check/redraft loop.
- recommended route: leave (reason: weakening an SC-pinned obligation; copies are author-facing, not enforcement).

## Open questions
none blocking.
