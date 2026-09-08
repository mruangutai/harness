# STATE

## Current

- feature: BUG-1309-mirror-build-entry
- run: .harness/harness/features/BUG-1309-mirror-build-entry/runs/2026-09-08-panelc7-validator/state.yaml
- squad: validator
- status: awaiting-user
- station: review — code-complete at review_sha 894adc0f (894adc0f..HEAD touches feature.json
  alone). All thirteen tasks done; the blocking qa test_matrix gate PASSES (unit 33 files exit 0,
  integration 50 files exit 0, test-merge-gate.py 19/19, T-07's unit cell not-applicable per D-12).
- review panel c7, run fresh today because the c6 lead verdict was lost to a provider interruption:
  ESCALATE, severity_max high, 0 send-backs. Three high findings survive, all promoted by one
  measurement — merge-gate.py/.sh do not exist at merge-base 6ad7233f and arrive at 4338ee44 inside
  this feature's range, so they are this feature's own code, not carry-forwards. Six earlier cycles
  had graded novelty against the pin's PARENT and filed two of them out of scope.
- goal-check at the pin: SC-01..SC-09 met with executed evidence, SC-10 user-gated and unrun
  (runs/2026-09-08-amend-gc-product/digest.md).
- SC-03 and SC-07 amended on the operator's ruling: the unevidenceable red-before-green sequencing
  clause became a present-tense DISCRIMINATION requirement, and pm executed both — the pre-change
  gh-sync.py fails all five SC-03 cases, the pre-change check-state.sh fails the SC-07 case. The
  BRIEF's ## Approval signature (2026-09-06) therefore no longer covers the file and only the main
  session may re-sign.
- two historical validator digests that failed the lead-digest contract (2026-09-07-03-validator,
  2026-09-06-panelc1-validator) were repaired by the validator lead by appending a conforming
  envelope; original blocks retained byte-for-byte, both now return `digest ok`.
- cycles 12/14. runs 39 against a 20-run budget (INV-22, informational, surfaced in the briefing).
- briefing for the operator: notes/ship-review-2026-09-08-resume.md (+ rendered .html).

## Open Questions

- F-01 (high) merge-gate.py:98-109 — feature_for's unordered glob.glob first-match decides a merge
  nondeterministically when two well-formed records share a branch: silent bypass one way,
  misattributed deny the other, 5/5 both directions. Remedy is main-session-direct (DEC-174).
- F-02 (high) merge-gate.py:44-48 — git_merge strips every `-`-prefixed token then reads args[0], so
  `git -C <dir> merge X`, `git -c k=v merge X` and `git --work-tree <d> merge X` fall through and the
  gate silently allows. Re-executed at the orchestrator tier. Main-session-direct (DEC-174).
- F-03 (high) gh-sync.py:1387-1389 — the non-era recovery notice names `open` where
  recovery_command_for and merge-gate.py's own deny say `recover-terminal`; following it creates
  sub-issues for finished work. The code MATCHES the signed plan (plan.yaml:779-791), so the remedy
  amends an approved plan string. Operator ruling, not a fix cycle.
- SC-10 UAT is owed by the operator: notes/uat-BUG-1309-mirror-build-entry.md, 8 steps, verified
  drift-free today. Independent of F-01/F-02/F-03 — no UAT step reaches gh-sync.py:1387-1389 — but
  it must run BEFORE the worktree is released, because the script points at that checkout.
- Ship backlog awaiting operator disposition: B-1..B-13 in the briefing. B-12 is a harness defect
  found while writing this seam's handoff — `plan-task:` and `brief-sc:` Authority pointers cannot
  resolve for a feature that lives only in a worktree, because handoff_done_when.py joins the
  feature path to the MAIN checkout root.
