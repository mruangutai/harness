# Handoff — BUG-148-gate-record-correction, build → validate — written at f60d5d27, seq-3

## Next

Dispatch the validate-phase review panel over the pinned `review_sha` in `feature.json`,
grading SC-01, SC-02 and SC-03 by inspection — they are the whole of the correctness evidence
for the prose, since the QA matrix required no test kind. Re-pin to the seam commit and run
`gh-sync.py status <feature-dir> review` BEFORE the panel is dispatched, in that order. Feed
the panel the two corrected passages and the QA note (`notes/qa-BUG-148-2026-09-06.md`), and
tell it NOT to re-run the matrix. Treat F-4 as live: SC-01/SC-02 restate T-01/T-02's own
verifies, so four inspection criteria are substantively two independent measurements — do not
read them as four. SC-06 is `verify: uat` and stays `not_met` until the operator reads both
passages; carry STATE.md's Q1 register question into that read rather than pre-deciding it.

## Trust

- Both corrections landed, committed, and independently re-verified at the orchestrator's own tier rather than accepted from a digest — T-01 verify exit 0 and T-02 verify exit 0, both re-run by me; `git diff 41c16c7..f60d5d2` — verified-at f60d5d27
- SC-04 is green AND proven red-capable on the index invariant — `notes/qa-BUG-148-2026-09-06.md`; 14 ok / 0 FAIL, fresh regeneration differs from the `41c16c7` index by 42 lines — verified-at f60d5d27
- SC-05 lists 17 paths, every one allowlisted — `git diff --name-only 41c16c7..f60d5d2` — verified-at f60d5d27
- SIMPLIFY was an empty pass and moved no product path, so the tip is safe to pin — `runs/2026-09-06-07-eng/digest.md`; `git diff --name-only f60d5d2 -- .harness/harness/docs` empty — verified-at f60d5d27
- Both records state the same mechanism in the same terms, as D-05 ruling 3 binds — my own side-by-side read of the DEC-174 region and `FEAT-05.../STATE.md:13-19`; NO automated check discriminates this, which the plan states outright — verified-at f60d5d27
- `test_no_amendment_construct_survives_in_the_authority` was observed green but never perturbed, so its red-capability is UNVERIFIED — `notes/qa-BUG-148-2026-09-06.md` adequacy notes

## Dead ends

- Do not re-open whether the `--stdout | diff` form belongs in only one record: the operator ruled it stays in BOTH — `plan.yaml` `decisions:` D-05 ruling 2, discharging PF-54450f537e28244ae73d9c0e48ae4efe — verified-at f60d5d27
- Do not treat FEAT-05 `STATE.md`'s 170-line / 7-heading shape as a finding: pre-existing, deliberately left as found — `plan.yaml` `decisions:` D-04 — verified-at f60d5d27
- Do not restore the untracked duplicate grilling artifact under `.harness/harness/notes/`: removed on purpose, and no agent lane may write it — `check-domain.sh --resolve` returns NOBODY — verified-at 63f7fc97
- `git merge-base origin/main HEAD` is not a usable diff baseline here; SC-03/SC-05 grade against the branch base `41c16c7` — `plan.yaml` `lanes.resolved_at` — verified-at f60d5d27
- Do not spend a cycle on SIMPLIFY's altitude finding: its premise fails against the approved BRIEF — REQ-01 positively requires the FEAT-05 record to name 2026-09-06, and D-05 ruling 1's "treatment" is the in-place mechanism, not the rhetorical register — verified-at f60d5d27

## Working set

- .harness/harness/features/BUG-148-gate-record-correction/BRIEF.md
- .harness/harness/features/BUG-148-gate-record-correction/STATE.md
- .harness/harness/features/BUG-148-gate-record-correction/feature.json
- .harness/harness/features/BUG-148-gate-record-correction/notes/qa-BUG-148-2026-09-06.md
- .harness/harness/docs/DECISIONS.md

## Done when

Scope: the review panel's inspection verdict on the two corrected passages at review_sha
Authority: finding:.claude/worktrees/harness/BUG-148-gate-record-correction/.harness/harness/features/BUG-148-gate-record-correction/notes/research-BUG-148-goalcheck-plan-c0.md#F-4
Authority: approval:.claude/worktrees/harness/BUG-148-gate-record-correction/.harness/harness/features/BUG-148-gate-record-correction/BRIEF.md#Approval
