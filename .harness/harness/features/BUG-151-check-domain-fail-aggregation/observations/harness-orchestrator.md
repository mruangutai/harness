# Observations - harness-orchestrator

- 2026-09-07: BUG-151. A handoff note written INSIDE a worktree cannot use `plan-task:` or
  `brief-sc:` authorities. handoff_done_when.py relativises the note against the worktree
  (FEATURE_RE anchors on `^.harness/`) but resolves `root` to the MAIN checkout, so
  feature_dir lands at <main>/.harness/harness/features/<FEAT>, which does not exist.
  `approval:` and `finding:` take an explicit path and DO work if spelled relative to the
  main root — i.e. beginning `.claude/worktrees/<repo>/<FEAT>/`. Absolute paths are refused
  outright ("is absolute").
- 2026-09-07: BUG-151. teams/plan-panel.yaml declares two readers; check-state.sh INV-32
  (line 534) expects three, including `goalcheck`. The goalcheck reader row has to be
  transcribed into panel.readers by hand after the product segment, or the plan goes `bad`
  the moment it is signed. Found only because pm read the invariant rather than the team file.
- 2026-09-07: BUG-151. feature-json-merge.py append-run REFUSES an entry without a non-empty
  `agent` (FEAT-31 SC-07) and the refusal names runs[0], not the entry you passed — it
  re-validates the whole array. The templates/feature.json example does not show the key.
- 2026-09-07: BUG-151. A crashed dispatch's leftover receipt named T-01 only, but `git diff --stat` on the one touched file showed 103 insertions and 46 DELETIONS against a task declared "purely ADDITIVE". The deletion count was the whole tell: it did not match T-01's shape, and reading the diff showed T-02's code had also landed with no receipt. A receipt describes the moment it was written, not the disk; reconciling a resume by diff SHAPE against the task's declared change_type caught a full task's worth of unrecorded work that the receipt actively denied ("the false comment ... was left untouched").
- 2026-09-07: BUG-151. Both tasks' `verify:` commands passed on the recovered disk state, and that was still not enough to accept the work: the deliverable was a SAFEGUARD, and every verify a safeguard has is a green one. The only measurement that separated a live gate from dead code was monkeypatching a real block to print a column-0 FAIL while returning 0 and watching main() return 1 through len(problems) rather than through arithmetic. Cost one 35s in-memory probe, no disk mutation. For any task whose product is a gate, budget that probe at the orchestrator tier instead of trusting the member's own red proof.
- 2026-09-07: BUG-151. STATE.md's shape gate rejects a `## Next` heading outright — the file is `## Current` + `## Open Questions` and nothing else (DEC-150 / SPEC §2). The next action has to live as prose INSIDE `## Current`. Wrote the section, got BLOCKED, refolded. Worth writing it folded the first time when the handoff-note route is unavailable from a worktree and STATE.md is carrying the working memory.
- 2026-09-07: BUG-151. A lead's job exited 1 on a null-data `yield` while its final turn carried a complete, well-formed VERDICT/DIGEST block naming a PASS. Read the exit code as yield MECHANICS, not as a work failure, and verified the digest's claims on disk instead — HEAD unmoved, porcelain clean, receipt present and complete. Had I routed the exit 1 as a FAIL it would have bought a fix cycle for a segment that was already done.
