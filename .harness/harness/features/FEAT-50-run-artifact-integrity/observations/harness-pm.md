# Observations - harness-pm

- 2026-08-31: FEAT-50 cycle-1 send-back: I invoked gen-decisions-index.py --check in SC-14 and T-07 verify; parse_argv rejects every flag but --stdout/--help and exits 2, so both were unrunnable. The docstring itself prescribes --stdout piped into diff against the index (exit 0 clean / 1 drift). Lesson: read the target script argv parser before writing any flag into a verify.
- 2026-08-31: FEAT-50 plan fix. A behavioural `verify:` fixture for check-domain.sh MUST write a
  minimal `.harness/team-config.yaml` into the temp root: harness_boundary DISCARDS a
  HARNESS_PROJECT_DIR carrying no manifest and falls back to the real repo root, so every probe
  exits 0 for the wrong reason and the verify is broken rather than discriminating. Caught only by
  running the block I had just authored against the pre-change tree.
- 2026-08-31: EFF-02's "extra POST read" turned out to be avoidable entirely rather than
  documentable: `has_shape_rules` gates ONLY the POST named-target route (check-domain.sh:1377)
  while the PRE route builds its target unconditionally (:1367-1370), so NOT adding the pattern to
  SHAPE_PATTERNS keeps the PRE rule working and closes the wasteful route. Read the gate's own
  route construction before accepting a plan's claim about which routes a pattern list reaches.
- 2026-08-31: an `edit` PUT anchored on line numbers read BEFORE two intervening edits silently
  overwrote `status: pending` with a verify line. The tag was stale by two edits. Re-read the exact
  region immediately before every single-line PUT, not just before multi-line ones.
- 2026-08-31: FEAT-50 panel goal-check c0. Grading a plan against the INTAKE rather than the BRIEF found four things a BRIEF-relative read cannot: the intake's own routing table pre-authorised T-08's shape (so the scope-creep suspicion died on the operator's own words), and three T-03 placement defects. The highest-yield move was re-deriving every placement anchor in an intent block against the real gate source: 'inside if _run_domain:' named the import guard, not domain_check()'s allow branch, and 'the single call site' named two of three targets construction sites. Anchors written from memory of a file's shape are the dead-remedy generator.
- 2026-08-31 (FEAT-50 plan fix c1): an absence-grep whose pattern carries parentheses is non-discriminating under this environment's grep — 'os.path.basename(worktree)' returned 0 against the file that contains it, '-cF' returned 1. Measured both directions before writing the criterion.
- 2026-08-31 (FEAT-50): a ruling recorded in plan.yaml approval.rulings is validated against panel.findings (check-state.sh:189-204) and needs finding/who/date; an operator answer belongs in the DEC-44 answers file under notes/, where no gate reads it. An earlier dispatch instructed the opposite and it would have reddened the feature at signature.
- 2026-08-31 (FEAT-50): never write a placeholder token (SRC_DEFS) into a verify: block for the doer to substitute — the lead carries verify verbatim, so the placeholder is a NameError at run time. Rewrote the bound as a runnable assertion.
- 2026-08-31: panel digest for FEAT-50 cycle 0 disagreed with itself on count — BLUF prose says "Six findings survive assessment", the authoritative yaml block lists seven (2 high, 2 med, 3 low). Transcribed all seven per the yaml block; the prose undercount looks like the two corroborated reports being merged into one entry after the BLUF was written.
- 2026-08-31: check-state.sh INV-32 expects three readers ({should-not-exist, scope, goalcheck}) but the plan-panel team only runs two — goalcheck runs in the earlier product segment and so is absent from the panel digest. pm must supply that third reader entry from outside the digest or INV-32 hard-fails on an unrecorded reader.
- 2026-08-31: .harness/ is UNTRACKED in the FEAT-50 worktree, so "git diff shows only plan.yaml" is a vacuous verification — the whole feature dir shows as ?? and diff prints nothing. Verify scope with git status --porcelain plus mtimes instead.
