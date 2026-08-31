# Handoff — build phase — FEAT-41-one-station-vocabulary

## Next

Dispatch the validator panel against `review_sha`. All 15 tasks are done and both
test kinds are green; nothing is left to build. Inputs: `plan.yaml` (15 tasks,
D-01..D-14), `BRIEF.md` (REQ-01..REQ-07, SC-01..SC-09), and the per-task receipts in
the commit messages `dedaadf..66acf06` — every measurement, deviation and mutant run
is recorded there rather than in a separate digest.

Two items need a VERDICT rather than a re-measurement, both recorded and neither fixed:
T-10's verify line 3 cannot pass as written, and T-15 was executed main-session-direct
though the plan declares it `team`. Both are argued in their commits; the panel should
rule on whether the reasoning holds, not repeat the work.

## Trust

- unit exit 0, 493 PASS; integration exit 0, 797 PASS — verified-at 66acf06, both kinds run after every task
- INV-26 reads ZERO lines against live board 3, which is T-10's regression bound — verified-at 66acf06
- The board pass is idempotent: a second run wrote 0 and skipped the same 8 — verified-at a425e40
- The 8 skipped cards are ALL feature PARENT cards of shipped features, so all sit outside INV-26's per-task walk — verified-at a425e40
- Every task's cases were mutation-proved, not merely run green; the mutant table is in `.harness/logs/2026-08-31.md` — verified-at 66acf06
- T-10 verify line 3 compares a lowercased board read against a capitalised column name and CANNOT pass; the corrected form ran exit 0 — verified-at a425e40
- `plan-merge.py apply` CREATES a plan.yaml when the base is absent, which is why T-09's denial of the Write route loses nothing — verified-at b72e93e
- INV-32 reports THIS feature's own review_sha until the pin moves; that is the invariant working, not a defect — verified-at a1dc932
- FEAT-38's inherited violation is GONE, fixed on main by the two commits this branch rebased onto — verified-at 66acf06
- T-14's four verify greps need `-F` or escaped parens under `pi-uu-grep 0.2.0`, which reads the pattern as ERE — verified-at a1dc932

## Dead Ends

- Do NOT re-run the one-time board pass; it is idempotent but it WRITES, and a run against a moved plan would move cards the panel has not seen
- Do NOT touch `review_sha` in any other feature.json — T-14's intent forbids it, and 19 directories carry honestly-stale-looking pins from layout history
- Do NOT edit `plan.yaml` with Write or Edit; T-09 closed that route for every author including the main session — use `plan-merge.py` verbs
- Do NOT treat `--kind unit` as the suite: it covers 29 of 56 scripts and that gap hid T-01's breakage for four tasks
- Do NOT re-litigate the nine inverted approval-guard cases as regressions; the ALLOW direction they asserted is unreachable by design (T-09)
- Do NOT quote a retired station spelling in a comment — SC-02 greps for it, and this feature tripped that four times

## Working Set

- .harness/harness/features/FEAT-41-one-station-vocabulary/plan.yaml
- .harness/harness/features/FEAT-41-one-station-vocabulary/BRIEF.md
- .harness/logs/2026-08-31.md
- .claude/skills/harness/bin/check-domain.sh
- .claude/skills/harness/bin/check-state.sh
