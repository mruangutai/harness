# Handoff — FEAT-48, validate → ship — written at 8e7f56dc, seq-3

## Next

**Do not ship. One bounded, main-session-direct fix step, then re-validate.** Deliver T-03's
in-file red proof into `.claude/skills/harness/bin/test-suite-independence.py` — the six cases
`plan.yaml` T-03 already mandates (injection idiom; mutant-beside-original; PID-named variant;
clean control; live-tree case asserting `discovered >= 50` with the root recomputed by an INLINE
walk, not by calling `harness_boundary`; root refusal). That is SC-03, graded `unmet`. It is
**approved-but-unmet** — the signed plan already requires it, so no operator ruling is needed and
it is a fix cycle, not a plan amendment. Every remedy here is `execution_mode: main-session-direct`
under DEC-174; **routing it to a squad spends a cycle proving nobody may edit the files.**
Then re-pin `review_sha` and re-check SC-01, SC-03, SC-04 and SC-09 at the new sha.

## Trust

- SC-01, SC-02, SC-04..SC-10 met, each graded by its own declared `verify:` method —
  `notes/research-FEAT-48-goalcheck-validate.md` — verified-at 8e7f56dc.
- SC-03 unmet; the invariant is scanner-only, 180 lines, zero case machinery, `tempfile` imported
  at :9 and never used — `notes/qa-c7.md`, and I re-read the file — verified-at 8e7f56dc.
- The scanner itself WORKS: T-03's verify block re-executed finds all ten `ea6f51f` sites, missing
  0, extra 0. **The defect is that no gate re-executes it** — test-only remedy, not a code defect —
  `notes/research-FEAT-48-goalcheck-validate.md` — verified-at 8e7f56dc.
- `qa_gate` PASSES: `matrix_ok: true`, unit 33/33, integration 30/30 — `notes/qa-c7.md` — at 8e7f56dc.
- Suite green and fast on a quiet tree: `--kind all` exit 0, `pool: 8 workers, 63 files, 48.09s
  wall`, zero `MUTATED` — my own run — verified-at 8e7f56dc.
- `run_pool.py --mutation-check` fails open on new **symlink-shaped** entries: a dangling symlink
  and a symlinked subdirectory each give exit 0 and no `MUTATED`, while an ordinary new file
  correctly gives exit 1 `MUTATED .mutant-x.sh` — my own tempdir probe — verified-at 8e7f56dc.
  T-04's approved intent requires catching a path that "APPEARED", so this is approved-but-unmet.
- `code_grade: fail` is MECHANICAL under DEC-209, not an opinion: `code-grade.py --base d135364e
  --head 8e7f56dc` gives 18 passing, 7 FAIL (5 grade-1) — my own run — verified-at 8e7f56dc.
- `review_sha` re-pinned `b86ce66a` → `8e7f56dc` to clear INV-33; the review target did not move —
  `git diff --stat b86ce66a 8e7f56dc -- .claude .github` empty — verified-at 8e7f56dc.
- FEAT-48 carries zero `check-state.sh` findings after the re-pin — my own run — verified-at 8e7f56dc.

## Dead ends

- Do not route any remedy to a dev squad — all land in `.claude/skills/harness/bin/**` or
  `DECISIONS.md`, every one `main-session-direct` — `plan.yaml` `lanes:`, DEC-174 — at 8e7f56dc.
- Do not put SC-03's reading to the operator. Both the panel and pm raised it; `plan.yaml` T-03
  ("ITS OWN RED PROOF, in the file, so CI keeps proving the guard can fail") settles it in the
  signed text — `plan.yaml` T-03 intent — verified-at 8e7f56dc.
- Do not grade T-07; `abandoned` history, no implementation — `plan.yaml` — verified-at 8e7f56dc.
- Do not read a red suite as a FEAT-48 defect before clearing the environment: with
  `HARNESS_AGENT_TYPE` set, `test-plan-merge.py` fails 11 `sign-approval` checks and the suite exits
  1; that file is not in the diff. Use `env -u HARNESS_AGENT_TYPE` — my own run — at 8e7f56dc.
- Do not raise the duplicate `PASS <file>` line as a REQ-06 regression: six test files print their
  own summary and `main`'s runner printed `PASS $s` identically — `git show
  d135364e:...run-unit-tests.sh` — verified-at 8e7f56dc.
- Do not cite `runs/**` downstream; `.gitignore:7` excludes them, so those digests die with the
  worktree. Cite `notes/` — `git check-ignore -v` — verified-at 8e7f56dc.

## Working set

- `.claude/skills/harness/bin/test-suite-independence.py`
- `.harness/harness/features/FEAT-48-parallel-safe-suite/notes/research-FEAT-48-goalcheck-validate.md`
- `.harness/harness/features/FEAT-48-parallel-safe-suite/notes/qa-c7.md`
- `.harness/harness/features/FEAT-48-parallel-safe-suite/notes/review-harness-code-reviewer-c7.md`
- `.harness/harness/features/FEAT-48-parallel-safe-suite/plan.yaml` (T-03, T-04 intent blocks)
