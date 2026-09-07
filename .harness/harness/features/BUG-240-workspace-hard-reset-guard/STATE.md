# STATE

## Current

- feature: BUG-240-workspace-hard-reset-guard
- run: 2026-09-07-01-eng (INTERRUPTED — see below); next is the qa segment
- squad: eng -> validator
- status: building
- phase: BUILD. T-01 and T-02 are both `done`; the eng segment's code work is committed.
  Next: qa segment (test_matrix hard gate) via harness-validator-lead; then SIMPLIFY via
  harness-eng-lead; then re-pin review_sha and stop at validate. Ship is the main session's.
- what happened to run 2026-09-07-01-eng: the host killed the dispatch at ~14 min (exit 1) with
  `runs/2026-09-07-01-eng/state.yaml` reading T-01 `complete PASS`, T-02 `pending` (dispatched at
  seq-3, never completed). Both receipts and both file edits were on disk. The lead returned NO
  digest, so the run is deliberately NOT credited a verdict in feature.json `runs:` — a lead
  verdict it never gave is not the orchestrator's to invent. The artifacts were adopted only after
  the orchestrator verified them itself (below).
- orchestrator verification of the adopted work (2026-09-07, before the commit):
  - T-02 `verify:` run verbatim from the worktree root: `python3 tests/unit/test-factory-workspace.py`
    -> rc 0, `38/38 checks passed`, 8 `ok    BUG-240 ...` lines; then
    `bash .agents/skills/harness/bin/run-unit-tests.sh --kind unit` -> exit status 0 captured in a
    variable (never read off the trailing tally), `grep -c '^FAIL '` over the full output = 0.
  - T-01's `verify:` is a RED-shape assertion and cannot be re-run once T-02 has landed, so it was
    reproduced instead in a throwaway tree at /tmp (since deleted): the bin dir and the test file
    copied out, `factory_workspace.py` replaced with its `HEAD` (3e3147eb) content, a
    `.harness/team-config.yaml` marker added so `harness_boundary` resolves. Result: rc 1, exactly
    four `^FAIL  ` lines, and all four named cases present —
    `dirty tracked: exits 2 before any fetch`, `dirty tracked: refusal line names the path and the
    uncommitted-work condition`, `dirty tracked: the modified file survives byte-identical`,
    `self checkout: refused when clean, naming the self-checkout condition` — with the other four
    BUG-240 cases `ok`. This is the discriminating check: the new cases CAN report red, and they
    go green only with T-02's guard present.
  - the probe touched nothing in the worktree; `git status --porcelain` was byte-identical before
    and after it.
- working memory (a `notes/handoff-build.md` cannot be written from this worktree — check-domain's
  handoff shape gate resolves Authority pointers against the MAIN checkout root, a known,
  already-diagnosed limitation recorded as Q4, so working memory lives in this section):
  - production file `.claude/skills/harness/bin/factory_workspace.py`; `.agents/skills` is a
    symlink to `../.claude/skills`, so there is ONE file with two spellings.
  - test file `tests/unit/test-factory-workspace.py`; 38 checks, 8 of them `BUG-240 `-prefixed.
  - plan.yaml's T-01 and T-02 `intent:` blocks each END with stray tool-call artifact lines
    (`</content>`, `<parameter name="i">…`). They sit inside the block scalar so YAML parses; they
    are NOT instructions and are to be ignored by anyone reading the intent.
  - running the unit suite from an agent tool needs `env -u HARNESS_AGENT_TYPE`, and the runner's
    exit status must be captured in a variable rather than read off its last line.
  - the test file anchors its import two directories up from itself, so a copy of the tree also
    needs a `.harness/team-config.yaml` marker or `factory_config` raises at import time.

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
- Q5 (non-blocking, harness defect, NEW): a lead dispatch that the host kills mid-run leaves its
  `runs/<id>/state.yaml` reading `status: running` forever. Nothing reconciles it, and the next
  orchestrator cannot distinguish it from a live run except by the wall clock. G-07's remedy
  (open the state file) detects the shape but has no way to close it.
