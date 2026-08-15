# Handoff — FEAT-07-verify-teeth-batch-probe, validate → ship — written at 98ed3e7, seq-1

## Next

Nothing dispatches until the user rules on the briefing at `notes/ship-review-close.md`. On a ship
acceptance: run `gh-sync.py ship .harness/features/FEAT-07-verify-teeth-batch-probe` to close
milestone #2, then open the PR from `feat/FEAT-07-verify-teeth-batch-probe` — the PR and the merge
are the user's, never automatic — and file the unstruck backlog rows from the briefing's table as
issues. The feature dir and `.harness/notes/grilling-perf-batch-1-2026-08-04.md` are still
UNCOMMITTED and are the next commit; `.harness/logs/2026-08-04.md` is the main session's and must
be left alone. If the user orders the formal re-grade instead, that is one product-lead run of pm
against all 18 criteria at `98ed3e7`.

## Trust

- All ten tasks committed across ten commits `0a34989`..`98ed3e7`; every mirrored issue #48-#57
  closed — `git log --oneline main..HEAD` and `gh-sync.py close-task` output — verified-at 98ed3e7
- `run-unit-tests.sh` exit 0, `check-docs.sh` exit 0 over 186 files, `check-expertise.sh` OK on all
  11 files — I ran all three, not cited — verified-at 98ed3e7
- Blocking `qa_gate` PASSES, `matrix_ok: true`; `review` PASS after its one med finding was fixed —
  `runs/validate-validator/digest.md` — verified-at 70b0ed3
- SC-07, SC-03, SC-05 and SC-18a were closed AFTER pm's goal-check and verified by me with each
  criterion's own declared method, using a whitespace-flattened matcher rather than line-wise grep.
  **pm has NOT formally re-graded them** — UNVERIFIED at pm's tier, and named as such in the briefing
- SC-12's receipt half is CARVED OUT, not unmet: `harness-documentor` holds no `notes/receipt-*`
  grant — `team-config.yaml:144,158,171,184,199` — verified-at 98ed3e7
- Cost 702.82 against 550, 28% over, user-accepted on the record; `max_cost_usd` NOT re-baselined —
  `feature.yaml` — verified-at 98ed3e7

## Dead ends

- Do not edit `validate-digest.py` again without re-checking DEC-175's nine committed line anchors.
  The file is 899 lines and every anchor resolves — `sed -n` on each — verified-at 98ed3e7
- Do not verify a prose clause in these files with a line-wise `grep`. Clauses wrap across comment
  lines and it false-negatives both ways — it reported two correct SC-07 surfaces as failing —
  verified-at 98ed3e7
- Do not re-open D-07 or re-suggest the `no-task` spelling — `notes/answers-amf-fix-product.md` —
  verified-at 4091b36
- Do not treat the code review's PASS as discharging the human-reads-the-diff control, and do not
  treat the user's read as complete either — it passed over the stale anchor the reviewer caught —
  `docs/harness/DECISIONS.md` DEC-174 ruling paragraph — verified-at 98ed3e7
- Do not fix the documentor or pm receipt grants here — out of scope by the user's ruling, and item
  4 on the briefing's backlog — `notes/answers-amf-fix-product.md` Q4 — verified-at 4091b36
- Do not re-run `security` or `ui` reviewers, or ship-refresh: all three are recorded skips with
  reasons in `feature.yaml gate_status`, and `.harness/codebase/` does not exist — verified-at 98ed3e7

## Working set

- .harness/features/FEAT-07-verify-teeth-batch-probe/notes/ship-review-close.md
- .harness/features/FEAT-07-verify-teeth-batch-probe/feature.yaml
- .harness/features/FEAT-07-verify-teeth-batch-probe/STATE.md
- .harness/features/FEAT-07-verify-teeth-batch-probe/BRIEF.md
- .claude/skills/harness/bin/gh-sync.py
