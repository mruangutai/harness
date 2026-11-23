# QA fix-c1 binding repair — FEAT-2398 — reviewed pin 2f50e8bb1f5e6442742c53e1e2997a8be341d58b

**BLUF.** Mission `fix` is now forwarded. Factual evidence is unchanged from `notes/review-harness-qa-fix-c1.md` (focused 69/69, unit 66/66, integration 95/95, all at the pin). This note only repairs receipt/dispatch binding.

## Ancestry and equivalence
- Trusted HEAD `9a975551102487553e9b4b7c11215c5826c34489`; pin `2f50e8bb` is its ancestor (`git merge-base --is-ancestor` exit 0).
- `git diff --name-only pin HEAD` lists only `.harness/harness/features/FEAT-2398-qa-test-kind-status/{feature.json,plan.yaml}`: ledger-only, zero production/test code differences. Commits: 434ef1ab (pin review station), 9a975551 (open fix-c1-validator run).
- Initial receipts (runner-written, unedited) carry tested_commit 2f50e8bb. Their sha256: unit `54be4ece927f4cf523f319fffee59da7d8d9be380ffcbbc8b32921930b84e08f`, integration `1406c4c5ccbede61c60b4c5497ee80879e2fe17370a1b721d85fa2f8b349468c`. A file copy into notes was denied by the write guard (DEC-151), so hashes are the preservation record.

## Candidate vs installed
Candidate claims rest only on the existing pin runs (focused 69/69; unit 66/66; integration 95/95 at 2f50e8bb). Any repair run at ledger HEAD is receipt/provenance evidence, not a pin rerun. Installed hook `validate-digest.py` differs from the candidate at the pin (prior note). Nothing claims the installed hook behaves as the candidate.

## Mutation assurance (advisory only)
Omission cases were absent in the earlier failed pin while the implementation there was already correct; natural reds at baseline 9eb07b4f (54 FAIL/15 ok over the 69-case file) support them. No mutation proof against 685e861a was run (guard denies in-place pin edits). Advisory, not a blocking gap. Independent code, security and UI reviewers have examined the fix; no second QA is required.

## Repair runs at ledger HEAD (receipt/provenance only)
First yield was refused: tested_commit 2f50e8bb is not checkout HEAD 9a975551 (mission fix now bound). I ran only the two printed production runner commands from the trusted checkout, `--kind unit` and `--kind integration`, `--shard 1/1`, each to its `runs/fix-c1-validator/qa/manifest-<kind>.json`.
- unit: exit 0, 66 files, tested_commit 9a975551, runner_exit 0.
- integration, attempt 1: runner_exit 1, only failure `test-typescript-typecheck.py` (no `node_modules/.bin/tsc`, environment prerequisite, not an assertion). I ran `bun install --frozen-lockfile` (ignored node_modules; tracked tree clean; not a named repair command, disclosed) and reran once.
- integration, attempt 2: exit 0, 95 files, ALL PASSED incl. `test-validate-digest.py` (69/69 feat2398 cases), runner_exit 0, tested_commit 9a975551. Output: /tmp/fix-c1b-{unit,integration,integration2}.txt.
These are provenance runs at ledger HEAD, not pin reruns; the candidate claim stays sourced to the pin runs. No receipt was hand-edited; no source, pin or HEAD changed.
