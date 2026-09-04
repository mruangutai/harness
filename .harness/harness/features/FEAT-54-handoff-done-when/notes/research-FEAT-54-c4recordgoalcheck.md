# FEAT-54 c4 panel goalcheck record repair

## Next

The c4 plan panel record is repaired. The product lead can consume this note and report this single record-repair send-back as `cycles_used: 1`; no reader, goalcheck, formatter, build, linter, or project-wide test was rerun.

## Trust

- The canonical product digest is PASS and identifies its one member as `goalcheck-plan-c4` / `harness-pm` / PASS (`runs/2026-09-02-goalcheck-plan-c4-product/digest.md:1-10`).
- The canonical validator digest is PASS, records `should-not-exist` / `fable-advisor` and `scope` / `harness-code-reviewer` as PASS, and carries the four canonical findings in the required order (`runs/2026-09-02-c4-validator/digest.md:3-41`).
- Run `2026-09-02-c4recordgoalcheck-product` invoked `python3 .claude/skills/harness/bin/plan-merge.py set-panel --file .harness/harness/features/FEAT-54-handoff-done-when/plan.yaml --value-file /tmp/FEAT-54-c4-panel.yaml`; the command reported `PANEL cycle 4` and `APPLIED`.
- The repaired parsed panel is exactly `last_run: 2026-09-02-c4-validator`, cycle 4, with ordered reader triples `should-not-exist/fable-advisor/ran`, `scope/harness-code-reviewer/ran`, and `goalcheck/harness-pm/ran` (`plan.yaml:12-24`).
- The finding ids remain ordered `C4-SNE-01`, `C4-SCOPE-01`, `C4-SNE-02`, `C4-SNE-03`; canonical JSON bytes of the parsed finding list match the pre-mutation snapshot at SHA-256 `897968ff186fcfffc4729a7dfc67f4b52ea79bd41289d71571f442d9a9acfe6b`. Their severities are med, med, low, and info, so high, critical, and unrated counts are zero (`plan.yaml:25-59`).
- The parsed approval mapping matches the pre-mutation snapshot byte-for-byte at canonical JSON SHA-256 `8aa5e351a3c165d9180eab9c7f83bcc09cafe68ea4fcabbd78dc60938d8847fd` (`plan.yaml:3-6`). `set-panel` was the only plan mutation invoked, so no non-panel mapping was edited.

## Dead ends

- Do not rerun either validator reader or the product goalcheck: their existing canonical digests are the evidence being recorded.
- Do not rewrite the four findings from digest prose: the pre-change parsed values were snapshotted and equality-checked after the panel mutation.

## Working set

- `.harness/harness/features/FEAT-54-handoff-done-when/plan.yaml`
- `.harness/harness/features/FEAT-54-handoff-done-when/runs/2026-09-02-goalcheck-plan-c4-product/digest.md`
- `.harness/harness/features/FEAT-54-handoff-done-when/runs/2026-09-02-c4-validator/digest.md`
- `.harness/harness/features/FEAT-54-handoff-done-when/notes/research-FEAT-54-c4recordgoalcheck.md`

## Done when

Scope: The c4 panel record includes the already-run product goalcheck beside both already-run validator readers without changing findings, approval, or any non-panel plan value.
Authority: finding:.harness/harness/features/FEAT-54-handoff-done-when/plan.yaml#C4-SNE-01
