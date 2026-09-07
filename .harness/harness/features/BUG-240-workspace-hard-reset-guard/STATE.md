# STATE

## Current

- feature: BUG-240-workspace-hard-reset-guard
- run: 2026-09-07-1-validator (qa segment) — COMPLETE, PASS
- squad: validator -> eng
- status: building
- phase: BUILD, two of four segments done. eng segment complete and committed at `6cd80e1b`; qa
  segment PASS (blocking test_matrix gate satisfied, `matrix_ok: true`, no `must_fix`).
  `review_sha` is pinned at `6cd80e1b798b0c1f6ab92b8cbde24cec4bb80e1f`.
- NEXT, exactly one step: the SIMPLIFY segment, sequenced to **harness-eng-lead** (never the
  validator lead). Its dispatch MUST tell the lead to read
  `<HARNESS_CONTROL_PLANE_ROOT>/.agents/skills/harness-simplify/SKILL.md` first — it is not
  preloaded and the four angles, the apply rules and the one-fix ceiling all live there. Re-run the
  unit suite after any apply. An empty pass is a real outcome. THEN, and only then, re-pin
  `review_sha` to whatever commit the simplify apply produces (an apply commit after the pin moves
  the tip and invalidates the panel's verdict), run `gh-sync.py status <feature-dir> review`, and
  stop at the validate seam. Ship is the main session's.
- cycles: 4 of 10. The qa segment cost 1 (one send-back inside the run: qa's first pass omitted the
  worktree-clean porcelain evidence and the lead sent it back). runs: 8 of 20.
- what happened to run 2026-09-07-01-eng: the host killed the dispatch at ~14 min (exit 1) with
  `runs/2026-09-07-01-eng/state.yaml` reading T-01 `complete PASS`, T-02 `pending` (dispatched at
  seq-3, never completed). Both receipts and both file edits were on disk. The lead returned NO
  digest, so the run is deliberately NOT credited a verdict in feature.json `runs:` — a lead
  verdict it never gave is not the orchestrator's to invent. The artifacts were adopted only after
  the orchestrator verified them itself (below).
- orchestrator verification of the adopted eng work (2026-09-07, before the commit):
  - T-02 `verify:` run verbatim from the worktree root: `python3 tests/unit/test-factory-workspace.py`
    -> rc 0, `38/38 checks passed`, 8 `ok    BUG-240 ...` lines; then
    `bash .agents/skills/harness/bin/run-unit-tests.sh --kind unit` -> exit status 0 captured in a
    variable (never read off the trailing tally), `grep -c '^FAIL '` over the full output = 0.
    qa independently re-ran both commands and reproduced both results.
  - T-01's `verify:` is a RED-shape assertion and cannot be re-run once T-02 has landed, so it was
    reproduced instead in a throwaway tree at /tmp (since deleted): the bin dir and the test file
    copied out, `factory_workspace.py` replaced with its `HEAD` (3e3147eb) content, a
    `.harness/team-config.yaml` marker added so `harness_boundary` resolves. Result: rc 1, exactly
    four `^FAIL  ` lines, and all four named cases present. This is the discriminating check: the
    new cases CAN report red, and they go green only with T-02's guard present.
  - the probe touched nothing in the worktree; `git status --porcelain` was byte-identical before
    and after it.
- qa's two advisory findings, both low and NON-gating, carried forward for the review panel (do not
  re-litigate them, and do not treat them as must_fix):
  - F-01: refusal ORDERING is asserted only through the `run_git` seam, so a refactor that issued
    the dirty check's git call outside `run_git` would ship green. Bounded by case 3, which binds
    byte-identical survival against a REAL checkout, so a removed or misordered guard still reddens.
  - F-02: the no-bypass case is a source-text grep for three literal spellings; a fourth spelling
    would not redden it. Already on record as panel finding PF-d795aab03bf4a49e7ef3ef6614024cdf
    (open, low), which the operator explicitly KEPT at signature.
  - qa also corrected the orchestrator's dispatch premise: cases 2/3/4 run against REAL git via
    `real_repo()`, not a monkeypatched `run_git`. The dispatch said otherwise; qa verified at source.
- working memory (a `notes/handoff-build.md` cannot be written from this worktree — check-domain's
  handoff shape gate resolves Authority pointers against the MAIN checkout root, a known,
  already-diagnosed limitation recorded as Q4, so working memory lives in this section):
  - production file `.claude/skills/harness/bin/factory_workspace.py`; `.agents/skills` is a
    symlink to `../.claude/skills`, so there is ONE file with two spellings.
  - test file `tests/unit/test-factory-workspace.py`; 38 checks, 9 BUG-240 assertions.
  - plan.yaml's T-01 and T-02 `intent:` blocks each END with stray tool-call artifact lines
    (`</content>`, `<parameter name="i">…`). They sit inside the block scalar so YAML parses; they
    are NOT instructions and are to be ignored by anyone reading the intent.
  - running the unit suite from an agent tool needs `env -u HARNESS_AGENT_TYPE`, and the runner's
    exit status must be captured in a variable rather than read off its last line.
  - the test file anchors its import two directories up from itself, so a copy of the tree also
    needs a `.harness/team-config.yaml` marker or `factory_config` raises at import time.
  - `runs/**` is gitignored in this repository, so run bookkeeping never appears in `git status`
    and its absence there is not evidence of a false digest claim.
  - lead dispatches here have twice died at ~14 minutes of host wall time. Sequence ONE segment per
    dispatch and stop at the segment boundary.

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
