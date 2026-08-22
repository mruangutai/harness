# Handoff — FEAT-31, validate → ship — written at ee608d2, seq-3

## Next

**Grade SC-15's behaviour half at FEAT-32's build-to-validate seam.** Read the NEW
`handoff-build.md`'s `## Next` FIRST, before spawning anything, then spawn one orchestrator given
only the feature directory and compare its first dispatch. Do not grade it against THIS feature's
handoffs — both are stale by construction and produce a confound in opposite directions
(`notes/uat-and-signature-2026-08-22.md`). Everything else here is closed: PR #698 merged at
15:48:38Z, all 20 attached issues CLOSED and at station Done.

## Trust

- All 19 tasks are done and the signature covers 19, confirmed by the operator rather than assumed — T-19 FULFILS the signature because SC-09 was already approved scope — `notes/uat-and-signature-2026-08-22.md` — verified-at ee608d2
- 38 test scripts pass, 0 FAIL, on `run-unit-tests.sh --kind all` — verified-at d4b3180
- CI's single `integration` job passed in 1m51s; one job is the design, matching merged PR #491 — `gh pr checks 698` — verified-at ee608d2
- The native close chain works end to end with NO harness station write: `closingIssuesReferences` returned 20 of 20, and all 20 read CLOSED at station Done within seconds of the merge — `gh api graphql` on PR #698 — verified-at ee608d2
- SC-10 is MET at 109 rows with two live orchestrators present, and 0 of 109 rows lack a `headroom=` or `overage=` field — asserted, not eyeballed — verified-at bff6e92
- SC-15's GATE half is automated and passing with a mutant red proof; only the BEHAVIOUR half defers — verified-at d4b3180
- `--check-kinds` exits 0: the script arrays and `test_kinds.integration.detect` agree — verified-at d4b3180
- 21 residual findings are filed as #677 through #697, so nothing uncovered is carried in the branch — verified-at d4b3180
- INV-17 fired on THIS feature's own status write and demanded this file — the invariant is load-bearing on its author — `check-state.sh` — verified-at ee608d2
- Whether FEAT-32's seam actually produces a gradeable `## Next` — UNVERIFIED

## Dead ends

- Do NOT grade SC-15 against this feature. Every task is done, so the only successor that could satisfy the criterion is one that IGNORES the tree in front of it. The predecessor's own relay was already refused by pm for a different confound — `notes/uat-and-signature-2026-08-22.md` — verified-at d4b3180
- Do NOT re-add `.harness/logs/` wholesale to `.gitignore`. The rule is `.harness/logs/gh-cost-*.jsonl` and THAT EXACT GLOB ONLY — the session journals in the same directory are TRACKED, and a blanket rule untracks the project journal — `.gitignore:34` — verified-at ee608d2
- Do NOT expect the harness to enable a Projects v2 workflow. There is no API: all 32 `ProjectV2` mutations include `deleteProjectV2Workflow` and nothing that creates or enables one — `.harness/notes/grilling-board-lifecycle-2026-08-22.md`, #673 — verified-at d065b3b
- Do NOT re-derive the residuals. #677–#697 hold them; re-finding one as new burns a cycle — verified-at d4b3180

## Working set

- `.claude/skills/harness/bin/context-watch.py` — the instrument; the two-line threshold seam is the red-proof target
- `.claude/skills/harness/bin/context-watch-hook.py` — the `PostToolUse` cutover; advises, never refuses
- `.claude/skills/harness/bin/check-state.sh` — INV-17's handoff shape pass, four headings, 60-line cap, no empty section
- `.claude/skills/harness/bin/feature_schema.py` — the `runs[].agent` rule and its GENERATED exempt map
- `.harness/harness/features/FEAT-31-orchestrator-context-watch/notes/uat-and-signature-2026-08-22.md` — why SC-15 defers
