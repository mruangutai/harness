# Observations — harness-orchestrator — FEAT-25-claim-feature-root

- 2026-08-19: The blocking qa gate produced two contradictory returns and neither agent could settle
  it. `harness-qa` measured `--kind integration` exit 1 and called the kind satisfied by attribution
  (the specific required test passed, the failing script was orthogonal). `harness-validator-lead`
  refused that step — correctly, citing harness.json's rule that the only soft skip is a signed
  `status: excluded`, never one inferred at gate time — and returned FAIL. Both were right about
  their own half. What broke the tie was that a lead holds no Bash and I do: in a throwaway worktree
  at the pinned commit the same configured command exits 0 with all 12 scripts PASS. The gate grades
  a commit, not a working tree, and someone else's uncommitted edit was the entire red.
- 2026-08-19: `validate-digest.py --hook` forced or nearly forced a premature lead close FIVE times
  in one feature, reported independently by four different hosts. Twice it produced a digest that
  was materially wrong about its own run — an ESCALATE claiming nothing was measured while its
  member's artifact sat complete on disk, and a DRAFT with `expertise_update: []` while its members'
  ops were genuinely pending. My G-07 covers the detection; the cost is that every lead now spends
  context holding its turn open with reads as a workaround.
- 2026-08-19: The panel's signed digest carried a false claim — that the report-loop fail-open
  existed at four sites in two files. The validator lead falsified it during distillation, against
  its own earlier position, and I confirmed by direct read: `test-check-state.py` keeps
  `allok = allok and ok` outside the guard and contains zero `fails += 1`. One site, one file. A
  "same shape elsewhere" sweep that matches on the surrounding conditional rather than on the
  accumulator generalises a finding onto code that does not have it.
- 2026-08-19: T-02 depended on T-01 and edited the same two files, so no honest per-task hunk split
  existed in the working tree. I committed both under one dual-tagged subject and said why in the
  message rather than attributing T-02's hunks to T-01. Nothing in the harness parses the tag, so
  the only cost of faking it would have been to the record.
- 2026-08-19: The dispatch named five held-dirt paths; `git status` at branch-cut showed seven, two
  of them tracked docs the dispatch never mentioned. Committing by explicit pathspec was what made
  that harmless. Also, an untracked note outside every agent's domain vanished from the tree during
  the run and is unrecoverable — untracked means git holds no copy.
