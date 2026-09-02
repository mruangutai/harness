# Handoff — FEAT-48-parallel-safe-suite, plan → operator signature gate — written at 32b6370d, seq-4

## Next

Nothing dispatches until the operator rules. Present `plan.yaml`'s `panel:` key as the one
batched signature review (DEC-176): eight open findings, `severity_max: high`. Signature MUST
carry either an `approval.rulings` overrule of `PF-58719ff7b430616b91b5a7cfe49bde10` by name, or
a send-back. On a send-back the next dispatch is `harness-product-lead` → pm, re-planning D-10,
T-01, T-02 and T-06 in ONE pass, with the census-shape decision (`PF-d6f80211bcb8f4748…`, med)
settled FIRST because it changes what the F-01 repair is. That re-plan resets approval to pending
and runs the panel again as cycle 5.

## Trust

- The panel record in `plan.yaml` is complete and machine-checkable: 8 findings, 3 readers all
  `ran`, `last_run: 2026-09-01-02-validator` — `plan.yaml:1036-1150`; `check-state.sh` INV-32
  raises nothing against it — verified-at 32b6370d
- Cycle 3's PASS is void as evidence about this tip: the three F-01 site groups are ABSENT at
  `d5c23a0` (what cycle 3 graded) and PRESENT at the tip — `git show d5c23a0:.claude/skills/harness/bin/test-bash-write-guard.py | grep -c feat50` → 0, tip → 1 — verified-at 32b6370d
- The three F-01 site groups exist at source: `test-bash-write-guard.py:898-901`,
  `test-check-domain.py:3285-3288`, `test-check-state.py:3591-3613` — verified-at a80d54a5
- SEC-01 blocks any pre-signature code-reviewer digest: `validate-digest.py harness-code-reviewer`
  refuses every `code_grade` value AND its omission while `review_sha` is `none` — measured
  directly against a probe digest — verified-at a80d54a5
- pm's aggregate "20 live sites over 59 files" is ONE measurement plus one derivation, not two —
  `runs/2026-09-01-02-validator/digest.md` adequacy note A3 — UNVERIFIED
- T-03's verify was never executed against any tree; F-01's T-03 leg is derivation only, because
  the scanner does not exist yet — same digest, note A1 — UNVERIFIED

## Dead ends

- Do NOT re-derive whether `plan-merge.py`/`test-plan-merge.py` (BUG-1128, +827 lines on the
  rebase) invalidates the plan: `grep -c "plan-merge" plan.yaml` → 0 and the added lines hold no
  live-tree mutation site — `runs/2026-09-01-02-validator/digest.md`, "Assessed and dismissed",
  item 6 — verified-at a80d54a5
- Do NOT re-open the FEAT-47 fold: #1053's "Folded into FEAT-47" is superseded bilaterally by
  FEAT-47 D-13 and FEAT-48 D-09 — `notes/research-FEAT-48-goalcheck-plan-c4.md` §2 —
  verified-at a80d54a5
- Do NOT run `gh-sync.py open` to silence INV-26: the mirror opens only after the approval gate
  passes — `.agents/skills/harness/references/github-mirror.md:38` — verified-at a80d54a5
- Do NOT pin `review_sha` to unblock SEC-01: INV-6 forbids a pin before the Building → Review
  seam, which is the deadlock BUG-1080 closed — orchestrator playbook, step 6 — verified-at 32b6370d

## Working set

- `.harness/harness/features/FEAT-48-parallel-safe-suite/plan.yaml` (`panel:` at :1036)
- `.harness/harness/features/FEAT-48-parallel-safe-suite/notes/research-FEAT-48-goalcheck-plan-c4.md`
- `.harness/harness/features/FEAT-48-parallel-safe-suite/notes/review-harness-code-reviewer-planpanel-c4.md`
- `.harness/harness/features/FEAT-48-parallel-safe-suite/runs/2026-09-01-02-validator/digest.md`
- `.harness/harness/features/FEAT-48-parallel-safe-suite/STATE.md`
