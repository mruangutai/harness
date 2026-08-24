```yaml
VERDICT: PASS
DIGEST:
  headline: "MF-01 cleared: a same-size/same-mtime CPython bytecode cache made the mutation test flaky; the isolated child now imports source and T-01 exits 0."
  team: engineering
  steps_run: 1
  cycles_used: 0
  members:
    - { step: MF-01, persona: harness-dev-ops, verdict: PASS, headline: "Proved the pre-existing bytecode-cache failure, corrected the isolated mutation fixture, and cleared the exact T-01 gate.", files_touched: [.agents/skills/harness/bin/test-bash-write-guard.py, .harness/harness/features/FEAT-36-merge-gitignore-coverage/notes/receipt-harness-dev-ops-review-fix-eng.md] }
  targeted_outcomes:
    current_before_fix: "Direct test-bash-write-guard.py exited 0 with 27/27, demonstrating the transient side; the initial all-kinds rerun reproduced the ONE IMPLEMENTATION 0/0 failure."
    base_control: "A clean temporary git-archive export of 0fa8f336e55dc57bca09a9f7df0524a35195ee7e exited 1 with 26/27 and ONE IMPLEMENTATION bash=0/write=0; export cleanup exited 0 and worktree HEAD was not moved."
    causal_control: "PYTHONDONTWRITEBYTECODE=1 made the unchanged targeted program exit 0 with ONE IMPLEMENTATION (2, 2), confirming stale timestamp-validated bytecode."
    current_after_fix: "Exact T-01 gate exited 0; bash-write-guard passed 27/27 and merge-gitignore passed 7/7 directly and in the runner."
  diagnosis: "The controlled mutant rewrites equal-length Python source within one filesystem timestamp tick. CPython can accept the baseline timestamp/size-validated .pyc, so both child routes observe unmutated code and return 0. Setting PYTHONDONTWRITEBYTECODE=1 only for isolated mutation children forces source import while retaining the mutation and required (2, 2) assertion."
  source_objects_before: { test-bash-write-guard.py: 5f494142, bash-write-guard.sh: 0b1bbb89, check-domain.sh: c6b581e, harness_boundary.py: de9689e, harness_yaml.py: a5c5367, test-merge-gitignore.py: 06507a2, run-unit-tests.sh: b688261, harness.json: ca29860 }
  source_objects_after: { test-bash-write-guard.py: a4ff275, bash-write-guard.sh: 0b1bbb89, check-domain.sh: c6b581e, harness_boundary.py: de9689e, harness_yaml.py: a5c5367, test-merge-gitignore.py: 06507a2, run-unit-tests.sh: b688261, harness.json: ca29860 }
  prescribed_command: |-
    python3 .agents/skills/harness/bin/test-merge-gitignore.py &&
    .agents/skills/harness/bin/run-unit-tests.sh --kind all
  prescribed_command_exit: 0
  verification_evidence: ".harness/harness/features/FEAT-36-merge-gitignore-coverage/notes/receipt-harness-dev-ops-review-fix-eng.md"
  must_fix: []
  files_touched: [.agents/skills/harness/bin/test-bash-write-guard.py, .harness/harness/features/FEAT-36-merge-gitignore-coverage/notes/receipt-harness-dev-ops-review-fix-eng.md, .harness/harness/features/FEAT-36-merge-gitignore-coverage/runs/review-fix-eng/state.yaml, .harness/harness/features/FEAT-36-merge-gitignore-coverage/runs/review-fix-eng/digest.md]
  branch: FEAT-36-merge-gitignore-coverage
  open_questions: []
  escalations: []
  expertise_update: []
  sc_status: []
artifact: .harness/harness/features/FEAT-36-merge-gitignore-coverage/runs/review-fix-eng/digest.md
```

MF-01 required a minimal correction to the pre-existing mutation fixture, not to FEAT-36's three product files. The dev-ops receipt contains the bounded provenance and exact-command evidence; F-02 was not revisited.
