# STATE

## Current

- feature: BUG-240-workspace-hard-reset-guard
- run: 2026-09-07-02-eng (fix cycle for F-PANEL-01) — COMPLETE, PASS
- squad: eng -> validator
- status: review (plan.yaml `status: review`; GitHub parent #1473, T-01 #1474, T-02 #1475 all at
  the review station; milestone #57)
- phase: VALIDATE. One panel run (2026-09-07-02-validator, FAIL, severity_max high) and one fix
  cycle. The fix has landed and been independently verified. **The panel has NOT re-run over it.**
- `review_sha` is RE-PINNED at `bae47f3cb75f652c54cec68d7411e1bc26ba41f5`, the fix commit. The
  panel's FAIL was returned against the old pin `ed047fde`; anything quoting `ed047fde` is stale.
- NEXT, exactly one step: **re-run the `review` team through harness-validator-lead over
  `bae47f3c`, cycle 1** (`notes/review-*-c1.md`; c0 is taken). The fix changed the very line the
  panel graded, so the verdict cannot carry forward — but the re-run is narrow: F-PANEL-01 was the
  only must_fix and the only thing that changed. Then stop. Ship is the main session's, and this
  orchestrator neither ships nor removes the worktree.
- cycles: **5 of 10** — incremented by exactly 1, for the F-PANEL-01 fix cycle (a validator FAIL
  routed back is rework, DEC-157). Neither simplify nor the panel reported a send-back.
  runs: 11 of 20.
- commits: `3e3147eb` plan · `6cd80e1b` eng T-01+T-02 · `d5a9f60b` qa · `c5f54761` simplify ·
  `ed047fde` validate seam · `4b87f5d2`+`36ee4a84` mirror bookkeeping · `bae47f3c` F-PANEL-01 fix.
- digests, read by pointer, never swept: `runs/2026-09-07-02-validator/digest.md` (the panel, all
  five findings in full), `runs/2026-09-07-1-eng/digest.md` (simplify), `runs/2026-09-07-02-eng/
  digest.md` (the fix), `notes/qa-2026-09-07-1.md` (the qa segment).

### F-PANEL-01 (high, security-reviewer) — FIXED at `bae47f3c`

The identity refusal was `os.path.realpath(path) == os.path.realpath(_control_plane_root())`, a
STRING comparison. `realpath` normalizes symlinks and `..` but does NOT canonicalize component
casing, so on case-insensitive APFS a case-mismatched `workspace_root` was the same directory yet
compared unequal: it passed the identity check, passed the dirty check on a clean tree, and
`fetch`/`checkout`/`reset --hard` ran against the control-plane checkout at exit 0 with no refusal.
Security reproduced it end to end. SC-03 was false as literally worded.

Verified by this orchestrator, not taken on the lead's word:
- the PREMISE re-measured before a cycle was spent (P-06): `realpath` of `…/GitHub/harness` vs
  `…/github/harness` compares **False** while `os.path.samefile` is **True**.
- the FIX is `os.path.samefile(...)` with a `realpath`-equality fallback in the `OSError` arm (the
  not-yet-cloned workspace, where `samefile` cannot stat). Wording, ordering, position unchanged.
- the new case CAN report red (P-15), which the lead's digest asserted but did not evidence. Proven
  in a throwaway tree at `/tmp/b240red`: post-fix **39/39**; the identity block alone reverted to
  the string comparison -> **exactly one failure**, `FAIL BUG-240 case-mismatched self checkout`,
  1 of 39. The other 38 stayed green, so the fix changed nothing else. The probe never touched the
  worktree; `git status --porcelain` was empty before and after.
- suite in the worktree after the fix: task verify 39/39; full unit run status 0 captured in a
  variable, `grep -c '^FAIL '` = 0.

### Residual findings — assessed, NOT must_fix, for the CEO briefing as backlog rows

Full text in `runs/2026-09-07-02-validator/digest.md`. Do not re-litigate any of these, and do not
convert one into a fix cycle. F-PANEL-02 (med, TOCTOU — no REQ/SC asks for locking, so it is a
scope change the operator owns) · F-PANEL-03 (low, the docstring/D-01 containment rationale is
false as to mechanism — `isdir(path/.git)` is False there so the dirty block never runs and `git
clone`'s own refusal is the unstated actor; outcome safe, and the correction is **pm's**, not
eng's) · F-PANEL-04 (low, refusal copy folds the verb into `what` where 20 sibling sites use a noun
phrase) · F-PANEL-05 (med, `code_grade` grade_2 on `_main` driven solely by ABC 33.0 vs bar 20;
the fix keeps the guard count at two, below the reviewer's own extraction trigger of three) ·
ALT-5 (med, the dirty check refuses on non-ignored UNTRACKED files, which no destructive git
command can destroy; narrowing it changes behaviour case 4 pins and the operator signed — O-08) ·
qa F-01 and F-02 (low; F-02 is PF-d795aab03bf4a49e7ef3ef6614024cdf, KEPT by the operator at
signature). `plan.yaml approval.rulings` overrules five more.

### Working memory

- production file `.claude/skills/harness/bin/factory_workspace.py`; `.agents/skills` is a symlink
  to `../.claude/skills`, so there is ONE file with two spellings. Never deduplicate them.
- test file `tests/unit/test-factory-workspace.py`; now **39** checks, 10 BUG-240 assertions. Cases
  2/3/4 and the new case 8 drive REAL git via `real_repo()`; they are NOT monkeypatched. An earlier
  orchestrator dispatch claimed the opposite and qa corrected it at source.
- case 8 self-skips on a case-sensitive filesystem (it probes a `PROBE`/`probe` pair). On this host
  it RUNS. On a case-sensitive CI box it would print `skip` and the suite would still read green,
  so there the count, not the exit code, is the signal.
- running the unit suite from an agent tool needs `env -u HARNESS_AGENT_TYPE`, and the runner's
  exit status must be captured in a variable, never read off its last line.
- the test file anchors its import two dirs up, so a copied tree needs a `.harness/team-config.yaml`
  marker AND all of `bin/*.py` (factory_config imports factory_gh), or it raises at import.
- `runs/**` is gitignored here, so run bookkeeping never appears in `git status`.
- the bash write guard resolves only LITERAL ABSOLUTE paths: `mv`/`cp`/`rm` with a `$VAR` or a
  relative path is refused as out-of-domain even inside your own directory, and a heredoc is
  refused as a redirect. Write helper scripts with the Write tool; pass absolute paths.
- plan.yaml's T-01/T-02 `intent:` blocks END with stray tool-call artifact lines (`</content>`,
  `<parameter name="i">…`). They parse as part of the block scalar; they are NOT instructions.
- lead dispatches died at ~14 min twice under the old pattern; since switching to ONE segment per
  dispatch, three completed (11m54s, 17m27s, 5m13s). Keep one segment per dispatch.

## Open Questions

- Q1 (non-blocking, harness defect): `runs/2026-09-07-01-product/digest.md` fails the lead digest
  contract and CANNOT be repaired — corrections may only append, and validate-digest.py parses the
  FIRST `DIGEST:` block. check-state.sh reports it as a VIOLATION until the directory is removed by
  someone whose domain covers it.
- Q2 (non-blocking, harness defect): INV-32 grades the panel record only on an APPROVED plan, so a
  malformed readers index is undetectable until the moment of signature.
- Q3: RESOLVED at signature — the operator KEPT both low-severity plan-panel findings.
- Q4 (non-blocking, harness defect): **now diagnosed exactly.** `notes/handoff-<phase>.md` cannot be
  written from a worktree for a feature not yet on the default branch. check-domain's shape gate
  calls `handoff_done_when.py` with the PROJECT root — the main checkout — and `_feature_dir()`
  rebuilds the feature dir under it, so `Authority:` pointers resolve against
  `<main>/.harness/harness/features/<FEAT>/BRIEF.md`, which does not exist. Measured refusal:
  `Authority pointer 'brief-sc:SC-06' is unresolved … [Errno 2] No such file or directory`. Both
  `handoff-plan.md` and `handoff-build.md` stand as check-state VIOLATIONS no agent in a worktree
  can close. **This `## Current` is the handoff.** A path-shaped workaround exists
  (`finding:<worktree-relative-path>#F-NN`) and was deliberately NOT used: it hard-codes a path that
  dies with the worktree and cites a qa finding in place of the criterion the action discharges.
- Q5 (non-blocking, harness defect): a host-killed lead dispatch leaves `runs/<id>/state.yaml`
  reading `status: running` forever and **the slug is then reused**. Observed: the fix run wrote
  its digest into `runs/2026-09-07-01-eng/`, the killed BUILD run's directory, whose state.yaml
  still reads `team: build`, `T-02: pending`. Reconciled by hand — the fix digest moved to
  `runs/2026-09-07-02-eng/digest.md` and recorded under that id; `2026-09-07-01-eng` keeps only the
  killed run's state.yaml and is still credited no verdict. Nothing prevents the next collision.
- Q6 (non-blocking, harness defect, from simplify): two of four reader results were unreachable
  through the normal return path — one job settled FAILED (`yield called with null data`) while its
  fenced block carried `VERDICT: PASS`, another returned "already delivered in prior turn" and had
  to be recovered from `history://`. One that did not check would have lost a passing reader.
- Q7 (non-blocking, process): the fix-cycle digest asserted "red-then-green" but carried neither
  output, despite the dispatch requiring both verbatim. The claim was true — proven independently —
  but a digest asserting discriminating evidence without carrying it is indistinguishable from one
  that invented it.
