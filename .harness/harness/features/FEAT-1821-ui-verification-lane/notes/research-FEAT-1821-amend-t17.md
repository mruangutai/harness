# FEAT-1821 T-17 plan amendment

## Conclusion

T-17 now names only `.omp/agents/harness-ui-reviewer.md` and `tests/unit/test-ui-reviewer-policy.py`, in that order, and its literal-block verification command is exactly `python3 tests/unit/test-ui-reviewer-policy.py`. Approval remains pending for Main.

## Legal mutation route

The control-plane `plan-merge.py amend` verb was used twice with compare-and-swap hashes obtained from `amend --show`: first `tasks:T-17.files` with `--yaml-value` and expected SHA-256 `7fcd260d15d5b5c4f545aa9eae7a895605a3c015239b3618541fa73773e79ab3`, then `tasks:T-17.verify` with expected SHA-256 `1bc65cf10b9e1d4275d41ecc7d238148786f20d39710d4fbafd98c0bd54725fc`. Both returned `AMENDED` and `APPLIED`; neither emitted `APPROVAL-RESET:`.

Exact mutation commands, run from the feature checkout after writing the requested replacement values to the two named temporary files:

    python3 /Users/molchairuangutai/GitHub/harness/.agents/skills/harness/bin/plan-merge.py amend --file .harness/harness/features/FEAT-1821-ui-verification-lane/plan.yaml --key tasks --id T-17 --field files --expect-sha256 7fcd260d15d5b5c4f545aa9eae7a895605a3c015239b3618541fa73773e79ab3 --value-file /tmp/feat1821-t17-files.yaml --yaml-value
    python3 /Users/molchairuangutai/GitHub/harness/.agents/skills/harness/bin/plan-merge.py amend --file .harness/harness/features/FEAT-1821-ui-verification-lane/plan.yaml --key tasks --id T-17 --field verify --expect-sha256 1bc65cf10b9e1d4275d41ecc7d238148786f20d39710d4fbafd98c0bd54725fc --value-file /tmp/feat1821-t17-verify.txt

## Scoped verification

Command:

    python3 /Users/molchairuangutai/GitHub/harness/.agents/skills/harness/bin/plan-merge.py check --file /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-1821-ui-verification-lane/.harness/harness/features/FEAT-1821-ui-verification-lane/plan.yaml --root /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-1821-ui-verification-lane

Result: `OK T-17 2 anchor(s) resolved`; final summary: `18 task(s), 49 anchor(s) resolved, 0 failure(s)`.

Post-mutation `amend --show --yaml-value` returned exactly the two requested files and field SHA-256 `41c60c1b774e4f11f7a4fd3ce8e462a92e240cd29f14cb911f62f83dd903cc46`. Post-mutation `amend --show` returned exactly the requested verification command and field SHA-256 `a9267f5cbc0f8adf18b6f7a8057bad049ee95606b357f95e759dc578b68e444c`.

## Change isolation

The plan path was clean before mutation. Its SHA-256 changed from `5d18d1f1f54af651479b179ebb4ee73b74b22229f59d57d1871dca901d59e1d9` to `a5ba84db6d7a4086631f77907a9114a5109a312df4b09fef031ddd4a8ed2aed9`. The complete Git diff reports one changed work file and only the T-17 `files` and `verify` blocks: 3 insertions and 4 deletions. No other task, decision, approval field, or T-17 field changed. `git diff --check` produced no output. The only changed work file is `.harness/harness/features/FEAT-1821-ui-verification-lane/plan.yaml`; this research note is the required PM handoff artifact.

Approval is still `status: pending`; its date, approver, reset timestamp, reset reason, and resume station are unchanged.
