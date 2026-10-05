# FEAT-1928 plan reconciliation apply

## Conclusion

Cycle 2 is fully reconciled without reopening SC-01–SC-08 or D-01–D-05. T-04 alone remains gated on FEAT-70 and operator re-signature; T-01 and T-02 remain independent. Both BRIEF and plan approval remain pending.

## Applied findings

- T-04 now requires re-anchoring and checking before the first re-signature when FEAT-70 lands first. Otherwise its post-FEAT-70 files amendment resets standing approval and implementation waits for operator re-signature (`plan.yaml` T-04 `intent`).
- T-04 integration coverage is limited to plan-merge consumer behavior: structured-key consumption, boundary refusal for malformed or absent durable input, reader/finding history, and record-amendments parity. T-01 alone owns digest_record.py final-block selection, historical extra-key acceptance, and byte-identity hashing (`plan.yaml` T-01 and T-04 `intent`).
- T-04 invokes the check verb through the resolved post-FEAT-70 plan-merge CLI entry point; the current HEAD reconciliation gate remains the scoped command below (`plan.yaml` T-04 `intent`).
- The affirmative info finding is recorded unchanged in severity, kind, and summary, then resolved as assessed no-action evidence rather than treated as a defect (`plan.yaml` `panel.findings` PF-312ebc7854e1119f794364fcc134bacc).

## Panel record

`record-panel` recorded cycle 2 from `runs/plan-reconcile-product/panel-c2.md`. The final record retains all five c0/c1 reader entries and all six historical findings with their resolved dispositions, then records cycle-2 scope, should-not-exist, and design readers as `ran`. All four new finding identities came from `record-panel`; their original severities, kinds, proportionality scope, and summaries are preserved. The three requested changes are resolved by T-04; the affirmative finding is resolved with an explicit assessed/no-action resolution.

## Verification

Command:

    python3 .claude/skills/harness/bin/plan-merge.py check --file .harness/harness/features/FEAT-1928-digest-object-contract/plan.yaml --root /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-1928-digest-object-contract

Exact summary:

- `OK T-01 22 anchor(s) resolved`
- `OK T-02 36 anchor(s) resolved`
- `OK T-03 6 anchor(s) resolved`
- `OK T-04 7 anchor(s) resolved`
- `4 task(s), 71 anchor(s) resolved, 0 failure(s)`

## Approval

`BRIEF.md` approval is pending. `plan.yaml` approval is pending and `needs_approval: true`; no signature or GitHub sync was performed. `feature.json` still records the settled rework history as 2 rounds / 90 minutes, pointing to `notes/approval-2026-09-28.md`.

## Open questions

None.
