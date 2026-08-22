# Handoff — FEAT-31, plan → signature/build — written at 7299669, plan4-product

## Next

The plan is AMENDED and UNSIGNED. The next act is the operator's signature on `plan.yaml`
`approval:` — nobody below layer 0 writes it. Do not re-plan, do not dispatch another
`harness-pm`, do not build. After the signature the build order is T-14 before T-10, and
T-11 before T-12.

TWO THINGS TO PUT TO THE OPERATOR FIRST, both verified below, neither in this round's scope:
T-01 and T-08 carry `verify:` commands that CANNOT FAIL, and Q-A/Q-B are unanswered (D-22
adopted a Q-A default that is overrulable in one read).

## Trust

- plan.yaml loads via `harness_yaml.load_file`: 14 tasks T-01..T-14, 22 decisions D-01..D-22,
  `approval.status: pending` — verified-at 7299669
- `approval:` byte-identical to the committed blob — sha256 of the extracted block is
  `96666915d78504ef` before and after; BRIEF.md `## Approval` is `4fac2b8b5d832525` both
  sides — verified-at 7299669
- `check-plan-routes.py` exits 0, 0 violations across 4 plans, 30 dirs examined, and it DOES
  reach this plan. Exactly 3 DEVIATION lines — T-10, T-12, T-14 — all main-session-direct on
  granted paths, the intended DEC-174 shape; T-04 is main-session-direct too but prints OK,
  its path granted to nobody — verified-at 7299669
- T-11's own `verify:` EXECUTED today exits 1 naming exactly the 8 files, so it discriminates
  rather than passing vacuously — verified-at 7299669
- All 69 `notes/handoff-*.md` in THIS worktree pass the four headings, the 60-line cap and
  T-10's empty-body rule, so T-14's widened glob adds zero violations. 10 of the 69 sit
  EXACTLY on 60, no headroom — verified-at 7299669
- `.harness/harness.json` resolves to `harness-dev-ops` alone, which is why T-11 owns it and
  T-05/T-07 carry do-not-edit clauses — `check-domain.sh --resolve` — verified-at 7299669
- DEC-174 am.4 anchors: category rule `DECISIONS.md:4851-4854`, library/cutover analogy
  `:4856-4859`; `:4861` is "Not a strike" — verified-at 7299669
- **T-01 and T-08 `verify:` CANNOT FAIL.** T-01's expected slug sits in a `#` comment while the
  command exits 0 whatever it prints; T-08 pipes to `grep -c`, which prints any count and exits
  0, with the expected 3 in a comment. Flagged by the previous handoff, absent from this round's
  rulings, re-verified live rather than inherited — verified-at 7299669

## Dead ends

- Two writers on plan.yaml. 14 tasks became 1 in 63 seconds; plan.yaml is deliberately absent
  from check-domain's `SHAPE_PATTERNS` — `check-domain.sh:670` — verified-at 7299669
- Writing any file through Bash. The guard resolves the UNEXPANDED token, so `cat >> "$F/x"` is
  refused while the same literal path succeeds, and a `>` in heredoc prose reads as a redirect —
  both reproduced this run — verified-at 7299669
- Folding A-2 into T-10. Rejected in D-20: a fold makes a failed refactor indistinguishable from
  a failed empty-body check — verified-at 7299669
- Deriving handoff stems from status values, or touching `SEAM_NOTES`. A-2 forbids both; the
  comment near `check-state.sh:495` records that deriving goes dark on Linux CI — verified-at 7299669
- A `test-*.py` name for SC-01's live half. The detector loops `"$BIN_DIR"/test-*.py`, and the
  skip-loudly variant is a green required step that verified nothing — `tests.yml:78,84` —
  verified-at 7299669

## Working set

- .harness/harness/features/FEAT-31-orchestrator-context-watch/plan.yaml
- .harness/harness/features/FEAT-31-orchestrator-context-watch/notes/answers-plan3.md
- .harness/harness/features/FEAT-31-orchestrator-context-watch/notes/research-plan3-amend.md
- .harness/harness/features/FEAT-31-orchestrator-context-watch/notes/verify-plan4-orchestrator.md
- .harness/harness/features/FEAT-31-orchestrator-context-watch/runs/plan4-product/digest.md
