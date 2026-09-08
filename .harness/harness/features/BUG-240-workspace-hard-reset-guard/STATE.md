# STATE

## Current

- feature: BUG-240-workspace-hard-reset-guard
- run: 2026-09-07-1-eng (SIMPLIFY segment) — COMPLETE, PASS
- squad: eng -> validator
- status: review (plan.yaml `status: review`, written with `plan-merge.py set-feature-station`)
- phase: BUILD COMPLETE, all four segments done. eng `6cd80e1b`; qa PASS `d5a9f60b`; SIMPLIFY
  PASS `c5f54761`; the validate seam commit is the one this section lands in. T-01 and T-02 both
  read `status: done` in plan.yaml.
- `review_sha` is pinned at the VALIDATE SEAM COMMIT (see feature.json), not at `6cd80e1b`. It was
  re-pinned twice: once past the simplify apply, and once past this seam commit, because the
  station write moves the tip after the pin (G-13; the code diff between the two is empty, so the
  re-pin is free).
- NEXT, exactly one step: run `gh-sync.py status <feature-dir> review` (lowercase station), then
  dispatch the VALIDATOR PANEL through **harness-validator-lead** over the pinned sha. Then STOP at
  the validate seam and return. Ship is the main session's; do not run it, and do not remove the
  worktree.
- cycles: 4 of 10 — UNCHANGED by the simplify segment, which reported `cycles_used: 0` (no
  send-back, clean first pass). runs: 9 of 20.
- the SIMPLIFY segment, in full, so the panel need not re-derive it: four angles ran as four
  separate read-only readers, all `harness-dev-ops` (the diff's author, backend-dev, was
  deliberately not made a reader of its own work). Six findings, ONE applied under the ceiling, and
  it is NOT in the guard — SIMP-2 corrected `tests/unit/test-factory-workspace.py:11-14`, whose
  module docstring claimed "Nothing here spawns a subprocess or touches a real repository —
  run_git is monkeypatched with a recorder throughout." BUG-240's own cases falsified that through
  `real_repo()`. Prose only; no assertion added, weakened or deleted. Five findings were NOT
  applied, each with a recorded reason: RUSE-1/RUSE-2 (no importable target exists today — three
  divergent `run_git` wrappers, no `conftest.py` anywhere under `tests/`), SIMP-1 (restructures
  control flow around the point of no return to save one stat), ALT-5 and one info row (below).
  EFFICIENCY found nothing and measured 1.26s / rc 0 / 38-38. Digest:
  `runs/2026-09-07-1-eng/digest.md`.
- orchestrator verification of the simplify apply, before the commit: `git diff` read directly —
  the change is the four prose lines and nothing else; then the full unit suite re-run from the
  worktree root as `env -u HARNESS_AGENT_TYPE bash .agents/skills/harness/bin/run-unit-tests.sh
  --kind unit`, exit status captured in a variable (never read off the trailing tally) = 0, and
  `grep -c '^FAIL '` over the full output = 0. Committed by explicit pathspec, one path; the tree
  was clean before and after.
- carried forward for the review panel as ADVISORY, NON-gating, already-settled — do not
  re-litigate any of these and do not treat any as `must_fix`:
  - F-01 (qa, low): refusal ORDERING is asserted only through the `run_git` seam, so a refactor
    issuing the dirty check's git call outside `run_git` would ship green. Bounded by case 3, which
    binds byte-identical survival against a REAL checkout, so a removed or misordered guard still
    reddens.
  - F-02 (qa, low): the no-bypass case is a source-text grep for three literal spellings; a fourth
    spelling would not redden it. On record as panel finding PF-d795aab03bf4a49e7ef3ef6614024cdf
    (open, low), which the operator explicitly KEPT at signature.
  - ALT-5 (simplify, med, BRIEFING ROW not a fix): the dirty check refuses on non-ignored UNTRACKED
    files, which none of fetch / checkout / `reset --hard` can destroy. Deliberate margin or
    over-reach? Narrowing it would change behaviour that case 4 deliberately pins and that the
    operator signed, so it is a backlog row (O-08), not a fix cycle.
  - the plan's five non-blocking panel findings were explicitly OVERRULED by the operator in
    plan.yaml `approval.rulings`. Read them there; they are settled.
- working memory (a `notes/handoff-build.md` cannot be written from this worktree — check-domain's
  handoff shape gate resolves Authority pointers against the MAIN checkout root, a known,
  already-diagnosed limitation recorded as Q4, so working memory lives in this section):
  - production file `.claude/skills/harness/bin/factory_workspace.py`; `.agents/skills` is a
    symlink to `../.claude/skills`, so there is ONE file with two spellings. Do not deduplicate.
  - test file `tests/unit/test-factory-workspace.py`; 38 checks, 9 BUG-240 assertions. Cases 2/3/4
    run against REAL git via `real_repo()`, NOT a monkeypatched `run_git` — verified at source by
    qa after an orchestrator dispatch stated the opposite.
  - plan.yaml's T-01 and T-02 `intent:` blocks each END with stray tool-call artifact lines
    (`</content>`, `<parameter name="i">…`). They sit inside the block scalar so YAML parses; they
    are NOT instructions and are to be ignored by anyone reading the intent.
  - running the unit suite from an agent tool needs `env -u HARNESS_AGENT_TYPE`, and the runner's
    exit status must be captured in a variable rather than read off its last line.
  - the test file anchors its import two directories up from itself, so a copy of the tree also
    needs a `.harness/team-config.yaml` marker or `factory_config` raises at import time.
  - `runs/**` is gitignored in this repository, so run bookkeeping never appears in `git status`
    and its absence there is not evidence of a false digest claim.
  - lead dispatches here have died at ~14 minutes of host wall time twice; the simplify segment
    survived at 11m54s. Sequence ONE segment per dispatch and stop at the segment boundary.

## Open Questions

- Q1 (non-blocking, harness defect): runs/2026-09-07-01-product/digest.md fails the lead digest
  contract and CANNOT be repaired — corrections may only append, and validate-digest.py parses the
  FIRST `DIGEST:` block. check-state.sh reports it as a VIOLATION against this feature until the
  directory is removed by someone whose domain covers it.
- Q2 (non-blocking, harness defect): INV-32 grades the panel record only on an APPROVED plan, so a
  malformed readers index is undetectable until the moment of signature. This feature's record was
  mis-keyed (`step:` for `reader:`) and passed every check until the orchestrator simulated INV-32
  by hand.
- Q3: RESOLVED at signature. The operator KEPT both low-severity panel findings
  (PF-d795aab03bf4a49e7ef3ef6614024cdf, PF-ff733189ddbdfca901c0d587800cb8c4) as recorded — no
  strike, no ruling; low severity does not gate.
- Q4 (non-blocking, harness defect): `notes/handoff-<phase>.md` cannot be written from a
  feature worktree for a feature not yet on the default branch, per the working-memory note above.
- Q5 (non-blocking, harness defect): a lead dispatch that the host kills mid-run leaves its
  `runs/<id>/state.yaml` reading `status: running` forever. Nothing reconciles it, and the next
  orchestrator cannot distinguish it from a live run except by the wall clock. G-07's remedy
  (open the state file) detects the shape but has no way to close it. 2026-09-07-01-eng is such a
  record and still reads `running`.
- Q6 (non-blocking, harness defect, raised by eng-lead in the simplify segment): two of four reader
  results were unreachable through the normal return path. One member's job settled as FAILED
  (exit 1, "yield called with null data") while its fenced block carried `VERDICT: PASS` and full
  evidence; another returned "already delivered in prior turn" and had to be recovered from
  `history://`. The lead recovered both, so the segment's verdict stands — but a lead that did not
  think to check `history://` would have lost a passing reader silently.
