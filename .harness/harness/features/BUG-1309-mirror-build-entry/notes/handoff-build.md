# Handoff — BUG-1309-mirror-build-entry, build → validate — written at 5d672120, seq-1

## Next

Nothing dispatchable remains in any squad. The next act is the OPERATOR's, on four items batched
into one sitting: rule on F-01, F-02 and F-03 in
`.harness/harness/features/BUG-1309-mirror-build-entry/notes/ship-review-2026-09-08-resume.md`,
re-sign `BRIEF.md ## Approval` (SC-03 and SC-07 were amended after the 2026-09-06 signature), and
run the SC-10 hand test at `notes/uat-BUG-1309-mirror-build-entry.md`. Only after those does a ship
dispatch make sense.

## Trust

- All thirteen planned tasks are done and the blocking qa test_matrix gate passes — unit 33 files
  exit 0, integration 50 files exit 0, `test-merge-gate.py` 19/19 —
  `notes/review-harness-qa-c7.md` — verified-at 894adc0f
- SC-01 through SC-09 are met with executed evidence; SC-10 is user-gated and unrun —
  `runs/2026-09-08-amend-gc-product/digest.md` `sc_status` — verified-at 894adc0f
- `merge-gate.py` and `merge-gate.sh` do not exist at merge-base 6ad7233f and arrive at 4338ee44
  inside this feature's own range, so defects in them are IN SCOPE, not carry-forwards —
  `git cat-file -e 6ad7233f:<path>` exit 128 — verified-at 894adc0f
- `git -C <dir> merge X`, `git -c k=v merge X` and `git --work-tree <d> merge X` all return None
  from `merge_ref`, so the gate silently allows them: `git_merge` strips every `-`-prefixed token
  and then reads args[0], which is the FLAG VALUE — `merge-gate.py:44-48` — verified-at 894adc0f
- `_build_entry_recovery_notice`'s non-era line names `open` while `recovery_command_for` returns
  `recover-terminal` for the same feature, and the plan signs that string verbatim —
  `gh-sync.py:1387-1389`, `feature_schema.py:324-338`, `plan.yaml:779-791` — verified-at 894adc0f
- The UAT script is drift-free against the pinned code across all eight substantive steps and no
  step reaches `gh-sync.py:1387-1389`, so F-03 need not be ruled on first —
  `runs/2026-09-08-amend-gc-product/digest.md` Q2 — verified-at 894adc0f
- `894adc0f..HEAD` touches `feature.json` alone, so the pin still covers every code change —
  `git diff --stat 894adc0f HEAD` — verified-at 5d672120

## Dead ends

- Routing F-01 or F-02 to a squad — both edit `merge-gate.py`, a registered PreToolUse gate script,
  and DEC-174 forbids the harness executing changes to its own gate scripts whatever
  `check-domain.sh --resolve` answers — `plan.yaml` lanes row `merge-gate.sh and merge-gate.py`
- Routing F-03 as a fix cycle — the code MATCHES the approved spec, so the remedy amends a signed
  plan string and needs the operator, not a builder — `plan.yaml:779-791`
- Grading novelty against the pin's parent — six cycles did, and it mislabels this feature's own new
  files as carry-forwards — `runs/2026-09-08-panelc7-validator/digest.md` novelty-base step
- Re-litigating the malformed-record posture — only a valid dict record whose branch matches owns a
  merge; the cycle-5 scan-wide sentinel was removed as a FAIL — `merge-gate.py:97-109`

## Working set

- `.harness/harness/features/BUG-1309-mirror-build-entry/notes/ship-review-2026-09-08-resume.md`
- `.harness/harness/features/BUG-1309-mirror-build-entry/runs/2026-09-08-panelc7-validator/digest.md`
- `.harness/harness/features/BUG-1309-mirror-build-entry/runs/2026-09-08-amend-gc-product/digest.md`
- `.harness/harness/features/BUG-1309-mirror-build-entry/notes/uat-BUG-1309-mirror-build-entry.md`
- `.claude/skills/harness/bin/merge-gate.py`

## Done when

Scope: operator rules on F-01/F-02/F-03, re-signs the amended BRIEF, and returns the SC-10 UAT result
Authority: approval:.claude/worktrees/harness/BUG-1309-mirror-build-entry/.harness/harness/features/BUG-1309-mirror-build-entry/BRIEF.md#Approval
Authority: finding:.claude/worktrees/harness/BUG-1309-mirror-build-entry/.harness/harness/features/BUG-1309-mirror-build-entry/notes/ship-review-2026-09-08-resume.md#F-01
