# Probe — handoff comprehension (locally_run, BRIEF verification gap)

Run by the main session on a credentialled host on 2026-11-21:
`python3 tests/manual/probe-handoff-comprehension.py` from the feature worktree at `bf09458a`, with
`omp` at `/Users/molchairuangutai/.bun/bin/omp` and model `anthropic/claude-sonnet-5`. Exit 0 in 18 s,
2 live model calls.

- Note probed: `notes/handoff-build.md` (seq-4), sha256 `d6d270f30849aad6161e55c470a7c219470d5dbcc5348c59f94c0b277060352e`.
- Required facts (4): the T-03 scope line, `brief-perspective:…BRIEF.md#orchestrator`, `plan-task:T-03.verify` and `plan-task:T-04.verify`.

| Arm | Coverage | Complete answers |
|---|---|---|
| as-written | 4/4 | 1/1 |
| done-when-stripped | 0/4 | 0/1 |

Overall: 1/2 complete answers. The as-written note gave the reader every required authority. With the
`Done when` block stripped, the reader still named the next action but substituted its own authorities
(DEC-174, build-phase.md) for the signed ones. This is evidence only: the probe always exits 0 and has
no pass bar.
