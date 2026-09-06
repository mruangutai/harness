# Handoff — BUG-1290-factory-claim-repo-root, ship → operator decision — written at e93a59c7, seq-1

## Next

Present `notes/ship-review-2026-09-05-13-ship.md` to the operator and take the ship/fix/re-scope/stop
decision. Two non-blocking questions ride with it: Q1, the REQ-05 wording correction (briefing row
B-10, the panel's F-1), and Q2, whether to spend a cycle closing the unproven issue-map clause of
REQ-02 (row B-3). On acceptance the main session — not the orchestrator — runs `gh-sync.py ship
<feature-dir> --body-file <the briefing>` from the MAIN checkout, then `gh-sync.py backlog` for every
unstruck row, then the merge, then feature-close distillation. Nothing here is shipped, merged or
PR'd yet.

## Trust

- All nine SC MET, each verified by pm's own command runs at the pin, not transcribed from a report — `runs/2026-09-05-12-product/digest.md` — verified-at 76e26386
- All five task `verify:` commands pass on the committed tree, re-run by the orchestrator itself rather than accepted from the build digest — `notes/build-digest-reconstructed-2026-09-05-07-eng.md` — verified-at 419614e5
- Panel PASS with `must_fix: []`; both self-scoping reviewers looked and stayed in scope rather than declining — `runs/2026-09-05-11-validator/digest.md` — verified-at 76e26386
- The main checkout is clean of this run's residue and its layout `features` surface re-measures CLEAN — backup at `/tmp/bug1290-main-residue/` — verified-at e93a59c7
- Simplify applied nothing; code outside the feature dir is byte-identical from 419614e5 to the pin — `runs/2026-09-05-10-eng/digest.md` — verified-at 76e26386
- REQ-02's issue-map clause is delivered in code but killed by no test — `runs/2026-09-05-12-product/digest.md` Q2 — verified-at 76e26386
- The plan panel's own digest and the build lead's own digest are destroyed, not merely misfiled — `runs/2026-09-05-08-validator/CLOBBERED.md` — verified-at e93a59c7
- The eng lead's claim that both checkouts were clean after T-01's stray edit was FALSE; T-04's edits were still in the main checkout — `notes/build-digest-reconstructed-2026-09-05-07-eng.md` Q2 — verified-at e93a59c7

## Dead ends

- Do not re-litigate the five signed choices: the two-function split seam, the paren-free `seg` local, `resolve_repo`'s bare-`harness` early return, the four out-of-scope owner-strip sites, and `mruangutai/harness`'s absence from the live fleet — `runs/2026-09-05-11-validator/digest.md` "The five signed choices" — verified-at 76e26386
- Do not widen `layout_migration`'s migrated pattern to accommodate an inlined `segment_of(...)` call; the paren-free local is the settled reconciliation — `plan.yaml` T-04 step 1 — verified-at 76e26386
- Do not treat `no_plan` on FEAT-04 from `main` as a regression; the brief discloses it and the fix is FEAT-04's — `BRIEF.md ## Constraints` — verified-at 76e26386
- Do not re-run the panel or re-pin for a briefing-row fix; every surviving finding is non-gating and B-3 is the only one the operator may convert into a cycle — `runs/2026-09-05-11-validator/digest.md` — verified-at 76e26386

## Working set

- `.harness/harness/features/BUG-1290-factory-claim-repo-root/notes/ship-review-2026-09-05-13-ship.md`
- `.harness/harness/features/BUG-1290-factory-claim-repo-root/feature.json`
- `.harness/harness/features/BUG-1290-factory-claim-repo-root/plan.yaml`
- `.harness/harness/features/BUG-1290-factory-claim-repo-root/runs/2026-09-05-11-validator/digest.md`
- `.harness/harness/features/BUG-1290-factory-claim-repo-root/runs/2026-09-05-12-product/digest.md`

## Done when

Scope: the operator returns a ship, fix, re-scope or stop decision on the briefing
Authority: finding:.claude/worktrees/harness/BUG-1290-factory-claim-repo-root/.harness/harness/features/BUG-1290-factory-claim-repo-root/runs/2026-09-05-11-validator/digest.md#F-1
