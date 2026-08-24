# Receipt — harness-documentor — FEAT-35 T-04

**DEC-201 is written and the index regenerates clean. `T-04-PASS` printed.**

## Gate — run verbatim from T-04's `verify:` in `plan.yaml`

```
python3 .claude/skills/harness/bin/gen-decisions-index.py --stdout | diff - .harness/harness/docs/DECISIONS-INDEX.md && grep -q "^- DEC-201 " .harness/harness/docs/DECISIONS-INDEX.md && echo T-04-PASS
```

Output, verbatim and complete (the `diff` emitted nothing, so the single line below is the whole
output):

```
T-04-PASS
```

The command string was cross-checked character-for-character against T-04's `verify:` block in
`.harness/harness/features/FEAT-35-orchestrator-stop-and-wake/plan.yaml` before running. It matches.

## What changed

- `.harness/harness/docs/DECISIONS.md` — `## DEC-201 — An orchestrator never waits: every dispatch
  ends its turn, and the platform's wake is measured, not documented`, appended at the end of the
  file, **after DEC-200** (FEAT-26's, at `DECISIONS.md:6729`). T-04's intent says "after DEC-199";
  that wording predates FEAT-26 landing 200 and the dispatch corrected it. Entry runs 63 lines
  against DEC-199's 60 and DEC-200's 50 — inside the neighbours' band.
- `.harness/harness/docs/DECISIONS-INDEX.md` — one new row, regenerated, with the ` :: ` summary
  hand-written (regeneration seeded it `⚠ RULING PENDING`). Auto-derived tags
  `[orchestrator,dispatch,state,budget]`, refs `DEC-118 DEC-120 DEC-148 DEC-158 DEC-159 DEC-198
  DEC-199`.

`git diff --stat` on `.harness/harness/docs/`: 65 insertions, 0 deletions across the two files. No
collateral edit to neighbouring entries.

## Substance the entry pins

- The three 2026-08-23 probes are the authority and the published sub-agent documentation says the
  opposite — the entry states that in those terms rather than reconciling them.
- The stalling incident numbers (354 of 450 Bash calls, 342 of them `echo hold`, killed by the
  platform's 600s watchdog) live here and not in the playbook, per DEC-158.
- The two-Bash-call self-identification, why it cannot be collapsed into one, and that it needed no
  new code (measured at `569d417`).
- **The open measurement is recorded as open.** SC-05's 1057.1s survived gap
  (`15:34:10.019Z` → `15:51:47.145Z`, 0 keep-alive Bash calls, 115-sidecar sweep with exactly two
  failures) appears **with its limit beside it**: that run was under a dispatch-level override, not
  under the rewritten playbook, so it proves the behaviour survives a long wait and does NOT prove
  the rewritten playbook causes it. Whether one post-merge run is needed is written down as a
  reviewer's call, not resolved.
- Branch `chore/744-never-wait-for-a-lead` recorded as absorbed and abandoned.

## Not touched, deliberately

`.claude/skills/harness/SKILL.md` (already reads `(DEC-201)` at line 50), `plan.yaml`,
`feature.json`, `STATE.md`, `BRIEF.md`, anything under `.claude/skills/harness/bin/`. No DEC-174
amendment, no DEC-NN collision guard, no board card moved. Nothing committed — HEAD is unmoved at
`d7e8c66`.

## For the reviewer

The one thing to check on reading the entry: the SC-05 paragraph's number and its override caveat
are a single unit. If a later edit lifts the 1057.1s figure out of that paragraph, it becomes a
causal claim the measurement does not support.
