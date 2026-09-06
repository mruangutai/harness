# Plan fix c1 — BUG-148 — F-1 and F-3 closed, F-2 citation strengthened

**Both must_fix findings are closed; the plan is ready for the adversarial panel.** No task was
added, removed or re-scoped; D-01's rewrite-in-place shape is unchanged; no record under correction
was touched. `git status --porcelain` in the worktree still reports exactly the two untracked
directories it reported before this run.

## What changed

- **F-1 (med) — SC-05 re-baselined** (`BRIEF.md:85-96`). Graded command is now
  `git diff --name-only 41c16c7..<review_sha>`, allowlist unchanged (the three record paths plus this
  feature's own directory). The text names `41c16c736e3cc4b2b331757081c90a24f2ba977d` in full, says
  it is the branch base recorded at `plan.yaml` `lanes.resolved_at`, and records why the merge-base
  form was dropped with the measurement (merge-base `8bdc2477`, three foreign paths).
- **F-1 knock-on — SC-03 uses the same base** (`BRIEF.md:68-74`): `git diff 41c16c7..<review_sha> --
  .harness/harness/docs/DECISIONS.md`. Its assertion about which lines may appear is unchanged; both
  criteria keep `verify: inspection`.
- **F-3 (low) — T-01's `verify:` now greps `2026-08-03`** (`plan.yaml:85`), added to the existing
  four strings inside the same `for t in ...` list. Changed through
  `plan-merge.py amend --key tasks --id T-01 --field verify --expect-sha256 33d5117a…`; every other
  line of the block is byte-identical and it is still a literal `|` block.
- **F-2 (advisory, no task change) — citation strengthened** (`BRIEF.md:120-127`, beside DEC-205).
  Cites `check-domain.sh:1798-1800`, quotes the denial message, and states the nuance: that sentence
  is the rationale attached to the LINE-BUDGET denial, **not** a standalone rule elsewhere in the
  file — read as the enforcement layer's own characterisation of `STATE.md` as a current-truth
  record, not an independent prohibition on appending. Verified at source (`check-domain.sh:1796-1800`).
- F-4, F-5, F-6 left as recorded advisories. `approval: {status: pending}`; no `panel:` key.

## Measured, read-only, in this worktree at HEAD `41c16c7` (2026-09-06)

```
$ git diff --name-only 41c16c7..HEAD          # SC-05
EXIT=0 LINES=0
$ git diff 41c16c7..HEAD -- .harness/harness/docs/DECISIONS.md   # SC-03
EXIT=0 LINES=0
$ git merge-base origin/main HEAD
8bdc24777233258706029071f43f75c3e725f0c8
$ git status --porcelain
?? .harness/harness/features/BUG-148-gate-record-correction/
?? .harness/harness/notes/
```

**Honest reading:** both commands execute and exit 0, but at HEAD = the base the range is empty, so
this proves executability and the absence of foreign paths in the range — it does not exercise the
allowlist against a real correction commit. That happens at `review_sha`. I did not grade the
working tree instead; the commands above are the criterion's own form with `<review_sha>` = HEAD.

`python3 .agents/skills/harness/bin/check-plan-routes.py <plan.yaml>` → `OK T-01 granted to
harness-documentor`, `OK T-02 granted to harness-orchestrator`, `0 violation(s)`, **exit 0**.

## Open questions

- **Q1 (non-blocking, for the panel or signature):** `.harness/harness/notes/` (the grilling note) is
  untracked today and lies **outside** this feature's own directory. If it is committed on this
  branch, SC-05's allowlist as written fails on it. I did not widen the allowlist — the dispatch
  fixed it — so either the note stays uncommitted, or SC-05 gains `.harness/harness/notes/` at
  signature.
- **Q2 (non-blocking):** T-01's new `2026-08-03` grep is non-discriminating in isolation — the
  pre-change evidence sentence already contains that date, so the grep is a *survival* assertion
  (REQ-01's "names the run it corrects" must not be lost in the rewrite), not proof of new work.
  The discriminating conjuncts remain the `Every gate was green` absence check and the three
  correction phrases.
