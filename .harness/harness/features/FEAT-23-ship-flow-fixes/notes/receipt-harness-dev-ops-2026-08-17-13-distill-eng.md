# Receipt — harness-dev-ops — FEAT-23 distillation

## check-expertise.sh — verbatim

```
$ bash .claude/skills/harness/bin/check-expertise.sh .harness/expertise/harness-dev-ops.md; echo "EXIT: $?"
OK   .harness/expertise/harness-dev-ops.md
EXIT: 0
```

## Section counts

| Section | Before | After |
|---|---|---|
| Patterns | 3 (P-02, P-03, P-04) | 6 (P-02..P-07) |
| Gotchas | 10 (G-01..G-10) | 10 (G-01..G-10), unchanged |
| Outcomes | 0 | 0, unchanged |
| Open | 0 | 0, unchanged |

Pre-existing entries survived intact: G-01..G-10 and P-02..P-04, byte-unchanged. No displacement —
no section was at cap.

## Accepted entries, by source

**(a) From an observations log** — zero. I have no observations log on FEAT-23 (only orchestrator,
pm and product-lead do); confirmed by dispatch and not re-checked further.

**(b) Surfaced by the digest-skim relay, re-derived by me at source before accepting** — all three:

- **P-05** (from C1). Re-verified against my own V-01 receipt §1 (lines 26-31): the unfiltered
  `git status --porcelain` capture surfaced 3 `M` files the dispatch had not pre-warned about.
  Routed as a Pattern (a practice — capture whole), not a Gotcha, per the dispatch's routing
  correction.
- **P-06** (from C2, judged the sharper of the two, and I agree on independent review). Re-verified
  against the receipt's addendum (lines 132-138): a second `git status --porcelain` taken after
  writing the receipt showed a new untracked file not present in the opening snapshot — concurrent
  activity in the same tree, not a static point in time. Distinct action from P-05 (re-check at the
  end vs. capture unfiltered at the start), so kept as a separate entry rather than merged — merging
  would have lost one of the two actions.
- **P-07** (from C3). Re-verified against receipt §4 (lines 84-107): the dispatch flagged
  `test-check-plan-routes.py`'s `case_20` as a standing gate T-05's own verify structurally could
  not execute, and did not say whether it currently passed. I ran it standalone and reported it
  green with the six `case_20` lines verbatim, explicitly calling that "a fact worth surfacing
  prominently" because the record would otherwise be silent on it.

**(c) Self-derived, absent from the relay entirely** — none accepted. Candidates considered and
rejected below.

## Rejections, with reasons

- **The S1 finding (`item 1`/`item 6` comment text)** — considered and rejected, independently of
  the fact that `harness-backend-dev` already rejected the same substance from the apply side this
  run. Reason: the rule ("a comment citing a plan's numbered list is a landmine for a reader who
  cannot see the plan") is real but is a special case of a broader, already-covered discipline —
  G-07 ("byte-check adjacent content, verify any new comment at the source you touched") already
  reaches the same corrective action. A second entry restating it from a different angle would not
  survive the six-spawns test as an addition; it would just be G-07 again with a narrower example.
- **The bare-`D-NN` misattribution I made and then withdrew** (segment digest, "I withdrew a finding
  of my own after checking it") — considered as a possible Gotcha ("bare decision IDs in a comment
  are scoped to the feature that introduced the surface, not the current feature's decisions doc").
  Rejected: this turns on this repository's specific convention of per-feature bare `D-NN`
  numbering reused across FEAT-18 and FEAT-23's own `D-02`. It is not craft — a repository that has
  never seen this numbering convention gets nothing from the rule — and per the dispatch's explicit
  instruction I am not to work around the unwired repository tier by placing it in the craft file.
  Not accepted anywhere; noted here only so it is not silently dropped.
- **The fake-`gh` isolation check (bypass question, receipt §"Bypass question")** — considered as a
  Gotcha extension of G-04. Rejected as redundant: G-04 already states "check source and the file's
  mode, not the transcript" for proving a runner's properties; verifying that every test case routes
  through an env-var-injected fake binary rather than trusting a module docstring's claim is an
  instance of that same rule, not a new one.

## Displacement

None. No section was at or near cap; nothing was condensed or dropped to make room.
