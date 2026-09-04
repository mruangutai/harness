# Plan revision c2 — the operator's batched rulings, applied

**Both approvals stay `pending`.** `plan.yaml` was recreated by `plan-merge.py apply` over a
verbatim transcription of `HEAD:.harness/harness/features/FEAT-52-handoff-done-when/plan.yaml`
(815 lines) with only the four rulings' hunks; the tool seeded `approval.status: pending`.
Result: `feature: FEAT-54-handoff-done-when`, `status: plan`, 12 tasks T-01..T-12 (no T-13),
9 decisions D-01..D-08 + D-10 (no D-09), `panel:`/`lanes:`/`source_issues:` untouched.

## What each ruling changed

**R1 rename.** `feature:` key; T-10's `Cite FEAT-54`; T-11's two `files:` paths, its verify glob
and its intent path; BRIEF title; BRIEF SC-07's path (struck with the experiment). No `FEAT-52`
token survives in `BRIEF.md` or `plan.yaml`. The `panel:` findings contain no feature-id token at
all, so the composed id-token sweep had nothing to touch there — finding wording is byte-identical.

**R2 write-time-only resolution (PF-4205e7e2 accepted).** New **D-10** (`dec: DEC-179`) records the
split: one module, one parser, one pointer grammar; `resolve` gates only whether a target is opened.
Grammar stays in the persisted pass — a typed prefix consults no target, so it cannot rot, and an
authority outside the four kinds is still caught. Edited: **T-01** (contract gains `resolve`; case
(d) pinned to `resolve=True`; new case (g) — four unresolvable/resolve-pairs, a ninth assertion that
`resolve=False` returns `[]` with every target file ABSENT, and (a)/(c)/(e) re-asserted under both
settings), **T-02** (implement it; resolution is the only gated behaviour), **T-03** and **T-04**
(write gate calls with `resolve=True`; substance unchanged), **T-06** (case (e) → the (e1)/(e2)
pair; `traces` gains REQ-06; expected-state list re-lettered), **T-07** (`resolve=False`; the
"resolution is checked for every note that has a block" clause replaced by shape-and-grammar-only
citing D-10), **T-08** and **T-10** (template, playbook and DEC wording: pointers resolve when the
note is written, no standing re-resolution), **T-11** (verify calls `resolve=True`). BRIEF: **REQ-06**
now carries both halves; **SC-15** added (`verify: automated  evidence: integration`).

**R3 probe kept whole (PF-1e45eb3a rejected).** D-04, T-09, T-12 and SC-09 transcribed
byte-for-byte — zero hunks touch them; `handoff_comprehension` stays `locally_run`, out of
UNIT_SCRIPTS, INTEGRATION_SCRIPTS and `test_matrix`.

**R4 mutation experiment struck (Q3).** T-13 and D-09 absent, nothing renumbered. Dangling-id sweep:
`T-13`, `D-09` and `mutation` return zero hits in the new plan except line 30, which is a panel
finding's own phrase "no-mutation audit" (an mtime/byte claim, unrelated). Nothing had T-13 in
`depends_on`; the `handoff_done_when.py` lanes row survives because T-02 needs it. **SC-07** rewritten
to the surviving claim: one implementation, graded by inspection at `review_sha` over the two import
sites and the ABSENCE of any second block parser or pointer resolver in either gate.

## Hunk → ruling

`@@2,3` R1+approval-omission · `@@136,4` R4 strike D-09 + R2 add D-10 · `@@167`,`@@171,2`,`@@182,3`,
`@@197` T-01 R2 · `@@220`,`@@246,3` T-02 R2 · `@@311` T-03 R2 · `@@336,3` T-04 R2 · `@@397`,`@@422`,
`@@442,3` T-06 R2 · `@@488,2` T-07 R2 · `@@533,3`,`@@539,2` T-08 R2 · `@@631`,`@@639,4` T-10 R2+R1 ·
`@@659,2`,`@@665`,`@@690` T-11 R1 · `@@678`,`@@698` T-11 R2 · `@@767,49` R4 strike T-13.
24 hunks, all attributed.

## REQ → task map (no orphan)

REQ-01 T-03,T-04,T-11 · REQ-02 T-01..T-04 · REQ-03 T-01,T-02,T-08 · REQ-04 T-01,T-02,T-03 ·
REQ-05 T-01..T-04 · **REQ-06 T-01,T-02,T-03,T-04,T-06** · REQ-07 T-05,T-06,T-07,T-11 ·
REQ-08 T-03,T-04,T-06,T-07 · REQ-09 T-08,T-10 · REQ-10 T-09,T-12.

## Checks run

- `yaml.safe_load` on the new plan: parses; every task carries `traces`, `files`, `verify`,
  `intent`, `change_type`.
- `check-plan-routes.py <plan>` → `0 violation(s) across 1 plan(s)`, exit 0 (9 DEVIATION lines are
  the expected DEC-174/DEC-179 carve-outs).
- BRIEF: REQ-01..REQ-10, SC-01..SC-15, each SC exactly one `verify:` and every `automated` one an
  `evidence:`; `## Approval` still `status: pending` with empty `approved-by`/`date`.

## Ambiguity / out of scope

- Older notes under this feature's `notes/` still spell `FEAT-52` (`handoff-plan.md` ×8,
  `research-FEAT-54-goalcheck-plan-c0/c1`, `research-FEAT-54-planfix-c1/c2`,
  `research-panel-transcription-c0`, `review-harness-code-reviewer-planpanel-c0`). Historical
  records, not rewritten per dispatch. `handoff-plan.md` is the one live consumer: T-11 edits it,
  and its `Authority:` pointers must be written against the FEAT-54 paths.
- The rulings left unstated whether `resolve` is positional or keyword-only. Reversible naming, so
  decided: written as a plain fourth parameter, called by keyword (`resolve=True/False`) at both
  gates so the call sites read unambiguously.
