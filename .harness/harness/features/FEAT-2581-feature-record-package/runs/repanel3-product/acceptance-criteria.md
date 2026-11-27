# repanel3-product — acceptance criteria (written before dispatch)

Authority: notes/answers-2026-11-27-plan-escalate.md (PL-11 a and the other rulings).

## apply1 (pm, one pass)
- T-03 verify restated as four invariants (strict decode; disclosed fields derived from the two refs, incl. d02# file/symbol/templates; every SC-08 record present incl. `divergence:` in build-divergences.md; every ruled id has a human-readable account, escaped literals alone insufficient). Keyed on guarantees, not per-finding patches.
- PL-03 applied: 24 caller-row remedies + canonical_reader_audit keys → feature_record.read.load_feature_json; two test expectations updated; Settled/D-01 "rows change only file and id" wording corrected.
- PL-04, PL-09, PL-10, PL-05, PL-01 reflected where text needs it. PF-7999938a, PF-d35d903d, PF-502d3541 NOT resolved/closed by pm.
- No change to T-01/T-02 task text, execution_mode/agent, approval (stays pending), .agents/.
- Per-field change list returned.
Send back: none (one pass). A deviation is recorded and goes to the readers/operator, not re-dispatched.

## Readers (one read each)
- scope: closed/not-closed + worktree pointer for PF-96cdf9f1, PF-3882d444, PF-cf9cf710; states newly-broken or not.
- design: same for PF-a37e5b40.
- every finding has kind + severity (+ scope for proportionality).

## record (pm)
- record-panel --cycle 4, set-panel resolving only reader-closed findings, plan-merge.py check; outputs verbatim with exit status. No substance applied.

## Run PASS iff
all four closed, no new substance, approval.status pending, panel cycle 4 recorded, check exit 0, open = {PF-7999938a, PF-d35d903d, PF-502d3541}.
