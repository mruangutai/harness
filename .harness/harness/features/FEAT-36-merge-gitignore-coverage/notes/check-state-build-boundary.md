# Canonical state check — build boundary

The canonical `.agents/skills/harness/bin/check-state.sh` was run before the trace commit. It returned exit 1 with three FEAT-36 findings:

```text
FEAT-36-merge-gitignore-coverage: a validator run exists but review_sha is not pinned — reviewers would diff HEAD (the GAP-7 failure).
INV-26 FEAT-36-merge-gitignore-coverage T-01 (issue #817): plan says done, so the card should read Done — the board reads Building.
INV-26 FEAT-36-merge-gitignore-coverage parent (issue #816): the plan derives Review — the board reads Building.
```

These are the expected transient at this explicitly requested build boundary. The first treats the pre-pin, build-phase `harness-qa` matrix gate as a review run even though the playbook requires QA before simplify and before the review pin. The other two arise because DEC-196 amendment 4 / D-23 forbids per-commit `close-task`, while the validation successor—not this build phase—must pin `review_sha` and run `gh-sync.py status <feature-dir> Review` at panel kickoff. No mirror retry, `close-task`, Review transition, review panel, or review pin was performed to silence the checker. All other reported violations/notes concerned pre-existing feature artifacts outside FEAT-36.
